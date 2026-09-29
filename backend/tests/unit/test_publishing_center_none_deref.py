"""Regression tests for the publish-center None-dereference crashes.

The repository's ``update()`` is typed ``dict[str, Any] | None`` and returns
None when the row is missing. Four methods -- ``start_validation``,
``sign_and_publish``, ``reject_publish`` and ``rollback_publish`` -- called
``updated.get("updated_at", "")`` to build the history entry *before* the
``return updated or existing`` fallback those same methods already wrote.

The author demonstrably expected None (that is why the fallback exists), but
the deref came first, so whenever ``update()`` returned None the call raised

    AttributeError: 'NoneType' object has no attribute 'get'

and the whole request failed instead of degrading to the pre-update state.
Each method now resolves the fallback once (``result = updated or existing``)
and uses it for both the history entry and the return.
"""

from __future__ import annotations

import pytest

from app.content_studio.repositories.content_studio_repository_impl import (
    InMemoryContentVersionRepository,
    InMemoryPublishHistoryRepository,
    InMemoryPublishRequestRepository,
)
from app.content_studio.services.publishing_center_service import (
    PublishingCenterService,
)


class _VanishingPublishRequestRepo(InMemoryPublishRequestRepository):
    """Simulates the row disappearing between get_by_id() and update()."""

    #: rollback_publish() only accepts an already-published request.
    status = "pending"

    def update(self, item_id: str, data: dict):  # type: ignore[override]
        return None

    def get_by_id(self, item_id: str):  # type: ignore[override]
        return {
            "id": item_id,
            "content_id": "content-1",
            "status": self.status,
            "version": 1,
        }


class _PublishedVanishingRepo(_VanishingPublishRequestRepo):
    status = "published"


def _service(repo=None) -> PublishingCenterService:
    return PublishingCenterService(
        repo or _VanishingPublishRequestRepo(),  # type: ignore[arg-type]
        InMemoryPublishHistoryRepository(),
        InMemoryContentVersionRepository(),
    )


class TestPublishCenterHandlesMissingUpdate:
    """update() -> None must degrade, not raise."""

    @pytest.mark.parametrize(
        ("method", "args", "repo"),
        [
            ("start_validation", ("req-1",), None),
            ("reject_publish", ("req-1", "not ready"), None),
            ("rollback_publish", ("req-1", "oops"), _PublishedVanishingRepo()),
        ],
    )
    def test_does_not_raise_when_update_returns_none(self, method, args, repo):
        service = _service(repo)
        # Regression: AttributeError 'NoneType' object has no attribute 'get'.
        result = getattr(service, method)(*args)
        assert isinstance(result, dict)
        assert result["id"] == "req-1"

    def test_history_entry_falls_back_to_pre_update_state(self):
        service = _service()
        service.start_validation("req-1")
        history = service.get_publish_history("content-1")
        assert history, "a history entry should still be recorded"
        assert history[-1]["action"] == "validation_started"
