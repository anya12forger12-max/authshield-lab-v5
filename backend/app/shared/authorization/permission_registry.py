"""Centralized permission registry with categories and groups."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from ...shared.logging_config import get_logger

logger = get_logger(__name__)


class PermissionCategory(str, Enum):
    """Categories for organizing permissions."""

    USER = "user"
    SESSION = "session"
    CONFIGURATION = "configuration"
    REPORTS = "reports"
    LEARNING = "learning"
    ADMINISTRATION = "administration"
    AUTHENTICATION = "authentication"
    ATTACK = "attack"
    DEFENSE = "defense"
    ANALYTICS = "analytics"
    AUDIT = "audit"


@dataclass(frozen=True)
class PermissionDefinition:
    """Immutable definition of a single permission."""

    name: str
    display_name: str
    description: str
    category: PermissionCategory
    is_active: bool = True
    version: int = 1


class PermissionRegistry:
    """Central registry for all permissions in the system.

    Maintains an in-memory catalogue of :class:`PermissionDefinition` objects
    organised by name and category.  Built-in system permissions are
    auto-registered on first use.
    """

    def __init__(self) -> None:
        self._permissions: dict[str, PermissionDefinition] = {}
        self._categories: dict[PermissionCategory, list[str]] = {}
        self._register_builtin_permissions()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, permission: PermissionDefinition) -> None:
        """Register a new permission or update an existing one.

        Parameters
        ----------
        permission:
            The permission definition to register.

        Raises
        ------
        ValueError
            If the permission name is empty.
        """
        if not permission.name:
            raise ValueError("Permission name cannot be empty")

        existing = self._permissions.get(permission.name)
        if existing is not None:
            logger.info(
                "permission_overwritten",
                name=permission.name,
                old_version=existing.version,
                new_version=permission.version,
            )
        else:
            logger.info("permission_registered", name=permission.name)

        self._permissions[permission.name] = permission
        self._categories.setdefault(permission.category, [])
        if permission.name not in self._categories[permission.category]:
            self._categories[permission.category].append(permission.name)

    def unregister(self, name: str) -> bool:
        """Remove a permission by name.

        Parameters
        ----------
        name:
            The dotted permission name (e.g. ``"user.read"``).

        Returns
        -------
        bool
            ``True`` if the permission existed and was removed, ``False``
            otherwise.
        """
        permission = self._permissions.pop(name, None)
        if permission is None:
            return False

        category_list = self._categories.get(permission.category, [])
        if name in category_list:
            category_list.remove(name)
            if not category_list:
                del self._categories[permission.category]

        logger.info("permission_unregistered", name=name)
        return True

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, name: str) -> Optional[PermissionDefinition]:
        """Return the permission definition for *name*, or ``None``."""
        return self._permissions.get(name)

    def get_all(self) -> list[PermissionDefinition]:
        """Return all registered permission definitions."""
        return list(self._permissions.values())

    def get_by_category(self, category: PermissionCategory) -> list[PermissionDefinition]:
        """Return all permissions belonging to *category*."""
        names = self._categories.get(category, [])
        return [self._permissions[n] for n in names if n in self._permissions]

    def has_permission(self, name: str) -> bool:
        """Return ``True`` if a permission with *name* is registered."""
        return name in self._permissions

    def search(self, query: str) -> list[PermissionDefinition]:
        """Search permissions by name, display name, or description.

        Parameters
        ----------
        query:
            Case-insensitive substring to match against permission fields.
        """
        query_lower = query.lower()
        return [
            p
            for p in self._permissions.values()
            if query_lower in p.name.lower()
            or query_lower in p.display_name.lower()
            or query_lower in p.description.lower()
        ]

    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------

    def export_permissions(self) -> dict[str, Any]:
        """Export all permissions as a serialisable dictionary."""
        return {
            "permissions": [
                {
                    "name": p.name,
                    "display_name": p.display_name,
                    "description": p.description,
                    "category": p.category.value,
                    "is_active": p.is_active,
                    "version": p.version,
                }
                for p in self._permissions.values()
            ],
            "total": len(self._permissions),
        }

    def import_permissions(self, data: dict[str, Any]) -> int:
        """Import permissions from a previously exported dictionary.

        Parameters
        ----------
        data:
            Dictionary in the format produced by :meth:`export_permissions`.

        Returns
        -------
        int
            The number of permissions successfully imported.
        """
        imported = 0
        for item in data.get("permissions", []):
            try:
                category = PermissionCategory(item["category"])
                perm = PermissionDefinition(
                    name=item["name"],
                    display_name=item.get("display_name", item["name"]),
                    description=item.get("description", ""),
                    category=category,
                    is_active=item.get("is_active", True),
                    version=item.get("version", 1),
                )
                self.register(perm)
                imported += 1
            except (KeyError, ValueError) as exc:
                logger.warning("permission_import_error", item=item, error=str(exc))

        logger.info("permissions_imported", count=imported)
        return imported

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def count(self) -> int:
        """Return the total number of registered permissions."""
        return len(self._permissions)

    def get_categories(self) -> list[PermissionCategory]:
        """Return all categories that contain at least one permission."""
        return sorted(self._categories.keys(), key=lambda c: c.value)

    # ------------------------------------------------------------------
    # Built-in registration
    # ------------------------------------------------------------------

    def _register_builtin_permissions(self) -> None:
        """Register all built-in system permissions."""
        builtins = [
            # User permissions
            PermissionDefinition("user.read", "Read Users", "View user profiles", PermissionCategory.USER),
            PermissionDefinition("user.write", "Write Users", "Create and edit users", PermissionCategory.USER),
            PermissionDefinition("user.delete", "Delete Users", "Delete user accounts", PermissionCategory.USER),
            # Session permissions
            PermissionDefinition("session.read", "Read Sessions", "View sessions", PermissionCategory.SESSION),
            PermissionDefinition("session.terminate", "Terminate Sessions", "Terminate user sessions", PermissionCategory.SESSION),
            # Configuration permissions
            PermissionDefinition("config.read", "Read Configuration", "View system configuration", PermissionCategory.CONFIGURATION),
            PermissionDefinition("config.write", "Write Configuration", "Modify system configuration", PermissionCategory.CONFIGURATION),
            # Reports
            PermissionDefinition("reports.read", "Read Reports", "View reports", PermissionCategory.REPORTS),
            PermissionDefinition("reports.generate", "Generate Reports", "Generate reports", PermissionCategory.REPORTS),
            # Learning
            PermissionDefinition("learning.read", "Read Learning", "Access learning modules", PermissionCategory.LEARNING),
            PermissionDefinition("learning.progress", "Learning Progress", "Track learning progress", PermissionCategory.LEARNING),
            # Administration
            PermissionDefinition("admin.access", "Administration Access", "Access admin panel", PermissionCategory.ADMINISTRATION),
            PermissionDefinition("admin.manage_roles", "Manage Roles", "Create and manage roles", PermissionCategory.ADMINISTRATION),
            # Authentication
            PermissionDefinition("auth.manage", "Manage Authentication", "Manage authentication settings", PermissionCategory.AUTHENTICATION),
            # Attack
            PermissionDefinition("attack.run", "Run Attacks", "Execute attack simulations", PermissionCategory.ATTACK),
            PermissionDefinition("attack.configure", "Configure Attacks", "Configure attack parameters", PermissionCategory.ATTACK),
            # Defense
            PermissionDefinition("defense.read", "Read Defenses", "View defense configurations", PermissionCategory.DEFENSE),
            PermissionDefinition("defense.write", "Write Defenses", "Configure defense policies", PermissionCategory.DEFENSE),
            # Analytics
            PermissionDefinition("analytics.read", "Read Analytics", "View security analytics", PermissionCategory.ANALYTICS),
            # Audit
            PermissionDefinition("audit.read", "Read Audit Logs", "View audit logs", PermissionCategory.AUDIT),
            PermissionDefinition("audit.export", "Export Audit Logs", "Export audit data", PermissionCategory.AUDIT),
        ]
        for p in builtins:
            self._permissions[p.name] = p
            self._categories.setdefault(p.category, []).append(p.name)


# ------------------------------------------------------------------
# Module-level singleton
# ------------------------------------------------------------------

_permission_registry: Optional[PermissionRegistry] = None


def get_permission_registry() -> PermissionRegistry:
    """Return the global :class:`PermissionRegistry`, creating it lazily."""
    global _permission_registry  # noqa: PLW0603
    if _permission_registry is None:
        _permission_registry = PermissionRegistry()
    return _permission_registry
