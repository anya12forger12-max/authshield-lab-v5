"""LMS SQLAlchemy ORM models."""

from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ....shared.base_model import (
    AuditMixin,
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class ClassroomModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "lms_classrooms"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    instructor_id: Mapped[str] = mapped_column(String(36), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")


class ClassroomMemberModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_classroom_members"

    classroom_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="learner")
    joined_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    member_status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")


class ClassroomSessionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_classroom_sessions"

    classroom_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    session_status: Mapped[str] = mapped_column(String(20), nullable=False, default="scheduled")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)


class EnrollmentModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "lms_enrollments"

    learner_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    course_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    enrollment_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    enrolled_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    grade: Mapped[str | None] = mapped_column(String(10), nullable=True, default=None)


class WaitlistEntryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_waitlist_entries"

    learner_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    course_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    added_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


class GradeItemModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_grade_items"

    gradebook_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="assignment")
    points_possible: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    due_date: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)


class GradeEntryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_grade_entries"

    grade_item_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    learner_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    graded_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    graded_by: Mapped[str | None] = mapped_column(String(36), nullable=True, default=None)


class GradeScaleModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_grade_scales"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scale_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class GradebookModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_gradebooks"

    course_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)


class CompetencyModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "lms_competencies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    domain: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="beginner")
    framework_id: Mapped[str | None] = mapped_column(String(36), nullable=True, default=None)


class CompetencyFrameworkModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "lms_competency_frameworks"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")


class LearnerCompetencyModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_learner_competencies"

    learner_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    competency_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="not_started")
    evidence_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    assessed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    assessor_id: Mapped[str | None] = mapped_column(String(36), nullable=True, default=None)


class LmsAssessmentModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "lms_assessments"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    assessment_type: Mapped[str] = mapped_column(String(20), nullable=False, default="quiz")
    course_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    passing_score: Mapped[float] = mapped_column(Float, nullable=False, default=70.0)
    time_limit_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    attempts_allowed: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    assessment_status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")


class AssessmentAttemptModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_assessment_attempts"

    assessment_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    learner_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    started_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    submitted_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    score: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)


class SubmissionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_submissions"

    attempt_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    submitted_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    attachments_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class QuestionGroupModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_question_groups"

    assessment_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    questions_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)


class AcademicEventModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_academic_events"

    calendar_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(20), nullable=False, default="class")
    start_time: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    recurring: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    recurrence_rule: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    color: Mapped[str] = mapped_column(String(20), nullable=False, default="#3B82F6")


class AcademicCalendarModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_academic_calendars"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)


class TermModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_terms"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


class ImportantDateModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_important_dates"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    date_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)


class PortfolioModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "lms_portfolios"

    learner_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")


class PortfolioItemModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_portfolio_items"

    portfolio_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    item_type: Mapped[str] = mapped_column(String(20), nullable=False, default="project")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class PortfolioCategoryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_portfolio_categories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")


class CompetencyEvidenceModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lms_competency_evidence"

    item_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    competency_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    date_earned: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
