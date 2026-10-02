"""Analytics module API routes."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ...shared.responses import SuccessResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ======================================================================
# Request / Response schemas
# ======================================================================


class RecordLearningProgressRequest(BaseModel):
    learner_id: str
    courses_enrolled: int = Field(default=0, ge=0)
    courses_completed: int = Field(default=0, ge=0)
    competencies_achieved: int = Field(default=0, ge=0)
    avg_score: float = Field(default=0.0, ge=0.0, le=100.0)
    total_time_hours: float = Field(default=0.0, ge=0.0)


class RecordCourseCompletionRequest(BaseModel):
    course_id: str
    course_name: str = Field(default="")
    enrolled: int = Field(default=0, ge=0)
    completed: int = Field(default=0, ge=0)
    in_progress: int = Field(default=0, ge=0)
    dropped: int = Field(default=0, ge=0)


class FilterOptionsRequest(BaseModel):
    institution: Optional[str] = None
    campus: Optional[str] = None
    department: Optional[str] = None
    program: Optional[str] = None
    course: Optional[str] = None
    instructor: Optional[str] = None
    term: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class GenerateQualityDashboardRequest(BaseModel):
    completion_rates: float = Field(default=0.0, ge=0.0, le=100.0)
    learning_objective_achievement: float = Field(default=0.0, ge=0.0, le=100.0)
    competency_growth: float = Field(default=0.0, ge=0.0, le=100.0)
    assessment_distribution: dict[str, float] = Field(default_factory=dict)
    lab_completion: float = Field(default=0.0, ge=0.0, le=100.0)
    portfolio_progress: float = Field(default=0.0, ge=0.0, le=100.0)
    certification_progress: float = Field(default=0.0, ge=0.0, le=100.0)
    reflection_participation: float = Field(default=0.0, ge=0.0, le=100.0)
    instructor_review_status: float = Field(default=0.0, ge=0.0, le=100.0)


class EvaluateCurriculumRequest(BaseModel):
    topics: list[str] = Field(default_factory=list)
    competencies: list[str] = Field(default_factory=list)
    mapped_competencies: Optional[list[str]] = None
    existing_content: Optional[list[dict[str, Any]]] = None
    review_frequency_days: int = Field(default=30, ge=1)


class RecordAssessmentOutcomeRequest(BaseModel):
    assessment_id: str
    title: str = Field(default="")
    total_attempts: int = Field(default=0, ge=0)
    passed: int = Field(default=0, ge=0)
    failed: int = Field(default=0, ge=0)
    question_scores: Optional[dict[str, list[float]]] = None


class AddContentHealthItemRequest(BaseModel):
    content_id: str
    content_type: str = Field(default="")
    title: str = Field(default="")
    version_status: str = Field(default="current")
    broken_refs: int = Field(default=0, ge=0)
    missing_metadata: int = Field(default=0, ge=0)
    doc_completeness: float = Field(default=0.0, ge=0.0, le=100.0)
    localization_status: str = Field(default="incomplete")
    a11y_status: str = Field(default="unknown")
    last_reviewed_days: int = Field(default=0, ge=0)
    publication_quality: float = Field(default=0.0, ge=0.0, le=100.0)
    dependency_health: float = Field(default=0.0, ge=0.0, le=100.0)


class GenerateProgramEvaluationRequest(BaseModel):
    program_name: str
    period: str = Field(default="")
    effectiveness_score: float = Field(default=0.0, ge=0.0, le=100.0)
    competency_coverage: float = Field(default=0.0, ge=0.0, le=100.0)
    course_performance: Optional[dict[str, float]] = None
    resource_utilization: float = Field(default=0.0, ge=0.0, le=100.0)
    instructor_workload: Optional[dict[str, float]] = None
    certification_outcomes: Optional[dict[str, float]] = None
    a11y_readiness: float = Field(default=0.0, ge=0.0, le=100.0)
    governance_compliance: float = Field(default=0.0, ge=0.0, le=100.0)
    doc_health: float = Field(default=0.0, ge=0.0, le=100.0)


class CreateActionPlanRequest(BaseModel):
    title: str
    description: str = Field(default="")
    owner: str = Field(default="")
    target_date: str = Field(default="")
    items: Optional[list[str]] = None


class CreateInitiativeRequest(BaseModel):
    name: str
    description: str = Field(default="")
    start_date: str = Field(default="")
    end_date: str = Field(default="")
    assignees: Optional[list[str]] = None
    metrics: Optional[dict] = None


class GenerateImprovementReportRequest(BaseModel):
    initiative_id: str
    period: str = Field(default="")
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    findings: Optional[list[str]] = None
    next_steps: Optional[list[str]] = None


class ComparePeriodsRequest(BaseModel):
    period_a_label: str
    period_b_label: str
    period_a_metrics: dict[str, float] = Field(default_factory=dict)
    period_b_metrics: dict[str, float] = Field(default_factory=dict)


# ======================================================================
# Helpers – lazy service singletons
# ======================================================================

_services: dict[str, Any] = {}


def _get_services() -> dict[str, Any]:
    """Lazy-initialise all analytics services with in-memory repos."""
    if _services:
        return _services

    from ..repositories.analytics_repository_impl import (
        InMemoryActionPlanItemRepository,
        InMemoryActionPlanRepository,
        InMemoryAnalyticsDashboardRepository,
        InMemoryAssessmentOutcomeRepository,
        InMemoryContentHealthDashboardRepository,
        InMemoryContentHealthRepository,
        InMemoryContentUsageRepository,
        InMemoryCourseCompletionRepository,
        InMemoryCurriculumCoverageRepository,
        InMemoryCurriculumEvaluationRepository,
        InMemoryExecutiveSummaryRepository,
        InMemoryEvaluationRecommendationRepository,
        InMemoryImprovementInitiativeRepository,
        InMemoryImprovementReportRepository,
        InMemoryLearningProgressRepository,
        InMemoryMaintenanceScheduleRepository,
        InMemoryProgramEvaluationRepository,
        InMemoryQualityDashboardRepository,
    )
    from ..services.analytics_center_service import AnalyticsCenterService
    from ..services.learning_quality_service import LearningQualityService
    from ..services.curriculum_evaluation_service import CurriculumEvaluationService
    from ..services.assessment_analytics_service import AssessmentAnalyticsService
    from ..services.a11y_analytics_service import A11yAnalyticsService
    from ..services.content_health_service import ContentHealthService
    from ..services.program_evaluation_service import ProgramEvaluationService
    from ..services.continuous_improvement_service import ContinuousImprovementService

    dashboard_repo = InMemoryAnalyticsDashboardRepository()
    progress_repo = InMemoryLearningProgressRepository()
    course_repo = InMemoryCourseCompletionRepository()
    assessment_repo = InMemoryAssessmentOutcomeRepository()
    coverage_repo = InMemoryCurriculumCoverageRepository()
    content_usage_repo = InMemoryContentUsageRepository()
    quality_dash_repo = InMemoryQualityDashboardRepository()
    eval_repo = InMemoryCurriculumEvaluationRepository()
    rec_repo = InMemoryEvaluationRecommendationRepository()
    content_health_repo = InMemoryContentHealthRepository()
    content_health_dash_repo = InMemoryContentHealthDashboardRepository()
    maintenance_repo = InMemoryMaintenanceScheduleRepository()
    program_eval_repo = InMemoryProgramEvaluationRepository()
    exec_summary_repo = InMemoryExecutiveSummaryRepository()
    plan_repo = InMemoryActionPlanRepository()
    plan_item_repo = InMemoryActionPlanItemRepository()
    initiative_repo = InMemoryImprovementInitiativeRepository()
    report_repo = InMemoryImprovementReportRepository()

    _services["analytics"] = AnalyticsCenterService(
        dashboard_repo, progress_repo, course_repo,
        assessment_repo, coverage_repo, content_usage_repo,
    )
    _services["quality"] = LearningQualityService(quality_dash_repo)
    _services["curriculum"] = CurriculumEvaluationService(eval_repo, rec_repo)
    _services["assessment"] = AssessmentAnalyticsService(assessment_repo)
    _services["a11y"] = A11yAnalyticsService(content_health_repo)
    _services["content_health"] = ContentHealthService(
        content_health_repo, content_health_dash_repo, maintenance_repo,
    )
    _services["program"] = ProgramEvaluationService(program_eval_repo, exec_summary_repo)
    _services["improvement"] = ContinuousImprovementService(
        plan_repo, plan_item_repo, initiative_repo, report_repo,
    )
    return _services


# ======================================================================
# Health
# ======================================================================


@router.get("/health")
async def analytics_health() -> dict:
    """Return basic analytics module health status."""
    return {
        "status": "healthy",
        "module": "analytics",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ======================================================================
# Analytics Center – Dashboards
# ======================================================================


@router.post("/dashboards/generate", status_code=201)
async def generate_dashboard(body: Optional[FilterOptionsRequest] = None) -> dict:
    svc = _get_services()["analytics"]
    from ..domain.entities.analytics import FilterOptions
    filters = None
    if body:
        filters = FilterOptions(
            institution=body.institution,
            campus=body.campus,
            department=body.department,
            program=body.program,
            course=body.course,
            instructor=body.instructor,
            term=body.term,
            date_from=body.date_from,
            date_to=body.date_to,
        )
    dashboard = await svc.generate_dashboard(filters=filters)
    return {"status": "success", "data": {
        "id": dashboard.id,
        "doc_quality": dashboard.doc_quality,
        "generated_at": dashboard.generated_at.isoformat(),
    }}


@router.get("/dashboards")
async def list_dashboards(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict:
    svc = _get_services()["analytics"]
    result = await svc.list_dashboards(page=page, per_page=per_page)
    items = [{"id": d.id, "doc_quality": d.doc_quality, "generated_at": d.generated_at.isoformat()}
             for d in result.get("items", [])]
    return {"status": "success", "items": items, "total": result.get("total", 0),
            "page": result.get("page", 1), "per_page": result.get("per_page", 20),
            "pages": result.get("pages", 1)}


@router.get("/dashboards/latest")
async def get_latest_dashboard() -> dict:
    svc = _get_services()["analytics"]
    dashboard = await svc.get_latest_dashboard()
    if dashboard is None:
        raise HTTPException(status_code=404, detail="No dashboards found")
    return {"status": "success", "data": {
        "id": dashboard.id,
        "doc_quality": dashboard.doc_quality,
        "generated_at": dashboard.generated_at.isoformat(),
    }}


@router.get("/dashboards/{dashboard_id}")
async def get_dashboard(dashboard_id: str) -> dict:
    svc = _get_services()["analytics"]
    dashboard = await svc.get_dashboard(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return {"status": "success", "data": {
        "id": dashboard.id,
        "doc_quality": dashboard.doc_quality,
        "generated_at": dashboard.generated_at.isoformat(),
    }}


@router.get("/metrics")
async def get_aggregate_metrics(
    institution: Optional[str] = Query(default=None),
    department: Optional[str] = Query(default=None),
    term: Optional[str] = Query(default=None),
) -> dict:
    svc = _get_services()["analytics"]
    from ..domain.entities.analytics import FilterOptions
    filters = FilterOptions(
        institution=institution, department=department, term=term,
    )
    metrics = await svc.get_aggregate_metrics(filters=filters)
    return {"status": "success", "data": metrics}


# ======================================================================
# Learning Progress
# ======================================================================


@router.post("/progress", status_code=201)
async def record_learning_progress(body: RecordLearningProgressRequest) -> dict:
    svc = _get_services()["analytics"]
    progress = await svc.record_learning_progress(
        learner_id=body.learner_id,
        courses_enrolled=body.courses_enrolled,
        courses_completed=body.courses_completed,
        competencies_achieved=body.competencies_achieved,
        avg_score=body.avg_score,
        total_time_hours=body.total_time_hours,
    )
    return {"status": "success", "data": {
        "learner_id": progress.learner_id,
        "courses_enrolled": progress.courses_enrolled,
        "courses_completed": progress.courses_completed,
    }}


@router.post("/courses", status_code=201)
async def record_course_completion(body: RecordCourseCompletionRequest) -> dict:
    svc = _get_services()["analytics"]
    completion = await svc.record_course_completion(
        course_id=body.course_id,
        course_name=body.course_name,
        enrolled=body.enrolled,
        completed=body.completed,
        in_progress=body.in_progress,
        dropped=body.dropped,
    )
    return {"status": "success", "data": {
        "course_id": completion.course_id,
        "completion_rate": completion.completion_rate,
    }}


# ======================================================================
# Learning Quality
# ======================================================================


@router.post("/quality/dashboards", status_code=201)
async def generate_quality_dashboard(body: GenerateQualityDashboardRequest) -> dict:
    svc = _get_services()["quality"]
    dashboard = await svc.generate_dashboard(
        completion_rates=body.completion_rates,
        learning_objective_achievement=body.learning_objective_achievement,
        competency_growth=body.competency_growth,
        assessment_distribution=body.assessment_distribution,
        lab_completion=body.lab_completion,
        portfolio_progress=body.portfolio_progress,
        certification_progress=body.certification_progress,
        reflection_participation=body.reflection_participation,
        instructor_review_status=body.instructor_review_status,
    )
    return {"status": "success", "data": {
        "id": dashboard.id,
        "generated_at": dashboard.generated_at.isoformat(),
    }}


@router.get("/quality/dashboards/latest")
async def get_latest_quality_dashboard() -> dict:
    svc = _get_services()["quality"]
    dashboard = await svc.get_latest_dashboard()
    if dashboard is None:
        raise HTTPException(status_code=404, detail="No quality dashboards found")
    return {"status": "success", "data": {
        "id": dashboard.id,
        "completion_rates": dashboard.completion_rates,
        "generated_at": dashboard.generated_at.isoformat(),
    }}


@router.get("/quality/dashboards/{dashboard_id}")
async def get_quality_dashboard(dashboard_id: str) -> dict:
    svc = _get_services()["quality"]
    dashboard = await svc.get_dashboard(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Quality dashboard not found")
    return {"status": "success", "data": {
        "id": dashboard.id,
        "completion_rates": dashboard.completion_rates,
        "generated_at": dashboard.generated_at.isoformat(),
    }}


@router.get("/quality/indicators")
async def get_quality_indicators() -> dict:
    svc = _get_services()["quality"]
    indicators = await svc.generate_quality_indicators()
    return {"status": "success", "items": [
        {"name": i.name, "value": i.value, "benchmark": i.benchmark,
         "status": i.status, "trend": i.trend}
        for i in indicators
    ]}


@router.get("/quality/overall-score")
async def get_overall_quality_score() -> dict:
    svc = _get_services()["quality"]
    score = await svc.compute_overall_quality_score()
    return {"status": "success", "data": {"overall_quality_score": score}}


# ======================================================================
# Curriculum Evaluation
# ======================================================================


@router.post("/curriculum/evaluate", status_code=201)
async def evaluate_curriculum(body: EvaluateCurriculumRequest) -> dict:
    svc = _get_services()["curriculum"]
    result = await svc.evaluate_curriculum(
        topics=body.topics,
        competencies=body.competencies,
        mapped_competencies=body.mapped_competencies,
        existing_content=body.existing_content,
        review_frequency_days=body.review_frequency_days,
    )
    return {"status": "success", "data": {
        "id": result.id,
        "assessment_alignment": result.assessment_alignment,
        "a11y_coverage": result.a11y_coverage,
        "generated_at": result.generated_at.isoformat(),
    }}


@router.get("/curriculum/evaluations")
async def list_curriculum_evaluations(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict:
    svc = _get_services()["curriculum"]
    result = await svc.list_evaluations(page=page, per_page=per_page)
    items = [{"id": e.id, "assessment_alignment": e.assessment_alignment,
              "generated_at": e.generated_at.isoformat()}
             for e in result.get("items", [])]
    return {"status": "success", "items": items, "total": result.get("total", 0),
            "page": result.get("page", 1), "per_page": result.get("per_page", 20),
            "pages": result.get("pages", 1)}


@router.get("/curriculum/evaluations/{evaluation_id}")
async def get_curriculum_evaluation(evaluation_id: str) -> dict:
    svc = _get_services()["curriculum"]
    result = await svc.get_evaluation(evaluation_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Curriculum evaluation not found")
    return {"status": "success", "data": {
        "id": result.id,
        "curriculum_balance": result.curriculum_balance,
        "topic_coverage": result.topic_coverage,
        "redundant_content": result.redundant_content,
        "missing_prerequisites": result.missing_prerequisites,
        "assessment_alignment": result.assessment_alignment,
        "a11y_coverage": result.a11y_coverage,
        "localization_coverage": result.localization_coverage,
        "content_freshness": result.content_freshness,
        "generated_at": result.generated_at.isoformat(),
    }}


@router.get("/curriculum/recommendations")
async def get_curriculum_recommendations() -> dict:
    svc = _get_services()["curriculum"]
    recs = await svc.get_recommendations()
    return {"status": "success", "items": [
        {"id": r.id, "category": r.category, "priority": r.priority,
         "recommendation": r.recommendation, "rationale": r.rationale,
         "impact": r.impact, "effort": r.effort}
        for r in recs
    ]}


@router.get("/curriculum/prerequisite-gaps")
async def get_prerequisite_gaps() -> dict:
    svc = _get_services()["curriculum"]
    gaps = await svc.analyze_prerequisite_gaps()
    return {"status": "success", "items": [
        {"missing_from": g.missing_from, "needed_by": g.needed_by, "severity": g.severity}
        for g in gaps
    ]}


# ======================================================================
# Assessment Analytics
# ======================================================================


@router.post("/assessments", status_code=201)
async def record_assessment_outcome(body: RecordAssessmentOutcomeRequest) -> dict:
    svc = _get_services()["assessment"]
    outcome = await svc.record_assessment_outcome(
        assessment_id=body.assessment_id,
        title=body.title,
        total_attempts=body.total_attempts,
        passed=body.passed,
        failed=body.failed,
        question_scores=body.question_scores,
    )
    return {"status": "success", "data": {
        "assessment_id": outcome.assessment_id,
        "pass_rate": outcome.pass_rate,
        "avg_score": outcome.avg_score,
    }}


@router.get("/assessments")
async def list_assessment_outcomes() -> dict:
    svc = _get_services()["assessment"]
    outcomes = await svc.list_all_outcomes()
    return {"status": "success", "items": [
        {"assessment_id": o.assessment_id, "title": o.title,
         "pass_rate": o.pass_rate, "avg_score": o.avg_score}
        for o in outcomes
    ]}


@router.get("/assessments/{assessment_id}")
async def get_assessment_outcome(assessment_id: str) -> dict:
    svc = _get_services()["assessment"]
    outcome = await svc.get_assessment_outcome(assessment_id)
    if outcome is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return {"status": "success", "data": {
        "assessment_id": outcome.assessment_id,
        "title": outcome.title,
        "total_attempts": outcome.total_attempts,
        "passed": outcome.passed,
        "failed": outcome.failed,
        "pass_rate": outcome.pass_rate,
        "avg_score": outcome.avg_score,
    }}


@router.get("/assessments/analysis/pass-rates")
async def get_pass_rate_analysis() -> dict:
    svc = _get_services()["assessment"]
    analysis = await svc.compute_pass_rate_analysis()
    return {"status": "success", "data": analysis}


@router.get("/assessments/{assessment_id}/items")
async def get_assessment_items(assessment_id: str) -> dict:
    svc = _get_services()["assessment"]
    analysis = await svc.analyze_question_items(assessment_id)
    if "error" in analysis:
        raise HTTPException(status_code=404, detail=analysis["error"])
    return {"status": "success", "data": analysis}


@router.get("/assessments/{assessment_id}/reliability")
async def get_assessment_reliability(assessment_id: str) -> dict:
    svc = _get_services()["assessment"]
    result = await svc.compute_reliability_index(assessment_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"status": "success", "data": result}


@router.get("/assessments/{assessment_id}/feedback")
async def get_assessment_feedback(assessment_id: str) -> dict:
    svc = _get_services()["assessment"]
    result = await svc.get_feedback_summary(assessment_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"status": "success", "data": result}


# ======================================================================
# Accessibility Analytics
# ======================================================================


@router.get("/a11y/overview")
async def get_a11y_overview() -> dict:
    svc = _get_services()["a11y"]
    overview = await svc.get_a11y_overview()
    return {"status": "success", "data": overview}


@router.get("/a11y/by-type")
async def get_a11y_by_type() -> dict:
    svc = _get_services()["a11y"]
    by_type = await svc.get_compliance_by_type()
    return {"status": "success", "data": by_type}


@router.get("/a11y/trend")
async def get_a11y_trend() -> dict:
    svc = _get_services()["a11y"]
    trend = await svc.get_compliance_trend()
    return {"status": "success", "items": trend}


@router.get("/a11y/improvement-plan")
async def get_a11y_improvement_plan() -> dict:
    svc = _get_services()["a11y"]
    plan = await svc.generate_improvement_plan()
    return {"status": "success", "data": plan}


@router.get("/a11y/items/{content_id}")
async def get_a11y_item_detail(content_id: str) -> dict:
    svc = _get_services()["a11y"]
    detail = await svc.get_item_a11y_detail(content_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Content item not found")
    return {"status": "success", "data": detail}


# ======================================================================
# Content Health
# ======================================================================


@router.post("/content-health/items", status_code=201)
async def add_content_health_item(body: AddContentHealthItemRequest) -> dict:
    svc = _get_services()["content_health"]
    item = await svc.add_content_item(
        content_id=body.content_id,
        content_type=body.content_type,
        title=body.title,
        version_status=body.version_status,
        broken_refs=body.broken_refs,
        missing_metadata=body.missing_metadata,
        doc_completeness=body.doc_completeness,
        localization_status=body.localization_status,
        a11y_status=body.a11y_status,
        last_reviewed_days=body.last_reviewed_days,
        publication_quality=body.publication_quality,
        dependency_health=body.dependency_health,
    )
    return {"status": "success", "data": {
        "id": item.id, "content_id": item.content_id, "title": item.title,
    }}


@router.get("/content-health/items")
async def list_content_health_items() -> dict:
    svc = _get_services()["content_health"]
    items = await svc.list_all_items()
    return {"status": "success", "items": [
        {"id": i.id, "content_id": i.content_id, "title": i.title,
         "content_type": i.content_type, "a11y_status": i.a11y_status}
        for i in items
    ]}


@router.get("/content-health/items/{content_id}")
async def get_content_health_item(content_id: str) -> dict:
    svc = _get_services()["content_health"]
    item = await svc.get_content_item(content_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Content item not found")
    return {"status": "success", "data": {
        "id": item.id, "content_id": item.content_id, "title": item.title,
        "version_status": item.version_status, "broken_refs": item.broken_refs,
        "a11y_status": item.a11y_status,
    }}


@router.post("/content-health/dashboard", status_code=201)
async def generate_content_health_dashboard() -> dict:
    svc = _get_services()["content_health"]
    dashboard = await svc.generate_health_dashboard()
    return {"status": "success", "data": {
        "id": dashboard.id,
        "total_items": dashboard.total_items,
        "healthy": dashboard.healthy,
        "needs_attention": dashboard.needs_attention,
        "critical": dashboard.critical,
        "by_type": dashboard.by_type,
        "generated_at": dashboard.generated_at.isoformat(),
    }}


@router.get("/content-health/dashboard/latest")
async def get_latest_content_health_dashboard() -> dict:
    svc = _get_services()["content_health"]
    dashboard = await svc.get_latest_dashboard()
    if dashboard is None:
        raise HTTPException(status_code=404, detail="No content health dashboards found")
    return {"status": "success", "data": {
        "id": dashboard.id,
        "total_items": dashboard.total_items,
        "healthy": dashboard.healthy,
        "generated_at": dashboard.generated_at.isoformat(),
    }}


@router.post("/content-health/maintenance", status_code=201)
async def generate_maintenance_schedule() -> dict:
    svc = _get_services()["content_health"]
    schedule = await svc.generate_maintenance_schedule()
    return {"status": "success", "data": {
        "id": schedule.id,
        "item_count": len(schedule.items),
        "generated_at": schedule.generated_at.isoformat(),
    }}


@router.get("/content-health/maintenance")
async def list_maintenance_schedules() -> dict:
    svc = _get_services()["content_health"]
    schedules = await svc.get_maintenance_schedules()
    return {"status": "success", "items": [
        {"id": s.id, "item_count": len(s.items), "generated_at": s.generated_at.isoformat()}
        for s in schedules
    ]}


@router.get("/content-health/attention")
async def get_items_needing_attention() -> dict:
    svc = _get_services()["content_health"]
    items = await svc.get_items_needing_attention()
    return {"status": "success", "items": [
        {"content_id": i.content_id, "title": i.title, "a11y_status": i.a11y_status}
        for i in items
    ]}


@router.get("/content-health/critical")
async def get_critical_items() -> dict:
    svc = _get_services()["content_health"]
    items = await svc.get_critical_items()
    return {"status": "success", "items": [
        {"content_id": i.content_id, "title": i.title, "a11y_status": i.a11y_status}
        for i in items
    ]}


# ======================================================================
# Program Evaluation
# ======================================================================


@router.post("/programs/evaluate", status_code=201)
async def evaluate_program(body: GenerateProgramEvaluationRequest) -> dict:
    svc = _get_services()["program"]
    evaluation = await svc.generate_evaluation(
        program_name=body.program_name,
        period=body.period,
        effectiveness_score=body.effectiveness_score,
        competency_coverage=body.competency_coverage,
        course_performance=body.course_performance,
        resource_utilization=body.resource_utilization,
        instructor_workload=body.instructor_workload,
        certification_outcomes=body.certification_outcomes,
        a11y_readiness=body.a11y_readiness,
        governance_compliance=body.governance_compliance,
        doc_health=body.doc_health,
    )
    return {"status": "success", "data": {
        "id": evaluation.id,
        "program_name": evaluation.program_name,
        "effectiveness_score": evaluation.effectiveness_score,
        "generated_at": evaluation.generated_at.isoformat(),
    }}


@router.get("/programs/evaluations")
async def list_program_evaluations(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict:
    svc = _get_services()["program"]
    result = await svc.list_evaluations(page=page, per_page=per_page)
    items = [{"id": e.id, "program_name": e.program_name,
              "effectiveness_score": e.effectiveness_score,
              "generated_at": e.generated_at.isoformat()}
             for e in result.get("items", [])]
    return {"status": "success", "items": items, "total": result.get("total", 0),
            "page": result.get("page", 1), "per_page": result.get("per_page", 20),
            "pages": result.get("pages", 1)}


@router.get("/programs/evaluations/{evaluation_id}")
async def get_program_evaluation(evaluation_id: str) -> dict:
    svc = _get_services()["program"]
    evaluation = await svc.get_evaluation(evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Program evaluation not found")
    return {"status": "success", "data": {
        "id": evaluation.id,
        "program_name": evaluation.program_name,
        "period": evaluation.period,
        "effectiveness_score": evaluation.effectiveness_score,
        "competency_coverage": evaluation.competency_coverage,
        "course_performance": evaluation.course_performance,
        "resource_utilization": evaluation.resource_utilization,
        "a11y_readiness": evaluation.a11y_readiness,
        "governance_compliance": evaluation.governance_compliance,
        "doc_health": evaluation.doc_health,
        "generated_at": evaluation.generated_at.isoformat(),
    }}


@router.get("/programs/executive-summary")
async def get_executive_summary() -> dict:
    svc = _get_services()["program"]
    summary = await svc.generate_executive_summary()
    return {"status": "success", "data": {
        "overall_health": summary.overall_health,
        "key_findings": summary.key_findings,
        "recommendations": summary.recommendations,
        "priorities": summary.priorities,
        "generated_at": summary.generated_at.isoformat(),
    }}


@router.get("/programs/executive-summary/latest")
async def get_latest_executive_summary() -> dict:
    svc = _get_services()["program"]
    summary = await svc.get_latest_summary()
    if summary is None:
        raise HTTPException(status_code=404, detail="No executive summary found")
    return {"status": "success", "data": {
        "overall_health": summary.overall_health,
        "key_findings": summary.key_findings,
        "recommendations": summary.recommendations,
        "generated_at": summary.generated_at.isoformat(),
    }}


@router.get("/programs/evaluations/{evaluation_id}/export")
async def export_program_evaluation(
    evaluation_id: str,
    format_type: str = Query(default="json"),
) -> dict:
    svc = _get_services()["program"]
    result = await svc.export_evaluation(evaluation_id, format_type)
    if result is None:
        raise HTTPException(status_code=404, detail="Program evaluation not found")
    return {"status": "success", "data": result}


# ======================================================================
# Continuous Improvement – Action Plans
# ======================================================================


@router.post("/improvement/plans", status_code=201)
async def create_action_plan(body: CreateActionPlanRequest) -> dict:
    svc = _get_services()["improvement"]
    plan = await svc.create_action_plan(
        title=body.title,
        description=body.description,
        owner=body.owner,
        target_date=body.target_date,
        items=body.items,
    )
    return {"status": "success", "data": {
        "id": plan.id, "title": plan.title, "status": plan.status.value,
        "created_at": plan.created_at.isoformat(),
    }}


@router.get("/improvement/plans")
async def list_action_plans(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict:
    svc = _get_services()["improvement"]
    result = await svc.list_action_plans(page=page, per_page=per_page)
    items = [{"id": p.id, "title": p.title, "status": p.status.value,
              "owner": p.owner, "target_date": p.target_date}
             for p in result.get("items", [])]
    return {"status": "success", "items": items, "total": result.get("total", 0),
            "page": result.get("page", 1), "per_page": result.get("per_page", 20),
            "pages": result.get("pages", 1)}


@router.get("/improvement/plans/{plan_id}")
async def get_action_plan(plan_id: str) -> dict:
    svc = _get_services()["improvement"]
    plan = await svc.get_action_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Action plan not found")
    return {"status": "success", "data": {
        "id": plan.id, "title": plan.title, "description": plan.description,
        "owner": plan.owner, "status": plan.status.value,
        "target_date": plan.target_date,
        "created_at": plan.created_at.isoformat(),
    }}


@router.patch("/improvement/plans/{plan_id}/status")
async def update_plan_status(plan_id: str, status: str) -> dict:
    svc = _get_services()["improvement"]
    try:
        plan = await svc.update_plan_status(plan_id, status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if plan is None:
        raise HTTPException(status_code=404, detail="Action plan not found")
    return {"status": "success", "data": {
        "id": plan.id, "status": plan.status.value,
    }}


@router.post("/improvement/plans/{plan_id}/items", status_code=201)
async def add_plan_item(plan_id: str, description: str, review_date: str = "") -> dict:
    svc = _get_services()["improvement"]
    item = await svc.add_plan_item(plan_id, description, review_date)
    if item is None:
        raise HTTPException(status_code=404, detail="Action plan not found")
    return {"status": "success", "data": {
        "id": item.id, "plan_id": item.plan_id,
        "description": item.description, "status": item.status,
    }}


@router.get("/improvement/plans/{plan_id}/items")
async def get_plan_items(plan_id: str) -> dict:
    svc = _get_services()["improvement"]
    items = await svc.get_plan_items(plan_id)
    return {"status": "success", "items": [
        {"id": i.id, "description": i.description, "status": i.status,
         "review_date": i.review_date}
        for i in items
    ]}


@router.get("/improvement/plans/{plan_id}/progress")
async def get_plan_progress(plan_id: str) -> dict:
    svc = _get_services()["improvement"]
    progress = await svc.compute_plan_progress(plan_id)
    return {"status": "success", "data": progress}


# ======================================================================
# Continuous Improvement – Initiatives & Reports
# ======================================================================


@router.post("/improvement/initiatives", status_code=201)
async def create_initiative(body: CreateInitiativeRequest) -> dict:
    svc = _get_services()["improvement"]
    initiative = await svc.create_initiative(
        name=body.name,
        description=body.description,
        start_date=body.start_date,
        end_date=body.end_date,
        assignees=body.assignees,
        metrics=body.metrics,
    )
    return {"status": "success", "data": {
        "id": initiative.id, "name": initiative.name,
        "progress_pct": initiative.progress_pct,
    }}


@router.get("/improvement/initiatives")
async def list_initiatives(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict:
    svc = _get_services()["improvement"]
    result = await svc.list_initiatives(page=page, per_page=per_page)
    items = [{"id": i.id, "name": i.name, "progress_pct": i.progress_pct}
             for i in result.get("items", [])]
    return {"status": "success", "items": items, "total": result.get("total", 0),
            "page": result.get("page", 1), "per_page": result.get("per_page", 20),
            "pages": result.get("pages", 1)}


@router.get("/improvement/initiatives/{initiative_id}")
async def get_initiative(initiative_id: str) -> dict:
    svc = _get_services()["improvement"]
    initiative = await svc.get_initiative(initiative_id)
    if initiative is None:
        raise HTTPException(status_code=404, detail="Initiative not found")
    return {"status": "success", "data": {
        "id": initiative.id, "name": initiative.name,
        "description": initiative.description,
        "progress_pct": initiative.progress_pct,
        "assignees": initiative.assignees,
    }}


@router.patch("/improvement/initiatives/{initiative_id}")
async def update_initiative(
    initiative_id: str,
    progress_pct: Optional[float] = None,
) -> dict:
    svc = _get_services()["improvement"]
    initiative = await svc.update_initiative(initiative_id, progress_pct=progress_pct)
    if initiative is None:
        raise HTTPException(status_code=404, detail="Initiative not found")
    return {"status": "success", "data": {
        "id": initiative.id, "name": initiative.name,
        "progress_pct": initiative.progress_pct,
    }}


@router.post("/improvement/reports", status_code=201)
async def generate_improvement_report(body: GenerateImprovementReportRequest) -> dict:
    svc = _get_services()["improvement"]
    report = await svc.generate_improvement_report(
        initiative_id=body.initiative_id,
        period=body.period,
        progress=body.progress,
        findings=body.findings,
        next_steps=body.next_steps,
    )
    if report is None:
        raise HTTPException(status_code=404, detail="Initiative not found")
    return {"status": "success", "data": {
        "id": report.id, "initiative_id": report.initiative_id,
        "period": report.period, "progress": report.progress,
        "generated_at": report.generated_at.isoformat(),
    }}


@router.get("/improvement/initiatives/{initiative_id}/reports")
async def get_initiative_reports(initiative_id: str) -> dict:
    svc = _get_services()["improvement"]
    reports = await svc.get_initiative_reports(initiative_id)
    return {"status": "success", "items": [
        {"id": r.id, "period": r.period, "progress": r.progress,
         "generated_at": r.generated_at.isoformat()}
        for r in reports
    ]}


@router.post("/improvement/compare")
async def compare_periods(body: ComparePeriodsRequest) -> dict:
    svc = _get_services()["improvement"]
    comparison = await svc.compare_periods(
        period_a_label=body.period_a_label,
        period_b_label=body.period_b_label,
        period_a_metrics=body.period_a_metrics,
        period_b_metrics=body.period_b_metrics,
    )
    return {"status": "success", "data": {
        "period_a": comparison.period_a,
        "period_b": comparison.period_b,
        "metrics": comparison.metrics,
        "changes": comparison.changes,
    }}
