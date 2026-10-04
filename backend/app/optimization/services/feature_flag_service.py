"""Feature flag service — toggle flags, manage config profiles."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.optimization import ConfigProfile, FeatureFlag
from ..domain.events.optimization_events import FeatureFlagToggled
from ..domain.interfaces.optimization_interfaces import (
    IConfigProfileRepository,
    IFeatureFlagRepository,
)

logger = logging.getLogger(__name__)


class FeatureFlagService:
    """Manages feature flags and configuration profiles."""

    def __init__(
        self,
        flag_repo: IFeatureFlagRepository,
        profile_repo: IConfigProfileRepository,
    ) -> None:
        self._flag_repo = flag_repo
        self._profile_repo = profile_repo

    # ------------------------------------------------------------------
    # Feature Flags
    # ------------------------------------------------------------------

    def create_flag(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new feature flag."""
        flag = FeatureFlag(
            name=data.get("name", ""),
            description=data.get("description", ""),
            enabled=data.get("enabled", False),
            category=data.get("category", ""),
            default_value=data.get("default_value", False),
            rollout_date=data.get("rollout_date", ""),
            removal_date=data.get("removal_date", ""),
        )
        result = self._flag_repo.create(flag.to_dict())
        logger.info("feature_flag_created", extra={"flag_id": result["id"], "name": flag.name})
        return result

    def get_flag(self, flag_id: str) -> Optional[dict[str, Any]]:
        return self._flag_repo.get_by_id(flag_id)

    def get_flag_by_name(self, name: str) -> Optional[dict[str, Any]]:
        return self._flag_repo.get_by_name(name)

    def list_flags(
        self,
        page: int = 1,
        per_page: int = 20,
        category: Optional[str] = None,
        enabled_only: bool = False,
    ) -> dict[str, Any]:
        return self._flag_repo.get_all(
            page=page, per_page=per_page, category=category, enabled_only=enabled_only
        )

    def toggle_flag(self, flag_id: str) -> Optional[dict[str, Any]]:
        """Toggle a feature flag's enabled state."""
        flag = self._flag_repo.get_by_id(flag_id)
        if not flag:
            return None
        new_enabled = not flag.get("enabled", False)
        result = self._flag_repo.update(flag_id, {"enabled": new_enabled})

        event = FeatureFlagToggled(
            flag_id=flag_id,
            flag_name=flag.get("name", ""),
            enabled=new_enabled,
        )
        logger.info(
            "feature_flag_toggled",
            extra={"flag_id": flag_id, "enabled": new_enabled, "event_id": event.event_id},
        )
        return result

    def enable_flag(self, flag_id: str) -> Optional[dict[str, Any]]:
        """Enable a feature flag."""
        flag = self._flag_repo.get_by_id(flag_id)
        if not flag:
            return None
        return self._flag_repo.update(flag_id, {"enabled": True})

    def disable_flag(self, flag_id: str) -> Optional[dict[str, Any]]:
        """Disable a feature flag."""
        flag = self._flag_repo.get_by_id(flag_id)
        if not flag:
            return None
        return self._flag_repo.update(flag_id, {"enabled": False})

    def is_enabled(self, name: str) -> bool:
        """Check whether a named feature flag is enabled."""
        flag = self._flag_repo.get_by_name(name)
        if not flag:
            return False
        return flag.get("enabled", False)

    def update_flag(self, flag_id: str, data: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Update flag properties."""
        return self._flag_repo.update(flag_id, data)

    def delete_flag(self, flag_id: str) -> bool:
        return self._flag_repo.delete(flag_id)

    def bulk_toggle(self, flag_ids: list[str], enabled: bool) -> list[dict[str, Any]]:
        """Set multiple flags to the same enabled state."""
        results: list[dict[str, Any]] = []
        for fid in flag_ids:
            updated = self._flag_repo.update(fid, {"enabled": enabled})
            if updated:
                results.append(updated)
        return results

    def get_enabled_flags(self) -> list[dict[str, Any]]:
        """Return every currently enabled flag.

        The repository applies ``enabled_only`` itself and answers with a
        *paginated* envelope, so reading a single default page silently dropped
        every enabled flag past ``per_page`` (the repository default is 20): a
        rollout past the twentieth flag would simply never take effect, with no
        error anywhere.  Page through the envelope until it is exhausted rather
        than re-implementing the filter here.
        """
        results: list[dict[str, Any]] = []
        page = 1
        while True:
            envelope = self._flag_repo.get_all(page=page, per_page=100, enabled_only=True)
            if not isinstance(envelope, dict):
                # Defensive: a plain sequence from an alternative implementation.
                return [f for f in envelope if isinstance(f, dict)]
            batch = list(envelope.get("items") or [])
            results.extend(f for f in batch if isinstance(f, dict))
            if not batch or page >= int(envelope.get("pages") or 1):
                return results
            page += 1

    # ------------------------------------------------------------------
    # Config Profiles
    # ------------------------------------------------------------------

    def create_profile(self, data: dict[str, Any]) -> dict[str, Any]:
        profile = ConfigProfile(
            name=data.get("name", ""),
            target_audience=data.get("target_audience", ""),
            settings=data.get("settings", {}),
            version=data.get("version", "1.0"),
        )
        return self._profile_repo.create(profile.to_dict())

    def get_profile(self, profile_id: str) -> Optional[dict[str, Any]]:
        return self._profile_repo.get_by_id(profile_id)

    def list_profiles(
        self,
        page: int = 1,
        per_page: int = 20,
        target_audience: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._profile_repo.get_all(
            page=page, per_page=per_page, target_audience=target_audience
        )

    def update_profile(
        self, profile_id: str, data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        return self._profile_repo.update(profile_id, data)

    def delete_profile(self, profile_id: str) -> bool:
        return self._profile_repo.delete(profile_id)

    def merge_profile_settings(
        self, profile_id: str, settings: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """Merge additional settings into an existing profile."""
        profile = self._profile_repo.get_by_id(profile_id)
        if not profile:
            return None
        existing_settings = profile.get("settings", {})
        existing_settings.update(settings)
        return self._profile_repo.update(profile_id, {"settings": existing_settings})

    def get_profile_setting(
        self, profile_id: str, key: str, default: Any = None
    ) -> Any:
        """Get a single setting value from a profile."""
        profile = self._profile_repo.get_by_id(profile_id)
        if not profile:
            return default
        return profile.get("settings", {}).get(key, default)
