"""LMS API routes — FastAPI APIRouter for all LMS operations."""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ...shared.responses import SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lms", tags=["lms"])

# ---------------------------------------------------------------------------
# Lazy-loaded service singletons (wired at application startup or first use)
# ---------------------------------------------------------------------------

_classroom_service: Any = None
_enrollment_service: Any = None
_gradebook_service: Any = None
_competency_service: Any = None
_assessment_service: Any = None
_calendar_service: Any = None
_portfolio_service: Any = None
_instructor_service: Any = None
_analytics_service: Any = None
_dashboard_service: Any = None


def _get_classroom_service() -> Any:
    global _classroom_service  # noqa: PLW0603
    if _classroom_service is None:
        from ..repositories.lms_repository_impl import InMemoryClassroomRepository
        from ..services.classroom_service import ClassroomService
        _classroom_service = ClassroomService(InMemoryClassroomRepository())
    return _classroom_service


def _get_enrollment_service() -> Any:
    global _enrollment_service  # noqa: PLW0603
    if _enrollment_service is None:
        from ..repositories.lms_repository_impl import InMemoryEnrollmentRepository
        from ..services.enrollment_service import EnrollmentService
        _enrollment_service = EnrollmentService(InMemoryEnrollmentRepository())
    return _enrollment_service


def _get_gradebook_service() -> Any:
    global _gradebook_service  # noqa: PLW0603
    if _gradebook_service is None:
        from ..repositories.lms_repository_impl import InMemoryGradebookRepository
        from ..services.gradebook_service import GradebookService
        _gradebook_service = GradebookService(InMemoryGradebookRepository())
    return _gradebook_service


def _get_competency_service() -> Any:
    global _competency_service  # noqa: PLW0603
    if _competency_service is None:
        from ..repositories.lms_repository_impl import InMemoryCompetencyRepository
        from ..services.competency_service import CompetencyService
        _competency_service = CompetencyService(InMemoryCompetencyRepository())
    return _competency_service


def _get_assessment_service() -> Any:
    global _assessment_service  # noqa: PLW0603
    if _assessment_service is None:
        from ..repositories.lms_repository_impl import InMemoryAssessmentRepository
        from ..services.assessment_service import AssessmentLmsService
        _assessment_service = AssessmentLmsService(InMemoryAssessmentRepository())
    return _assessment_service


def _get_calendar_service() -> Any:
    global _calendar_service  # noqa: PLW0603
    if _calendar_service is None:
        from ..repositories.lms_repository_impl import InMemoryCalendarRepository
        from ..services.calendar_service import CalendarService
        _calendar_service = CalendarService(InMemoryCalendarRepository())
    return _calendar_service


def _get_portfolio_service() -> Any:
    global _portfolio_service  # noqa: PLW0603
    if _portfolio_service is None:
        from ..repositories.lms_repository_impl import InMemoryPortfolioRepository
        from ..services.portfolio_service import PortfolioService
        _portfolio_service = PortfolioService(InMemoryPortfolioRepository())
    return _portfolio_service


def _get_instructor_service() -> Any:
    global _instructor_service  # noqa: PLW0603
    if _instructor_service is None:
        from ..services.instructor_service import InstructorService
        _instructor_service = InstructorService(
            classroom_service=_get_classroom_service(),
            enrollment_service=_get_enrollment_service(),
            gradebook_service=_get_gradebook_service(),
            assessment_service=_get_assessment_service(),
            competency_service=_get_competency_service(),
        )
    return _instructor_service


def _get_analytics_service() -> Any:
    global _analytics_service  # noqa: PLW0603
    if _analytics_service is None:
        from ..services.analytics_service import AnalyticsService
        _analytics_service = AnalyticsService(
            classroom_service=_get_classroom_service(),
            enrollment_service=_get_enrollment_service(),
            gradebook_service=_get_gradebook_service(),
            competency_service=_get_competency_service(),
            assessment_service=_get_assessment_service(),
        )
    return _analytics_service


