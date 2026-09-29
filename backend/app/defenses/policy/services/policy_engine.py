"""Complete PolicyEngine implementing IPolicyEngine."""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ....shared.logging_config import get_logger
from ...shared.events.event_bus import DomainEvent, EventBus, EventType, EventSeverity
from ...shared.monitoring.performance import PerformanceMonitor

from ..domain.entities.policy_entity import (
    PolicyCategory,
    PolicyDecision,
    PolicyDecisionResult,
    PolicyStatus,
    SecurityPolicy,
)
from ..domain.events.policy_events import (
    PolicyDecisionEvent,
    PolicyEvaluatedEvent,
)
from ..domain.interfaces.policy_engine_interface import IPolicyEngine
from ..registry.policy_registry import PolicyRegistry

logger = get_logger(__name__)


class PolicyEngine(IPolicyEngine):
    """Central policy evaluation engine.

    Loads applicable policies from the registry, evaluates them in priority
    order, produces :class:`PolicyDecision` results, publishes events via
    the :class:`EventBus`, and records performance metrics.

    Individual policy failures are caught and logged without crashing the
    overall evaluation cycle.
    """

    def __init__(
        self,
        registry: PolicyRegistry,
        event_bus: EventBus,
        performance_monitor: PerformanceMonitor,
    ) -> None:
        self._registry = registry
        self._event_bus = event_bus
        self._performance_monitor = performance_monitor

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    async def evaluate(
        self,
        event_type: str,
        context: dict[str, Any],
        correlation_id: str = "",
    ) -> list[PolicyDecision]:
        """Evaluate an event against all applicable enabled policies.

        Parameters
        ----------
        event_type:
            The type of event to evaluate.
        context:
            Contextual data for evaluation.
        correlation_id:
            Optional correlation ID for distributed tracing.

        Returns
        -------
        list[PolicyDecision]
            One decision per applicable policy that was successfully
            evaluated.
        """
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        self._performance_monitor.start_timer(f"policy.evaluate.{event_type}")

        all_policies = await self._registry.get_all()
        applicable = [
            p
            for p in all_policies
            if p.is_usable()
            and (
                not p.supported_event_types
                or event_type in p.supported_event_types
            )
        ]

        decisions: list[PolicyDecision] = []

        for policy in applicable:
            decision = await self._evaluate_single_policy(
                policy, event_type, context, correlation_id
            )
            if decision is not None:
                decisions.append(decision)

        timer_result = self._performance_monitor.stop_timer(
            f"policy.evaluate.{event_type}"
        )

        # Publish aggregate evaluation event
        try:
            eval_event = PolicyEvaluatedEvent(
                event_type_evaluated=event_type,
                result=f"{len(decisions)} policies evaluated",
                execution_time_ms=timer_result.duration_ms,
                correlation_id=correlation_id,
            )
            await self._event_bus.publish(
                DomainEvent(
                    event_type=EventType.POLICY_EVALUATED,
                    module="defenses.policy",
                    severity=EventSeverity.INFO,
                    message=f"Evaluated {len(decisions)} policies for '{event_type}'",
                    correlation_id=correlation_id,
                    metadata={
                        "event_type": event_type,
                        "policies_evaluated": len(applicable),
                        "decisions_produced": len(decisions),
                    },
                )
            )
        except Exception:
            logger.exception("failed_to_publish_evaluation_event")

        return decisions

    async def _evaluate_single_policy(
        self,
        policy: SecurityPolicy,
        event_type: str,
        context: dict[str, Any],
        correlation_id: str,
    ) -> Optional[PolicyDecision]:
        """Evaluate a single policy, catching all exceptions."""
        start = time.perf_counter()

        try:
            config = policy.configuration
            result = self._compute_decision(policy, event_type, context)
            elapsed_ms = (time.perf_counter() - start) * 1000

            decision = PolicyDecision(
                decision_id=str(uuid.uuid4()),
                policy_id=policy.policy_id,
                timestamp=datetime.now(timezone.utc),
                result=result,
                reason=f"Policy '{policy.name}' evaluated '{event_type}'",
                severity=self._severity_for_result(result),
                risk_score=policy.risk_weight if result == PolicyDecisionResult.DENY else 0.0,
                execution_time_ms=elapsed_ms,
                correlation_id=correlation_id,
                metadata={
                    "policy_name": policy.name,
                    "policy_category": policy.category.value,
                },
            )

            # Record metrics
            self._registry.record_evaluation(
                policy.policy_id, result.value, elapsed_ms
            )
            self._performance_monitor.record_metric(
                f"policy.{policy.policy_id}.evaluate",
                elapsed_ms,
                unit="ms",
            )

            # Publish per-policy event
            try:
                decision_event = PolicyDecisionEvent(
                    policy_id=policy.policy_id,
                    decision=result.value,
                    reason=decision.reason,
                    risk_score=decision.risk_score,
                    correlation_id=correlation_id,
                )
                await self._event_bus.publish(
                    DomainEvent(
                        event_type=EventType.POLICY_DECISION,
                        module="defenses.policy",
                        severity=EventSeverity.INFO,
                        message=decision.reason,
                        correlation_id=correlation_id,
                        metadata=decision_event.metadata,
                    )
                )
            except Exception:
                logger.exception("failed_to_publish_decision_event")

            return decision

        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000
            self._registry.record_error()
            logger.exception(
                "policy_evaluation_failed",
                policy_id=policy.policy_id,
                error=str(exc),
            )
            return PolicyDecision(
                decision_id=str(uuid.uuid4()),
                policy_id=policy.policy_id,
                timestamp=datetime.now(timezone.utc),
                result=PolicyDecisionResult.UNKNOWN,
                reason=f"Policy evaluation failed: {exc}",
                severity="error",
                execution_time_ms=elapsed_ms,
                correlation_id=correlation_id,
            )

    def _compute_decision(
        self,
        policy: SecurityPolicy,
        event_type: str,
        context: dict[str, Any],
    ) -> PolicyDecisionResult:
        """Compute the decision for a policy based on its configuration.

        This is a framework-level implementation that checks thresholds and
        timing rules defined in the policy configuration.  Custom logic
        should extend this via subclassing or plugin policies.
        """
        config = policy.configuration

        # Check thresholds
        for threshold_key, threshold_value in config.thresholds.items():
            context_value = context.get(threshold_key)
            if context_value is not None:
                try:
                    if float(context_value) >= float(threshold_value):
                        return PolicyDecisionResult.DENY
                except (TypeError, ValueError):
                    pass

        # Check timing constraints
        for timing_key, timing_value in config.timing.items():
            context_value = context.get(timing_key)
            if context_value is not None and timing_value:
                try:
                    from datetime import datetime as dt_type
                    event_time = dt_type.fromisoformat(str(context_value))
                    max_seconds = float(timing_value)
                    now = datetime.now(timezone.utc)
                    if hasattr(event_time, 'tzinfo') and event_time.tzinfo is None:
                        event_time = event_time.replace(tzinfo=timezone.utc)
                    elapsed = (now - event_time).total_seconds()
                    if elapsed > max_seconds:
                        return PolicyDecisionResult.WARN
                except (ValueError, TypeError, OSError):
                    pass

        return PolicyDecisionResult.ALLOW

    def _severity_for_result(self, result: PolicyDecisionResult) -> str:
        """Map a decision result to a severity string."""
        mapping = {
            PolicyDecisionResult.ALLOW: "info",
            PolicyDecisionResult.DENY: "warning",
            PolicyDecisionResult.WARN: "warning",
            PolicyDecisionResult.MONITOR: "info",
            PolicyDecisionResult.IGNORE: "debug",
            PolicyDecisionResult.REVIEW: "info",
            PolicyDecisionResult.UNKNOWN: "error",
        }
        return mapping.get(result, "info")

    # ------------------------------------------------------------------
    # Policy management (delegates to registry)
    # ------------------------------------------------------------------

    async def register_policy(self, policy: SecurityPolicy) -> bool:
        """Register a new policy."""
        success = await self._registry.register(policy)
        if success:
            self._performance_monitor.increment_counter("policy.registered")
        return success

    async def unregister_policy(self, policy_id: str) -> bool:
        """Remove a policy."""
        success = await self._registry.unregister(policy_id)
        if success:
            self._performance_monitor.increment_counter("policy.unregistered")
        return success

    async def enable_policy(self, policy_id: str) -> bool:
        """Enable a policy."""
        success = await self._registry.enable(policy_id)
        if success:
            self._performance_monitor.increment_counter("policy.enabled")
        return success

    async def disable_policy(self, policy_id: str) -> bool:
        """Disable a policy."""
        success = await self._registry.disable(policy_id)
        if success:
            self._performance_monitor.increment_counter("policy.disabled")
        return success

    async def get_policy(self, policy_id: str) -> Optional[SecurityPolicy]:
        """Return a policy by ID."""
        return await self._registry.get(policy_id)

    async def list_policies(
        self,
        category: Optional[PolicyCategory] = None,
        status: Optional[PolicyStatus] = None,
    ) -> list[SecurityPolicy]:
        """Return policies, optionally filtered."""
        all_policies = await self._registry.get_all()
        result = all_policies

        if category is not None:
            result = [p for p in result if p.category == category]
        if status is not None:
            result = [p for p in result if p.status == status]

        return result

    async def update_policy(
        self, policy_id: str, data: dict[str, Any]
    ) -> Optional[SecurityPolicy]:
        """Update a policy's fields."""
        policy = await self._registry.get(policy_id)
        if policy is None:
            return None

        from ..domain.entities.policy_entity import PolicyCategory as PC, PolicyConfiguration

        if "name" in data:
            policy.name = data["name"]
        if "description" in data:
            policy.description = data["description"]
        if "category" in data:
            policy.category = PC(data["category"])
        if "priority" in data:
            policy.priority = data["priority"]
        if "configuration" in data:
            policy.configuration = PolicyConfiguration.from_dict(data["configuration"])
        if "dependencies" in data:
            policy.dependencies = data["dependencies"]
        if "risk_weight" in data:
            policy.risk_weight = data["risk_weight"]
        if "supported_event_types" in data:
            policy.supported_event_types = data["supported_event_types"]
        if "metadata" in data:
            policy.metadata = data["metadata"]

        policy.updated_at = datetime.now(timezone.utc)
        policy.version += 1

        return policy

    def get_metrics(self) -> dict[str, Any]:
        """Return engine and registry metrics."""
        registry_metrics = self._registry.get_metrics()
        return {
            **registry_metrics,
            "engine_status": "active",
        }
