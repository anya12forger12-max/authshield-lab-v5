"""In-memory PolicyRepository for configuration-based policies."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ....shared.logging_config import get_logger
from ..domain.entities.policy_entity import (
    PolicyCategory,
    PolicyConfiguration,
    PolicyStatus,
    SecurityPolicy,
    VALID_STATUS_TRANSITIONS,
)

logger = get_logger(__name__)


class PolicyRepository:
    """In-memory repository for security policy configurations.

    Provides CRUD with search/filter, versioning, and import/export.
    This is not backed by a database since policies are runtime
    configuration that should be lightweight and fast to query.
    """

    def __init__(self) -> None:
        self._policies: dict[str, SecurityPolicy] = {}
        self._versions: dict[str, list[dict[str, Any]]] = {}

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(self, data: dict[str, Any]) -> SecurityPolicy:
        """Create a new policy from raw data.

        Parameters
        ----------
        data:
            Dictionary with policy fields.

        Returns
        -------
        SecurityPolicy
            The newly created policy.
        """
        policy_id = data.get("policy_id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc)

        category = PolicyCategory(data.get("category", "authentication"))
        config_data = data.get("configuration", {})
        configuration = (
            PolicyConfiguration.from_dict(config_data)
            if isinstance(config_data, dict)
            else PolicyConfiguration()
        )

        policy = SecurityPolicy(
            policy_id=policy_id,
            name=data.get("name", ""),
            description=data.get("description", ""),
            version=1,
            category=category,
            priority=data.get("priority", 100),
            status=PolicyStatus(data.get("status", "draft")),
            created_at=now,
            updated_at=now,
            author=data.get("author", "system"),
            configuration=configuration,
            dependencies=data.get("dependencies", []),
            execution_order=data.get("execution_order", 0),
            risk_weight=data.get("risk_weight", 1.0),
            metadata=data.get("metadata", {}),
            supported_event_types=data.get("supported_event_types", []),
        )

        self._policies[policy_id] = policy
        self._versions[policy_id] = [policy.to_dict()]

        logger.info("policy_created", policy_id=policy_id, name=policy.name)
        return policy

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_by_id(self, policy_id: str) -> Optional[SecurityPolicy]:
        """Return a policy by ID, or ``None``."""
        return self._policies.get(policy_id)

    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[PolicyStatus] = None,
        category: Optional[PolicyCategory] = None,
    ) -> dict[str, Any]:
        """Return a paginated list of policies.

        Returns
        -------
        dict
            ``{"items": [...], "total": int, "page": int, "per_page": int,
            "pages": int}``
        """
        items = list(self._policies.values())

        if status is not None:
            items = [p for p in items if p.status == status]
        if category is not None:
            items = [p for p in items if p.category == category]

        items.sort(key=lambda p: (p.priority, p.name))

        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        page_items = items[offset : offset + per_page]

        return {
            "items": page_items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    def search(
        self,
        query: str,
        category: Optional[PolicyCategory] = None,
    ) -> list[SecurityPolicy]:
        """Search policies by name or description.

        Parameters
        ----------
        query:
            Case-insensitive substring.
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

        return sorted(results, key=lambda p: (p.priority, p.name))

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(
        self, policy_id: str, data: dict[str, Any]
    ) -> Optional[SecurityPolicy]:
        """Update a policy's fields.

        Parameters
        ----------
        policy_id:
            The policy to update.
        data:
            Fields to merge into the policy.

        Returns
        -------
        SecurityPolicy or None
        """
        policy = self._policies.get(policy_id)
        if policy is None:
            return None

        # Save version snapshot before update
        self._versions.setdefault(policy_id, [])
        self._versions[policy_id].append(policy.to_dict())

        if "name" in data:
            policy.name = data["name"]
        if "description" in data:
            policy.description = data["description"]
        if "category" in data:
            policy.category = PolicyCategory(data["category"])
        if "priority" in data:
            policy.priority = data["priority"]
        if "status" in data:
            policy.status = PolicyStatus(data["status"])
        if "configuration" in data:
            config_data = data["configuration"]
            if isinstance(config_data, dict):
                policy.configuration = PolicyConfiguration.from_dict(config_data)
        if "dependencies" in data:
            policy.dependencies = data["dependencies"]
        if "execution_order" in data:
            policy.execution_order = data["execution_order"]
        if "risk_weight" in data:
            policy.risk_weight = data["risk_weight"]
        if "metadata" in data:
            policy.metadata = data["metadata"]
        if "supported_event_types" in data:
            policy.supported_event_types = data["supported_event_types"]

        policy.updated_at = datetime.now(timezone.utc)
        policy.version += 1

        logger.info("policy_updated", policy_id=policy_id, version=policy.version)
        return policy

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, policy_id: str) -> bool:
        """Delete a policy.

        Returns
        -------
        bool
            ``True`` if the policy existed and was deleted.
        """
        if policy_id not in self._policies:
            return False

        del self._policies[policy_id]
        self._versions.pop(policy_id, None)

        logger.info("policy_deleted", policy_id=policy_id)
        return True

    # ------------------------------------------------------------------
    # Enable / disable
    # ------------------------------------------------------------------

    def enable(self, policy_id: str) -> bool:
        """Enable a policy.

        Returns
        -------
        bool
            ``True`` on success.
        """
        policy = self._policies.get(policy_id)
        if policy is None:
            return False

        allowed = VALID_STATUS_TRANSITIONS.get(policy.status, set())
        if PolicyStatus.ENABLED not in allowed:
            return False

        policy.status = PolicyStatus.ENABLED
        policy.updated_at = datetime.now(timezone.utc)
        return True

    def disable(self, policy_id: str) -> bool:
        """Disable a policy.

        Returns
        -------
        bool
            ``True`` on success.
        """
        policy = self._policies.get(policy_id)
        if policy is None:
            return False

        allowed = VALID_STATUS_TRANSITIONS.get(policy.status, set())
        if PolicyStatus.DISABLED not in allowed:
            return False

        policy.status = PolicyStatus.DISABLED
        policy.updated_at = datetime.now(timezone.utc)
        return True

    # ------------------------------------------------------------------
    # Versioning
    # ------------------------------------------------------------------

    def get_versions(self, policy_id: str) -> list[dict[str, Any]]:
        """Return version history snapshots for a policy."""
        return list(self._versions.get(policy_id, []))

    def rollback(self, policy_id: str, version_index: int) -> Optional[SecurityPolicy]:
        """Rollback a policy to a previous version.

        Parameters
        ----------
        policy_id:
            The policy to rollback.
        version_index:
            Index into the version history to restore.

        Returns
        -------
        SecurityPolicy or None
        """
        versions = self._versions.get(policy_id, [])
        if version_index < 0 or version_index >= len(versions):
            return None

        snapshot = versions[version_index]
        policy = self._policies.get(policy_id)
        if policy is None:
            return None

        config_data = snapshot.get("configuration", {})
        configuration = (
            PolicyConfiguration.from_dict(config_data)
            if isinstance(config_data, dict)
            else PolicyConfiguration()
        )

        policy.name = snapshot.get("name", policy.name)
        policy.description = snapshot.get("description", policy.description)
        policy.category = PolicyCategory(snapshot.get("category", policy.category.value))
        policy.priority = snapshot.get("priority", policy.priority)
        policy.configuration = configuration
        policy.dependencies = snapshot.get("dependencies", policy.dependencies)
        policy.execution_order = snapshot.get("execution_order", policy.execution_order)
        policy.risk_weight = snapshot.get("risk_weight", policy.risk_weight)
        policy.metadata = snapshot.get("metadata", policy.metadata)
        policy.supported_event_types = snapshot.get("supported_event_types", policy.supported_event_types)
        policy.updated_at = datetime.now(timezone.utc)
        policy.version += 1

        logger.info("policy_rolled_back", policy_id=policy_id, version=policy.version)
        return policy

    # ------------------------------------------------------------------
    # Import / export
    # ------------------------------------------------------------------

    def export_all(self) -> dict[str, Any]:
        """Export all policies as a serialisable dictionary."""
        return {
            "policies": [p.to_dict() for p in self._policies.values()],
            "total": len(self._policies),
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

    def import_data(self, data: dict[str, Any]) -> int:
        """Import policies from a previously exported dictionary.

        Returns
        -------
        int
            The number of policies imported.
        """
        imported = 0
        for item in data.get("policies", []):
            try:
                self.create(item)
                imported += 1
            except (KeyError, ValueError) as exc:
                logger.warning("policy_import_error", item=item, error=str(exc))

        logger.info("policies_imported", count=imported)
        return imported

    # ------------------------------------------------------------------
    # Count
    # ------------------------------------------------------------------

    def count(self) -> int:
        """Return the total number of stored policies."""
        return len(self._policies)
