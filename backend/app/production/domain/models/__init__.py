"""SQLAlchemy models for production entities."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from ....shared.base_model import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ReleaseModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for software releases."""

    __tablename__ = "production_releases"

    version: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="in_development")
    build_info_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    release_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    release_notes_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    features_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    bug_fixes_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    known_issues_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    deprecations_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    minimum_platform_version: Mapped[str] = mapped_column(String(32), nullable=False, default="")

    @property
    def release_notes(self) -> list[str]:
        return json.loads(self.release_notes_json)

    @release_notes.setter
    def release_notes(self, value: list[str]) -> None:
        self.release_notes_json = json.dumps(value)

    @property
    def features(self) -> list[str]:
        return json.loads(self.features_json)

    @features.setter
    def features(self, value: list[str]) -> None:
        self.features_json = json.dumps(value)

    @property
    def bug_fixes(self) -> list[str]:
        return json.loads(self.bug_fixes_json)

    @bug_fixes.setter
    def bug_fixes(self, value: list[str]) -> None:
        self.bug_fixes_json = json.dumps(value)

    @property
    def known_issues(self) -> list[str]:
        return json.loads(self.known_issues_json)

    @known_issues.setter
    def known_issues(self, value: list[str]) -> None:
        self.known_issues_json = json.dumps(value)

    @property
    def deprecations(self) -> list[str]:
        return json.loads(self.deprecations_json)

    @deprecations.setter
    def deprecations(self, value: list[str]) -> None:
        self.deprecations_json = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "version": self.version,
            "name": self.name,
            "status": self.status,
            "build_info_id": self.build_info_id,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "release_notes": self.release_notes,
            "features": self.features,
            "bug_fixes": self.bug_fixes,
            "known_issues": self.known_issues,
            "deprecations": self.deprecations,
            "minimum_platform_version": self.minimum_platform_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ReleasePackageModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for release packages."""

    __tablename__ = "production_release_packages"

    release_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    package_type: Mapped[str] = mapped_column(String(32), nullable=False, default="installer")
    platform: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    checksum: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "release_id": self.release_id,
            "name": self.name,
            "package_type": self.package_type,
            "platform": self.platform,
            "checksum": self.checksum,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class BuildInfoModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for build information."""

    __tablename__ = "production_build_info"

    version: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    build_number: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    built_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    build_environment: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    python_version: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    platform: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    checksum: Mapped[str] = mapped_column(String(128), nullable=False, default="")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "version": self.version,
            "build_number": self.build_number,
            "built_at": self.built_at.isoformat() if self.built_at else None,
            "build_environment": self.build_environment,
            "python_version": self.python_version,
            "platform": self.platform,
            "checksum": self.checksum,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class LtsVersionModel(UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for LTS versions."""

    __tablename__ = "production_lts_versions"

    version: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    release_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    end_of_support: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    compatible_versions_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    migration_path: Mapped[str] = mapped_column(Text, nullable=False, default="")
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    @property
    def compatible_versions(self) -> list[str]:
        return json.loads(self.compatible_versions_json)

    @compatible_versions.setter
    def compatible_versions(self, value: list[str]) -> None:
        self.compatible_versions_json = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "version": self.version,
            "release_date": self.release_date,
            "end_of_support": self.end_of_support,
            "status": self.status,
            "compatible_versions": self.compatible_versions,
            "migration_path": self.migration_path,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MigrationStepModel(UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for migration steps."""

    __tablename__ = "production_migration_steps"

    from_version: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    to_version: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    requires_backup: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rollback_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "from_version": self.from_version,
            "to_version": self.to_version,
            "step_number": self.step_number,
            "description": self.description,
            "requires_backup": self.requires_backup,
            "estimated_minutes": self.estimated_minutes,
            "rollback_available": self.rollback_available,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CompatibilityMatrixModel(UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for version compatibility records."""

    __tablename__ = "production_compatibility_matrix"

    version_a: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    version_b: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    compatible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "version_a": self.version_a,
            "version_b": self.version_b,
            "compatible": self.compatible,
            "notes": self.notes,
            "checked_at": self.checked_at.isoformat() if self.checked_at else None,
        }


class DeprecationEntryModel(UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for deprecation entries."""

    __tablename__ = "production_deprecation_entries"

    feature: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    deprecated_in_version: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    replacement: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    removal_version: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    announced_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "feature": self.feature,
            "deprecated_in_version": self.deprecated_in_version,
            "replacement": self.replacement,
            "removal_version": self.removal_version,
            "announced_at": self.announced_at,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class GovernanceReviewModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for governance reviews."""

    __tablename__ = "production_governance_reviews"

    area: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    reviewer: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recommendations_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    @property
    def recommendations(self) -> list[str]:
        return json.loads(self.recommendations_json)

    @recommendations.setter
    def recommendations(self, value: list[str]) -> None:
        self.recommendations_json = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "area": self.area,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "reviewer": self.reviewer,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class GovernancePolicyModel(UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for governance policies."""

    __tablename__ = "production_governance_policies"

    area: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    requirements_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    review_frequency_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    @property
    def requirements(self) -> list[str]:
        return json.loads(self.requirements_json)

    @requirements.setter
    def requirements(self, value: list[str]) -> None:
        self.requirements_json = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "area": self.area,
            "name": self.name,
            "description": self.description,
            "requirements": self.requirements,
            "review_frequency_days": self.review_frequency_days,
            "last_reviewed_at": self.last_reviewed_at.isoformat() if self.last_reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CertificationModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for certifications."""

    __tablename__ = "production_certifications"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    cert_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    certified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    evidence_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    metrics_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    recommendations_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    approved_by: Mapped[str] = mapped_column(String(64), nullable=False, default="")

    @property
    def evidence(self) -> list[str]:
        return json.loads(self.evidence_json)

    @evidence.setter
    def evidence(self, value: list[str]) -> None:
        self.evidence_json = json.dumps(value)

    @property
    def metrics(self) -> dict[str, float]:
        return json.loads(self.metrics_json)

    @metrics.setter
    def metrics(self, value: dict[str, float]) -> None:
        self.metrics_json = json.dumps(value)

    @property
    def recommendations(self) -> list[str]:
        return json.loads(self.recommendations_json)

    @recommendations.setter
    def recommendations(self, value: list[str]) -> None:
        self.recommendations_json = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "cert_type": self.cert_type,
            "status": self.status,
            "certified_at": self.certified_at.isoformat() if self.certified_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "evidence": self.evidence,
            "metrics": self.metrics,
            "recommendations": self.recommendations,
            "approved_by": self.approved_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CertificationRequirementModel(UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for certification requirements."""

    __tablename__ = "production_certification_requirements"

    certification_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    requirement: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    met: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    evidence: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "certification_id": self.certification_id,
            "requirement": self.requirement,
            "description": self.description,
            "met": self.met,
            "evidence": self.evidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ProductionValidationModel(UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for production validations."""

    __tablename__ = "production_validations"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    subsystem: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pass")
    checks_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    validated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    details: Mapped[str] = mapped_column(Text, nullable=False, default="")

    @property
    def checks(self) -> dict[str, bool]:
        return json.loads(self.checks_json)

    @checks.setter
    def checks(self, value: dict[str, bool]) -> None:
        self.checks_json = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "subsystem": self.subsystem,
            "status": self.status,
            "checks": self.checks,
            "validated_at": self.validated_at.isoformat() if self.validated_at else None,
            "details": self.details,
        }


class ProjectHealthModel(UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for project health snapshots."""

    __tablename__ = "production_project_health"

    indicators_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    grade: Mapped[str] = mapped_column(String(2), nullable=False, default="F")
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    @property
    def indicators(self) -> list[dict]:
        return json.loads(self.indicators_json)

    @indicators.setter
    def indicators(self, value: list[dict]) -> None:
        self.indicators_json = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "indicators": self.indicators,
            "overall_score": self.overall_score,
            "grade": self.grade,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
        }


class ArchitectureDecisionRecordModel(UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for architecture decision records."""

    __tablename__ = "production_adrs"

    title: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="proposed")
    context: Mapped[str] = mapped_column(Text, nullable=False, default="")
    decision: Mapped[str] = mapped_column(Text, nullable=False, default="")
    consequences: Mapped[str] = mapped_column(Text, nullable=False, default="")
    alternatives: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "context": self.context,
            "decision": self.decision,
            "consequences": self.consequences,
            "alternatives": self.alternatives,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }


class MigrationHistoryModel(UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for migration history."""

    __tablename__ = "production_migration_history"

    from_version: Mapped[str] = mapped_column(String(32), nullable=False)
    to_version: Mapped[str] = mapped_column(String(32), nullable=False)
    migration_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    steps_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_steps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "from_version": self.from_version,
            "to_version": self.to_version,
            "migration_date": self.migration_date,
            "status": self.status,
            "steps_completed": self.steps_completed,
            "total_steps": self.total_steps,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ReleaseHistoryModel(UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for release history."""

    __tablename__ = "production_release_history"

    release_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    release_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "release_id": self.release_id,
            "version": self.version,
            "release_date": self.release_date,
            "summary": self.summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class KnowledgeEntryModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for knowledge entries."""

    __tablename__ = "production_knowledge_entries"

    title: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tags_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    version: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    author: Mapped[str] = mapped_column(String(64), nullable=False, default="")

    @property
    def tags(self) -> list[str]:
        return json.loads(self.tags_json)

    @tags.setter
    def tags(self, value: list[str]) -> None:
        self.tags_json = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "content": self.content,
            "tags": self.tags,
            "version": self.version,
            "author": self.author,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CodingStandardModel(UUIDPrimaryKeyMixin, Base):
    """SQLAlchemy model for coding standards."""

    __tablename__ = "production_coding_standards"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    examples_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    references_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    @property
    def examples(self) -> list[str]:
        return json.loads(self.examples_json)

    @examples.setter
    def examples(self, value: list[str]) -> None:
        self.examples_json = json.dumps(value)

    @property
    def references(self) -> list[str]:
        return json.loads(self.references_json)

    @references.setter
    def references(self, value: list[str]) -> None:
        self.references_json = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "examples": self.examples,
            "references": self.references,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
