"""Collaboration event handlers."""

from __future__ import annotations

from typing import Any

from ..domain.events.collaboration_events import (
    PackageExchanged,
    ReviewSubmitted,
    ReviewApproved,
    ResearchProjectCreated,
    KnowledgeArticlePublished,
    ResourceImported,
    PublicationQueued,
)


_event_log: list[dict[str, Any]] = []


def handle_package_exchanged(event: PackageExchanged) -> None:
    _event_log.append({
        "type": "PackageExchanged",
        "package_id": event.package_id,
        "package_name": event.package_name,
        "version": event.version,
        "source_institution": event.source_institution,
        "performed_by": event.performed_by,
        "occurred_at": event.occurred_at.isoformat(),
    })


def handle_review_submitted(event: ReviewSubmitted) -> None:
    _event_log.append({
        "type": "ReviewSubmitted",
        "review_id": event.review_id,
        "title": event.title,
        "submitter": event.submitter,
        "content_type": event.content_type,
        "occurred_at": event.occurred_at.isoformat(),
    })


def handle_review_approved(event: ReviewApproved) -> None:
    _event_log.append({
        "type": "ReviewApproved",
        "review_id": event.review_id,
        "title": event.title,
        "stage": event.stage,
        "reviewer": event.reviewer,
        "occurred_at": event.occurred_at.isoformat(),
    })


def handle_research_project_created(event: ResearchProjectCreated) -> None:
    _event_log.append({
        "type": "ResearchProjectCreated",
        "project_id": event.project_id,
        "name": event.name,
        "principal_investigator": event.principal_investigator,
        "occurred_at": event.occurred_at.isoformat(),
    })


def handle_knowledge_article_published(event: KnowledgeArticlePublished) -> None:
    _event_log.append({
        "type": "KnowledgeArticlePublished",
        "article_id": event.article_id,
        "title": event.title,
        "author": event.author,
        "category": event.category,
        "occurred_at": event.occurred_at.isoformat(),
    })


def handle_resource_imported(event: ResourceImported) -> None:
    _event_log.append({
        "type": "ResourceImported",
        "resource_id": event.resource_id,
        "package_id": event.package_id,
        "imported_by": event.imported_by,
        "status": event.status,
        "occurred_at": event.occurred_at.isoformat(),
    })


def handle_publication_queued(event: PublicationQueued) -> None:
    _event_log.append({
        "type": "PublicationQueued",
        "item_id": event.item_id,
        "content_id": event.content_id,
        "content_type": event.content_type,
        "title": event.title,
        "submitted_by": event.submitted_by,
        "occurred_at": event.occurred_at.isoformat(),
    })


_HANDLERS = {
    PackageExchanged: handle_package_exchanged,
    ReviewSubmitted: handle_review_submitted,
    ReviewApproved: handle_review_approved,
    ResearchProjectCreated: handle_research_project_created,
    KnowledgeArticlePublished: handle_knowledge_article_published,
    ResourceImported: handle_resource_imported,
    PublicationQueued: handle_publication_queued,
}


def dispatch(event: PackageExchanged | ReviewSubmitted | ReviewApproved | ResearchProjectCreated | KnowledgeArticlePublished | ResourceImported | PublicationQueued) -> None:
    handler = _HANDLERS.get(type(event))
    if handler:
        handler(event)


def get_event_log() -> list[dict[str, Any]]:
    return _event_log.copy()


def clear_event_log() -> None:
    _event_log.clear()
