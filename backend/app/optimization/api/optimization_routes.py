"""Optimization API routes — FastAPI APIRouter for all optimization operations."""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ...shared.responses import SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/optimization", tags=["optimization"])

# ---------------------------------------------------------------------------
# Lazy-loaded service singletons
# ---------------------------------------------------------------------------

_performance_service: Any = None
_ai_assistant_service: Any = None
_sustainability_service: Any = None
_release_governance_service: Any = None
_compatibility_service: Any = None
_feature_flag_service: Any = None
_observability_service: Any = None


def _get_performance_service() -> Any:
    global _performance_service  # noqa: PLW0603
    if _performance_service is None:
        from ..repositories.optimization_repository_impl import (
            InMemoryBenchmarkRepository,
            InMemoryDashboardRepository,
            InMemoryPerformanceMetricRepository,
        )
        from ..services.performance_service import PerformanceService
        _performance_service = PerformanceService(
            InMemoryPerformanceMetricRepository(),
            InMemoryBenchmarkRepository(),
            InMemoryDashboardRepository(),
        )
    return _performance_service


def _get_ai_assistant_service() -> Any:
    global _ai_assistant_service  # noqa: PLW0603
    if _ai_assistant_service is None:
        from ..repositories.optimization_repository_impl import InMemoryAIAssistantRepository
        from ..services.ai_assistant_service import AIAssistantService
        _ai_assistant_service = AIAssistantService(InMemoryAIAssistantRepository())
    return _ai_assistant_service


def _get_sustainability_service() -> Any:
    global _sustainability_service  # noqa: PLW0603
    if _sustainability_service is None:
        from ..repositories.optimization_repository_impl import InMemorySustainabilityRepository
        from ..services.sustainability_service import SustainabilityService
        _sustainability_service = SustainabilityService(InMemorySustainabilityRepository())
    return _sustainability_service


def _get_release_governance_service() -> Any:
    global _release_governance_service  # noqa: PLW0603
    if _release_governance_service is None:
        from ..repositories.optimization_repository_impl import InMemoryReleaseRepository
        from ..services.release_governance_service import ReleaseGovernanceService
        _release_governance_service = ReleaseGovernanceService(InMemoryReleaseRepository())
    return _release_governance_service


def _get_compatibility_service() -> Any:
    global _compatibility_service  # noqa: PLW0603
    if _compatibility_service is None:
        from ..repositories.optimization_repository_impl import InMemoryCompatibilityRepository
        from ..services.compatibility_service import CompatibilityService
        _compatibility_service = CompatibilityService(InMemoryCompatibilityRepository())
    return _compatibility_service


def _get_feature_flag_service() -> Any:
    global _feature_flag_service  # noqa: PLW0603
    if _feature_flag_service is None:
        from ..repositories.optimization_repository_impl import (
            InMemoryConfigProfileRepository,
            InMemoryFeatureFlagRepository,
        )
        from ..services.feature_flag_service import FeatureFlagService
        _feature_flag_service = FeatureFlagService(
            InMemoryFeatureFlagRepository(),
            InMemoryConfigProfileRepository(),
        )
    return _feature_flag_service


def _get_observability_service() -> Any:
    global _observability_service  # noqa: PLW0603
    if _observability_service is None:
        from ..repositories.optimization_repository_impl import InMemoryDiagnosticTraceRepository
        from ..services.observability_extended_service import ObservabilityExtendedService
        _observability_service = ObservabilityExtendedService(InMemoryDiagnosticTraceRepository())
    return _observability_service


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class PerformanceMetricRequest(BaseModel):
    name: str
    category: str = ""
    value: float
    unit: str = ""
    threshold: float = 0.0


class BenchmarkRequest(BaseModel):
    name: str
    category: str = ""
    value: float
    unit: str = ""
    threshold: float = 0.0
    baseline_value: float = 0.0