def _get_dashboard_service() -> Any:
    global _dashboard_service  # noqa: PLW0603
    if _dashboard_service is None:
        from ..services.lms_dashboard_service import LmsDashboardService
        _dashboard_service = LmsDashboardService(
            classroom_service=_get_classroom_service(),
            enrollment_service=_get_enrollment_service(),
            gradebook_service=_get_gradebook_service(),
            competency_service=_get_competency_service(),
            assessment_service=_get_assessment_service(),
            calendar_service=_get_calendar_service(),
            portfolio_service=_get_portfolio_service(),
        )
    return _dashboard_service


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ClassroomRequest(BaseModel):
    name: str
    description: str = ""
    capacity: int = 30
    instructor_id: str = ""
    status: str = "active"


class ClassroomUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    capacity: Optional[int] = None
    instructor_id: Optional[str] = None
    status: Optional[str] = None


class MemberRequest(BaseModel):
    user_id: str
    role: str = "learner"


class EnrollmentRequest(BaseModel):
    learner_id: str
    course_id: str
    status: str = "pending"


class GradebookCreateRequest(BaseModel):
    course_id: str


class GradeItemRequest(BaseModel):
    name: str
    category: str = "assignment"
    points_possible: float = 100.0
    weight: float = 1.0
    due_date: Optional[str] = None


class GradeEntryRequest(BaseModel):
    learner_id: str
    score: float
    feedback: Optional[str] = None
    graded_by: Optional[str] = None


class CompetencyRequest(BaseModel):
    name: str
    description: str = ""
    domain: str = ""
    level: str = "beginner"
    framework_id: Optional[str] = None


class FrameworkRequest(BaseModel):
    name: str
    description: str = ""
    version: str = "1.0"


class AssessmentRequest(BaseModel):
    title: str
    assessment_type: str = "quiz"
    course_id: str
    passing_score: float = 70.0
    time_limit_minutes: Optional[int] = None
    attempts_allowed: int = 1


class AttemptSubmitRequest(BaseModel):
    score: float
    feedback: Optional[str] = None


class SubmissionRequest(BaseModel):
    content: str = ""
    attachments: list[str] = Field(default_factory=list)


class QuestionGroupRequest(BaseModel):
    name: str
    questions: list[dict[str, Any]] = Field(default_factory=list)
    weight: float = 1.0


class CalendarRequest(BaseModel):
    name: str
    year: Optional[int] = None


class CalendarEventRequest(BaseModel):
    title: str
    event_type: str = "class"
    start_time: str
    end_time: str
    recurring: bool = False
    recurrence_rule: Optional[str] = None
    description: Optional[str] = None
    color: str = "#3B82F6"


class TermRequest(BaseModel):
    name: str
    start_date: str
    end_date: str


class ImportantDateRequest(BaseModel):
    title: str
    date: str
    date_type: str = "enrollment_deadline"
    description: Optional[str] = None


class PortfolioRequest(BaseModel):
    learner_id: str
    title: str
    description: str = ""


class PortfolioItemRequest(BaseModel):
    title: str
    description: str = ""
    item_type: str = "project"
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceRequest(BaseModel):
    competency_id: str
    description: str


# ===================================================================
# Dashboard endpoints
# ===================================================================

@router.get("/dashboard/summary")
async def get_dashboard_summary() -> dict[str, Any]:
    service = _get_dashboard_service()
    return service.get_dashboard_summary()


@router.get("/dashboard/instructor/{instructor_id}")
async def get_instructor_dashboard(instructor_id: str) -> dict[str, Any]:
    service = _get_dashboard_service()
    return service.get_instructor_dashboard(instructor_id)


@router.get("/dashboard/learner/{learner_id}")
async def get_learner_dashboard(learner_id: str) -> dict[str, Any]:
    service = _get_dashboard_service()
    return service.get_learner_dashboard(learner_id)


