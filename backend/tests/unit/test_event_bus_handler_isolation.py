"""Regression tests for the EventBus handler-failure path.

``EventBus.publish`` is documented as isolating handler failures: "Each
handler is invoked inside a ``try / except`` so that a single handler failure
is logged but does **not** prevent other handlers from running."

It did not. ``DomainEvent.event_type`` is typed as the ``EventType`` enum,
but every domain event subclass declares it as a plain ``str`` (e.g.
``event_type: str = "audit.event_recorded"``). The except branch logged
``event.event_type.value``, so handling a failing handler raised

    AttributeError: 'str' object has no attribute 'value'

*from inside the except block* -- turning one bad handler into an unhandled
crash of ``publish()`` itself and abandoning every handler queued after it.
"""

from __future__ import annotations

import asyncio

import pytest

from app.audit.domain.events.audit_events import AuditEventRecordedEvent
from app.shared.events.event_bus import DomainEvent, EventBus, EventType


def _run(coro):
    return asyncio.run(coro)


async def _boom(_event):
    raise RuntimeError("handler exploded")


async def _ok(_event):
    return None


class TestHandlerFailureIsIsolated:
    @pytest.mark.parametrize(
        "event",
        [
            pytest.param(AuditEventRecordedEvent(), id="str-event_type"),
            pytest.param(DomainEvent(event_type=EventType.AUDIT_EVENT), id="enum-event_type"),
        ],
    )
    def test_publish_does_not_raise_when_a_handler_fails(self, event):
        bus = EventBus()
        bus.subscribe(event.event_type, _boom)
        # Regression: AttributeError 'str' object has no attribute 'value'.
        _run(bus.publish(event))

    def test_later_handlers_still_run(self):
        bus = EventBus()
        seen: list[object] = []

        async def _record(e):
            seen.append(e)

        bus.subscribe("audit.event_recorded", _boom)
        bus.subscribe("audit.event_recorded", _record)
        _run(bus.publish(AuditEventRecordedEvent()))
        # Regression: the failing handler aborted the whole loop.
        assert len(seen) == 1

    def test_event_is_still_logged_to_the_circular_buffer(self):
        bus = EventBus()
        event = AuditEventRecordedEvent()
        bus.subscribe("audit.event_recorded", _boom)
        _run(bus.publish(event))
        assert len(bus.get_event_log()) == 1

    def test_successful_publish_is_unaffected(self):
        bus = EventBus()
        seen: list[object] = []

        async def _record(e):
            seen.append(e)

        bus.subscribe("audit.event_recorded", _record)
        _run(bus.publish(AuditEventRecordedEvent()))
        assert len(seen) == 1
