"""User-specific validators."""

from __future__ import annotations

from ...shared.validation.validator import Validator, ValidationResult
from ..domain.entities.identity_lifecycle import (
    UserLifecycleState,
    can_transition,
)


_user_validator = Validator()


def validate_profile_update(data: dict) -> ValidationResult:
    """Validate profile update data."""
    result = ValidationResult()

    display_name = data.get("display_name")
    if display_name is not None:
        name_result = _user_validator.validate_length(
            str(display_name), "display_name", min_len=1, max_len=64
        )
        if not name_result.is_valid:
            # Use merge() rather than errors.extend(): is_valid only flips
            # via add_error()/merge(), so extending the list directly
            # would leave is_valid True and let invalid input through.
            result.merge(name_result)

    email = data.get("email")
    if email is not None and email:
        email_str = str(email)
        if "@" not in email_str or "." not in email_str:
            result.add_error("email", "Invalid email address format.", "invalid_format")
        if len(email_str) > 254:
            result.add_error("email", "Email must be at most 254 characters.", "max_length")

    bio = data.get("bio")
    if bio is not None and len(str(bio)) > 1024:
        result.add_error("bio", "Bio must be at most 1024 characters.", "max_length")

    profile_picture = data.get("profile_picture")
    if profile_picture is not None and len(str(profile_picture)) > 512:
        result.add_error(
            "profile_picture",
            "Profile picture URL must be at most 512 characters.",
            "max_length",
        )

    return result


def validate_status_transition(current: str, target: str) -> ValidationResult:
    """Validate that an account status transition is allowed."""
    result = ValidationResult()

    try:
        current_state = UserLifecycleState(current)
    except ValueError:
        result.add_error(
            "current_status",
            f"Unknown current status: {current}",
            "invalid_value",
        )
        return result

    try:
        target_state = UserLifecycleState(target)
    except ValueError:
        result.add_error(
            "target_status",
            f"Unknown target status: {target}",
            "invalid_value",
        )
        return result

    if not can_transition(current_state, target_state):
        from ..domain.entities.identity_lifecycle import VALID_LIFECYCLE_TRANSITIONS
        allowed = VALID_LIFECYCLE_TRANSITIONS.get(current_state, set())
        allowed_names = sorted(s.value for s in allowed) or ["(none)"]
        result.add_error(
            "status_transition",
            f"Cannot transition from '{current}' to '{target}'. "
            f"Allowed: {', '.join(allowed_names)}",
            "invalid_transition",
        )

    return result


def validate_role_assignment(user_role: str, role_name: str) -> ValidationResult:
    """Validate a role assignment operation."""
    result = ValidationResult()

    if not role_name or not role_name.strip():
        result.add_error("role_name", "Role name is required.", "required")
        return result

    valid_roles = {"administrator", "instructor", "student", "developer", "readonly"}
    if role_name not in valid_roles:
        result.add_error(
            "role_name",
            f"Invalid role '{role_name}'. Must be one of: {', '.join(sorted(valid_roles))}",
            "invalid_value",
        )

    return result


def validate_preferences(data: dict) -> ValidationResult:
    """Validate preference update data."""
    result = ValidationResult()

    theme = data.get("theme")
    if theme is not None:
        valid_themes = {"dark", "light", "system", "high-contrast"}
        if theme not in valid_themes:
            result.add_error(
                "theme",
                f"Invalid theme '{theme}'. Must be one of: {', '.join(sorted(valid_themes))}",
                "invalid_value",
            )

    language = data.get("language")
    if language is not None:
        if not language or len(str(language)) > 10:
            result.add_error(
                "language",
                "Language code must be between 1 and 10 characters.",
                "invalid_length",
            )

    accessibility = data.get("accessibility")
    if accessibility is not None and isinstance(accessibility, dict):
        valid_keys = {
            "high_contrast", "large_text", "screen_reader",
            "reduced_motion", "keyboard_navigation",
        }
        for key in accessibility:
            if key not in valid_keys:
                result.add_error(
                    "accessibility",
                    f"Unknown accessibility setting: {key}",
                    "invalid_key",
                )

    return result
