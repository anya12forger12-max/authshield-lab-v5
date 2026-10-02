"""SQLAlchemy ORM models for the ecosystem module."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import Base, TimestampMixin, UUIDPrimaryKeyMixin


class LocalPackageModel(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_packages"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    author: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    tags: Mapped[str] = mapped_column(JSON, default=list)
    checksum: Mapped[str] = mapped_column(String(128), default="")
    signature: Mapped[str] = mapped_column(String(512), default="")
    license: Mapped[str] = mapped_column(String(100), default="")
    compatibility: Mapped[str] = mapped_column(String(100), default="")
    dependencies: Mapped[str] = mapped_column(JSON, default=list)
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    installed: Mapped[bool] = mapped_column(Boolean, default=False)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    rating: Mapped[int] = mapped_column(Integer, default=0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    installed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    installations = relationship("InstallationRecordModel", back_populates="package", cascade="all, delete-orphan")


class InstallationRecordModel(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_installation_records"

    package_id: Mapped[str] = mapped_column(String(36), ForeignKey("ecosystem_packages.id"), nullable=False)
    installed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="installed")
    config: Mapped[str] = mapped_column(JSON, default=dict)

    package = relationship("LocalPackageModel", back_populates="installations")


class LibraryItemModel(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_library_items"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(255), default="")
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[str] = mapped_column(JSON, default=list)
    category: Mapped[str] = mapped_column(String(100), default="")
    format: Mapped[str] = mapped_column(String(20), default="pdf")
    file_path: Mapped[str] = mapped_column(String(512), default="")
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    bookmarked: Mapped[bool] = mapped_column(Boolean, default=False)
    accessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    bookmarks = relationship("BookmarkModel", back_populates="item", cascade="all, delete-orphan")
    annotations = relationship("AnnotationModel", back_populates="item", cascade="all, delete-orphan")
    citations_as_source = relationship(
        "app.ecosystem.domain.models.CitationModel",
        foreign_keys="app.ecosystem.domain.models.CitationModel.source_item_id",
        back_populates="source_item",
        cascade="all, delete-orphan",
    )
    citations_as_target = relationship(
        "app.ecosystem.domain.models.CitationModel",
        foreign_keys="app.ecosystem.domain.models.CitationModel.target_item_id",
        back_populates="target_item",
        cascade="all, delete-orphan",
    )


class BookmarkModel(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_bookmarks"

    item_id: Mapped[str] = mapped_column(String(36), ForeignKey("ecosystem_library_items.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    note: Mapped[str] = mapped_column(Text, default="")
    page: Mapped[int] = mapped_column(Integer, default=0)

    item = relationship("LibraryItemModel", back_populates="bookmarks")


class AnnotationModel(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_annotations"

    item_id: Mapped[str] = mapped_column(String(36), ForeignKey("ecosystem_library_items.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    highlight: Mapped[str] = mapped_column(Text, default="")
    page: Mapped[int] = mapped_column(Integer, default=0)

    item = relationship("LibraryItemModel", back_populates="annotations")


class CitationModel(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_citations"

    source_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("ecosystem_library_items.id"), nullable=False)
    target_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("ecosystem_library_items.id"), nullable=False)
    citation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    page: Mapped[int] = mapped_column(Integer, default=0)
    note: Mapped[str] = mapped_column(Text, default="")

    source_item = relationship("LibraryItemModel", foreign_keys=[source_item_id], back_populates="citations_as_source")
    target_item = relationship("LibraryItemModel", foreign_keys=[target_item_id], back_populates="citations_as_target")


class ResearchProjectModel(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_research_projects"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="active")

    literature = relationship(
        "app.ecosystem.domain.models.LiteratureEntryModel",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    knowledge_maps = relationship(
        "app.ecosystem.domain.models.KnowledgeMapModel",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    reading_lists = relationship(
        "app.ecosystem.domain.models.ReadingListModel",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    bibliographies = relationship(
        "app.ecosystem.domain.models.BibliographyModel",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class LiteratureEntryModel(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_literature_entries"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("ecosystem_research_projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), default="")
    year: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(512), default="")
    abstract: Mapped[str] = mapped_column(Text, default="")
    keywords: Mapped[str] = mapped_column(JSON, default=list)
    notes: Mapped[str] = mapped_column(Text, default="")
    read_status: Mapped[str] = mapped_column(String(20), default="unread")
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    project = relationship(
        "app.ecosystem.domain.models.ResearchProjectModel",
        back_populates="literature",
    )
    noterefs = relationship(
        "app.ecosystem.domain.models.ResearchNoteModel",
        back_populates="entry",
        cascade="all, delete-orphan",
    )


class ResearchNoteModel(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_research_notes"

    entry_id: Mapped[str] = mapped_column(String(36), ForeignKey("ecosystem_literature_entries.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    entry = relationship(
        "app.ecosystem.domain.models.LiteratureEntryModel",
        back_populates="noterefs",
    )


class KnowledgeMapModel(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_knowledge_maps"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("ecosystem_research_projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    concepts: Mapped[str] = mapped_column(JSON, default=list)
    links: Mapped[str] = mapped_column(JSON, default=list)

    project = relationship(
        "app.ecosystem.domain.models.ResearchProjectModel",
        back_populates="knowledge_maps",
    )


class ReadingListModel(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_reading_lists"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("ecosystem_research_projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    entries: Mapped[str] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    project = relationship(
        "app.ecosystem.domain.models.ResearchProjectModel",
        back_populates="reading_lists",
    )


class BibliographyModel(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_bibliographies"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("ecosystem_research_projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), default="default")
    entries: Mapped[str] = mapped_column(JSON, default=list)
    format: Mapped[str] = mapped_column(String(20), default="apa")
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    project = relationship(
        "app.ecosystem.domain.models.ResearchProjectModel",
        back_populates="bibliographies",
    )


class OrganizationModel(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    org_type: Mapped[str] = mapped_column(String(50), nullable=False)
    departments: Mapped[str] = mapped_column(JSON, default=list)
    settings: Mapped[str] = mapped_column(JSON, default=dict)


class DepartmentModel(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_departments"

    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("ecosystem_organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    instructors: Mapped[str] = mapped_column(JSON, default=list)
    learners: Mapped[str] = mapped_column(JSON, default=list)
    programs: Mapped[str] = mapped_column(JSON, default=list)


class AcademicProgramModel(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_academic_programs"

    department_id: Mapped[str] = mapped_column(String(36), ForeignKey("ecosystem_departments.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    duration_months: Mapped[int] = mapped_column(Integer, default=0)
    competencies: Mapped[str] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(20), default="active")


class DistributionPackageModel(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_distribution_packages"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    content_type: Mapped[str] = mapped_column(String(100), default="")
    version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    checksum: Mapped[str] = mapped_column(String(128), default="")
    signature: Mapped[str] = mapped_column(String(512), default="")
    created_by: Mapped[str] = mapped_column(String(255), default="")
    exported: Mapped[bool] = mapped_column(Boolean, default=False)
    imported: Mapped[bool] = mapped_column(Boolean, default=False)


class ImportRecordModel(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "ecosystem_import_records"

    package_id: Mapped[str] = mapped_column(String(36), ForeignKey("ecosystem_distribution_packages.id"), nullable=False)
    imported_by: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    conflicts: Mapped[str] = mapped_column(JSON, default=list)
