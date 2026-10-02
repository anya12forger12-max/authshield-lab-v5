"""Production module API routes."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ...shared.responses import SuccessResponse

router = APIRouter(prefix="/production", tags=["production"])


# ======================================================================
# Request / Response schemas
# ======================================================================


class CreateReleaseRequest(BaseModel):
    version: str
    name: str
    release_notes: list[str] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)
    bug_fixes: list[str] = Field(default_factory=list)
    known_issues: list[str] = Field(default_factory=list)
    deprecations: list[str] = Field(default_factory=list)
    minimum_platform_version: str = Field(default="")


class UpdateReleaseStatusRequest(BaseModel):
    status: str


class CreateBuildInfoRequest(BaseModel):
    version: str
    build_number: str
    build_environment: str = Field(default="local")
    python_version: Optional[str] = Field(default=None)
    platform: Optional[str] = Field(default=None)


class CreatePackageRequest(BaseModel):
    release_id: str
    name: str
    package_type: str = Field(default="installer")
    platform: str = Field(default="")
    checksum: str = Field(default="")
    file_size: int = Field(default=0)


class CreateLtsVersionRequest(BaseModel):
    version: str
    release_date: str
    end_of_support: str
    compatible_versions: list[str] = Field(default_factory=list)
    migration_path: str = Field(default="")
    notes: str = Field(default="")


class UpdateLtsStatusRequest(BaseModel):
    status: str


class CreateMigrationStepRequest(BaseModel):
    from_version: str
    to_version: str
    step_number: int
    description: str
    requires_backup: bool = Field(default=False)
    estimated_minutes: int = Field(default=0)
    rollback_available: bool = Field(default=True)


class CheckCompatibilityRequest(BaseModel):
    version_a: str
    version_b: str
    compatible: bool = Field(default=True)
    notes: str = Field(default="")


class CreateDeprecationRequest(BaseModel):
    feature: str
    deprecated_in_version: str
    replacement: str = Field(default="")
    removal_version: str = Field(default="")
    announced_at: str = Field(default="")


class CreateGovernanceReviewRequest(BaseModel):
    area: str
    title: str
    description: str = Field(default="")
    reviewer: str = Field(default="")


class CompleteReviewRequest(BaseModel):
    status: str
    recommendations: list[str] = Field(default_factory=list)


class CreateGovernancePolicyRequest(BaseModel):
    area: str
    name: str
    description: str = Field(default="")
    requirements: list[str] = Field(default_factory=list)
    review_frequency_days: int = Field(default=30)


class RunAuditRequest(BaseModel):
    name: str
    checks: list[dict[str, str]] = Field(default_factory=list)


class GenerateReportRequest(BaseModel):
    title: str
    area: str
    findings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class CreateCertificationRequest(BaseModel):
    name: str
    cert_type: str
    approved_by: str = Field(default="")


class AddRequirementRequest(BaseModel):
    requirement: str
    description: str = Field(default="")


class FulfillRequirementRequest(BaseModel):
    evidence: str = Field(default="")


class CreateKnowledgeEntryRequest(BaseModel):
    title: str
    category: str
    content: str
    tags: list[str] = Field(default_factory=list)
    version: str = Field(default="")
    author: str = Field(default="")


class UpdateKnowledgeEntryRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list[str]] = None
    version: Optional[str] = None


class CreateAdrRequest(BaseModel):
    title: str
    context: str
    decision: str
    consequences: str = Field(default="")
    alternatives: str = Field(default="")


class UpdateAdrStatusRequest(BaseModel):
    status: str


class CreateCodingStandardRequest(BaseModel):
    name: str
    category: str
    description: str
    examples: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)


class CreateFeatureFlagRequest(BaseModel):
    name: str
    description: str = Field(default="")
    enabled: bool = Field(default=False)
    rollout_percentage: float = Field(default=0.0)
    allowed_environments: list[str] = Field(default_factory=list)
    allowed_roles: list[str] = Field(default_factory=list)


class UpdateFeatureFlagRequest(BaseModel):
    description: Optional[str] = None
    enabled: Optional[bool] = None
    rollout_percentage: Optional[float] = None
    allowed_environments: Optional[list[str]] = None
    allowed_roles: Optional[list[str]] = None


class CreateConfigProfileRequest(BaseModel):
    name: str
    environment: str = Field(default="development")
    values: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = Field(default=False)


class UpdateConfigProfileRequest(BaseModel):
    values: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class CreateApiVersionRequest(BaseModel):
    version: str
    base_path: str
    status: str = Field(default="active")


class CreateExperimentalFeatureRequest(BaseModel):
    name: str
    description: str
    flag_id: str = Field(default="")
    min_version: str = Field(default="")
    required_roles: list[str] = Field(default_factory=list)


class HealthIndicatorInput(BaseModel):
    name: str
    value: float
    threshold: float


class GenerateHealthReportRequest(BaseModel):
    indicators: list[HealthIndicatorInput] = Field(default_factory=list)


class RecordMigrationRequest(BaseModel):
    from_version: str
    to_version: str
    status: str
    steps_completed: int
    total_steps: int
    notes: str = Field(default="")


class RecordReleaseHistoryRequest(BaseModel):
    release_id: str
    version: str
    summary: str = Field(default="")


# ======================================================================
# Helpers – lazy service singletons
# ======================================================================

_services: dict[str, Any] = {}


def _get_services() -> dict[str, Any]:
    """Lazy-initialise all production services with in-memory repos."""
    if _services:
        return _services

    from ..repositories.production_repository_impl import (
        InMemoryReleaseRepository,
        InMemoryReleasePackageRepository,
        InMemoryBuildInfoRepository,
        InMemoryLtsVersionRepository,
        InMemoryMigrationStepRepository,
        InMemoryCompatibilityMatrixRepository,
        InMemoryDeprecationEntryRepository,
        InMemoryGovernanceReviewRepository,
        InMemoryGovernancePolicyRepository,
        InMemoryArchitectureAuditRepository,
        InMemoryGovernanceReportRepository,
        InMemoryCertificationRepository,
        InMemoryCertificationRequirementRepository,
        InMemoryProductionValidationRepository,
        InMemoryProjectHealthRepository,
        InMemoryArchitectureDecisionRecordRepository,
        InMemoryMigrationHistoryRepository,
        InMemoryReleaseHistoryRepository,
        InMemoryKnowledgeEntryRepository,
        InMemoryCodingStandardRepository,
    )
    from ..services.release_service import ReleaseService
    from ..services.lts_service import LtsService
    from ..services.governance_service import GovernanceService
    from ..services.certification_service import CertificationService
    from ..services.production_validation_service import ProductionValidationService
    from ..services.health_dashboard_service import HealthDashboardService
    from ..services.knowledge_service import KnowledgeService
    from ..services.feature_flag_service import FeatureFlagService

    release_repo = InMemoryReleaseRepository()
    package_repo = InMemoryReleasePackageRepository()
    build_repo = InMemoryBuildInfoRepository()
    lts_repo = InMemoryLtsVersionRepository()
    step_repo = InMemoryMigrationStepRepository()
    compat_repo = InMemoryCompatibilityMatrixRepository()
    deprecation_repo = InMemoryDeprecationEntryRepository()
    review_repo = InMemoryGovernanceReviewRepository()
    policy_repo = InMemoryGovernancePolicyRepository()
    audit_repo = InMemoryArchitectureAuditRepository()
    report_repo = InMemoryGovernanceReportRepository()
    cert_repo = InMemoryCertificationRepository()
    req_repo = InMemoryCertificationRequirementRepository()
    val_repo = InMemoryProductionValidationRepository()
    health_repo = InMemoryProjectHealthRepository()
    adr_repo = InMemoryArchitectureDecisionRecordRepository()
    mig_hist_repo = InMemoryMigrationHistoryRepository()
    rel_hist_repo = InMemoryReleaseHistoryRepository()
    knowledge_repo = InMemoryKnowledgeEntryRepository()
    standard_repo = InMemoryCodingStandardRepository()

    _services["release"] = ReleaseService(release_repo, package_repo, build_repo)
    _services["lts"] = LtsService(lts_repo, step_repo, compat_repo, deprecation_repo)
    _services["governance"] = GovernanceService(review_repo, policy_repo, audit_repo, report_repo)
    _services["certification"] = CertificationService(cert_repo, req_repo)
    _services["validation"] = ProductionValidationService(val_repo)
    _services["health"] = HealthDashboardService(health_repo)
    _services["knowledge"] = KnowledgeService(
        adr_repo, knowledge_repo, standard_repo, mig_hist_repo, rel_hist_repo
    )
    _services["feature_flag"] = FeatureFlagService()
    return _services


# ======================================================================
# Health
# ======================================================================


@router.get("/health")
async def production_health() -> dict:
    """Return basic production module health status."""
    return {
        "status": "healthy",
        "module": "production",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ======================================================================
# Releases
# ======================================================================


@router.post("/releases", status_code=201)
async def create_release(body: CreateReleaseRequest) -> dict:
    svc = _get_services()["release"]
    release = await svc.create_release(
        version=body.version,
        name=body.name,
        release_notes=body.release_notes,
        features=body.features,
        bug_fixes=body.bug_fixes,
        known_issues=body.known_issues,
        deprecations=body.deprecations,
        minimum_platform_version=body.minimum_platform_version,
    )
    return {"status": "success", "data": {
        "id": release.id, "version": release.version, "name": release.name,
        "status": release.status.value, "created_at": release.created_at.isoformat(),
    }}


@router.get("/releases")
async def list_releases(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict:
    svc = _get_services()["release"]
    result = await svc.list_releases(page=page, per_page=per_page)
    items = []
    for r in result["items"]:
        items.append({
            "id": r.id, "version": r.version, "name": r.name,
            "status": r.status.value,
            "created_at": r.created_at.isoformat(),
        })
    return {"status": "success", "items": items, "total": result["total"],
            "page": result["page"], "per_page": result["per_page"], "pages": result["pages"]}


@router.get("/releases/{release_id}")
async def get_release(release_id: str) -> dict:
    svc = _get_services()["release"]
    release = await svc.get_release(release_id)
    if release is None:
        raise HTTPException(status_code=404, detail="Release not found")
    return {"status": "success", "data": {
        "id": release.id, "version": release.version, "name": release.name,
        "status": release.status.value,
        "release_notes": release.release_notes,
        "features": release.features,
        "bug_fixes": release.bug_fixes,
        "known_issues": release.known_issues,
        "deprecations": release.deprecations,
        "minimum_platform_version": release.minimum_platform_version,
        "created_at": release.created_at.isoformat(),
    }}


@router.patch("/releases/{release_id}/status")
async def update_release_status(release_id: str, body: UpdateReleaseStatusRequest) -> dict:
    svc = _get_services()["release"]
    from ..domain.entities.release_center import ReleaseStatus
    try:
        new_status = ReleaseStatus(body.status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {body.status}")
    try:
        release = await svc.update_release_status(release_id, new_status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if release is None:
        raise HTTPException(status_code=404, detail="Release not found")
    return {"status": "success", "data": {
        "id": release.id, "version": release.version, "status": release.status.value,
    }}


@router.delete("/releases/{release_id}")
async def delete_release(release_id: str) -> dict:
    svc = _get_services()["release"]
    deleted = await svc.delete_release(release_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Release not found")
    return {"status": "success", "message": "Release deleted"}


@router.post("/releases/build-info", status_code=201)
async def create_build_info(body: CreateBuildInfoRequest) -> dict:
    svc = _get_services()["release"]
    bi = await svc.create_build_info(
        version=body.version,
        build_number=body.build_number,
        build_environment=body.build_environment,
        python_version=body.python_version,
        platform_name=body.platform,
    )
    return {"status": "success", "data": {
        "id": bi.id, "version": bi.version, "build_number": bi.build_number,
        "checksum": bi.checksum, "built_at": bi.built_at.isoformat(),
    }}


@router.post("/releases/packages", status_code=201)
async def create_package(body: CreatePackageRequest) -> dict:
    svc = _get_services()["release"]
    pkg = await svc.create_package(
        release_id=body.release_id,
        name=body.name,
        package_type=body.package_type,
        platform=body.platform,
        checksum=body.checksum,
        file_size=body.file_size,
    )
    return {"status": "success", "data": {
        "id": pkg.id, "release_id": pkg.release_id, "name": pkg.name,
        "package_type": pkg.package_type, "file_size": pkg.file_size,
    }}


@router.get("/releases/{release_id}/packages")
async def list_packages(release_id: str) -> dict:
    svc = _get_services()["release"]
    packages = await svc.get_packages_for_release(release_id)
    return {"status": "success", "items": [
        {"id": p.id, "name": p.name, "package_type": p.package_type,
         "platform": p.platform, "file_size": p.file_size}
        for p in packages
    ]}


# ======================================================================
# LTS Versions
# ======================================================================


@router.post("/lts", status_code=201)
async def create_lts_version(body: CreateLtsVersionRequest) -> dict:
    svc = _get_services()["lts"]
    lts = await svc.create_lts_version(
        version=body.version,
        release_date=body.release_date,
        end_of_support=body.end_of_support,
        compatible_versions=body.compatible_versions,
        migration_path=body.migration_path,
        notes=body.notes,
    )
    return {"status": "success", "data": {
        "id": lts.id, "version": lts.version, "status": lts.status,
        "release_date": lts.release_date, "end_of_support": lts.end_of_support,
    }}


@router.get("/lts")
async def list_lts_versions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict:
    svc = _get_services()["lts"]
    result = await svc.list_lts_versions(page=page, per_page=per_page)
    items = [{"id": l.id, "version": l.version, "status": l.status,
              "release_date": l.release_date, "end_of_support": l.end_of_support}
             for l in result["items"]]
    return {"status": "success", "items": items, "total": result["total"],
            "page": result["page"], "per_page": result["per_page"], "pages": result["pages"]}


@router.get("/lts/{lts_id}")
async def get_lts_version(lts_id: str) -> dict:
    svc = _get_services()["lts"]
    lts = await svc.get_lts_version(lts_id)
    if lts is None:
        raise HTTPException(status_code=404, detail="LTS version not found")
    return {"status": "success", "data": {
        "id": lts.id, "version": lts.version, "status": lts.status,
        "release_date": lts.release_date, "end_of_support": lts.end_of_support,
        "compatible_versions": lts.compatible_versions,
        "migration_path": lts.migration_path, "notes": lts.notes,
    }}


@router.patch("/lts/{lts_id}/status")
async def update_lts_status(lts_id: str, body: UpdateLtsStatusRequest) -> dict:
    svc = _get_services()["lts"]
    try:
        lts = await svc.update_lts_status(lts_id, body.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if lts is None:
        raise HTTPException(status_code=404, detail="LTS version not found")
    return {"status": "success", "data": {"id": lts.id, "version": lts.version, "status": lts.status}}


@router.post("/lts/migration-steps", status_code=201)
async def create_migration_step(body: CreateMigrationStepRequest) -> dict:
    svc = _get_services()["lts"]
    step = await svc.add_migration_step(
        from_version=body.from_version,
        to_version=body.to_version,
        step_number=body.step_number,
        description=body.description,
        requires_backup=body.requires_backup,
        estimated_minutes=body.estimated_minutes,
        rollback_available=body.rollback_available,
    )
    return {"status": "success", "data": {
        "id": step.id, "from_version": step.from_version, "to_version": step.to_version,
        "step_number": step.step_number, "description": step.description,
    }}


@router.get("/lts/migration-path/{from_version}/{to_version}")
async def get_migration_path(from_version: str, to_version: str) -> dict:
    svc = _get_services()["lts"]
    path = await svc.get_migration_path(from_version, to_version)
    return {"status": "success", "data": path}


@router.post("/lts/compatibility")
async def check_compatibility(body: CheckCompatibilityRequest) -> dict:
    svc = _get_services()["lts"]
    entry = await svc.update_compatibility(
        body.version_a, body.version_b, body.compatible, body.notes,
    )
    return {"status": "success", "data": {
        "id": entry.id, "version_a": entry.version_a, "version_b": entry.version_b,
        "compatible": entry.compatible, "notes": entry.notes,
    }}


@router.get("/lts/compatibility-matrix")
async def get_compatibility_matrix() -> dict:
    svc = _get_services()["lts"]
    matrix = await svc.get_compatibility_matrix()
    return {"status": "success", "items": [
        {"id": m.id, "version_a": m.version_a, "version_b": m.version_b,
         "compatible": m.compatible, "notes": m.notes}
        for m in matrix
    ]}


@router.post("/lts/deprecations", status_code=201)
async def create_deprecation(body: CreateDeprecationRequest) -> dict:
    svc = _get_services()["lts"]
    dep = await svc.add_deprecation(
        feature=body.feature,
        deprecated_in_version=body.deprecated_in_version,
        replacement=body.replacement,
        removal_version=body.removal_version,
        announced_at=body.announced_at,
    )
    return {"status": "success", "data": {
        "id": dep.id, "feature": dep.feature,
        "deprecated_in_version": dep.deprecated_in_version,
        "replacement": dep.replacement,
    }}


@router.get("/lts/deprecations")
async def list_deprecations() -> dict:
    svc = _get_services()["lts"]
    deps = await svc.list_deprecations()
    return {"status": "success", "items": [
        {"id": d.id, "feature": d.feature, "deprecated_in_version": d.deprecated_in_version,
         "replacement": d.replacement, "removal_version": d.removal_version}
        for d in deps
    ]}


@router.get("/lts/deprecations/{feature}")
async def get_deprecation(feature: str) -> dict:
    svc = _get_services()["lts"]
    dep = await svc.get_deprecation(feature)
    if dep is None:
        raise HTTPException(status_code=404, detail="Deprecation not found")
    return {"status": "success", "data": {
        "id": dep.id, "feature": dep.feature, "deprecated_in_version": dep.deprecated_in_version,
        "replacement": dep.replacement, "removal_version": dep.removal_version,
    }}


# ======================================================================
# Governance
# ======================================================================


@router.post("/governance/reviews", status_code=201)
async def create_governance_review(body: CreateGovernanceReviewRequest) -> dict:
    svc = _get_services()["governance"]
    from ..domain.entities.governance import GovernanceArea
    try:
        area = GovernanceArea(body.area)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid area: {body.area}")
    review = await svc.schedule_review(area=area, title=body.title,
                                       description=body.description, reviewer=body.reviewer)
    return {"status": "success", "data": {
        "id": review.id, "area": review.area.value, "title": review.title,
        "status": review.status, "reviewer": review.reviewer,
    }}


@router.get("/governance/reviews")
async def list_governance_reviews(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict:
    svc = _get_services()["governance"]
    result = await svc.list_reviews(page=page, per_page=per_page)
    items = [{"id": r.id, "area": r.area.value, "title": r.title,
              "status": r.status, "reviewer": r.reviewer}
             for r in result["items"]]
    return {"status": "success", "items": items, "total": result["total"],
            "page": result["page"], "per_page": result["per_page"], "pages": result["pages"]}


@router.get("/governance/reviews/{review_id}")
async def get_governance_review(review_id: str) -> dict:
    svc = _get_services()["governance"]
    review = await svc.get_review(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"status": "success", "data": {
        "id": review.id, "area": review.area.value, "title": review.title,
        "description": review.description, "status": review.status,
        "reviewer": review.reviewer, "recommendations": review.recommendations,
    }}


@router.patch("/governance/reviews/{review_id}/complete")
async def complete_governance_review(review_id: str, body: CompleteReviewRequest) -> dict:
    svc = _get_services()["governance"]
    try:
        review = await svc.complete_review(review_id, body.status, body.recommendations)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"status": "success", "data": {
        "id": review.id, "status": review.status,
        "completed_at": review.completed_at.isoformat() if review.completed_at else None,
        "recommendations": review.recommendations,
    }}


@router.post("/governance/policies", status_code=201)
async def create_governance_policy(body: CreateGovernancePolicyRequest) -> dict:
    svc = _get_services()["governance"]
    from ..domain.entities.governance import GovernanceArea
    try:
        area = GovernanceArea(body.area)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid area: {body.area}")
    policy = await svc.create_policy(area=area, name=body.name, description=body.description,
                                      requirements=body.requirements,
                                      review_frequency_days=body.review_frequency_days)
    return {"status": "success", "data": {
        "id": policy.id, "area": policy.area.value, "name": policy.name,
        "requirements": policy.requirements,
        "review_frequency_days": policy.review_frequency_days,
    }}


@router.get("/governance/policies")
async def list_governance_policies() -> dict:
    svc = _get_services()["governance"]
    policies = await svc.list_policies()
    return {"status": "success", "items": [
        {"id": p.id, "area": p.area.value, "name": p.name,
         "description": p.description, "requirements": p.requirements,
         "review_frequency_days": p.review_frequency_days}
        for p in policies
    ]}


@router.get("/governance/policies/overdue")
async def list_overdue_policies() -> dict:
    svc = _get_services()["governance"]
    policies = await svc.get_policies_needing_review()
    return {"status": "success", "items": [
        {"id": p.id, "area": p.area.value, "name": p.name,
         "last_reviewed_at": p.last_reviewed_at.isoformat() if p.last_reviewed_at else None,
         "review_frequency_days": p.review_frequency_days}
        for p in policies
    ]}


@router.post("/governance/audits", status_code=201)
async def run_architecture_audit(body: RunAuditRequest) -> dict:
    svc = _get_services()["governance"]
    audit = await svc.run_architecture_audit(name=body.name, checks=body.checks)
    return {"status": "success", "data": {
        "id": audit.id, "name": audit.name, "overall_status": audit.overall_status,
        "score": audit.score,
        "checks": [{"name": c.name, "category": c.category, "status": c.status, "details": c.details}
                    for c in audit.checks],
    }}


@router.get("/governance/audits")
async def list_architecture_audits(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict:
    svc = _get_services()["governance"]
    result = await svc.list_audits(page=page, per_page=per_page)
    items = [{"id": a.id, "name": a.name, "overall_status": a.overall_status,
              "score": a.score, "generated_at": a.generated_at.isoformat()}
             for a in result["items"]]
    return {"status": "success", "items": items, "total": result["total"],
            "page": result["page"], "per_page": result["per_page"], "pages": result["pages"]}


@router.get("/governance/audits/{audit_id}")
async def get_architecture_audit(audit_id: str) -> dict:
    svc = _get_services()["governance"]
    audit = await svc.get_audit(audit_id)
    if audit is None:
        raise HTTPException(status_code=404, detail="Audit not found")
    return {"status": "success", "data": {
        "id": audit.id, "name": audit.name, "overall_status": audit.overall_status,
        "score": audit.score, "generated_at": audit.generated_at.isoformat(),
        "checks": [{"name": c.name, "category": c.category, "status": c.status, "details": c.details}
                    for c in audit.checks],
    }}


@router.post("/governance/reports", status_code=201)
async def generate_governance_report(body: GenerateReportRequest) -> dict:
    svc = _get_services()["governance"]
    from ..domain.entities.governance import GovernanceArea
    try:
        area = GovernanceArea(body.area)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid area: {body.area}")
    report = await svc.generate_report(title=body.title, area=area,
                                       findings=body.findings, recommendations=body.recommendations)
    return {"status": "success", "data": {
        "id": report.id, "title": report.title, "area": report.area.value,
        "score": report.score, "findings": report.findings,
        "recommendations": report.recommendations,
        "generated_at": report.generated_at.isoformat(),
    }}


@router.get("/governance/reports")
async def list_governance_reports(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict:
    svc = _get_services()["governance"]
    result = await svc.list_reports(page=page, per_page=per_page)
    items = [{"id": rp.id, "title": rp.title, "area": rp.area.value,
              "score": rp.score, "generated_at": rp.generated_at.isoformat()}
             for rp in result["items"]]
    return {"status": "success", "items": items, "total": result["total"],
            "page": result["page"], "per_page": result["per_page"], "pages": result["pages"]}


# ======================================================================
# Certifications
# ======================================================================


@router.post("/certifications", status_code=201)
async def create_certification(body: CreateCertificationRequest) -> dict:
    svc = _get_services()["certification"]
    from ..domain.entities.certification import CertificationType
    try:
        cert_type = CertificationType(body.cert_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid cert_type: {body.cert_type}")
    cert = await svc.create_certification(name=body.name, cert_type=cert_type,
                                          approved_by=body.approved_by)
    return {"status": "success", "data": {
        "id": cert.id, "name": cert.name, "cert_type": cert.cert_type.value,
        "status": cert.status,
    }}


@router.get("/certifications")
async def list_certifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict:
    svc = _get_services()["certification"]
    result = await svc.list_certifications(page=page, per_page=per_page)
    items = [{"id": c.id, "name": c.name, "cert_type": c.cert_type.value,
              "status": c.status, "approved_by": c.approved_by}
             for c in result["items"]]
    return {"status": "success", "items": items, "total": result["total"],
            "page": result["page"], "per_page": result["per_page"], "pages": result["pages"]}


@router.get("/certifications/{cert_id}")
async def get_certification(cert_id: str) -> dict:
    svc = _get_services()["certification"]
    cert = await svc.get_certification(cert_id)
    if cert is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    return {"status": "success", "data": {
        "id": cert.id, "name": cert.name, "cert_type": cert.cert_type.value,
        "status": cert.status, "evidence": cert.evidence, "metrics": cert.metrics,
        "recommendations": cert.recommendations, "approved_by": cert.approved_by,
    }}


@router.post("/certifications/{cert_id}/requirements", status_code=201)
async def add_certification_requirement(cert_id: str, body: AddRequirementRequest) -> dict:
    svc = _get_services()["certification"]
    try:
        req = await svc.add_requirement(cert_id, body.requirement, body.description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"status": "success", "data": {
        "id": req.id, "certification_id": req.certification_id,
        "requirement": req.requirement, "description": req.description, "met": req.met,
    }}


@router.get("/certifications/{cert_id}/requirements")
async def list_certification_requirements(cert_id: str) -> dict:
    svc = _get_services()["certification"]
    reqs = await svc.get_requirements(cert_id)
    return {"status": "success", "items": [
        {"id": r.id, "requirement": r.requirement, "description": r.description,
         "met": r.met, "evidence": r.evidence}
        for r in reqs
    ]}


@router.patch("/certifications/requirements/{req_id}/fulfill")
async def fulfill_certification_requirement(req_id: str, body: FulfillRequirementRequest) -> dict:
    svc = _get_services()["certification"]
    req = await svc.fulfill_requirement(req_id, body.evidence)
    if req is None:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return {"status": "success", "data": {
        "id": req.id, "requirement": req.requirement, "met": req.met, "evidence": req.evidence,
    }}


@router.post("/certifications/{cert_id}/evaluate")
async def evaluate_certification(cert_id: str) -> dict:
    svc = _get_services()["certification"]
    cert = await svc.evaluate_certification(cert_id)
    if cert is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    return {"status": "success", "data": {
        "id": cert.id, "name": cert.name, "status": cert.status,
        "certified_at": cert.certified_at.isoformat() if cert.certified_at else None,
    }}


@router.post("/certifications/{cert_id}/revoke")
async def revoke_certification(cert_id: str) -> dict:
    svc = _get_services()["certification"]
    cert = await svc.revoke_certification(cert_id)
    if cert is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    return {"status": "success", "data": {"id": cert.id, "status": cert.status}}


# ======================================================================
# Production Validation
# ======================================================================


@router.post("/validation/subsystem/{subsystem}")
async def validate_subsystem(subsystem: str) -> dict:
    svc = _get_services()["validation"]
    try:
        result = await svc.validate_subsystem(subsystem)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"status": "success", "data": {
        "id": result.id, "name": result.name, "subsystem": result.subsystem,
        "status": result.status, "checks": result.checks,
        "details": result.details,
    }}


@router.post("/validation/all")
async def validate_all_subsystems() -> dict:
    svc = _get_services()["validation"]
    results = await svc.validate_all_subsystems()
    return {"status": "success", "items": [
        {"id": v.id, "name": v.name, "subsystem": v.subsystem, "status": v.status,
         "checks": v.checks}
        for v in results
    ]}


@router.get("/validation/summary")
async def get_validation_summary() -> dict:
    svc = _get_services()["validation"]
    summary = await svc.get_validation_summary()
    return {"status": "success", "data": summary}


# ======================================================================
# Health Dashboard
# ======================================================================


@router.post("/health/report")
async def generate_health_report(body: Optional[GenerateHealthReportRequest] = None) -> dict:
    svc = _get_services()["health"]
    indicators = None
    if body and body.indicators:
        indicators = [{"name": i.name, "value": i.value, "threshold": i.threshold}
                      for i in body.indicators]
    report = await svc.generate_health_report(custom_indicators=indicators)
    return {"status": "success", "data": {
        "id": report.id, "overall_score": report.overall_score, "grade": report.grade,
        "generated_at": report.generated_at.isoformat(),
        "indicators": [{"name": i.name, "value": i.value, "threshold": i.threshold,
                        "status": i.status}
                       for i in report.indicators],
    }}


@router.get("/health/latest")
async def get_latest_health() -> dict:
    svc = _get_services()["health"]
    report = await svc.get_latest_health()
    if report is None:
        raise HTTPException(status_code=404, detail="No health report found")
    return {"status": "success", "data": {
        "id": report.id, "overall_score": report.overall_score, "grade": report.grade,
        "generated_at": report.generated_at.isoformat(),
        "indicators": [{"name": i.name, "value": i.value, "threshold": i.threshold,
                        "status": i.status}
                       for i in report.indicators],
    }}


@router.get("/health/history")
async def get_health_history() -> dict:
    svc = _get_services()["health"]
    reports = await svc.get_health_history()
    return {"status": "success", "items": [
        {"id": h.id, "overall_score": h.overall_score, "grade": h.grade,
         "generated_at": h.generated_at.isoformat(),
         "indicator_count": len(h.indicators)}
        for h in reports
    ]}


@router.get("/health/trend/{indicator_name}")
async def get_indicator_trend(indicator_name: str) -> dict:
    svc = _get_services()["health"]
    trend = await svc.get_indicator_trend(indicator_name)
    return {"status": "success", "items": trend}


@router.get("/health/unhealthy")
async def get_unhealthy_indicators() -> dict:
    svc = _get_services()["health"]
    indicators = await svc.get_unhealthy_indicators()
    return {"status": "success", "items": indicators}


# ======================================================================
# Knowledge
# ======================================================================


@router.post("/knowledge/entries", status_code=201)
async def create_knowledge_entry(body: CreateKnowledgeEntryRequest) -> dict:
    svc = _get_services()["knowledge"]
    entry = await svc.create_knowledge_entry(
        title=body.title, category=body.category, content=body.content,
        tags=body.tags, version=body.version, author=body.author,
    )
    return {"status": "success", "data": {
        "id": entry.id, "title": entry.title, "category": entry.category,
        "created_at": entry.created_at.isoformat(),
    }}


@router.get("/knowledge/entries")
async def list_knowledge_entries(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict:
    svc = _get_services()["knowledge"]
    result = await svc.list_knowledge_entries(page=page, per_page=per_page)
    items = [{"id": e.id, "title": e.title, "category": e.category,
              "tags": e.tags, "version": e.version, "author": e.author}
             for e in result["items"]]
    return {"status": "success", "items": items, "total": result["total"],
            "page": result["page"], "per_page": result["per_page"], "pages": result["pages"]}


@router.get("/knowledge/entries/{entry_id}")
async def get_knowledge_entry(entry_id: str) -> dict:
    svc = _get_services()["knowledge"]
    entry = await svc.get_knowledge_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    return {"status": "success", "data": {
        "id": entry.id, "title": entry.title, "category": entry.category,
        "content": entry.content, "tags": entry.tags, "version": entry.version,
        "author": entry.author,
        "created_at": entry.created_at.isoformat(),
        "updated_at": entry.updated_at.isoformat(),
    }}


@router.get("/knowledge/search")
async def search_knowledge_entries(q: str = Query(..., min_length=1)) -> dict:
    svc = _get_services()["knowledge"]
    entries = await svc.search_knowledge_entries(q)
    return {"status": "success", "items": [
        {"id": e.id, "title": e.title, "category": e.category, "tags": e.tags}
        for e in entries
    ]}


@router.patch("/knowledge/entries/{entry_id}")
async def update_knowledge_entry(entry_id: str, body: UpdateKnowledgeEntryRequest) -> dict:
    svc = _get_services()["knowledge"]
    data: dict[str, Any] = {}
    if body.title is not None:
        data["title"] = body.title
    if body.category is not None:
        data["category"] = body.category
    if body.content is not None:
        data["content"] = body.content
    if body.tags is not None:
        data["tags"] = body.tags
    if body.version is not None:
        data["version"] = body.version
    entry = await svc.update_knowledge_entry(entry_id, data)
    if entry is None:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    return {"status": "success", "data": {
        "id": entry.id, "title": entry.title, "category": entry.category,
    }}


@router.delete("/knowledge/entries/{entry_id}")
async def delete_knowledge_entry(entry_id: str) -> dict:
    svc = _get_services()["knowledge"]
    deleted = await svc.delete_knowledge_entry(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    return {"status": "success", "message": "Knowledge entry deleted"}


@router.post("/knowledge/adr", status_code=201)
async def create_adr(body: CreateAdrRequest) -> dict:
    svc = _get_services()["knowledge"]
    adr = await svc.create_adr(
        title=body.title, context=body.context, decision=body.decision,
        consequences=body.consequences, alternatives=body.alternatives,
    )
    return {"status": "success", "data": {
        "id": adr.id, "title": adr.title, "status": adr.status,
        "created_at": adr.created_at.isoformat(),
    }}


@router.get("/knowledge/adr")
async def list_adrs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict:
    svc = _get_services()["knowledge"]
    result = await svc.list_adrs(page=page, per_page=per_page)
    items = [{"id": a.id, "title": a.title, "status": a.status,
              "created_at": a.created_at.isoformat()}
             for a in result["items"]]
    return {"status": "success", "items": items, "total": result["total"],
            "page": result["page"], "per_page": result["per_page"], "pages": result["pages"]}


@router.get("/knowledge/adr/{adr_id}")
async def get_adr(adr_id: str) -> dict:
    svc = _get_services()["knowledge"]
    adr = await svc.get_adr(adr_id)
    if adr is None:
        raise HTTPException(status_code=404, detail="ADR not found")
    return {"status": "success", "data": {
        "id": adr.id, "title": adr.title, "status": adr.status,
        "context": adr.context, "decision": adr.decision,
        "consequences": adr.consequences, "alternatives": adr.alternatives,
        "created_at": adr.created_at.isoformat(),
    }}


@router.patch("/knowledge/adr/{adr_id}/status")
async def update_adr_status(adr_id: str, body: UpdateAdrStatusRequest) -> dict:
    svc = _get_services()["knowledge"]
    try:
        adr = await svc.update_adr_status(adr_id, body.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if adr is None:
        raise HTTPException(status_code=404, detail="ADR not found")
    return {"status": "success", "data": {
        "id": adr.id, "title": adr.title, "status": adr.status,
    }}


@router.delete("/knowledge/adr/{adr_id}")
async def delete_adr(adr_id: str) -> dict:
    svc = _get_services()["knowledge"]
    deleted = await svc.delete_adr(adr_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="ADR not found")
    return {"status": "success", "message": "ADR deleted"}


@router.post("/knowledge/coding-standards", status_code=201)
async def create_coding_standard(body: CreateCodingStandardRequest) -> dict:
    svc = _get_services()["knowledge"]
    std = await svc.create_coding_standard(
        name=body.name, category=body.category, description=body.description,
        examples=body.examples, references=body.references,
    )
    return {"status": "success", "data": {
        "id": std.id, "name": std.name, "category": std.category,
        "description": std.description,
    }}


@router.get("/knowledge/coding-standards")
async def list_coding_standards() -> dict:
    svc = _get_services()["knowledge"]
    standards = await svc.list_coding_standards()
    return {"status": "success", "items": [
        {"id": s.id, "name": s.name, "category": s.category,
         "description": s.description}
        for s in standards
    ]}


@router.post("/knowledge/migration-history", status_code=201)
async def record_migration(body: RecordMigrationRequest) -> dict:
    svc = _get_services()["knowledge"]
    history = await svc.record_migration(
        from_version=body.from_version, to_version=body.to_version,
        status=body.status, steps_completed=body.steps_completed,
        total_steps=body.total_steps, notes=body.notes,
    )
    return {"status": "success", "data": {
        "id": history.id, "from_version": history.from_version,
        "to_version": history.to_version, "status": history.status,
    }}


@router.get("/knowledge/migration-history")
async def list_migration_history() -> dict:
    svc = _get_services()["knowledge"]
    history = await svc.get_migration_history()
    return {"status": "success", "items": [
        {"id": h.id, "from_version": h.from_version, "to_version": h.to_version,
         "status": h.status, "steps_completed": h.steps_completed,
         "total_steps": h.total_steps}
        for h in history
    ]}


@router.post("/knowledge/release-history", status_code=201)
async def record_release_history(body: RecordReleaseHistoryRequest) -> dict:
    svc = _get_services()["knowledge"]
    history = await svc.record_release_history(
        release_id=body.release_id, version=body.version, summary=body.summary,
    )
    return {"status": "success", "data": {
        "id": history.id, "version": history.version,
        "release_date": history.release_date, "summary": history.summary,
    }}


@router.get("/knowledge/release-history")
async def list_release_history() -> dict:
    svc = _get_services()["knowledge"]
    history = await svc.get_release_history()
    return {"status": "success", "items": [
        {"id": h.id, "release_id": h.release_id, "version": h.version,
         "release_date": h.release_date, "summary": h.summary}
        for h in history
    ]}


# ======================================================================
# Feature Flags
# ======================================================================


@router.post("/feature-flags", status_code=201)
async def create_feature_flag(body: CreateFeatureFlagRequest) -> dict:
    svc = _get_services()["feature_flag"]
    flag = await svc.create_flag(
        name=body.name, description=body.description, enabled=body.enabled,
        rollout_percentage=body.rollout_percentage,
        allowed_environments=body.allowed_environments,
        allowed_roles=body.allowed_roles,
    )
    return {"status": "success", "data": {
        "id": flag.id, "name": flag.name, "enabled": flag.enabled,
        "rollout_percentage": flag.rollout_percentage,
    }}


@router.get("/feature-flags")
async def list_feature_flags() -> dict:
    svc = _get_services()["feature_flag"]
    flags = await svc.list_flags()
    return {"status": "success", "items": [
        {"id": f.id, "name": f.name, "enabled": f.enabled,
         "description": f.description, "rollout_percentage": f.rollout_percentage}
        for f in flags
    ]}


@router.get("/feature-flags/{flag_id}")
async def get_feature_flag(flag_id: str) -> dict:
    svc = _get_services()["feature_flag"]
    flag = await svc.get_flag(flag_id)
    if flag is None:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    return {"status": "success", "data": {
        "id": flag.id, "name": flag.name, "description": flag.description,
        "enabled": flag.enabled, "rollout_percentage": flag.rollout_percentage,
        "allowed_environments": flag.allowed_environments,
        "allowed_roles": flag.allowed_roles,
    }}


@router.patch("/feature-flags/{flag_id}")
async def update_feature_flag(flag_id: str, body: UpdateFeatureFlagRequest) -> dict:
    svc = _get_services()["feature_flag"]
    data: dict[str, Any] = {}
    if body.description is not None:
        data["description"] = body.description
    if body.enabled is not None:
        data["enabled"] = body.enabled
    if body.rollout_percentage is not None:
        data["rollout_percentage"] = body.rollout_percentage
    if body.allowed_environments is not None:
        data["allowed_environments"] = body.allowed_environments
    if body.allowed_roles is not None:
        data["allowed_roles"] = body.allowed_roles
    flag = await svc.update_flag(flag_id, data)
    if flag is None:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    return {"status": "success", "data": {
        "id": flag.id, "name": flag.name, "enabled": flag.enabled,
    }}


@router.post("/feature-flags/{flag_id}/toggle")
async def toggle_feature_flag(flag_id: str) -> dict:
    svc = _get_services()["feature_flag"]
    flag = await svc.toggle_flag(flag_id)
    if flag is None:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    return {"status": "success", "data": {
        "id": flag.id, "name": flag.name, "enabled": flag.enabled,
    }}


@router.get("/feature-flags/check/{name}")
async def check_feature_flag(
    name: str,
    environment: str = Query(default="development"),
    role: str = Query(default=""),
) -> dict:
    svc = _get_services()["feature_flag"]
    enabled = await svc.is_enabled(name, environment=environment, role=role)
    return {"status": "success", "data": {"name": name, "enabled": enabled}}


@router.delete("/feature-flags/{flag_id}")
async def delete_feature_flag(flag_id: str) -> dict:
    svc = _get_services()["feature_flag"]
    deleted = await svc.delete_flag(flag_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    return {"status": "success", "message": "Feature flag deleted"}


# ======================================================================
# Configuration Profiles
# ======================================================================


@router.post("/config-profiles", status_code=201)
async def create_config_profile(body: CreateConfigProfileRequest) -> dict:
    svc = _get_services()["feature_flag"]
    profile = await svc.create_profile(
        name=body.name, environment=body.environment,
        values=body.values, is_active=body.is_active,
    )
    return {"status": "success", "data": {
        "id": profile.id, "name": profile.name, "environment": profile.environment,
        "is_active": profile.is_active, "values": profile.values,
    }}


@router.get("/config-profiles")
async def list_config_profiles(
    environment: Optional[str] = Query(default=None),
) -> dict:
    svc = _get_services()["feature_flag"]
    profiles = await svc.list_profiles(environment=environment)
    return {"status": "success", "items": [
        {"id": p.id, "name": p.name, "environment": p.environment,
         "is_active": p.is_active, "values": p.values}
        for p in profiles
    ]}


@router.get("/config-profiles/active")
async def get_active_profile(
    environment: str = Query(default="development"),
) -> dict:
    svc = _get_services()["feature_flag"]
    profile = await svc.get_active_profile(environment)
    if profile is None:
        raise HTTPException(status_code=404, detail="No active profile for environment")
    return {"status": "success", "data": {
        "id": profile.id, "name": profile.name, "environment": profile.environment,
        "is_active": profile.is_active, "values": profile.values,
    }}


@router.patch("/config-profiles/{profile_id}")
async def update_config_profile(profile_id: str, body: UpdateConfigProfileRequest) -> dict:
    svc = _get_services()["feature_flag"]
    data: dict[str, Any] = {}
    if body.values is not None:
        data["values"] = body.values
    if body.is_active is not None:
        data["is_active"] = body.is_active
    profile = await svc.update_profile(profile_id, data)
    if profile is None:
        raise HTTPException(status_code=404, detail="Config profile not found")
    return {"status": "success", "data": {
        "id": profile.id, "name": profile.name, "values": profile.values,
    }}


@router.post("/config-profiles/{profile_id}/activate")
async def activate_config_profile(profile_id: str) -> dict:
    svc = _get_services()["feature_flag"]
    profile = await svc.set_active_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Config profile not found")
    return {"status": "success", "data": {
        "id": profile.id, "name": profile.name, "environment": profile.environment,
        "is_active": profile.is_active,
    }}


@router.delete("/config-profiles/{profile_id}")
async def delete_config_profile(profile_id: str) -> dict:
    svc = _get_services()["feature_flag"]
    deleted = await svc.delete_profile(profile_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Config profile not found")
    return {"status": "success", "message": "Config profile deleted"}


# ======================================================================
# API Versioning
# ======================================================================


@router.post("/api-versions", status_code=201)
async def register_api_version(body: CreateApiVersionRequest) -> dict:
    svc = _get_services()["feature_flag"]
    ver = await svc.register_api_version(
        version=body.version, base_path=body.base_path, status=body.status,
    )
    return {"status": "success", "data": {
        "id": ver.id, "version": ver.version, "base_path": ver.base_path,
        "status": ver.status,
    }}


@router.get("/api-versions")
async def list_api_versions() -> dict:
    svc = _get_services()["feature_flag"]
    versions = await svc.list_api_versions()
    return {"status": "success", "items": [
        {"id": v.id, "version": v.version, "base_path": v.base_path, "status": v.status}
        for v in versions
    ]}


@router.post("/api-versions/{version_id}/deprecate")
async def deprecate_api_version(version_id: str) -> dict:
    svc = _get_services()["feature_flag"]
    ver = await svc.deprecate_api_version(version_id)
    if ver is None:
        raise HTTPException(status_code=404, detail="API version not found")
    return {"status": "success", "data": {
        "id": ver.id, "version": ver.version, "status": ver.status,
    }}


@router.post("/api-versions/{version_id}/sunset")
async def sunset_api_version(version_id: str) -> dict:
    svc = _get_services()["feature_flag"]
    ver = await svc.sunset_api_version(version_id)
    if ver is None:
        raise HTTPException(status_code=404, detail="API version not found")
    return {"status": "success", "data": {
        "id": ver.id, "version": ver.version, "status": ver.status,
    }}


@router.delete("/api-versions/{version_id}")
async def delete_api_version(version_id: str) -> dict:
    svc = _get_services()["feature_flag"]
    deleted = await svc.delete_api_version(version_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="API version not found")
    return {"status": "success", "message": "API version deleted"}


# ======================================================================
# Experimental Features
# ======================================================================


@router.post("/experimental-features", status_code=201)
async def create_experimental_feature(body: CreateExperimentalFeatureRequest) -> dict:
    svc = _get_services()["feature_flag"]
    feature = await svc.create_experimental_feature(
        name=body.name, description=body.description, flag_id=body.flag_id,
        min_version=body.min_version, required_roles=body.required_roles,
    )
    return {"status": "success", "data": {
        "id": feature.id, "name": feature.name, "description": feature.description,
        "status": feature.status,
    }}


@router.get("/experimental-features")
async def list_experimental_features() -> dict:
    svc = _get_services()["feature_flag"]
    features = await svc.list_experimental_features()
    return {"status": "success", "items": [
        {"id": f.id, "name": f.name, "description": f.description,
         "status": f.status, "flag_id": f.flag_id}
        for f in features
    ]}


@router.post("/experimental-features/{feature_id}/promote")
async def promote_experimental_feature(feature_id: str) -> dict:
    svc = _get_services()["feature_flag"]
    feature = await svc.promote_experimental_feature(feature_id)
    if feature is None:
        raise HTTPException(status_code=404, detail="Experimental feature not found")
    return {"status": "success", "data": {
        "id": feature.id, "name": feature.name, "status": feature.status,
    }}


@router.post("/experimental-features/{feature_id}/archive")
async def archive_experimental_feature(feature_id: str) -> dict:
    svc = _get_services()["feature_flag"]
    feature = await svc.archive_experimental_feature(feature_id)
    if feature is None:
        raise HTTPException(status_code=404, detail="Experimental feature not found")
    return {"status": "success", "data": {
        "id": feature.id, "name": feature.name, "status": feature.status,
    }}


@router.delete("/experimental-features/{feature_id}")
async def delete_experimental_feature(feature_id: str) -> dict:
    svc = _get_services()["feature_flag"]
    deleted = await svc.delete_experimental_feature(feature_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Experimental feature not found")
    return {"status": "success", "message": "Experimental feature deleted"}
