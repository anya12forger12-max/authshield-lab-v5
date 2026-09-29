"""Production domain event handlers."""

from __future__ import annotations

from typing import Any

from ...shared.logging_config import get_logger
from ...shared.events.event_bus import DomainEvent, EventBus, EventType
from ..domain.events.production_events import (
    CertificationCompletedEvent,
    GovernanceReviewCompletedEvent,
    KnowledgeEntryCreatedEvent,
    MigrationCompletedEvent,
    ProductionDomainEvent,
    ReleaseCreatedEvent,
    ReleasePublishedEvent,
)

logger = get_logger("production.event_handlers")


async def handle_release_created(event: DomainEvent) -> None:
    """Handle ReleaseCreatedEvent — log and track new releases."""
    logger.info(
        "event_handler.release_created",
        event_id=event.event_id,
        module=event.module,
        metadata=event.metadata,
    )


async def handle_release_published(event: DomainEvent) -> None:
    """Handle ReleasePublishedEvent — log stable release publication."""
    logger.info(
        "event_handler.release_published",
        event_id=event.event_id,
        module=event.module,
        metadata=event.metadata,
    )


async def handle_certification_completed(event: DomainEvent) -> None:
    """Handle CertificationCompletedEvent — log certification outcomes."""
    logger.info(
        "event_handler.certification_completed",
        event_id=event.event_id,
        module=event.module,
        metadata=event.metadata,
    )


async def handle_governance_review_completed(event: DomainEvent) -> None:
    """Handle GovernanceReviewCompletedEvent — log governance outcomes."""
    logger.info(
        "event_handler.governance_review_completed",
        event_id=event.event_id,
        module=event.module,
        metadata=event.metadata,
    )


async def handle_migration_completed(event: DomainEvent) -> None:
    """Handle MigrationCompletedEvent — log migration completions."""
    logger.info(
        "event_handler.migration_completed",
        event_id=event.event_id,
        module=event.module,
        metadata=event.metadata,
    )


async def handle_knowledge_entry_created(event: DomainEvent) -> None:
    """Handle KnowledgeEntryCreatedEvent — log new knowledge entries."""
    logger.info(
        "event_handler.knowledge_entry_created",
        event_id=event.event_id,
        module=event.module,
        metadata=event.metadata,
    )


def register_production_event_handlers(event_bus: EventBus) -> None:
    """Register all production event handlers on the given event bus.

    This maps internal production domain event types to the shared
    EventType enum values used by the event bus, then subscribes
    the corresponding handler functions.
    """
    handler_mapping: dict[str, Any] = {
        EventType.AUDIT_EVENT: handle_release_created,
        EventType.CONFIG_CHANGED: handle_release_published,
        EventType.CONFIG_VALIDATED: handle_certification_completed,
        EventType.POLICY_REGISTERED: handle_governance_review_completed,
        EventType.POLICY_ENABLED: handle_migration_completed,
        EventType.POLICY_DECISION: handle_knowledge_entry_created,
    }

    for event_type, handler in handler_mapping.items():
        event_bus.subscribe(event_type, handler)

    logger.info(
        "production_event_handlers_registered",
        handler_count=len(handler_mapping),
    )
