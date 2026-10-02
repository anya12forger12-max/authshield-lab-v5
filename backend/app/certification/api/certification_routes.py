"""Certification module API routes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/certification", tags=["certification"])


# ======================================================================
# Request / Response schemas
# ======================================================================


class RegisterServiceRequest(BaseModel):
    name: str
    status: str = Field(default="healthy")
    response_time_ms: float = Field(default=0.0)
    error_rate: float = Field(default=0.0)


class RegisterModuleRequest(BaseModel):
    name: str
    version: str = Field(default="0.1.0")
    status: str = Field(default="active")
    enabled: bool = Field(default=True)
    dependencies: list[str] = Field(default_factory=list)


class RegisterPackageRequest(BaseModel):
    name: str
    version: str = Field(default="")
    integrity: bool = Field(default=True)
    compatibility: bool = Field(default=True)
    health_score: float = Field(default=100.0)


class CreateCertificationRequest(BaseModel):
    name: str
    cert_type: str
    approved_by: str | None = Field(default=None)


class AddRequirementRequest(BaseModel):
    requirement: str
    description: str = Field(default="")


class FulfillRequirementRequest(BaseModel):
    evidence: str = Field(default="")


class IssueCertificationRequest(BaseModel):
    approver: str
    expires_at: str | None = Field(default=None)
    evidence: list[str] = Field(default_factory=list)
    metrics: dict[str, float] = Field(default_factory=dict)


class AddFindingRequest(BaseModel):
    finding: str


class AddCorrectiveActionRequest(BaseModel):
    action: str


class RegisterDependencyRequest(BaseModel):
    name: str
    version: str
    end_of_life_date: str | None = Field(default=None)
    status: str = Field(default="supported")
    update_available: bool = Field(default=False)
    latest_version: str = Field(default="")


class RecordApiStabilityRequest(BaseModel):
    version: str
    endpoints: int = Field(default=0)
    deprecated: int = Field(default=0)
    breaking_changes: int = Field(default=0)


class SetModuleOwnerRequest(BaseModel):
    module: str
    owner: str
    health: float = Field(default=100.0)


class RecordDocFreshnessRequest(BaseModel):
    component: str


class CreateRoadmapRequest(BaseModel):
    title: str
    priority: str = Field(default="medium")


class AddRoadmapItemRequest(BaseModel):
    description: str
    category: str = Field(default="")
    effort_hours: float = Field(default=0.0)
    status: str = Field(default="planned")
    target_date: str = Field(default="")


class CreateReleasePlanRequest(BaseModel):
    version: str
    code_name: str = Field(default="")
    end_date: str = Field(default="")


class CreateReleaseValidationRequest(BaseModel):
    release_id: str
    validation_type: str


class CreatePackageResultRequest(BaseModel):
    release_id: str
    platform: str
    package_type: str = Field(default="")
    output_path: str = Field(default="")
    checksum: str = Field(default="")


class RecordRegressionRequest(BaseModel):
    release_id: str
    tests_run: int = Field(default=0)
    passed: int = Field(default=0)
    failed: int = Field(default=0)
    skipped: int = Field(default=0)
    coverage: float = Field(default=0.0)


class RecordReleaseHistoryRequest(BaseModel):
    version: str
    summary: str = Field(default="")
    highlights: list[str] = Field(default_factory=list)
    known_issues: list[str] = Field(default_factory=list)


class ValidateBackupRequest(BaseModel):
    backup_id: str
    backup_type: str = Field(default="")
    size_bytes: int = Field(default=0)
    integrity: bool = Field(default=True)
    restorable: bool = Field(default=True)


class CompleteRestoreTestRequest(BaseModel):
    success: bool
    duration_ms: int = Field(default=0)
    data_integrity: bool = Field(default=True)


class StartArchiveRecoveryRequest(BaseModel):
    archive_id: str


class CompleteArchiveRecoveryRequest(BaseModel):
    items_recovered: int
    total_items: int


class RunCheckRequest(BaseModel):
    subsystem: str
    check_name: str
    status: str = Field(default="passed")
    details: str = Field(default="")
    evidence: str = Field(default="")


class RunAcceptanceTestRequest(BaseModel):
    version: str
    sign_off_required: list[str] = Field(default_factory=list)


# ======================================================================
# Helpers
# ======================================================================

_services: dict[str, Any] = {}


def _get_services() -> dict[str, Any]:
    """Lazy-initialise all certification services with in-memory repos."""
    if _services:
        return _services

    from ..repositories.certification_repository_impl import (
        InMemoryServiceStatusRepository,
        InMemoryPlatformHealthRepository,
        InMemoryModuleInventoryRepository,
        InMemoryPackageHealthRepository,
        InMemoryEcosystemDashboardRepository,
        InMemoryPlatformCertificationRepository,
        InMemoryCertificationRequirementRepository,
        InMemoryCertificationReportRepository,
        InMemoryDependencyLifecycleRepository,
        InMemoryAPIStabilityRepository,
        InMemoryModuleOwnershipRepository,
        InMemoryDocumentationFreshnessRepository,
        InMemorySustainabilityDashboardRepository,
        InMemoryMaintenanceRoadmapRepository,
        InMemoryReleasePlanRepository,
        InMemoryReleaseValidationRepository,
        InMemoryPackagingResultRepository,
        InMemoryRegressionResultRepository,
        InMemoryReleaseHistoryRepository,
        InMemoryBackupValidationRepository,
        InMemoryRestoreTestRepository,
        InMemoryArchiveRecoveryRepository,
        InMemoryRecoveryReadinessRepository,
        InMemoryValidationCheckRepository,
        InMemorySubsystemValidationRepository,
        InMemoryPlatformValidationReportRepository,
        InMemoryFinalAcceptanceTestRepository,
    )
    from ..services.operations_service import OperationsService
    from ..services.certification_service import CertificationService
    from ..services.sustainability_service import SustainabilityService
    from ..services.release_engineering_service import ReleaseEngineeringService
    from ..services.disaster_recovery_service import DisasterRecoveryService
    from ..services.platform_validation_service import PlatformValidationService

    svc_ops = OperationsService(
        InMemoryServiceStatusRepository(),
        InMemoryPlatformHealthRepository(),
        InMemoryModuleInventoryRepository(),
        InMemoryPackageHealthRepository(),
        InMemoryEcosystemDashboardRepository(),
    )
    svc_cert = CertificationService(
        InMemoryPlatformCertificationRepository(),
        InMemoryCertificationRequirementRepository(),
        InMemoryCertificationReportRepository(),
    )
    svc_sustain = SustainabilityService(
        InMemoryDependencyLifecycleRepository(),
        InMemoryAPIStabilityRepository(),
        InMemoryModuleOwnershipRepository(),
        InMemoryDocumentationFreshnessRepository(),
        InMemorySustainabilityDashboardRepository(),
        InMemoryMaintenanceRoadmapRepository(),
    )
    svc_release = ReleaseEngineeringService(
        InMemoryReleasePlanRepository(),
        InMemoryReleaseValidationRepository(),
        InMemoryPackagingResultRepository(),
        InMemoryRegressionResultRepository(),
        InMemoryReleaseHistoryRepository(),
    )
    svc_recovery = DisasterRecoveryService(
        InMemoryBackupValidationRepository(),
        InMemoryRestoreTestRepository(),
        InMemoryArchiveRecoveryRepository(),
        InMemoryRecoveryReadinessRepository(),
    )
    svc_validation = PlatformValidationService(
        InMemoryValidationCheckRepository(),
        InMemorySubsystemValidationRepository(),
        InMemoryPlatformValidationReportRepository(),
        InMemoryFinalAcceptanceTestRepository(),
    )

    _services["operations"] = svc_ops
    _services["certification"] = svc_cert
    _services["sustainability"] = svc_sustain
    _services["release"] = svc_release
    _services["recovery"] = svc_recovery
    _services["validation"] = svc_validation
    return _services


def _to_dict(obj: Any) -> Any:
    """Recursively convert dataclass instances to dicts."""
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if isinstance(obj, list):
        return [_to_dict(i) for i in obj]
    return obj


# ======================================================================
# Health
# ======================================================================


@router.get("/health")
async def certification_health() -> dict:
    return {
        "status": "healthy",
        "module": "certification",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ======================================================================
# Operations
# ======================================================================


@router.post("/operations/services", status_code=201)
async def register_service(body: RegisterServiceRequest) -> dict:
    svc = _get_services()["operations"]
    from ..domain.entities.operations import ServiceHealthStatus
    try:
        shs = ServiceHealthStatus(body.status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {body.status}")
    result = await svc.register_service(body.name, shs, body.response_time_ms, body.error_rate)
    return {"status": "success", "data": _to_dict(result)}


@router.get("/operations/services")
async def list_services() -> dict:
    svc = _get_services()["operations"]
    items = await svc.list_services()
    return {"status": "success", "items": _to_dict(items)}


@router.get("/operations/services/{name}")
async def get_service_status(name: str) -> dict:
    svc = _get_services()["operations"]
    result = await svc.get_service_status(name)
    if result is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"status": "success", "data": _to_dict(result)}


@router.post("/operations/platform-health")
async def generate_platform_health(uptime_hours: float = Query(default=0.0)) -> dict:
    svc = _get_services()["operations"]
    result = await svc.generate_platform_health(uptime_hours)
    return {"status": "success", "data": _to_dict(result)}


@router.get("/operations/platform-health/latest")
async def get_latest_platform_health() -> dict:
    svc = _get_services()["operations"]
    result = await svc.get_latest_platform_health()
    if result is None:
        raise HTTPException(status_code=404, detail="No platform health data")
    return {"status": "success", "data": _to_dict(result)}


@router.post("/operations/modules", status_code=201)
async def register_module(body: RegisterModuleRequest) -> dict:
    svc = _get_services()["operations"]
    result = await svc.register_module(body.name, body.version, body.status, body.enabled, body.dependencies)
    return {"status": "success", "data": _to_dict(result)}


@router.get("/operations/modules")
async def list_modules() -> dict:
    svc = _get_services()["operations"]
    items = await svc.list_modules()
    return {"status": "success", "items": _to_dict(items)}


@router.get("/operations/modules/{name}")
async def get_module(name: str) -> dict:
    svc = _get_services()["operations"]
    result = await svc.get_module(name)
    if result is None:
        raise HTTPException(status_code=404, detail="Module not found")
    return {"status": "success", "data": _to_dict(result)}


@router.delete("/operations/modules/{module_id}")
async def remove_module(module_id: str) -> dict:
    svc = _get_services()["operations"]
    deleted = await svc.remove_module(module_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Module not found")
    return {"status": "success", "message": "Module removed"}


@router.post("/operations/packages", status_code=201)
async def register_package(body: RegisterPackageRequest) -> dict:
    svc = _get_services()["operations"]
    result = await svc.register_package(body.name, body.version, body.integrity, body.compatibility, body.health_score)
    return {"status": "success", "data": _to_dict(result)}


@router.get("/operations/packages")
async def list_packages() -> dict:
    svc = _get_services()["operations"]
    items = await svc.list_packages()
    return {"status": "success", "items": _to_dict(items)}


@router.post("/operations/ecosystem-dashboard")
async def generate_ecosystem_dashboard(
    doc_status: float = Query(default=0.0),
    a11y_score: float = Query(default=0.0),
    security_score: float = Query(default=0.0),
    performance_score: float = Query(default=0.0),
) -> dict:
    svc = _get_services()["operations"]
    result = await svc.generate_ecosystem_dashboard(doc_status, a11y_score, security_score, performance_score)
    return {"status": "success", "data": _to_dict(result)}


@router.get("/operations/ecosystem-dashboard/latest")
async def get_latest_ecosystem_dashboard() -> dict:
    svc = _get_services()["operations"]
    result = await svc.get_latest_dashboard()
    if result is None:
        raise HTTPException(status_code=404, detail="No dashboard data")
    return {"status": "success", "data": _to_dict(result)}


# ======================================================================
# Certifications
# ======================================================================


@router.post("/certs", status_code=201)
async def create_certification(body: CreateCertificationRequest) -> dict:
    svc = _get_services()["certification"]
    cert = await svc.create_certification(body.name, body.cert_type, body.approved_by)
    return {"status": "success", "data": _to_dict(cert)}


@router.get("/certs")
async def list_certifications() -> dict:
    svc = _get_services()["certification"]
    items = await svc.list_certifications()
    return {"status": "success", "items": _to_dict(items)}


@router.get("/certs/{cert_id}")
async def get_certification(cert_id: str) -> dict:
    svc = _get_services()["certification"]
    cert = await svc.get_certification(cert_id)
    if cert is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    return {"status": "success", "data": _to_dict(cert)}


@router.post("/certs/{cert_id}/start")
async def start_certification(cert_id: str) -> dict:
    svc = _get_services()["certification"]
    cert = await svc.start_certification(cert_id)
    if cert is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    return {"status": "success", "data": _to_dict(cert)}


@router.post("/certs/{cert_id}/requirements", status_code=201)
async def add_requirement(cert_id: str, body: AddRequirementRequest) -> dict:
    svc = _get_services()["certification"]
    try:
        req = await svc.add_requirement(cert_id, body.requirement, body.description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"status": "success", "data": _to_dict(req)}


@router.get("/certs/{cert_id}/requirements")
async def list_requirements(cert_id: str) -> dict:
    svc = _get_services()["certification"]
    items = await svc.get_requirements(cert_id)
    return {"status": "success", "items": _to_dict(items)}


@router.patch("/certs/requirements/{req_id}/fulfill")
async def fulfill_requirement(req_id: str, body: FulfillRequirementRequest) -> dict:
    svc = _get_services()["certification"]
    req = await svc.fulfill_requirement(req_id, body.evidence)
    if req is None:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return {"status": "success", "data": _to_dict(req)}


@router.post("/certs/{cert_id}/evaluate")
async def evaluate_certification(cert_id: str) -> dict:
    svc = _get_services()["certification"]
    cert = await svc.evaluate_certification(cert_id)
    if cert is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    return {"status": "success", "data": _to_dict(cert)}


@router.post("/certs/{cert_id}/issue")
async def issue_certification(cert_id: str, body: IssueCertificationRequest) -> dict:
    svc = _get_services()["certification"]
    cert = await svc.issue_certification(cert_id, body.approver, evidence=body.evidence, metrics=body.metrics)
    if cert is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    return {"status": "success", "data": _to_dict(cert)}


@router.post("/certs/{cert_id}/revoke")
async def revoke_certification(cert_id: str) -> dict:
    svc = _get_services()["certification"]
    cert = await svc.revoke_certification(cert_id)
    if cert is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    return {"status": "success", "data": _to_dict(cert)}


@router.post("/certs/{cert_id}/findings", status_code=201)
async def add_finding(cert_id: str, body: AddFindingRequest) -> dict:
    svc = _get_services()["certification"]
    cert = await svc.add_finding(cert_id, body.finding)
    if cert is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    return {"status": "success", "data": _to_dict(cert)}


@router.post("/certs/{cert_id}/corrective-actions", status_code=201)
async def add_corrective_action(cert_id: str, body: AddCorrectiveActionRequest) -> dict:
    svc = _get_services()["certification"]
    cert = await svc.add_corrective_action(cert_id, body.action)
    if cert is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    return {"status": "success", "data": _to_dict(cert)}


@router.delete("/certs/{cert_id}")
async def delete_certification(cert_id: str) -> dict:
    svc = _get_services()["certification"]
    deleted = await svc.delete_certification(cert_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Certification not found")
    return {"status": "success", "message": "Certification deleted"}


@router.post("/certs/reports", status_code=201)
async def generate_certification_report(title: str = Query(default="Certification Report")) -> dict:
    svc = _get_services()["certification"]
    report = await svc.generate_report(title)
    return {"status": "success", "data": _to_dict(report)}


@router.get("/certs/reports/latest")
async def get_latest_certification_report() -> dict:
    svc = _get_services()["certification"]
    report = await svc.get_latest_report()
    if report is None:
        raise HTTPException(status_code=404, detail="No report available")
    return {"status": "success", "data": _to_dict(report)}


# ======================================================================
# Sustainability
# ======================================================================


@router.post("/sustainability/dependencies", status_code=201)
async def register_dependency(body: RegisterDependencyRequest) -> dict:
    svc = _get_services()["sustainability"]
    dep = await svc.register_dependency(
        body.name, body.version, body.end_of_life_date, body.status,
        body.update_available, body.latest_version,
    )
    return {"status": "success", "data": _to_dict(dep)}


@router.get("/sustainability/dependencies")
async def list_dependencies() -> dict:
    svc = _get_services()["sustainability"]
    items = await svc.list_dependencies()
    return {"status": "success", "items": _to_dict(items)}


@router.get("/sustainability/dependencies/{name}")
async def get_dependency(name: str) -> dict:
    svc = _get_services()["sustainability"]
    dep = await svc.get_dependency(name)
    if dep is None:
        raise HTTPException(status_code=404, detail="Dependency not found")
    return {"status": "success", "data": _to_dict(dep)}


@router.delete("/sustainability/dependencies/{name}")
async def remove_dependency(name: str) -> dict:
    svc = _get_services()["sustainability"]
    deleted = await svc.remove_dependency(name)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dependency not found")
    return {"status": "success", "message": "Dependency removed"}


@router.post("/sustainability/api-stability", status_code=201)
async def record_api_stability(body: RecordApiStabilityRequest) -> dict:
    svc = _get_services()["sustainability"]
    report = await svc.record_api_stability(body.version, body.endpoints, body.deprecated, body.breaking_changes)
    return {"status": "success", "data": _to_dict(report)}


@router.get("/sustainability/api-stability/latest")
async def get_latest_api_stability() -> dict:
    svc = _get_services()["sustainability"]
    report = await svc.get_latest_api_stability()
    if report is None:
        raise HTTPException(status_code=404, detail="No API stability data")
    return {"status": "success", "data": _to_dict(report)}


@router.post("/sustainability/ownership", status_code=201)
async def set_module_owner(body: SetModuleOwnerRequest) -> dict:
    svc = _get_services()["sustainability"]
    result = await svc.set_module_owner(body.module, body.owner, body.health)
    return {"status": "success", "data": _to_dict(result)}


@router.get("/sustainability/ownership")
async def list_ownership() -> dict:
    svc = _get_services()["sustainability"]
    items = await svc.list_ownership()
    return {"status": "success", "items": _to_dict(items)}


@router.post("/sustainability/documentation", status_code=201)
async def record_doc_freshness(body: RecordDocFreshnessRequest) -> dict:
    svc = _get_services()["sustainability"]
    result = await svc.record_doc_freshness(body.component)
    return {"status": "success", "data": _to_dict(result)}


@router.get("/sustainability/documentation")
async def list_doc_freshness() -> dict:
    svc = _get_services()["sustainability"]
    items = await svc.list_doc_freshness()
    return {"status": "success", "items": _to_dict(items)}


@router.post("/sustainability/dashboard")
async def generate_sustainability_dashboard(
    technical_debt_hours: float = Query(default=0.0),
) -> dict:
    svc = _get_services()["sustainability"]
    result = await svc.generate_dashboard(technical_debt_hours)
    return {"status": "success", "data": _to_dict(result)}


@router.get("/sustainability/dashboard/latest")
async def get_latest_sustainability_dashboard() -> dict:
    svc = _get_services()["sustainability"]
    result = await svc.get_latest_dashboard()
    if result is None:
        raise HTTPException(status_code=404, detail="No dashboard data")
    return {"status": "success", "data": _to_dict(result)}


@router.post("/sustainability/roadmaps", status_code=201)
async def create_roadmap(body: CreateRoadmapRequest) -> dict:
    svc = _get_services()["sustainability"]
    roadmap = await svc.create_roadmap(body.title, body.priority)
    return {"status": "success", "data": _to_dict(roadmap)}


@router.get("/sustainability/roadmaps")
async def list_roadmaps() -> dict:
    svc = _get_services()["sustainability"]
    items = await svc.list_roadmaps()
    return {"status": "success", "items": _to_dict(items)}


@router.get("/sustainability/roadmaps/{roadmap_id}")
async def get_roadmap(roadmap_id: str) -> dict:
    svc = _get_services()["sustainability"]
    roadmap = await svc.get_roadmap(roadmap_id)
    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    return {"status": "success", "data": _to_dict(roadmap)}


@router.post("/sustainability/roadmaps/{roadmap_id}/items", status_code=201)
async def add_roadmap_item(roadmap_id: str, body: AddRoadmapItemRequest) -> dict:
    svc = _get_services()["sustainability"]
    roadmap = await svc.add_roadmap_item(
        roadmap_id, body.description, body.category, body.effort_hours, body.status, body.target_date,
    )
    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    return {"status": "success", "data": _to_dict(roadmap)}


# ======================================================================
# Release Engineering
# ======================================================================


@router.post("/releases", status_code=201)
async def create_release_plan(body: CreateReleasePlanRequest) -> dict:
    svc = _get_services()["release"]
    plan = await svc.create_plan(body.version, body.code_name, body.end_date)
    return {"status": "success", "data": _to_dict(plan)}


@router.get("/releases")
async def list_release_plans() -> dict:
    svc = _get_services()["release"]
    items = await svc.list_plans()
    return {"status": "success", "items": _to_dict(items)}


@router.get("/releases/{plan_id}")
async def get_release_plan(plan_id: str) -> dict:
    svc = _get_services()["release"]
    plan = await svc.get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Release plan not found")
    return {"status": "success", "data": _to_dict(plan)}


@router.post("/releases/{plan_id}/advance")
async def advance_release_plan(plan_id: str) -> dict:
    svc = _get_services()["release"]
    plan = await svc.advance_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Release plan not found")
    return {"status": "success", "data": _to_dict(plan)}


@router.delete("/releases/{plan_id}")
async def delete_release_plan(plan_id: str) -> dict:
    svc = _get_services()["release"]
    deleted = await svc.delete_plan(plan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Release plan not found")
    return {"status": "success", "message": "Release plan deleted"}


@router.post("/releases/validations", status_code=201)
async def create_release_validation(body: CreateReleaseValidationRequest) -> dict:
    svc = _get_services()["release"]
    val = await svc.create_validation(body.release_id, body.validation_type)
    return {"status": "success", "data": _to_dict(val)}


@router.get("/releases/{release_id}/validations")
async def list_release_validations(release_id: str) -> dict:
    svc = _get_services()["release"]
    items = await svc.get_validations_for_release(release_id)
    return {"status": "success", "items": _to_dict(items)}


@router.post("/releases/validations/{val_id}/pass")
async def pass_validation(val_id: str, details: str = Query(default="")) -> dict:
    svc = _get_services()["release"]
    val = await svc.pass_validation(val_id, details)
    if val is None:
        raise HTTPException(status_code=404, detail="Validation not found")
    return {"status": "success", "data": _to_dict(val)}


@router.post("/releases/validations/{val_id}/fail")
async def fail_validation(val_id: str, details: str = Query(default="")) -> dict:
    svc = _get_services()["release"]
    val = await svc.fail_validation(val_id, details)
    if val is None:
        raise HTTPException(status_code=404, detail="Validation not found")
    return {"status": "success", "data": _to_dict(val)}


@router.post("/releases/packages", status_code=201)
async def create_packaging_result(body: CreatePackageResultRequest) -> dict:
    svc = _get_services()["release"]
    pkg = await svc.create_package(body.release_id, body.platform, body.package_type, body.output_path, body.checksum)
    return {"status": "success", "data": _to_dict(pkg)}


@router.get("/releases/{release_id}/packages")
async def list_packaging_results(release_id: str) -> dict:
    svc = _get_services()["release"]
    items = await svc.get_packages_for_release(release_id)
    return {"status": "success", "items": _to_dict(items)}


@router.post("/releases/regression", status_code=201)
async def record_regression(body: RecordRegressionRequest) -> dict:
    svc = _get_services()["release"]
    result = await svc.record_regression(
        body.release_id, body.tests_run, body.passed, body.failed, body.skipped, body.coverage,
    )
    return {"status": "success", "data": _to_dict(result)}


@router.get("/releases/{release_id}/regression")
async def list_regression_results(release_id: str) -> dict:
    svc = _get_services()["release"]
    items = await svc.get_regression_results(release_id)
    return {"status": "success", "items": _to_dict(items)}


@router.post("/releases/history", status_code=201)
async def record_release_history(body: RecordReleaseHistoryRequest) -> dict:
    svc = _get_services()["release"]
    entry = await svc.record_history(body.version, body.summary, body.highlights, body.known_issues)
    return {"status": "success", "data": _to_dict(entry)}


@router.get("/releases/history")
async def list_release_history() -> dict:
    svc = _get_services()["release"]
    items = await svc.list_history()
    return {"status": "success", "items": _to_dict(items)}


# ======================================================================
# Disaster Recovery
# ======================================================================


@router.post("/recovery/backups", status_code=201)
async def validate_backup(body: ValidateBackupRequest) -> dict:
    svc = _get_services()["recovery"]
    result = await svc.validate_backup(body.backup_id, body.backup_type, body.size_bytes, body.integrity, body.restorable)
    return {"status": "success", "data": _to_dict(result)}


@router.get("/recovery/backups")
async def list_backup_validations() -> dict:
    svc = _get_services()["recovery"]
    items = await svc.list_backup_validations()
    return {"status": "success", "items": _to_dict(items)}


@router.post("/recovery/restore-tests", status_code=201)
async def create_restore_test(backup_id: str = Query(...)) -> dict:
    svc = _get_services()["recovery"]
    test = await svc.create_restore_test(backup_id)
    return {"status": "success", "data": _to_dict(test)}


@router.patch("/recovery/restore-tests/{test_id}/complete")
async def complete_restore_test(test_id: str, body: CompleteRestoreTestRequest) -> dict:
    svc = _get_services()["recovery"]
    test = await svc.complete_restore_test(test_id, body.success, body.duration_ms, body.data_integrity)
    if test is None:
        raise HTTPException(status_code=404, detail="Restore test not found")
    return {"status": "success", "data": _to_dict(test)}


@router.get("/recovery/restore-tests")
async def list_restore_tests() -> dict:
    svc = _get_services()["recovery"]
    items = await svc.list_restore_tests()
    return {"status": "success", "items": _to_dict(items)}


@router.post("/recovery/archive", status_code=201)
async def start_archive_recovery(body: StartArchiveRecoveryRequest) -> dict:
    svc = _get_services()["recovery"]
    result = await svc.start_archive_recovery(body.archive_id)
    return {"status": "success", "data": _to_dict(result)}


@router.patch("/recovery/archive/{recovery_id}/complete")
async def complete_archive_recovery(recovery_id: str, body: CompleteArchiveRecoveryRequest) -> dict:
    svc = _get_services()["recovery"]
    result = await svc.complete_archive_recovery(recovery_id, body.items_recovered, body.total_items)
    if result is None:
        raise HTTPException(status_code=404, detail="Archive recovery not found")
    return {"status": "success", "data": _to_dict(result)}


@router.get("/recovery/archive")
async def list_archive_recoveries() -> dict:
    svc = _get_services()["recovery"]
    items = await svc.list_archive_recoveries()
    return {"status": "success", "items": _to_dict(items)}


@router.post("/recovery/readiness")
async def generate_readiness_report() -> dict:
    svc = _get_services()["recovery"]
    report = await svc.generate_readiness_report()
    return {"status": "success", "data": _to_dict(report)}


@router.get("/recovery/readiness/latest")
async def get_latest_readiness() -> dict:
    svc = _get_services()["recovery"]
    report = await svc.get_latest_readiness()
    if report is None:
        raise HTTPException(status_code=404, detail="No readiness data")
    return {"status": "success", "data": _to_dict(report)}


# ======================================================================
# Platform Validation
# ======================================================================


@router.post("/validation/checks", status_code=201)
async def run_check(body: RunCheckRequest) -> dict:
    svc = _get_services()["validation"]
    check = await svc.run_check(body.subsystem, body.check_name, body.status, body.details, body.evidence)
    return {"status": "success", "data": _to_dict(check)}


@router.get("/validation/checks")
async def list_checks() -> dict:
    svc = _get_services()["validation"]
    items = await svc.list_checks()
    return {"status": "success", "items": _to_dict(items)}


@router.get("/validation/checks/{subsystem}")
async def get_checks_for_subsystem(subsystem: str) -> dict:
    svc = _get_services()["validation"]
    items = await svc.get_checks_for_subsystem(subsystem)
    return {"status": "success", "items": _to_dict(items)}


@router.post("/validation/subsystems/{subsystem}")
async def validate_subsystem(subsystem: str) -> dict:
    svc = _get_services()["validation"]
    result = await svc.validate_subsystem(subsystem)
    return {"status": "success", "data": _to_dict(result)}


@router.get("/validation/subsystems")
async def list_subsystem_validations() -> dict:
    svc = _get_services()["validation"]
    items = await svc.list_subsystem_validations()
    return {"status": "success", "items": _to_dict(items)}


@router.post("/validation/all")
async def validate_all_subsystems() -> dict:
    svc = _get_services()["validation"]
    report = await svc.validate_all_subsystems()
    return {"status": "success", "data": _to_dict(report)}


@router.get("/validation/reports/latest")
async def get_latest_validation_report() -> dict:
    svc = _get_services()["validation"]
    report = await svc.get_latest_report()
    if report is None:
        raise HTTPException(status_code=404, detail="No validation report")
    return {"status": "success", "data": _to_dict(report)}


@router.post("/validation/acceptance", status_code=201)
async def run_acceptance_test(body: RunAcceptanceTestRequest) -> dict:
    svc = _get_services()["validation"]
    fat = await svc.run_acceptance_test(body.version, body.sign_off_required)
    return {"status": "success", "data": _to_dict(fat)}


@router.get("/validation/acceptance")
async def list_acceptance_tests() -> dict:
    svc = _get_services()["validation"]
    items = await svc.list_acceptance_tests()
    return {"status": "success", "items": _to_dict(items)}


@router.get("/validation/acceptance/version/{version}")
async def get_acceptance_test_by_version(version: str) -> dict:
    svc = _get_services()["validation"]
    fat = await svc.get_acceptance_test_by_version(version)
    if fat is None:
        raise HTTPException(status_code=404, detail="No acceptance test for version")
    return {"status": "success", "data": _to_dict(fat)}
