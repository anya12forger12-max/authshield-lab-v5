"""Complete in-memory policy registry implementing IPolicyRegistry."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ....shared.logging_config import get_logger
from ..domain.entities.policy_entity import (
    PolicyCategory,
    PolicyStatus,
    SecurityPolicy,
    VALID_STATUS_TRANSITIONS,
)
from ..domain.interfaces.policy_engine_interface import IPolicyRegistry

logger = get_logger(__name__)


class PolicyRegistry(IPolicyRegistry):
    """In-memory registry for security policies.

    Provides CRUD operations, search/filter, enable/disable, import/export,
    and basic metrics.  Since policies are configuration data (not persistent
    entities) this registry holds everything in memory.
    """

    def __init__(self) -> None:
        self._policies: dict[str, SecurityPolicy] = {}
        self._evaluation_count: int = 0
        self._evaluations_by_policy: dict[str, int] = {}
        self._evaluations_by_result: dict[str, int] = {}
        self._total_evaluation_time_ms: float = 0.0
        self._error_count: int = 0

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    async def register(self, policy: SecurityPolicy) -> bool:
        """Register a new policy.

        Parameters
        ----------
        policy:
            The policy to register.  If ``policy_id`` is empty a new UUID
            is generated.

        Returns
        -------
        bool
            ``True`` on success.
        """
        if not policy.policy_id:
            policy.policy_id = str(uuid.uuid4())

        if policy.policy_id in self._policies:
            logger.warning(
                "policy_already_registered",
                policy_id=policy.policy_id,
            )
            return False

        now = datetime.now(timezone.utc)
        policy.created_at = now
        policy.updated_at = now

        self._policies[policy.policy_id] = policy
        logger.info(
            "policy_registered",
            policy_id=policy.policy_id,
            name=policy.name,
        )
        return True

    async def unregister(self, policy_id: str) -> bool:
        """Remove a policy by ID.

        Returns
        -------
        bool
            ``True`` if the policy existed and was removed.
        """
        if policy_id not in self._policies:
            return False

        del self._policies[policy_id]
        self._evaluations_by_policy.pop(policy_id, None)
        logger.info("policy_unregistered", policy_id=policy_id)
        return True

    async def get(self, policy_id: str) -> Optional[SecurityPolicy]:
        """Return a policy by ID, or ``None``."""
        return self._policies.get(policy_id)

    async def get_all(self) -> list[SecurityPolicy]:
        """Return all registered policies sorted by priority."""
        return sorted(self._policies.values(), key=lambda p: p.priority)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    async def search(
        self,
        query: str,
        category: Optional[PolicyCategory] = None,
    ) -> list[SecurityPolicy]:
        """Search policies by name or description.

        Parameters
        ----------
        query:
            Case-insensitive substring to match.
        category:
            Optional category filter.
        """
        query_lower = query.lower()
        results: list[SecurityPolicy] = []

        for policy in self._policies.values():
            if query_lower:
                name_match = query_lower in policy.name.lower()
                desc_match = query_lower in policy.description.lower()
                if not name_match and not desc_match:
                    continue

            if category is not None and policy.category != category:
                continue

            results.append(policy)

        return sorted(results, key=lambda p: p.priority)

    # ------------------------------------------------------------------
    # Enable / disable
    # ------------------------------------------------------------------

    async def enable(self, policy_id: str) -> bool:
        """Enable a policy.

        Returns
        -------
        bool
            ``True`` if the policy was found and successfully transitioned
            to enabled.
        """
        policy = self._policies.get(policy_id)
        if policy is None:
            return False

        allowed = VALID_STATUS_TRANSITIONS.get(policy.status, set())
        if PolicyStatus.ENABLED not in allowed:
            logger.warning(
                "invalid_status_transition",
                policy_id=policy_id,
                current=policy.status.value,
                target="enabled",
            )
            return False

        policy.status = PolicyStatus.ENABLED
        policy.updated_at = datetime.now(timezone.utc)
        logger.info("policy_enabled", policy_id=policy_id)
        return True

    async def disable(self, policy_id: str) -> bool:
        """Disable a policy.

        Returns
        -------
        bool
            ``True`` if the policy was found and successfully transitioned
            to disabled.
        """
        policy = self._policies.get(policy_id)
        if policy is None:
            return False

        allowed = VALID_STATUS_TRANSITIONS.get(policy.status, set())
        if PolicyStatus.DISABLED not in allowed:
            logger.warning(
                "invalid_status_transition",
                policy_id=policy_id,
                current=policy.status.value,
                target="disabled",
            )
            return False

        policy.status = PolicyStatus.DISABLED
        policy.updated_at = datetime.now(timezone.utc)
        logger.info("policy_disabled", policy_id=policy_id)
        return True

    # ------------------------------------------------------------------
    # Import / export
    # ------------------------------------------------------------------

    async def export_policies(self) -> dict[str, Any]:
        """Export all policies as a serialisable dictionary."""
        return {
            "policies": [p.to_dict() for p in self._policies.values()],
            "total": len(self._policies),
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

    async def import_policies(self, data: dict) -> int:
        """Import policies from a previously exported dictionary.

        Parameters
        ----------
        data:
            Dictionary in the format produced by :meth:`export_policies`.

        Returns
        -------
        int
            The number of policies successfully imported.
        """
        imported = 0
        for item in data.get("policies", []):
            try:
                category = PolicyCategory(item.get("category", "authentication"))
                status = PolicyStatus(item.get("status", "draft"))

                from ..domain.entities.policy_entity import PolicyConfiguration

                config_data = item.get("configuration", {})
                configuration = PolicyConfiguration.from_dict(config_data)

                policy = SecurityPolicy(
                    policy_id=item.get("policy_id", str(uuid.uuid4())),
                    name=item.get("name", ""),
                    description=item.get("description", ""),
                    version=item.get("version", 1),
                    category=category,
                    priority=item.get("priority", 100),
                    status=status,
                    author=item.get("author", "system"),
                    configuration=configuration,
                    dependencies=item.get("dependencies", []),
                    execution_order=item.get("execution_order", 0),
                    risk_weight=item.get("risk_weight", 1.0),
                    metadata=item.get("metadata", {}),
                    supported_event_types=item.get("supported_event_types", []),
                )

                if await self.register(policy):
                    imported += 1
            except (KeyError, ValueError) as exc:
                logger.warning("policy_import_error", item=item, error=str(exc))

        logger.info("policies_imported", count=imported)
        return imported

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def record_evaluation(
        self, policy_id: str, result: str, duration_ms: float
    ) -> None:
        """Record a policy evaluation for metrics purposes.

        Parameters
        ----------
        policy_id:
            The evaluated policy's ID.
        result:
            The decision result string.
        duration_ms:
            Evaluation duration in milliseconds.
        """
        self._evaluation_count += 1
        self._evaluations_by_policy[policy_id] = (
            self._evaluations_by_policy.get(policy_id, 0) + 1
        )
        self._evaluations_by_result[result] = (
            self._evaluations_by_result.get(result, 0) + 1
        )
        self._total_evaluation_time_ms += duration_ms

    def record_error(self) -> None:
        """Increment the error counter."""
        self._error_count += 1

    def get_metrics(self) -> dict[str, Any]:
        """Return registry-level metrics."""
        avg_time = (
            self._total_evaluation_time_ms / self._evaluation_count
            if self._evaluation_count > 0
            else 0.0
        )
        active_count = sum(
            1 for p in self._policies.values()
            if p.status == PolicyStatus.ENABLED
        )
        return {
            "total_policies": len(self._policies),
            "active_policies": active_count,
            "total_evaluations": self._evaluation_count,
            "evaluations_by_policy": dict(self._evaluations_by_policy),
            "evaluations_by_result": dict(self._evaluations_by_result),
            "average_evaluation_time_ms": round(avg_time, 3),
            "error_count": self._error_count,
        }

    # ------------------------------------------------------------------
    # Count (convenience)
    # ------------------------------------------------------------------

    def count(self) -> int:
        """Return the total number of registered policies."""
        return len(self._policies)
