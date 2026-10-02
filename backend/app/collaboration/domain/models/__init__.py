"""SQLAlchemy ORM models for the Collaboration module."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base, TimestampMixin, UUIDPrimaryKeyMixin


# ---------------------------------------------------------------------------
# Academic Hub Models
# ---------------------------------------------------------------------------


class InstitutionalProjectModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "collab_institutional_projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    department: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    lead: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    members: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class SharedCurriculumPackageModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "collab_shared_curriculum_packages"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_institution: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    content_type: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    checksum: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    signature: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    compatibility: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    accessibility_report: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    localization_report: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class ImportedResourceModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_imported_resources"

    package_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    imported_by: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    validation_results: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class ReviewRequestModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "collab_review_requests"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    request_type: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    submitter: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    assignees: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    due_date: Mapped[str] = mapped_column(String(20), nullable=False, default="")


class PublicationQueueItemModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_publication_queue"

    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    submitted_by: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="queued")


class VersionHistoryModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_version_history"

    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    changes: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    author: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Curriculum Exchange Models
# ---------------------------------------------------------------------------


class ExchangePackageModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "collab_exchange_packages"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    package_type: Mapped[str] = mapped_column(String(50), nullable=False, default="course")
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    author: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    source_institution: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    checksum: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    signature: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    license: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    compatibility: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    dependencies: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class ExchangeManifestModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_exchange_manifests"

    package_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    items: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    total_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    checksum: Mapped[str] = mapped_column(String(128), nullable=False, default="")


class PackageValidationReportModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_package_validation_reports"

    package_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    integrity: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    compatibility: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    a11y: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    localization: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    documentation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dependencies: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    licensing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    issues: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    validated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ExchangeHistoryModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_exchange_history"

    package_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    performed_by: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    details: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


# ---------------------------------------------------------------------------
# Research Workspace Models
# ---------------------------------------------------------------------------


class ResearchProjectModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "collab_research_projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    principal_investigator: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    team: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class LiteratureCollectionModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_literature_collections"

    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    entries: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class LiteratureEntryModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_literature_entries"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    year: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    abstract: Mapped[str] = mapped_column(Text, nullable=False, default="")
    keywords: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    read_status: Mapped[str] = mapped_column(String(20), nullable=False, default="unread")


class ResearchNoteModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_research_notes"

    entry_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_by: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class CitationModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_citations"

    source_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    citation_type: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    page: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")


class KnowledgeMapModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_knowledge_maps"

    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    concepts: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    links: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class ReadingListModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_reading_lists"

    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    item_ids: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class BibliographyModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_bibliographies"

    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    entries: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    format: Mapped[str] = mapped_column(String(20), nullable=False, default="apa")
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Peer Review Models
# ---------------------------------------------------------------------------


class PeerReviewModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "collab_peer_reviews"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    current_stage: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    submitter: Mapped[str] = mapped_column(String(255), nullable=False, default="")


class ReviewCommentModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_review_comments"

    review_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    stage: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    comment: Mapped[str] = mapped_column(Text, nullable=False, default="")
    severity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ReviewDecisionModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_review_decisions"

    review_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    reviewer: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    decision: Mapped[str] = mapped_column(String(20), nullable=False, default="approved")
    comments: Mapped[str] = mapped_column(Text, nullable=False, default="")
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ReviewRevisionModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_review_revisions"

    review_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    changes: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    author: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ReviewHistoryModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_review_histories"

    review_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    events: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


# ---------------------------------------------------------------------------
# Knowledge Base Models
# ---------------------------------------------------------------------------


class KnowledgeArticleModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "collab_knowledge_articles"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    tags: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    author: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")


class KnowledgeCategoryModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_knowledge_categories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    parent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    article_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class ArticleVersionModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_article_versions"

    article_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    author: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ArticleCitationModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "collab_article_citations"

    source_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    citation_type: Mapped[str] = mapped_column(String(50), nullable=False, default="")
