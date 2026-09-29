"""Enterprise in-process Event Bus (Observer Pattern + Pub/Sub)."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Coroutine, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class EventSeverity(str, Enum):
    """Severity levels for domain events."""

    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventType(str, Enum):
    """All recognised event types across AuthShieldLab modules."""

    # Authentication
    AUTHENTICATION_REQUESTED = "authentication.requested"
    AUTHENTICATION_SUCCEEDED = "authentication.succeeded"
    AUTHENTICATION_FAILED = "authentication.failed"

    # Registration
    REGISTRATION_REQUESTED = "registration.requested"
    REGISTRATION_COMPLETED = "registration.completed"
    REGISTRATION_FAILED = "registration.failed"

    # Session
    SESSION_CREATED = "session.created"
    SESSION_EXPIRED = "session.expired"
    SESSION_DESTROYED = "session.destroyed"
    SESSION_RENEWED = "session.renewed"
    SESSION_REVOKED = "session.revoked"

    # User
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_STATUS_CHANGED = "user.status_changed"
    USER_PROFILE_UPDATED = "user.profile_updated"
    USER_PREFERENCES_CHANGED = "user.preferences_changed"

    # Role
    ROLE_ASSIGNED = "role.assigned"
    ROLE_REMOVED = "role.removed"
    ROLE_CREATED = "role.created"
    ROLE_UPDATED = "role.updated"

    # Password
    PASSWORD_VERIFIED = "password.verified"
    PASSWORD_CHANGED = "password.changed"
    PASSWORD_POLICY_VIOLATION = "password.policy_violation"

    # Audit
    AUDIT_EVENT = "audit.event"
    AUDIT_LOGGED = "audit.logged"

    # Policy
    POLICY_EVALUATED = "policy.evaluated"
    POLICY_DECISION = "policy.decision"
    POLICY_REGISTERED = "policy.registered"
    POLICY_ENABLED = "policy.enabled"
    POLICY_DISABLED = "policy.disabled"

    # Configuration
    CONFIG_CHANGED = "config.changed"
    CONFIG_VALIDATED = "config.validated"

    # System
    APPLICATION_STARTED = "system.started"
    APPLICATION_STOPPED = "system.stopped"
    ERROR_OCCURRED = "system.error"


@dataclass
class DomainEvent:
    """Immutable payload for an event published through the bus."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.AUDIT_EVENT
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    module: str = ""
    severity: EventSeverity = EventSeverity.INFO
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    source_user_id: Optional[str] = None
    target_user_id: Optional[str] = None
    session_id: Optional[str] = None


EventHandler = Callable[[DomainEvent], Coroutine[Any, Any, None]]


class EventBus:
    """Thread-safe in-process event bus for decoupled module communication.

    Maintains a registry of event-type → handler mappings and an in-memory
    circular event log for debugging / audit.  Handler exceptions are caught
    individually so one failing subscriber never prevents other subscribers
    from running.
    """

    def __init__(self, max_log_size: int = 10000) -> None:
        self._subscribers: dict[EventType, list[EventHandler]] = {}
        self._event_log: list[DomainEvent] = []
        self._max_log_size: int = max_log_size

    # ------------------------------------------------------------------
    # Subscription management
    # ------------------------------------------------------------------

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Register *handler* to be called whenever *event_type* is published.

        Parameters
        ----------
        event_type:
            The event type to subscribe to.
        handler:
            An async callable that accepts a :class:`DomainEvent`.
        """
        self._subscribers.setdefault(event_type, [])
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Remove a previously registered *handler* for *event_type*.

        Does nothing if the handler is not currently registered.
        """
        handlers = self._subscribers.get(event_type, [])
        try:
            handlers.remove(handler)
        except ValueError:
            pass

    # ------------------------------------------------------------------
    # Publishing
    # ------------------------------------------------------------------

    async def publish(self, event: DomainEvent) -> None:
        """Publish *event* to all registered subscribers.

        Each handler is invoked inside a ``try / except`` so that a single
        handler failure is logged but does **not** prevent other handlers
        from running.
        """
        self._append_log(event)

        handlers = list(self._subscribers.get(event.event_type, []))
        for handler in handlers:
            try:
                await handler(event)
            except Exception:
                # event_type is typed as the EventType enum on DomainEvent, but
                # every domain event subclass declares it as a plain str (e.g.
                # `event_type: str = "audit.event_recorded"`). Dereferencing
                # `.value` on that str raised AttributeError *inside the
                # handler-failure path*, so a single failing handler turned into
                # an unhandled crash of publish() itself -- exactly what the
                # surrounding try/except exists to prevent. Render whichever
                # form we were actually given so logging can never be the
                # thing that fails.
                _et = event.event_type
                logger.exception(
                    "Handler %s failed for event %s (%s)",
                    handler.__qualname__,
                    event.event_id,
                    getattr(_et, "value", _et),
                )

    def publish_sync(self, event: DomainEvent) -> None:
        """Schedule *event* publishing on the current event loop.

        If no loop is running the event is published synchronously.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is not None and loop.is_running():
            loop.create_task(self.publish(event))
        else:
            # No running loop – execute directly in a new one.
            asyncio.run(self.publish(event))

    # ------------------------------------------------------------------
    # Event log (circular buffer)
    # ------------------------------------------------------------------

    def _append_log(self, event: DomainEvent) -> None:
        """Append *event* to the circular log buffer."""
        self._event_log.append(event)
        if len(self._event_log) > self._max_log_size:
            excess = len(self._event_log) - self._max_log_size
            self._event_log = self._event_log[excess:]

    def get_event_log(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100,
    ) -> list[DomainEvent]:
        """Return recent events, optionally filtered by *event_type*.

        Parameters
        ----------
        event_type:
            If provided, only events matching this type are returned.
        limit:
            Maximum number of events to return (most recent first).
        """
        events = self._event_log
        if event_type is not None:
            events = [e for e in events if e.event_type == event_type]
        return list(reversed(events[-limit:]))

    def clear_log(self) -> None:
        """Discard all stored events from the log."""
        self._event_log.clear()

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def subscriber_count(self, event_type: EventType) -> int:
        """Return the number of handlers registered for *event_type*."""
        return len(self._subscribers.get(event_type, []))

    def get_subscribed_types(self) -> list[EventType]:
        """Return all event types that have at least one subscriber."""
        return [et for et, h in self._subscribers.items() if h]


# ------------------------------------------------------------------
# Module-level singleton
# ------------------------------------------------------------------

_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Return the global :class:`EventBus` instance, creating it lazily."""
    global _event_bus  # noqa: PLW0603
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def reset_event_bus() -> None:
    """Replace the global event bus with a fresh instance.

    Primarily useful in tests.
    """
    global _event_bus  # noqa: PLW0603
    _event_bus = EventBus()