class DashboardRequest(BaseModel):
    app_start_ms: float = 0.0
    db_init_ms: float = 0.0
    module_load_ms: dict[str, float] = Field(default_factory=dict)
    plugin_load_ms: dict[str, float] = Field(default_factory=dict)
    memory_used_mb: float = 0.0
    memory_available_mb: float = 0.0
    memory_peak_mb: float = 0.0
    gc_collections: int = 0
    storage_total_mb: float = 0.0
    storage_used_mb: float = 0.0
    storage_by_module: dict[str, float] = Field(default_factory=dict)
    backup_mb: float = 0.0
    archive_mb: float = 0.0
    search_query_count: int = 0
    search_avg_response_ms: float = 0.0
    search_cache_hit_rate: float = 0.0
    search_index_size: int = 0
    avg_render_ms: float = 0.0
    paint_time_ms: float = 0.0
    interactive_time_ms: float = 0.0
    frame_rate: float = 0.0


class FeatureFlagRequest(BaseModel):
    name: str
    description: str = ""
    enabled: bool = False
    category: str = ""
    default_value: bool = False
    rollout_date: str = ""
    removal_date: str = ""


class ConfigProfileRequest(BaseModel):
    name: str
    target_audience: str = ""
    settings: dict[str, Any] = Field(default_factory=dict)
    version: str = "1.0"


class AISuggestionRequest(BaseModel):
    suggestion_type: str = "outline"
    content: str = ""
    source_material: str = ""


class CompatibilityCheckRequest(BaseModel):
    platforms: list[str] = Field(default_factory=list)
    components: list[str] = Field(default_factory=list)
    checks: dict[str, Any] = Field(default_factory=dict)


class SustainabilityMetricRequest(BaseModel):
    name: str
    category: str = ""
    score: float
    max_score: float = 100.0
    trend: str = "stable"


class TechnicalDebtRequest(BaseModel):
    category: str = ""
    description: str
    severity: str = "low"
    estimated_hours: float = 0.0


class ReleaseWorkflowRequest(BaseModel):
    release_id: str
    version: str
    created_by: str = ""
    initial_stage: Optional[str] = None


class ReleaseApprovalRequest(BaseModel):
    workflow_id: str
    stage: str = "planning"
    approver: str


class ReleaseGateRequest(BaseModel):
    release_id: str
    gate_type: str
    required: bool = True


class ReleaseChecklistRequest(BaseModel):
    release_id: str
    item: str
    category: str = ""
    assignee: str = ""
    due_date: str = ""


class ReadingLevelRequest(BaseModel):
    text: str


class ConsistencyCheckRequest(BaseModel):
    contents: list[str] = Field(default_factory=list)


class TraceRequest(BaseModel):
    name: str
    spans: list[dict[str, Any]] = Field(default_factory=list)


class StorageAnalysisRequest(BaseModel):
    total_mb: float = 0.0
    used_mb: float = 0.0
    by_module: dict[str, float] = Field(default_factory=dict)
    backup_mb: float = 0.0
    archive_mb: float = 0.0


# ===================================================================
# Performance endpoints
# ===================================================================

@router.post("/metrics", status_code=201)
async def collect_metric(request: PerformanceMetricRequest) -> dict[str, Any]:
    service = _get_performance_service()
    return service.collect_metric(request.model_dump())


