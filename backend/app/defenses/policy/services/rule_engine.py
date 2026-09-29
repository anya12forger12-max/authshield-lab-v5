"""Complete RuleEngine implementing IRuleEngine."""

from __future__ import annotations

import uuid
from typing import Any, Optional

from ....shared.logging_config import get_logger
from ..domain.entities.rule_entity import (
    RuleAction,
    RuleExecutionMode,
    SecurityRule,
)
from ..domain.interfaces.policy_engine_interface import IRuleEngine

logger = get_logger(__name__)


class RuleEngine(IRuleEngine):
    """Evaluates security rules against an event context.

    Supports all condition operators and execution modes
    (sequential, parallel, short-circuit).  Returns matched rules and
    their associated actions.
    """

    def __init__(self) -> None:
        self._rules: dict[str, SecurityRule] = {}

    async def evaluate_rules(
        self, rules: list[SecurityRule], context: dict[str, Any]
    ) -> list[tuple[SecurityRule, bool, list[RuleAction]]]:
        """Evaluate a set of rules against the context.

        Parameters
        ----------
        rules:
            Rules to evaluate.
        context:
            The evaluation context dictionary.

        Returns
        -------
        list[tuple[SecurityRule, bool, list[RuleAction]]]
            Each tuple contains ``(rule, all_conditions_met, matching_actions)``.
        """
        results: list[tuple[SecurityRule, bool, list[RuleAction]]] = []

        sorted_rules = sorted(rules, key=lambda r: r.priority)

        for rule in sorted_rules:
            if not rule.is_active:
                results.append((rule, False, []))
                continue

            try:
                all_met, actions = rule.evaluate(context)
                results.append((rule, all_met, actions))

                if all_met and rule.execution_mode == RuleExecutionMode.SHORT_CIRCUIT:
                    logger.debug(
                        "short_circuit_triggered",
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                    )
                    break

            except Exception as exc:
                logger.exception(
                    "rule_evaluation_error",
                    rule_id=rule.rule_id,
                    error=str(exc),
                )
                results.append((rule, False, []))

        return results

    async def add_rule(self, rule: SecurityRule) -> bool:
        """Add a rule to the engine.

        Parameters
        ----------
        rule:
            The rule to add.

        Returns
        -------
        bool
            ``True`` on success.
        """
        if not rule.rule_id:
            rule.rule_id = str(uuid.uuid4())

        if rule.rule_id in self._rules:
            logger.warning("rule_already_exists", rule_id=rule.rule_id)
            return False

        self._rules[rule.rule_id] = rule
        logger.info("rule_added", rule_id=rule.rule_id, name=rule.name)
        return True

    async def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID.

        Returns
        -------
        bool
            ``True`` if the rule existed and was removed.
        """
        if rule_id not in self._rules:
            return False

        del self._rules[rule_id]
        logger.info("rule_removed", rule_id=rule_id)
        return True

    async def get_rule(self, rule_id: str) -> Optional[SecurityRule]:
        """Return a rule by ID, or ``None``."""
        return self._rules.get(rule_id)

    async def list_rules(self, active_only: bool = True) -> list[SecurityRule]:
        """Return all rules, optionally filtered to active ones.

        Parameters
        ----------
        active_only:
            When ``True``, only rules with ``is_active == True`` are
            returned.
        """
        rules = list(self._rules.values())
        if active_only:
            rules = [r for r in rules if r.is_active]
        return sorted(rules, key=lambda r: r.priority)
