"""Authorization engine - prepares RBAC/ABAC/PBAC architecture (not yet enforced)."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from ...shared.logging_config import get_logger

logger = get_logger(__name__)


class AuthorizationDecision(str, Enum):
    """Possible outcomes of an authorization evaluation."""

    ALLOW = "allow"
    DENY = "deny"
    NOT_APPLICABLE = "not_applicable"
    ERROR = "error"


@dataclass
class AuthorizationRequest:
    """Input payload for an authorization check."""

    user_id: str = ""
    permission: str = ""
    resource_type: str = ""
    resource_id: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    correlation_id: str = ""


@dataclass
class AuthorizationResult:
    """Output of an authorization evaluation."""

    decision: AuthorizationDecision = AuthorizationDecision.NOT_APPLICABLE
    reason: str = ""
    policy_id: Optional[str] = None
    evaluation_time_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class IAuthorizationPolicy(ABC):
    """Interface for authorization policies - Strategy Pattern.

    Each concrete policy evaluates an :class:`AuthorizationRequest` and
    returns an :class:`AuthorizationResult`.
    """

    @abstractmethod
    def evaluate(self, request: AuthorizationRequest) -> AuthorizationResult:
        """Evaluate the authorization request against this policy."""
        ...

    @abstractmethod
    def get_policy_id(self) -> str:
        """Return a unique identifier for this policy."""
        ...

    @abstractmethod
    def get_policy_name(self) -> str:
        """Return a human-readable name for this policy."""
        ...


class RBACPolicy(IAuthorizationPolicy):
    """Role-Based Access Control policy.

    Evaluates whether a user's assigned roles grant the requested
    permission based on a role-to-permission mapping.
    """

    def __init__(self, role_permissions: dict[str, set[str]]) -> None:
        self._role_permissions = role_permissions

    def evaluate(self, request: AuthorizationRequest) -> AuthorizationResult:
        """Evaluate RBAC permissions.

        Checks if any of the user's roles (provided via context ``"roles"``)
        grants the requested permission.
        """
        start = time.perf_counter()

        roles: list[str] = request.context.get("roles", [])
        if not roles:
            return AuthorizationResult(
                decision=AuthorizationDecision.DENY,
                reason="No roles assigned to user",
                policy_id=self.get_policy_id(),
                evaluation_time_ms=(time.perf_counter() - start) * 1000,
            )

        for role in roles:
            permissions = self._role_permissions.get(role, set())
            if request.permission in permissions:
                elapsed_ms = (time.perf_counter() - start) * 1000
                return AuthorizationResult(
                    decision=AuthorizationDecision.ALLOW,
                    reason=f"Role '{role}' grants permission '{request.permission}'",
                    policy_id=self.get_policy_id(),
                    evaluation_time_ms=elapsed_ms,
                    metadata={"matched_role": role},
                )

        elapsed_ms = (time.perf_counter() - start) * 1000
        return AuthorizationResult(
            decision=AuthorizationDecision.DENY,
            reason=f"No role grants permission '{request.permission}'",
            policy_id=self.get_policy_id(),
            evaluation_time_ms=elapsed_ms,
        )

    def get_policy_id(self) -> str:
        """Return the static RBAC policy identifier."""
        return "rbac-default"

    def get_policy_name(self) -> str:
        """Return the human-readable RBAC policy name."""
        return "Role-Based Access Control"


class AuthorizationEngine:
    """Central authorization engine with extensible policy chain.

    Maintains an ordered list of :class:`IAuthorizationPolicy` instances.
    Policies are evaluated in registration order; the first ``ALLOW`` or
    ``DENY`` decision wins.  If no policy is applicable the engine returns
    ``NOT_APPLICABLE``.

    The engine starts in a **disabled** state (``_enabled = False``).  When
    disabled, all evaluations return ``NOT_APPLICABLE`` immediately — this
    allows the framework to be wired in without enforcing authorization
    until it is explicitly enabled.
    """

    def __init__(self) -> None:
        self._policies: list[IAuthorizationPolicy] = []
        self._enabled: bool = False

    # ------------------------------------------------------------------
    # Policy management
    # ------------------------------------------------------------------

    def register_policy(self, policy: IAuthorizationPolicy) -> None:
        """Add a policy to the evaluation chain.

        Parameters
        ----------
        policy:
            A concrete authorization policy implementation.

        Raises
        ------
        ValueError
            If a policy with the same ID is already registered.
        """
        policy_id = policy.get_policy_id()
        for existing in self._policies:
            if existing.get_policy_id() == policy_id:
                raise ValueError(
                    f"Policy '{policy_id}' is already registered"
                )

        self._policies.append(policy)
        logger.info(
            "policy_registered",
            policy_id=policy_id,
            policy_name=policy.get_policy_name(),
            total_policies=len(self._policies),
        )

    def unregister_policy(self, policy_id: str) -> bool:
        """Remove a policy by its ID.

        Parameters
        ----------
        policy_id:
            The unique identifier of the policy to remove.

        Returns
        -------
        bool
            ``True`` if the policy was found and removed.
        """
        for i, policy in enumerate(self._policies):
            if policy.get_policy_id() == policy_id:
                self._policies.pop(i)
                logger.info("policy_unregistered", policy_id=policy_id)
                return True
        return False

    # ------------------------------------------------------------------
    # Enable / disable
    # ------------------------------------------------------------------

    def enable(self) -> None:
        """Enable the authorization engine.

        Once enabled, :meth:`evaluate` will run the policy chain.
        """
        self._enabled = True
        logger.info("authorization_engine_enabled")

    def disable(self) -> None:
        """Disable the authorization engine.

        When disabled, :meth:`evaluate` returns ``NOT_APPLICABLE``
        immediately without running any policies.
        """
        self._enabled = False
        logger.info("authorization_engine_disabled")

    def is_enabled(self) -> bool:
        """Return ``True`` if the engine is currently enforcing."""
        return self._enabled

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    async def evaluate(self, request: AuthorizationRequest) -> AuthorizationResult:
        """Evaluate the authorization request against the policy chain.

        Parameters
        ----------
        request:
            The authorization request to evaluate.

        Returns
        -------
        AuthorizationResult
            The result of the first applicable policy, or
            ``NOT_APPLICABLE`` if no policy matched or the engine is
            disabled.
        """
        if not self._enabled:
            return AuthorizationResult(
                decision=AuthorizationDecision.NOT_APPLICABLE,
                reason="Authorization engine is disabled",
            )

        start = time.perf_counter()

        for policy in self._policies:
            try:
                result = policy.evaluate(request)
                if result.decision in (
                    AuthorizationDecision.ALLOW,
                    AuthorizationDecision.DENY,
                ):
                    elapsed_ms = (time.perf_counter() - start) * 1000
                    result.evaluation_time_ms = elapsed_ms
                    logger.info(
                        "authorization_evaluated",
                        decision=result.decision.value,
                        policy_id=policy.get_policy_id(),
                        permission=request.permission,
                        user_id=request.user_id,
                    )
                    return result
            except Exception as exc:
                logger.exception(
                    "policy_evaluation_error",
                    policy_id=policy.get_policy_id(),
                    error=str(exc),
                )
                elapsed_ms = (time.perf_counter() - start) * 1000
                return AuthorizationResult(
                    decision=AuthorizationDecision.ERROR,
                    reason=f"Policy '{policy.get_policy_id()}' raised an error: {exc}",
                    policy_id=policy.get_policy_id(),
                    evaluation_time_ms=elapsed_ms,
                )

        elapsed_ms = (time.perf_counter() - start) * 1000
        return AuthorizationResult(
            decision=AuthorizationDecision.NOT_APPLICABLE,
            reason="No policy produced a definitive decision",
            evaluation_time_ms=elapsed_ms,
        )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def get_policies(self) -> list[dict[str, str]]:
        """Return metadata for all registered policies."""
        return [
            {
                "policy_id": p.get_policy_id(),
                "policy_name": p.get_policy_name(),
            }
            for p in self._policies
        ]


# ------------------------------------------------------------------
# Module-level singleton
# ------------------------------------------------------------------

_authorization_engine: Optional[AuthorizationEngine] = None


def get_authorization_engine() -> AuthorizationEngine:
    """Return the global :class:`AuthorizationEngine`, creating it lazily."""
    global _authorization_engine  # noqa: PLW0603
    if _authorization_engine is None:
        _authorization_engine = AuthorizationEngine()
    return _authorization_engine