@router.get("/metrics")
async def list_metrics(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_performance_service()
    return service.list_metrics(page=page, per_page=per_page, category=category)


@router.get("/metrics/{metric_id}")
async def get_metric(metric_id: str) -> dict[str, Any]:
    service = _get_performance_service()
    metric = service.get_metric(metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_id}' not found")
    return metric


@router.delete("/metrics/{metric_id}")
async def delete_metric(metric_id: str) -> SuccessResponse:
    service = _get_performance_service()
    service.delete_metric(metric_id)
    return SuccessResponse(message=f"Metric '{metric_id}' deleted")


@router.get("/metrics/category/{category}")
async def get_metrics_by_category(category: str) -> dict[str, Any]:
    service = _get_performance_service()
    metrics = service.get_metrics_by_category(category)
    return {"category": category, "metrics": metrics}


# ===================================================================
# Benchmark endpoints
# ===================================================================

@router.post("/benchmarks", status_code=201)
async def run_benchmark(request: BenchmarkRequest) -> dict[str, Any]:
    service = _get_performance_service()
    return service.run_benchmark(request.model_dump())


@router.get("/benchmarks")
async def list_benchmarks(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_performance_service()
    return service.list_benchmarks(page=page, per_page=per_page, category=category)


@router.get("/benchmarks/history/{name}")
async def get_benchmark_history(name: str) -> dict[str, Any]:
    service = _get_performance_service()
    return service.get_benchmark_history(name)


@router.get("/benchmarks/regressions")
async def detect_regressions() -> dict[str, Any]:
    service = _get_performance_service()
    regressions = service.detect_regressions()
    return {"regressions": regressions, "count": len(regressions)}


# ===================================================================
# Dashboard endpoints
# ===================================================================

@router.post("/dashboard", status_code=201)
async def generate_dashboard(request: DashboardRequest) -> dict[str, Any]:
    service = _get_performance_service()
    return service.generate_dashboard(request.model_dump())


@router.get("/dashboard/latest")
async def get_latest_dashboard() -> dict[str, Any]:
    service = _get_performance_service()
    dashboard = service.get_latest_dashboard()
    if not dashboard:
        raise HTTPException(status_code=404, detail="No dashboard data available")
    return dashboard


@router.get("/dashboard/{dashboard_id}")
async def get_dashboard(dashboard_id: str) -> dict[str, Any]:
    service = _get_performance_service()
    dashboard = service.get_dashboard(dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail=f"Dashboard '{dashboard_id}' not found")
    return dashboard


@router.delete("/dashboard/{dashboard_id}")
async def delete_dashboard(dashboard_id: str) -> SuccessResponse:
    service = _get_performance_service()
    service.delete_dashboard(dashboard_id)
    return SuccessResponse(message=f"Dashboard '{dashboard_id}' deleted")


# ===================================================================
# Feature Flag endpoints
# ===================================================================

@router.post("/feature-flags", status_code=201)
async def create_feature_flag(request: FeatureFlagRequest) -> dict[str, Any]:
    service = _get_feature_flag_service()
    return service.create_flag(request.model_dump())


@router.get("/feature-flags")
async def list_feature_flags(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    enabled_only: bool = Query(False),
) -> dict[str, Any]:
    service = _get_feature_flag_service()
    return service.list_flags(page=page, per_page=per_page, category=category, enabled_only=enabled_only)


@router.get("/feature-flags/{flag_id}")
async def get_feature_flag(flag_id: str) -> dict[str, Any]:
    service = _get_feature_flag_service()
    flag = service.get_flag(flag_id)
    if not flag:
        raise HTTPException(status_code=404, detail=f"Flag '{flag_id}' not found")
    return flag


@router.put("/feature-flags/{flag_id}/toggle")
async def toggle_feature_flag(flag_id: str) -> dict[str, Any]:
    service = _get_feature_flag_service()
    result = service.toggle_flag(flag_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Flag '{flag_id}' not found")
    return result


@router.put("/feature-flags/{flag_id}/enable")
async def enable_feature_flag(flag_id: str) -> dict[str, Any]:
    service = _get_feature_flag_service()
    result = service.enable_flag(flag_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Flag '{flag_id}' not found")
    return result


@router.put("/feature-flags/{flag_id}/disable")
async def disable_feature_flag(flag_id: str) -> dict[str, Any]:
    service = _get_feature_flag_service()
    result = service.disable_flag(flag_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Flag '{flag_id}' not found")
    return result


@router.get("/feature-flags/check/{name}")
async def check_feature_flag(name: str) -> dict[str, Any]:
    service = _get_feature_flag_service()
    return {"name": name, "enabled": service.is_enabled(name)}


@router.delete("/feature-flags/{flag_id}")
async def delete_feature_flag(flag_id: str) -> SuccessResponse:
    service = _get_feature_flag_service()
    service.delete_flag(flag_id)
    return SuccessResponse(message=f"Flag '{flag_id}' deleted")


# ===================================================================
# Config Profile endpoints
# ===================================================================

@router.post("/config-profiles", status_code=201)
async def create_config_profile(request: ConfigProfileRequest) -> dict[str, Any]:
    service = _get_feature_flag_service()
    return service.create_profile(request.model_dump())


@router.get("/config-profiles")
async def list_config_profiles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    target_audience: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_feature_flag_service()
    return service.list_profiles(page=page, per_page=per_page, target_audience=target_audience)


@router.get("/config-profiles/{profile_id}")
async def get_config_profile(profile_id: str) -> dict[str, Any]:
    service = _get_feature_flag_service()
    profile = service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found")
    return profile


@router.put("/config-profiles/{profile_id}")
async def update_config_profile(profile_id: str, request: ConfigProfileRequest) -> dict[str, Any]:
    service = _get_feature_flag_service()
    result = service.update_profile(profile_id, request.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found")
    return result


@router.delete("/config-profiles/{profile_id}")
async def delete_config_profile(profile_id: str) -> SuccessResponse:
    service = _get_feature_flag_service()
    service.delete_profile(profile_id)
    return SuccessResponse(message=f"Profile '{profile_id}' deleted")


# ===================================================================
# AI Assistant endpoints
# ===================================================================

@router.post("/ai/suggestions", status_code=201)
async def generate_ai_suggestion(request: AISuggestionRequest) -> dict[str, Any]:
    service = _get_ai_assistant_service()
    return service.generate_suggestion(request.model_dump())


@router.get("/ai/suggestions")
async def list_ai_suggestions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    suggestion_type: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_ai_assistant_service()
    return service.list_suggestions(page=page, per_page=per_page, suggestion_type=suggestion_type)


@router.get("/ai/suggestions/{suggestion_id}")
async def get_ai_suggestion(suggestion_id: str) -> dict[str, Any]:
    service = _get_ai_assistant_service()
    suggestion = service.get_suggestion(suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail=f"Suggestion '{suggestion_id}' not found")
    return suggestion


@router.put("/ai/suggestions/{suggestion_id}/review")
async def review_ai_suggestion(suggestion_id: str, accepted: bool = Query(...)) -> dict[str, Any]:
    service = _get_ai_assistant_service()
    result = service.review_suggestion(suggestion_id, accepted)
    if not result:
        raise HTTPException(status_code=404, detail=f"Suggestion '{suggestion_id}' not found")
    return result


@router.delete("/ai/suggestions/{suggestion_id}")
async def delete_ai_suggestion(suggestion_id: str) -> SuccessResponse:
    service = _get_ai_assistant_service()
    service.delete_suggestion(suggestion_id)
    return SuccessResponse(message=f"Suggestion '{suggestion_id}' deleted")


@router.post("/ai/reading-level")
async def analyze_reading_level(request: ReadingLevelRequest) -> dict[str, Any]:
    service = _get_ai_assistant_service()
    analysis = service.analyze_reading_level(request.text)
    return analysis.to_dict()


@router.post("/ai/glossary")
async def extract_glossary(request: ReadingLevelRequest) -> dict[str, Any]:
    service = _get_ai_assistant_service()
    terms = service.extract_glossary(request.text)
    return {"terms": terms, "count": len(terms)}


@router.post("/ai/consistency")
async def check_consistency(request: ConsistencyCheckRequest) -> dict[str, Any]:
    service = _get_ai_assistant_service()
    return service.check_consistency(request.contents)


@router.post("/ai/audit", status_code=201)
async def record_ai_generation(
    content_id: str = Query(...),
    ai_type: str = Query(...),
    input_text: str = Query(""),
    output_text: str = Query(""),
    model_version: str = Query("rule-based-1.0"),
) -> dict[str, Any]:
    service = _get_ai_assistant_service()
    return service.record_generation(content_id, ai_type, input_text, output_text, model_version)


@router.get("/ai/audits/{content_id}")
async def get_audits_for_content(content_id: str) -> dict[str, Any]:
    service = _get_ai_assistant_service()
    audits = service.get_audits_for_content(content_id)
    return {"content_id": content_id, "audits": audits}


@router.put("/ai/audits/{audit_id}/review")
async def review_audit(audit_id: str, approved: bool = Query(...)) -> dict[str, Any]:
    service = _get_ai_assistant_service()
    result = service.review_audit(audit_id, approved)
    if not result:
        raise HTTPException(status_code=404, detail=f"Audit '{audit_id}' not found")
    return result


# ===================================================================
# Compatibility endpoints
# ===================================================================

@router.post("/compatibility/reports", status_code=201)
async def generate_compatibility_report(request: CompatibilityCheckRequest) -> dict[str, Any]:
    service = _get_compatibility_service()
    return service.generate_report(request.model_dump())


@router.get("/compatibility/reports")
async def list_compatibility_reports(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    service = _get_compatibility_service()
    return service.list_reports(page=page, per_page=per_page)


@router.get("/compatibility/reports/{report_id}")
async def get_compatibility_report(report_id: str) -> dict[str, Any]:
    service = _get_compatibility_service()
    report = service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found")
    return report


@router.delete("/compatibility/reports/{report_id}")
async def delete_compatibility_report(report_id: str) -> SuccessResponse:
    service = _get_compatibility_service()
    service.delete_report(report_id)
    return SuccessResponse(message=f"Report '{report_id}' deleted")


@router.post("/compatibility/quick-check")
async def quick_compatibility_check(
    platform: str = Query(...),
    component: str = Query(...),
) -> dict[str, Any]:
    service = _get_compatibility_service()
    return service.quick_check(platform, component)


@router.post("/compatibility/matrix")
async def matrix_compatibility_check(request: CompatibilityCheckRequest) -> dict[str, Any]:
    service = _get_compatibility_service()
    return service.matrix_check(request.platforms, request.components)


# ===================================================================
# Sustainability endpoints
# ===================================================================

@router.post("/sustainability/metrics", status_code=201)
async def create_sustainability_metric(request: SustainabilityMetricRequest) -> dict[str, Any]:
    service = _get_sustainability_service()
    return service.create_metric(request.model_dump())


@router.get("/sustainability/metrics")
async def list_sustainability_metrics() -> list[dict[str, Any]]:
    service = _get_sustainability_service()
    return service.list_metrics()


@router.get("/sustainability/metrics/{metric_id}")
async def get_sustainability_metric(metric_id: str) -> dict[str, Any]:
    service = _get_sustainability_service()
    metric = service.get_metric(metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_id}' not found")
    return metric


@router.delete("/sustainability/metrics/{metric_id}")
async def delete_sustainability_metric(metric_id: str) -> SuccessResponse:
    service = _get_sustainability_service()
    service.delete_metric(metric_id)
    return SuccessResponse(message=f"Metric '{metric_id}' deleted")


@router.post("/sustainability/debt", status_code=201)
async def create_technical_debt(request: TechnicalDebtRequest) -> dict[str, Any]:
    service = _get_sustainability_service()
    return service.create_debt_item(request.model_dump())


@router.get("/sustainability/debt")
async def list_technical_debt(
    resolved: Optional[bool] = Query(None),
) -> list[dict[str, Any]]:
    service = _get_sustainability_service()
    return service.list_debt_items(resolved=resolved)


@router.get("/sustainability/debt/summary")
async def get_debt_summary() -> dict[str, Any]:
    service = _get_sustainability_service()
    return service.debt_summary()


@router.put("/sustainability/debt/{item_id}/resolve")
async def resolve_technical_debt(item_id: str) -> dict[str, Any]:
    service = _get_sustainability_service()
    result = service.resolve_debt_item(item_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Debt item '{item_id}' not found")
    return result


@router.delete("/sustainability/debt/{item_id}")
async def delete_technical_debt(item_id: str) -> SuccessResponse:
    service = _get_sustainability_service()
    service.delete_debt_item(item_id)
    return SuccessResponse(message=f"Debt item '{item_id}' deleted")


@router.post("/sustainability/dashboard", status_code=201)
async def generate_sustainability_dashboard(request: DashboardRequest) -> dict[str, Any]:
    service = _get_sustainability_service()
    return service.generate_dashboard(request.model_dump())


@router.post("/sustainability/api-stability")
async def assess_api_stability(request: DashboardRequest) -> dict[str, Any]:
    service = _get_sustainability_service()
    return service.assess_api_stability(request.model_dump())


# ===================================================================
# Release Governance endpoints
# ===================================================================

@router.post("/release/workflows", status_code=201)
async def create_release_workflow(request: ReleaseWorkflowRequest) -> dict[str, Any]:
    service = _get_release_governance_service()
    return service.create_workflow(request.model_dump())


@router.get("/release/workflows")
async def list_release_workflows(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    service = _get_release_governance_service()
    return service.list_workflows(page=page, per_page=per_page)


@router.get("/release/workflows/{workflow_id}")
async def get_release_workflow(workflow_id: str) -> dict[str, Any]:
    service = _get_release_governance_service()
    workflow = service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    return workflow


@router.put("/release/workflows/{workflow_id}/advance")
async def advance_release_workflow(
    workflow_id: str, notes: str = Query("")
) -> dict[str, Any]:
    service = _get_release_governance_service()
    try:
        return service.advance_workflow(workflow_id, notes=notes)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.put("/release/workflows/{workflow_id}/complete")
async def complete_release_workflow(workflow_id: str) -> dict[str, Any]:
    service = _get_release_governance_service()
    result = service.complete_workflow(workflow_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    return result


@router.post("/release/approvals", status_code=201)
async def create_release_approval(request: ReleaseApprovalRequest) -> dict[str, Any]:
    service = _get_release_governance_service()
    return service.create_approval(request.model_dump())


@router.put("/release/approvals/{approval_id}/approve")
async def approve_release(approval_id: str, comments: str = Query("")) -> dict[str, Any]:
    service = _get_release_governance_service()
    result = service.approve(approval_id, comments=comments)
    if not result:
        raise HTTPException(status_code=404, detail=f"Approval '{approval_id}' not found")
    return result


@router.put("/release/approvals/{approval_id}/reject")
async def reject_release(approval_id: str, comments: str = Query("")) -> dict[str, Any]:
    service = _get_release_governance_service()
    result = service.reject(approval_id, comments=comments)
    if not result:
        raise HTTPException(status_code=404, detail=f"Approval '{approval_id}' not found")
    return result


@router.post("/release/gates", status_code=201)
async def create_release_gate(request: ReleaseGateRequest) -> dict[str, Any]:
    service = _get_release_governance_service()
    return service.create_gate(request.model_dump())


@router.put("/release/gates/{gate_id}/check")
async def check_release_gate(
    gate_id: str, passed: bool = Query(...), evidence: str = Query("")
) -> dict[str, Any]:
    service = _get_release_governance_service()
    result = service.check_gate(gate_id, passed, evidence=evidence)
    if not result:
        raise HTTPException(status_code=404, detail=f"Gate '{gate_id}' not found")
    return result


@router.get("/release/gates/{release_id}")
async def get_release_gates(release_id: str) -> dict[str, Any]:
    service = _get_release_governance_service()
    gates = service.get_gates_for_release(release_id)
    return {"release_id": release_id, "gates": gates}


@router.post("/release/checklist", status_code=201)
async def create_checklist_item(request: ReleaseChecklistRequest) -> dict[str, Any]:
    service = _get_release_governance_service()
    return service.create_checklist_item(request.model_dump())


@router.put("/release/checklist/{item_id}/complete")
async def complete_checklist_item(item_id: str) -> dict[str, Any]:
    service = _get_release_governance_service()
    result = service.complete_checklist_item(item_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Checklist item '{item_id}' not found")
    return result


@router.get("/release/checklist/{release_id}")
async def get_release_checklist(release_id: str) -> dict[str, Any]:
    service = _get_release_governance_service()
    items = service.get_checklist_for_release(release_id)
    return {"release_id": release_id, "items": items}


@router.get("/release/checklist/{release_id}/progress")
async def get_checklist_progress(release_id: str) -> dict[str, Any]:
    service = _get_release_governance_service()
    return service.checklist_progress(release_id)


@router.get("/release/{release_id}/readiness")
async def check_release_readiness(release_id: str) -> dict[str, Any]:
    service = _get_release_governance_service()
    return service.is_release_ready(release_id)


# ===================================================================
# Observability endpoints
# ===================================================================

@router.post("/observability/traces", status_code=201)
async def create_diagnostic_trace(request: TraceRequest) -> dict[str, Any]:
    service = _get_observability_service()
    return service.create_trace(request.model_dump())


@router.get("/observability/traces")
async def list_diagnostic_traces(
    limit: int = Query(50, ge=1, le=200),
) -> list[dict[str, Any]]:
    service = _get_observability_service()
    return service.list_traces(limit=limit)


@router.get("/observability/traces/{trace_id}")
async def get_diagnostic_trace(trace_id: str) -> dict[str, Any]:
    service = _get_observability_service()
    trace = service.get_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Trace '{trace_id}' not found")
    return trace


@router.delete("/observability/traces/{trace_id}")
async def delete_diagnostic_trace(trace_id: str) -> SuccessResponse:
    service = _get_observability_service()
    service.delete_trace(trace_id)
    return SuccessResponse(message=f"Trace '{trace_id}' deleted")


@router.post("/observability/events/{timeline_id}", status_code=201)
async def record_event(timeline_id: str, event_data: dict[str, Any]) -> dict[str, Any]:
    service = _get_observability_service()
    return service.record_event(timeline_id, event_data)


@router.get("/observability/events/{timeline_id}")
async def get_timeline(
    timeline_id: str, limit: int = Query(100, ge=1, le=1000)
) -> dict[str, Any]:
    service = _get_observability_service()
    return service.get_timeline(timeline_id, limit=limit)


@router.get("/observability/timelines")
async def list_timelines() -> dict[str, Any]:
    service = _get_observability_service()
    timelines = service.list_timelines()
    return {"timelines": timelines}


@router.post("/observability/tasks", status_code=201)
async def register_background_task(
    task_id: str = Query(...),
    name: str = Query(...),
    description: str = Query(""),
) -> dict[str, Any]:
    service = _get_observability_service()
    return service.register_task(task_id, name, description=description)


@router.get("/observability/tasks")
async def list_background_tasks(
    status: Optional[str] = Query(None),
) -> list[dict[str, Any]]:
    service = _get_observability_service()
    return service.list_tasks(status=status)


@router.put("/observability/tasks/{task_id}/start")
async def start_background_task(task_id: str) -> dict[str, Any]:
    service = _get_observability_service()
    result = service.start_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return result


@router.put("/observability/tasks/{task_id}/complete")
async def complete_background_task(task_id: str) -> dict[str, Any]:
    service = _get_observability_service()
    result = service.complete_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return result


@router.post("/observability/storage-analytics")
async def analyze_storage(request: StorageAnalysisRequest) -> dict[str, Any]:
    service = _get_observability_service()
    return service.analyze_storage(request.model_dump())
