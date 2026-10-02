"""Policy validation utilities."""

from __future__ import annotations

import re
from typing import Any

from ..domain.entities.policy_entity import (
    PolicyCategory,
    PolicyStatus,
    VALID_STATUS_TRANSITIONS,
)
from ..domain.entities.rule_entity import RuleCondition, RuleExecutionMode
from ....shared.validation.validator import ValidationResult


def validate_policy_data(data: dict[str, Any]) -> ValidationResult:
    """Validate data for policy creation or update.

    Parameters
    ----------
    data:
        Dictionary containing policy fields.

    Returns
    -------
    ValidationResult
    """
    result = ValidationResult()

    name = data.get("name", "")
    if not name or not name.strip():
        result.add_error("name", "Policy name is required", "REQUIRED")
    elif len(name.strip()) > 128:
        result.add_error(
            "name", "Policy name must be at most 128 characters", "MAX_LENGTH"
        )

    description = data.get("description", "")
    if description and len(description) > 512:
        result.add_error(
            "description", "Description must be at most 512 characters", "MAX_LENGTH"
        )

    category = data.get("category", "")
    if category:
        valid_categories = {c.value for c in PolicyCategory}
        if category not in valid_categories:
            result.add_error(
                "category",
                f"Invalid category. Must be one of: {', '.join(sorted(valid_categories))}",
                "INVALID_VALUE",
            )

    priority = data.get("priority")
    if priority is not None:
        if not isinstance(priority, int) or priority < 1 or priority > 1000:
            result.add_error(
                "priority", "Priority must be an integer between 1 and 1000", "INVALID_VALUE"
            )

    risk_weight = data.get("risk_weight")
    if risk_weight is not None:
        if not isinstance(risk_weight, (int, float)) or risk_weight < 0.0 or risk_weight > 10.0:
            result.add_error(
                "risk_weight", "Risk weight must be between 0.0 and 10.0", "INVALID_VALUE"
            )

    event_types = data.get("supported_event_types")
    if event_types is not None:
        if not isinstance(event_types, list):
            result.add_error(
                "supported_event_types", "Must be a list", "TYPE"
            )
        else:
            for et in event_types:
                if not isinstance(et, str) or not et.strip():
                    result.add_error(
                        "supported_event_types",
                        "Each event type must be a non-empty string",
                        "INVALID",
                    )

    return result


def validate_policy_config(config: dict[str, Any]) -> ValidationResult:
    """Validate a policy configuration dictionary.

    Parameters
    ----------
    config:
        The configuration to validate.

    Returns
    -------
    ValidationResult
    """
    result = ValidationResult()

    if not isinstance(config, dict):
        result.add_error("configuration", "Configuration must be a dictionary", "TYPE")
        return result

    thresholds = config.get("thresholds", {})
    if not isinstance(thresholds, dict):
        result.add_error("thresholds", "Thresholds must be a dictionary", "TYPE")
    else:
        for key, value in thresholds.items():
            if not isinstance(key, str) or not key.strip():
                result.add_error(
                    "thresholds", "Threshold keys must be non-empty strings", "INVALID"
                )
            try:
                float(value)
            except (TypeError, ValueError):
                result.add_error(
                    f"thresholds.{key}",
                    "Threshold values must be numeric",
                    "INVALID_VALUE",
                )

    timing = config.get("timing", {})
    if not isinstance(timing, dict):
        result.add_error("timing", "Timing must be a dictionary", "TYPE")
    else:
        for key, value in timing.items():
            if not isinstance(key, str) or not key.strip():
                result.add_error(
                    "timing", "Timing keys must be non-empty strings", "INVALID"
                )
            try:
                float(value)
            except (TypeError, ValueError):
                result.add_error(
                    f"timing.{key}",
                    "Timing values must be numeric",
                    "INVALID_VALUE",
                )

    messages = config.get("messages", {})
    if not isinstance(messages, dict):
        result.add_error("messages", "Messages must be a dictionary", "TYPE")

    for bool_key in ("logging_enabled", "audit_enabled", "metrics_enabled"):
        if bool_key in config and not isinstance(config[bool_key], bool):
            result.add_error(bool_key, f"{bool_key} must be a boolean", "TYPE")

    return result


