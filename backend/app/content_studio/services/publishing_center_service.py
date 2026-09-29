"""Publishing center service — publish workflow, validation, signatures, rollback."""

from __future__ import annotations

import hashlib
import logging
import uuid
from typing import Any, Optional

from ..domain.entities.publishing import (
    ContentVersion,
    PublishHistory,
    PublishRequest,
    PublishStatus,
)
from ..domain.events.content_studio_events import ContentPublished, PublishRequested
from ..domain.interfaces.content_studio_interfaces import (
    IContentVersionRepository,
    IPublishHistoryRepository,
    IPublishRequestRepository,
)

logger = logging.getLogger(__name__)


class PublishingCenterService:
    """Service for the content publishing pipeline."""

    def __init__(
        self,
        publish_repo: IPublishRequestRepository,
        history_repo: IPublishHistoryRepository,
        version_repo: IContentVersionRepository,
    ) -> None:
        self._publish_repo = publish_repo
        self._history_repo = history_repo
        self._version_repo = version_repo

    def request_publish(
        self,
        content_id: str,
        content_type: str,
        requested_by: str,
        release_notes: str = "",
        version: int = 1,
    ) -> dict[str, Any]:
        request = PublishRequest(
            content_id=content_id,
            content_type=content_type,
            version=version,
            requested_by=requested_by,
            release_notes=release_notes,
        )
        result = self._publish_repo.create({
            "id": request.id,
            "content_id": content_id,
            "content_type": content_type,
            "version": version,
            "requested_by": requested_by,
            "requested_at": request.requested_at.isoformat(),
            "validation_results": {},
            "a11y_check_results": {},
            "localization_results": {},
            "dependency_results": {},
            "digital_signature": "",
            "release_notes": release_notes,
            "status": PublishStatus.PENDING.value,
        })

        self._history_repo.create({
            "content_id": content_id,
            "version": version,
            "action": "publish_requested",
            "performed_by": requested_by,
            "performed_at": request.requested_at.isoformat(),
            "details": {"request_id": result["id"], "release_notes": release_notes},
        })

        event = PublishRequested(
            request_id=result["id"],
            content_id=content_id,
            content_type=content_type,
            version=version,
            requested_by=requested_by,
        )
        logger.info("publish_requested", extra={"request_id": result["id"], "event_id": event.event_id})
        return result

    def get_publish_request(self, request_id: str) -> Optional[dict[str, Any]]:
        return self._publish_repo.get_by_id(request_id)

    def list_publish_requests(
        self, page: int = 1, per_page: int = 20, status: Optional[str] = None
    ) -> dict[str, Any]:
        return self._publish_repo.get_all(page=page, per_page=per_page, status=status)

    def get_requests_by_content(self, content_id: str) -> list[dict[str, Any]]:
        return self._publish_repo.get_by_content(content_id)

    def start_validation(self, request_id: str) -> dict[str, Any]:
        existing = self._publish_repo.get_by_id(request_id)
        if not existing:
            raise ValueError(f"Publish request '{request_id}' not found.")
        if existing.get("status") != PublishStatus.PENDING.value:
            raise ValueError(f"Request must be in 'pending' status, current: {existing.get('status')}")

        updated = self._publish_repo.update(request_id, {"status": PublishStatus.VALIDATING.value})
        result = updated or existing
        self._history_repo.create({
            "content_id": existing["content_id"],
            "version": existing.get("version", 1),
            "action": "validation_started",
            "performed_by": "system",
            "performed_at": result.get("updated_at", ""),
            "details": {"request_id": request_id},
        })
        return result

    def set_validation_results(
        self, request_id: str, results: dict[str, Any]
    ) -> dict[str, Any]:
        existing = self._publish_repo.get_by_id(request_id)
        if not existing:
            raise ValueError(f"Publish request '{request_id}' not found.")

        all_passed = results.get("failed", 0) == 0
        status = PublishStatus.VALIDATED.value if all_passed else PublishStatus.REJECTED.value

        updated = self._publish_repo.update(request_id, {
            "validation_results": results,
            "status": status,
        })
        return updated or existing

    def set_a11y_results(
        self, request_id: str, results: dict[str, Any]
    ) -> dict[str, Any]:
        existing = self._publish_repo.get_by_id(request_id)
        if not existing:
            raise ValueError(f"Publish request '{request_id}' not found.")
        updated = self._publish_repo.update(request_id, {"a11y_check_results": results})
        return updated or existing

    def set_localization_results(
        self, request_id: str, results: dict[str, Any]
    ) -> dict[str, Any]:
        existing = self._publish_repo.get_by_id(request_id)
        if not existing:
            raise ValueError(f"Publish request '{request_id}' not found.")
        updated = self._publish_repo.update(request_id, {"localization_results": results})
        return updated or existing

    def set_dependency_results(
        self, request_id: str, results: dict[str, Any]
    ) -> dict[str, Any]:
        existing = self._publish_repo.get_by_id(request_id)
        if not existing:
            raise ValueError(f"Publish request '{request_id}' not found.")
        updated = self._publish_repo.update(request_id, {"dependency_results": results})
        return updated or existing

    def sign_and_publish(self, request_id: str, digital_signature: str) -> dict[str, Any]:
        existing = self._publish_repo.get_by_id(request_id)
        if not existing:
            raise ValueError(f"Publish request '{request_id}' not found.")
        if existing.get("status") != PublishStatus.VALIDATED.value:
            raise ValueError(
                f"Request must be in 'validated' status to publish, current: {existing.get('status')}"
            )
        if not digital_signature:
            raise ValueError("Digital signature is required for publishing.")

        updated = self._publish_repo.update(request_id, {
            "digital_signature": digital_signature,
            "status": PublishStatus.PUBLISHED.value,
        })
        result = updated or existing

        content_id = existing["content_id"]
        version = existing.get("version", 1)
        self._history_repo.create({
            "content_id": content_id,
            "version": version,
            "action": "published",
            "performed_by": existing.get("requested_by", ""),
            "performed_at": result.get("updated_at", ""),
            "details": {
                "request_id": request_id,
                "digital_signature": digital_signature,
                "release_notes": existing.get("release_notes", ""),
            },
        })

        content_version = ContentVersion(
            content_id=content_id,
            version=version,
            changes=[existing.get("release_notes", "")],
            author=existing.get("requested_by", ""),
            checksum=hashlib.sha256(content_id.encode()).hexdigest(),
        )
        self._version_repo.create({
            "id": content_version.id,
            "content_id": content_id,
            "version": version,
            "changes": content_version.changes,
            "author": content_version.author,
            "checksum": content_version.checksum,
        })

        event = ContentPublished(
            content_id=content_id,
            content_type=existing.get("content_type", ""),
            version=version,
            published_by=existing.get("requested_by", ""),
        )
        logger.info("content_published", extra={"request_id": request_id, "event_id": event.event_id})
        return result

    def reject_publish(self, request_id: str, reason: str = "") -> dict[str, Any]:
        existing = self._publish_repo.get_by_id(request_id)
        if not existing:
            raise ValueError(f"Publish request '{request_id}' not found.")

        updated = self._publish_repo.update(request_id, {"status": PublishStatus.REJECTED.value})
        result = updated or existing
        self._history_repo.create({
            "content_id": existing["content_id"],
            "version": existing.get("version", 1),
            "action": "publish_rejected",
            "performed_by": "system",
            "performed_at": result.get("updated_at", ""),
            "details": {"request_id": request_id, "reason": reason},
        })
        return result

    def rollback_publish(self, request_id: str, reason: str = "") -> dict[str, Any]:
        existing = self._publish_repo.get_by_id(request_id)
        if not existing:
            raise ValueError(f"Publish request '{request_id}' not found.")
        if existing.get("status") != PublishStatus.PUBLISHED.value:
            raise ValueError("Can only rollback a published request.")

        updated = self._publish_repo.update(request_id, {"status": PublishStatus.ROLLED_BACK.value})
        result = updated or existing
        self._history_repo.create({
            "content_id": existing["content_id"],
            "version": existing.get("version", 1),
            "action": "publish_rolled_back",
            "performed_by": "system",
            "performed_at": result.get("updated_at", ""),
            "details": {"request_id": request_id, "reason": reason},
        })
        return updated or existing

    def get_publish_history(self, content_id: str) -> list[dict[str, Any]]:
        return self._history_repo.get_by_content(content_id)

    def get_content_versions(self, content_id: str) -> list[dict[str, Any]]:
        return self._version_repo.get_all_for_content(content_id)

    def get_latest_version(self, content_id: str) -> Optional[dict[str, Any]]:
        return self._version_repo.get_latest(content_id)

    def list_all_history(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        return self._history_repo.get_all(page=page, per_page=per_page)
