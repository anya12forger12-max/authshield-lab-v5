"""Analytics domain event handlers."""

from __future__ import annotations

from typing import Any

from ...shared.logging_config import get_logger
from ...shared.events.event_bus import DomainEvent, EventType, EventBus
from ..domain.events.analytics_events import (
    AnalyticsDashboardGenerated,
    AnalyticsDomainEvent,
    ContentHealthChecked,
    CurriculumEvaluated,
    ImprovementPlanCreated,
    ProgramEvaluated,
    QualityDashboardGenerated,
)

logger = get_logger("analytics.event_handlers")


async def handle_analytics_dashboard_generated(event: DomainEvent) -> None:
    """Handle AnalyticsDashboardGenerated – log dashboard creation."""
    logger.info(
        "event_handler.analytics_dashboard_generated",
        event_id=event.event_id,
        module=event.module,
        metadata=event.metadata,
    )


async def handle_quality_dashboard_generated(event: DomainEvent) -> None:
    """Handle QualityDashboardGenerated – log quality dashboard creation."""
    logger.info(
        "event_handler.quality_dashboard_generated",
        event_id=event.event_id,
        module=event.module,
        metadata=event.metadata,
    )


async def handle_curriculum_evaluated(event: DomainEvent) -> None:
    """Handle CurriculumEvaluated – log curriculum evaluation completion."""
    logger.info(
        "event_handler.curriculum_evaluated",
        event_id=event.event_id,
        module=event.module,
        metadata=event.metadata,
    )


async def handle_content_health_checked(event: DomainEvent) -> None:
    """Handle ContentHealthChecked – log content health check."""
    logger.info(
        "event_handler.content_health_checked",
        event_id=event.event_id,
        module=event.module,
        metadata=event.metadata,
    )


async def handle_program_evaluated(event: DomainEvent) -> None:
    """Handle ProgramEvaluated – log program evaluation completion."""
    logger.info(
        "event_handler.program_evaluated",
        event_id=event.event_id,
        module=event.module,
        metadata=event.metadata,
    )


async def handle_improvement_plan_created(event: DomainEvent) -> None:
    """Handle ImprovementPlanCreated – log improvement plan creation."""
    logger.info(
        "event_handler.improvement_plan_created",
        event_id=event.event_id,
        module=event.module,
        metadata=event.metadata,
    )


def register_analytics_event_handlers(event_bus: EventBus) -> None:
    """Register all analytics event handlers on the given event bus.

    Maps analytics domain event types to shared EventType enum values
    and subscribes the corresponding handler functions.
    """
    handler_mapping: dict[EventType, Any] = {
        EventType.AUDIT_EVENT: handle_analytics_dashboard_generated,
        EventType.CONFIG_CHANGED: handle_quality_dashboard_generated,
        EventType.CONFIG_VALIDATED: handle_curriculum_evaluated,
        EventType.POLICY_REGISTERED: handle_content_health_checked,
        EventType.POLICY_ENABLED: handle_program_evaluated,
        EventType.POLICY_DECISION: handle_improvement_plan_created,
    }

    for event_type, handler in handler_mapping.items():
        event_bus.subscribe(event_type, handler)

    logger.info(
        "analytics_event_handlers_registered",
        handler_count=len(handler_mapping),
    )