def validate_rule_data(data: dict[str, Any]) -> ValidationResult:
    """Validate data for rule creation.

    Parameters
    ----------
    data:
        Dictionary containing rule fields.

    Returns
    -------
    ValidationResult
    """
    result = ValidationResult()

    name = data.get("name", "")
    if not name or not name.strip():
        result.add_error("name", "Rule name is required", "REQUIRED")
    elif len(name.strip()) > 128:
        result.add_error(
            "name", "Rule name must be at most 128 characters", "MAX_LENGTH"
        )

    description = data.get("description", "")
    if description and len(description) > 512:
        result.add_error(
            "description", "Description must be at most 512 characters", "MAX_LENGTH"
        )

    priority = data.get("priority")
    if priority is not None:
        if not isinstance(priority, int) or priority < 1 or priority > 1000:
            result.add_error(
                "priority", "Priority must be an integer between 1 and 1000", "INVALID_VALUE"
            )

    conditions = data.get("conditions", [])
    if not isinstance(conditions, list):
        result.add_error("conditions", "Conditions must be a list", "TYPE")
    elif len(conditions) == 0:
        result.add_error("conditions", "At least one condition is required", "REQUIRED")
    else:
        valid_operators = {op.value for op in RuleCondition}
        for i, condition in enumerate(conditions):
            if not isinstance(condition, dict):
                result.add_error(
                    f"conditions[{i}]", "Each condition must be a dictionary", "TYPE"
                )
                continue
            operator = condition.get("operator", "")
            if operator not in valid_operators:
                result.add_error(
                    f"conditions[{i}].operator",
                    f"Invalid operator. Must be one of: {', '.join(sorted(valid_operators))}",
                    "INVALID_VALUE",
                )
            if not condition.get("field_name") and operator != "always_true":
                result.add_error(
                    f"conditions[{i}].field_name",
                    "Field name is required for non-always-true conditions",
                    "REQUIRED",
                )

    actions = data.get("actions", [])
    if not isinstance(actions, list):
        result.add_error("actions", "Actions must be a list", "TYPE")
    elif len(actions) == 0:
        result.add_error("actions", "At least one action is required", "REQUIRED")
    else:
        valid_action_types = {"block", "allow", "warn", "log", "monitor"}
        for i, action in enumerate(actions):
            if not isinstance(action, dict):
                result.add_error(
                    f"actions[{i}]", "Each action must be a dictionary", "TYPE"
                )
                continue
            action_type = action.get("action_type", "")
            if action_type not in valid_action_types:
                result.add_error(
                    f"actions[{i}].action_type",
                    f"Invalid action type. Must be one of: {', '.join(sorted(valid_action_types))}",
                    "INVALID_VALUE",
                )

    execution_mode = data.get("execution_mode", "sequential")
    valid_modes = {m.value for m in RuleExecutionMode}
    if execution_mode not in valid_modes:
        result.add_error(
            "execution_mode",
            f"Invalid execution mode. Must be one of: {', '.join(sorted(valid_modes))}",
            "INVALID_VALUE",
        )

    return result


def validate_status_transition(
    current_status: str, target_status: str
) -> ValidationResult:
    """Validate that a status transition is allowed.

    Parameters
    ----------
    current_status:
        The current status value.
    target_status:
        The desired target status.

    Returns
    -------
    ValidationResult
    """
    result = ValidationResult()

    try:
        current = PolicyStatus(current_status)
    except ValueError:
        result.add_error(
            "current_status",
            f"Invalid current status: '{current_status}'",
            "INVALID_STATUS",
        )
        return result

    try:
        target = PolicyStatus(target_status)
    except ValueError:
        result.add_error(
            "target_status",
            f"Invalid target status: '{target_status}'",
            "INVALID_STATUS",
        )
        return result

    allowed = VALID_STATUS_TRANSITIONS.get(current, set())
    if target not in allowed:
        allowed_names = sorted(s.value for s in allowed)
        result.add_error(
            "status_transition",
            f"Cannot transition from '{current_status}' to '{target_status}'. "
            f"Allowed transitions: {', '.join(allowed_names) if allowed_names else 'none'}",
            "INVALID_TRANSITION",
        )

    return result