@router.get("/dashboard/recent-activity")
async def get_recent_activity(limit: int = Query(20, ge=1, le=100)) -> dict[str, Any]:
    service = _get_dashboard_service()
    return service.get_recent_activity(limit=limit)


# ===================================================================
# Classroom endpoints
# ===================================================================

@router.post("/classrooms", status_code=201)
async def create_classroom(request: ClassroomRequest) -> dict[str, Any]:
    service = _get_classroom_service()
    try:
        return service.create_classroom(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/classrooms")
async def list_classrooms(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_classroom_service()
    return service.list_classrooms(page=page, per_page=per_page, status=status)


@router.get("/classrooms/{classroom_id}")
async def get_classroom(classroom_id: str) -> dict[str, Any]:
    service = _get_classroom_service()
    classroom = service.get_classroom(classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail=f"Classroom '{classroom_id}' not found")
    return classroom


@router.put("/classrooms/{classroom_id}")
async def update_classroom(classroom_id: str, request: ClassroomUpdateRequest) -> dict[str, Any]:
    service = _get_classroom_service()
    try:
        data = request.model_dump(exclude_unset=True)
        result = service.update_classroom(classroom_id, data)
        if not result:
            raise HTTPException(status_code=404, detail=f"Classroom '{classroom_id}' not found")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/classrooms/{classroom_id}")
async def delete_classroom(classroom_id: str) -> SuccessResponse:
    service = _get_classroom_service()
    try:
        service.delete_classroom(classroom_id)
        return SuccessResponse(message=f"Classroom '{classroom_id}' deleted")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/classrooms/search/{query}")
async def search_classrooms(
    query: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    service = _get_classroom_service()
    return service.search_classrooms(query, page=page, per_page=per_page)


@router.post("/classrooms/{classroom_id}/members", status_code=201)
async def add_classroom_member(classroom_id: str, request: MemberRequest) -> dict[str, Any]:
    service = _get_classroom_service()
    try:
        return service.add_member(classroom_id, request.user_id, request.role)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/classrooms/{classroom_id}/members/{user_id}")
async def remove_classroom_member(classroom_id: str, user_id: str) -> SuccessResponse:
    service = _get_classroom_service()
    try:
        result = service.remove_member(classroom_id, user_id)
        if not result:
            raise HTTPException(status_code=404, detail="Member not found")
        return SuccessResponse(message=f"Member '{user_id}' removed from classroom")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/classrooms/{classroom_id}/members")
async def get_classroom_members(classroom_id: str) -> dict[str, Any]:
    service = _get_classroom_service()
    try:
        members = service.get_members(classroom_id)
        return {"classroom_id": classroom_id, "members": members}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ===================================================================
# Enrollment endpoints
# ===================================================================

@router.post("/enrollments", status_code=201)
async def create_enrollment(request: EnrollmentRequest) -> dict[str, Any]:
    service = _get_enrollment_service()
    try:
        return service.create_enrollment(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/enrollments")
async def list_enrollments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    course_id: Optional[str] = Query(None),
    learner_id: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_enrollment_service()
    return service.list_enrollments(
        page=page, per_page=per_page, status=status, course_id=course_id, learner_id=learner_id
    )


@router.get("/enrollments/{enrollment_id}")
async def get_enrollment(enrollment_id: str) -> dict[str, Any]:
    service = _get_enrollment_service()
    enrollment = service.get_enrollment(enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail=f"Enrollment '{enrollment_id}' not found")
    return enrollment


@router.put("/enrollments/{enrollment_id}/activate")
async def activate_enrollment(enrollment_id: str) -> dict[str, Any]:
    service = _get_enrollment_service()
    try:
        return service.activate_enrollment(enrollment_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.put("/enrollments/{enrollment_id}/complete")
async def complete_enrollment(
    enrollment_id: str, grade: Optional[str] = Query(None)
) -> dict[str, Any]:
    service = _get_enrollment_service()
    try:
        return service.complete_enrollment(enrollment_id, grade=grade)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.put("/enrollments/{enrollment_id}/drop")
async def drop_enrollment(enrollment_id: str) -> dict[str, Any]:
    service = _get_enrollment_service()
    try:
        return service.drop_enrollment(enrollment_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/enrollments/{enrollment_id}")
async def delete_enrollment(enrollment_id: str) -> SuccessResponse:
    service = _get_enrollment_service()
    try:
        service.delete_enrollment(enrollment_id)
        return SuccessResponse(message=f"Enrollment '{enrollment_id}' deleted")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/enrollments/learner/{learner_id}")
async def get_learner_enrollments(learner_id: str) -> dict[str, Any]:
    service = _get_enrollment_service()
    enrollments = service.get_learner_enrollments(learner_id)
    return {"learner_id": learner_id, "enrollments": enrollments}


@router.get("/enrollments/course/{course_id}")
async def get_course_enrollments(course_id: str) -> dict[str, Any]:
    service = _get_enrollment_service()
    enrollments = service.get_course_enrollments(course_id)
    return {"course_id": course_id, "enrollments": enrollments}


# ===================================================================
# Gradebook endpoints
# ===================================================================

@router.post("/gradebooks", status_code=201)
async def create_gradebook(request: GradebookCreateRequest) -> dict[str, Any]:
    service = _get_gradebook_service()
    try:
        return service.create_gradebook(request.course_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/gradebooks/{entry_id}")
async def get_gradebook(entry_id: str) -> dict[str, Any]:
    service = _get_gradebook_service()
    gradebook = service.get_gradebook(entry_id)
    if not gradebook:
        raise HTTPException(status_code=404, detail=f"Gradebook '{entry_id}' not found")
    return gradebook


@router.get("/gradebooks/course/{course_id}")
async def get_gradebook_by_course(course_id: str) -> dict[str, Any]:
    service = _get_gradebook_service()
    gradebook = service.get_gradebook_by_course(course_id)
    if not gradebook:
        raise HTTPException(status_code=404, detail=f"No gradebook for course '{course_id}'")
    return gradebook


@router.post("/gradebooks/{gradebook_id}/items", status_code=201)
async def add_grade_item(gradebook_id: str, request: GradeItemRequest) -> dict[str, Any]:
    service = _get_gradebook_service()
    try:
        return service.add_grade_item(gradebook_id, request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/gradebooks/items/{item_id}/grades", status_code=201)
async def add_grade_entry(item_id: str, request: GradeEntryRequest) -> dict[str, Any]:
    service = _get_gradebook_service()
    try:
        return service.add_grade_entry(item_id, request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/gradebooks/{gradebook_id}/learners/{learner_id}/grades")
async def get_learner_grades(gradebook_id: str, learner_id: str) -> dict[str, Any]:
    service = _get_gradebook_service()
    grades = service.get_learner_grades(gradebook_id, learner_id)
    return {"gradebook_id": gradebook_id, "learner_id": learner_id, "grades": grades}


@router.get("/gradebooks/{gradebook_id}/learners/{learner_id}/average")
async def get_learner_average(gradebook_id: str, learner_id: str) -> dict[str, Any]:
    service = _get_gradebook_service()
    try:
        average = service.calculate_learner_average(gradebook_id, learner_id)
        return {"gradebook_id": gradebook_id, "learner_id": learner_id, "average": average}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/gradebooks/{gradebook_id}/statistics")
async def get_gradebook_statistics(gradebook_id: str) -> dict[str, Any]:
    service = _get_gradebook_service()
    try:
        return service.get_course_statistics(gradebook_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/gradebooks/{entry_id}")
async def delete_gradebook(entry_id: str) -> SuccessResponse:
    service = _get_gradebook_service()
    try:
        service.delete_gradebook(entry_id)
        return SuccessResponse(message=f"Gradebook '{entry_id}' deleted")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ===================================================================
# Competency endpoints
# ===================================================================

@router.post("/competencies/frameworks", status_code=201)
async def create_framework(request: FrameworkRequest) -> dict[str, Any]:
    service = _get_competency_service()
    try:
        return service.create_framework(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/competencies/frameworks")
async def list_frameworks() -> list[dict[str, Any]]:
    service = _get_competency_service()
    return service.list_frameworks()


@router.get("/competencies/frameworks/{framework_id}")
async def get_framework(framework_id: str) -> dict[str, Any]:
    service = _get_competency_service()
    framework = service.get_framework(framework_id)
    if not framework:
        raise HTTPException(status_code=404, detail=f"Framework '{framework_id}' not found")
    return framework


@router.post("/competencies", status_code=201)
async def create_competency(request: CompetencyRequest) -> dict[str, Any]:
    service = _get_competency_service()
    try:
        return service.create_competency(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/competencies")
async def list_competencies() -> list[dict[str, Any]]:
    service = _get_competency_service()
    return service.list_competencies()


@router.get("/competencies/{competency_id}")
async def get_competency(competency_id: str) -> dict[str, Any]:
    service = _get_competency_service()
    competency = service.get_competency(competency_id)
    if not competency:
        raise HTTPException(status_code=404, detail=f"Competency '{competency_id}' not found")
    return competency


@router.put("/competencies/{competency_id}")
async def update_competency(competency_id: str, request: CompetencyRequest) -> dict[str, Any]:
    service = _get_competency_service()
    try:
        result = service.update_competency(competency_id, request.model_dump())
        if not result:
            raise HTTPException(status_code=404, detail=f"Competency '{competency_id}' not found")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/competencies/{competency_id}")
async def delete_competency(competency_id: str) -> SuccessResponse:
    service = _get_competency_service()
    try:
        service.delete_competency(competency_id)
        return SuccessResponse(message=f"Competency '{competency_id}' deleted")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/competencies/progress/{learner_id}")
async def get_learner_competency_progress(
    learner_id: str, competency_id: Optional[str] = Query(None)
) -> dict[str, Any]:
    service = _get_competency_service()
    progress = service.get_learner_progress(learner_id, competency_id)
    return {"learner_id": learner_id, "progress": progress}


@router.post("/competencies/progress/{learner_id}/start/{competency_id}")
async def start_competency(learner_id: str, competency_id: str) -> dict[str, Any]:
    service = _get_competency_service()
    try:
        return service.start_competency(learner_id, competency_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/competencies/progress/{learner_id}/achieve/{competency_id}")
async def achieve_competency(
    learner_id: str,
    competency_id: str,
    assessor_id: Optional[str] = Query(None),
    evidence: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_competency_service()
    try:
        return service.achieve_competency(learner_id, competency_id, assessor_id=assessor_id, evidence=evidence)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/competencies/progress/{learner_id}/master/{competency_id}")
async def master_competency(
    learner_id: str,
    competency_id: str,
    assessor_id: Optional[str] = Query(None),
    evidence: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_competency_service()
    try:
        return service.master_competency(learner_id, competency_id, assessor_id=assessor_id, evidence=evidence)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/competencies/summary/{learner_id}")
async def get_learner_competency_summary(learner_id: str) -> dict[str, Any]:
    service = _get_competency_service()
    return service.get_learner_summary(learner_id)


# ===================================================================
# Assessment endpoints
# ===================================================================

@router.post("/assessments", status_code=201)
async def create_assessment(request: AssessmentRequest) -> dict[str, Any]:
    service = _get_assessment_service()
    try:
        return service.create_assessment(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/assessments/{assessment_id}")
async def get_assessment(assessment_id: str) -> dict[str, Any]:
    service = _get_assessment_service()
    assessment = service.get_assessment(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail=f"Assessment '{assessment_id}' not found")
    return assessment


@router.get("/assessments/course/{course_id}")
async def list_assessments_by_course(course_id: str) -> dict[str, Any]:
    service = _get_assessment_service()
    assessments = service.list_assessments_by_course(course_id)
    return {"course_id": course_id, "assessments": assessments}


@router.put("/assessments/{assessment_id}")
async def update_assessment(assessment_id: str, request: AssessmentRequest) -> dict[str, Any]:
    service = _get_assessment_service()
    try:
        result = service.update_assessment(assessment_id, request.model_dump())
        if not result:
            raise HTTPException(status_code=404, detail=f"Assessment '{assessment_id}' not found")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/assessments/{assessment_id}")
async def delete_assessment(assessment_id: str) -> SuccessResponse:
    service = _get_assessment_service()
    try:
        service.delete_assessment(assessment_id)
        return SuccessResponse(message=f"Assessment '{assessment_id}' deleted")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/assessments/{assessment_id}/publish")
async def publish_assessment(assessment_id: str) -> dict[str, Any]:
    service = _get_assessment_service()
    try:
        return service.publish_assessment(assessment_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/assessments/{assessment_id}/close")
async def close_assessment(assessment_id: str) -> dict[str, Any]:
    service = _get_assessment_service()
    try:
        return service.close_assessment(assessment_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/assessments/{assessment_id}/attempts/{learner_id}", status_code=201)
async def start_attempt(assessment_id: str, learner_id: str) -> dict[str, Any]:
    service = _get_assessment_service()
    try:
        return service.start_attempt(assessment_id, learner_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.put("/assessments/attempts/{attempt_id}/submit")
async def submit_attempt(attempt_id: str, request: AttemptSubmitRequest) -> dict[str, Any]:
    service = _get_assessment_service()
    try:
        return service.submit_attempt(attempt_id, request.score, feedback=request.feedback)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/assessments/{assessment_id}/attempts")
async def get_attempts(
    assessment_id: str, learner_id: Optional[str] = Query(None)
) -> dict[str, Any]:
    service = _get_assessment_service()
    attempts = service.get_attempts(assessment_id, learner_id)
    return {"assessment_id": assessment_id, "attempts": attempts}


@router.post("/assessments/attempts/{attempt_id}/submissions", status_code=201)
async def create_submission(attempt_id: str, request: SubmissionRequest) -> dict[str, Any]:
    service = _get_assessment_service()
    try:
        return service.create_submission(attempt_id, request.content, attachments=request.attachments)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/assessments/{assessment_id}/question-groups", status_code=201)
async def create_question_group(assessment_id: str, request: QuestionGroupRequest) -> dict[str, Any]:
    service = _get_assessment_service()
    try:
        return service.create_question_group(assessment_id, request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/assessments/{assessment_id}/question-groups")
async def get_question_groups(assessment_id: str) -> dict[str, Any]:
    service = _get_assessment_service()
    groups = service.get_question_groups(assessment_id)
    return {"assessment_id": assessment_id, "question_groups": groups}


@router.get("/assessments/{assessment_id}/statistics")
async def get_assessment_statistics(assessment_id: str) -> dict[str, Any]:
    service = _get_assessment_service()
    try:
        return service.get_assessment_statistics(assessment_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ===================================================================
# Calendar endpoints
# ===================================================================

@router.post("/calendars", status_code=201)
async def create_calendar(request: CalendarRequest) -> dict[str, Any]:
    service = _get_calendar_service()
    try:
        return service.create_calendar(request.name, year=request.year)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/calendars")
async def list_calendars() -> list[dict[str, Any]]:
    service = _get_calendar_service()
    return service.list_calendars()


@router.get("/calendars/{calendar_id}")
async def get_calendar(calendar_id: str) -> dict[str, Any]:
    service = _get_calendar_service()
    calendar = service.get_calendar(calendar_id)
    if not calendar:
        raise HTTPException(status_code=404, detail=f"Calendar '{calendar_id}' not found")
    return calendar


@router.delete("/calendars/{calendar_id}")
async def delete_calendar(calendar_id: str) -> SuccessResponse:
    service = _get_calendar_service()
    try:
        service.delete_calendar(calendar_id)
        return SuccessResponse(message=f"Calendar '{calendar_id}' deleted")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/calendars/{calendar_id}/events", status_code=201)
async def add_calendar_event(calendar_id: str, request: CalendarEventRequest) -> dict[str, Any]:
    service = _get_calendar_service()
    try:
        return service.add_event(calendar_id, request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/calendars/{calendar_id}/events")
async def get_calendar_events(calendar_id: str) -> dict[str, Any]:
    service = _get_calendar_service()
    try:
        events = service.get_events(calendar_id)
        return {"calendar_id": calendar_id, "events": events}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/calendars/{calendar_id}/events/{event_id}")
async def remove_calendar_event(calendar_id: str, event_id: str) -> SuccessResponse:
    service = _get_calendar_service()
    try:
        result = service.remove_event(calendar_id, event_id)
        if not result:
            raise HTTPException(status_code=404, detail="Event not found")
        return SuccessResponse(message="Event removed")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/calendars/{calendar_id}/events/upcoming")
async def get_upcoming_events(calendar_id: str) -> dict[str, Any]:
    service = _get_calendar_service()
    try:
        events = service.get_upcoming_events(calendar_id)
        return {"calendar_id": calendar_id, "upcoming_events": events}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/terms", status_code=201)
async def create_term(request: TermRequest) -> dict[str, Any]:
    service = _get_calendar_service()
    try:
        return service.create_term(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/terms")
async def list_terms() -> list[dict[str, Any]]:
    service = _get_calendar_service()
    return service.list_terms()


@router.post("/important-dates", status_code=201)
async def create_important_date(request: ImportantDateRequest) -> dict[str, Any]:
    service = _get_calendar_service()
    try:
        return service.create_important_date(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/important-dates")
async def list_important_dates() -> list[dict[str, Any]]:
    service = _get_calendar_service()
    return service.list_important_dates()


# ===================================================================
# Portfolio endpoints
# ===================================================================

@router.post("/portfolios", status_code=201)
async def create_portfolio(request: PortfolioRequest) -> dict[str, Any]:
    service = _get_portfolio_service()
    try:
        return service.create_portfolio(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/portfolios/{portfolio_id}")
async def get_portfolio(portfolio_id: str) -> dict[str, Any]:
    service = _get_portfolio_service()
    portfolio = service.get_portfolio(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail=f"Portfolio '{portfolio_id}' not found")
    return portfolio


@router.get("/portfolios/learner/{learner_id}")
async def get_portfolio_by_learner(learner_id: str) -> dict[str, Any]:
    service = _get_portfolio_service()
    portfolio = service.get_portfolio_by_learner(learner_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail=f"No portfolio for learner '{learner_id}'")
    return portfolio


@router.get("/portfolios")
async def list_portfolios() -> list[dict[str, Any]]:
    service = _get_portfolio_service()
    return service.list_portfolios()


@router.put("/portfolios/{portfolio_id}")
async def update_portfolio(portfolio_id: str, request: PortfolioRequest) -> dict[str, Any]:
    service = _get_portfolio_service()
    try:
        result = service.update_portfolio(portfolio_id, request.model_dump(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail=f"Portfolio '{portfolio_id}' not found")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/portfolios/{portfolio_id}")
async def delete_portfolio(portfolio_id: str) -> SuccessResponse:
    service = _get_portfolio_service()
    try:
        service.delete_portfolio(portfolio_id)
        return SuccessResponse(message=f"Portfolio '{portfolio_id}' deleted")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/portfolios/{portfolio_id}/items", status_code=201)
async def add_portfolio_item(portfolio_id: str, request: PortfolioItemRequest) -> dict[str, Any]:
    service = _get_portfolio_service()
    try:
        return service.add_item(portfolio_id, request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/portfolios/{portfolio_id}/items")
async def get_portfolio_items(portfolio_id: str) -> dict[str, Any]:
    service = _get_portfolio_service()
    try:
        items = service.get_items(portfolio_id)
        return {"portfolio_id": portfolio_id, "items": items}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/portfolios/{portfolio_id}/items/{item_id}")
async def remove_portfolio_item(portfolio_id: str, item_id: str) -> SuccessResponse:
    service = _get_portfolio_service()
    try:
        result = service.remove_item(portfolio_id, item_id)
        if not result:
            raise HTTPException(status_code=404, detail="Item not found")
        return SuccessResponse(message="Item removed")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/portfolios/items/{item_id}/evidence", status_code=201)
async def add_competency_evidence(item_id: str, request: EvidenceRequest) -> dict[str, Any]:
    service = _get_portfolio_service()
    try:
        return service.add_evidence(item_id, request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/portfolios/items/{item_id}/evidence")
async def get_item_evidence(item_id: str) -> dict[str, Any]:
    service = _get_portfolio_service()
    evidence = service.get_evidence(item_id)
    return {"item_id": item_id, "evidence": evidence}


@router.get("/portfolios/{portfolio_id}/summary")
async def get_portfolio_summary(portfolio_id: str) -> dict[str, Any]:
    service = _get_portfolio_service()
    try:
        return service.get_portfolio_summary(portfolio_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ===================================================================
# Instructor endpoints
# ===================================================================

@router.post("/instructor/create-course")
async def instructor_create_course(
    instructor_id: str = Query(...),
    name: str = Query(...),
    description: str = Query(""),
    capacity: int = Query(30, ge=1),
) -> dict[str, Any]:
    service = _get_instructor_service()
    try:
        return service.create_course_classroom(instructor_id, name, description=description, capacity=capacity)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/instructor/enroll-learner/{classroom_id}")
async def instructor_enroll_learner(
    classroom_id: str,
    learner_id: str = Query(...),
    auto_activate: bool = Query(True),
) -> dict[str, Any]:
    service = _get_instructor_service()
    try:
        return service.enroll_learner(classroom_id, learner_id, auto_activate=auto_activate)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/instructor/record-grade/{gradebook_id}/{grade_item_id}")
async def instructor_record_grade(
    gradebook_id: str,
    grade_item_id: str,
    learner_id: str = Query(...),
    score: float = Query(...),
    feedback: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_instructor_service()
    try:
        return service.record_grade(gradebook_id, grade_item_id, learner_id, score, feedback=feedback)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/instructor/roster/{classroom_id}")
async def instructor_get_roster(classroom_id: str) -> dict[str, Any]:
    service = _get_instructor_service()
    return service.get_classroom_roster(classroom_id)


# ===================================================================
# Analytics endpoints
# ===================================================================

@router.get("/analytics/learner/{learner_id}")
async def get_learner_analytics(learner_id: str) -> dict[str, Any]:
    service = _get_analytics_service()
    return service.get_learner_overview(learner_id)


@router.get("/analytics/course/{course_id}")
async def get_course_analytics(course_id: str) -> dict[str, Any]:
    service = _get_analytics_service()
    return service.get_course_analytics(course_id)


@router.get("/analytics/platform")
async def get_platform_analytics() -> dict[str, Any]:
    service = _get_analytics_service()
    return service.get_platform_overview()


@router.get("/analytics/course/{course_id}/top-performers")
async def get_top_performers(
    course_id: str, limit: int = Query(10, ge=1, le=100)
) -> dict[str, Any]:
    service = _get_analytics_service()
    return {"course_id": course_id, "top_performers": service.get_top_performers(course_id, limit=limit)}


@router.get("/analytics/learner/{learner_id}/competency-heatmap")
async def get_competency_heatmap(learner_id: str) -> dict[str, Any]:
    service = _get_analytics_service()
    return service.get_competency_heatmap(learner_id)


@router.get("/analytics/learner/{learner_id}/progress-report")
async def get_learner_progress_report(learner_id: str) -> dict[str, Any]:
    service = _get_analytics_service()
    return service.get_learner_progress_report(learner_id)
