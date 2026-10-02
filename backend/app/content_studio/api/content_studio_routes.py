"""Content Production Studio API routes — FastAPI APIRouter."""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ...shared.responses import SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/content-studio", tags=["content-studio"])

# ---------------------------------------------------------------------------
# Lazy-loaded service singletons
# ---------------------------------------------------------------------------

_program_repo: Any = None
_course_repo: Any = None
_lab_repo: Any = None
_lab_template_repo: Any = None
_asset_repo: Any = None
_collection_repo: Any = None
_template_repo: Any = None
_publish_repo: Any = None
_history_repo: Any = None
_version_repo: Any = None
_review_repo: Any = None
_comment_repo: Any = None
_decision_repo: Any = None
_a11y_check_repo: Any = None
_a11y_report_repo: Any = None
_a11y_remediation_repo: Any = None


def _get_repos() -> dict[str, Any]:
    global _program_repo, _course_repo, _lab_repo, _lab_template_repo  # noqa: PLW0603
    global _asset_repo, _collection_repo, _template_repo  # noqa: PLW0603
    global _publish_repo, _history_repo, _version_repo  # noqa: PLW0603
    global _review_repo, _comment_repo, _decision_repo  # noqa: PLW0603
    global _a11y_check_repo, _a11y_report_repo, _a11y_remediation_repo  # noqa: PLW0603

    from ..repositories.content_studio_repository_impl import (
        InMemoryA11yCheckRepository,
        InMemoryA11yRemediationRepository,
        InMemoryA11yValidationReportRepository,
        InMemoryAssetCollectionRepository,
        InMemoryContentTemplateRepository,
        InMemoryContentVersionRepository,
        InMemoryCourseDesignRepository,
        InMemoryEditorialReviewRepository,
        InMemoryLabTemplateRepository,
        InMemoryMultimediaAssetRepository,
        InMemoryProgramRepository,
        InMemoryPublishHistoryRepository,
        InMemoryPublishRequestRepository,
        InMemoryReviewCommentRepository,
        InMemoryReviewDecisionRepository,
        InMemoryVirtualLabRepository,
    )

    if _program_repo is None:
        _program_repo = InMemoryProgramRepository()
    if _course_repo is None:
        _course_repo = InMemoryCourseDesignRepository()
    if _lab_repo is None:
        _lab_repo = InMemoryVirtualLabRepository()
    if _lab_template_repo is None:
        _lab_template_repo = InMemoryLabTemplateRepository()
    if _asset_repo is None:
        _asset_repo = InMemoryMultimediaAssetRepository()
    if _collection_repo is None:
        _collection_repo = InMemoryAssetCollectionRepository()
    if _template_repo is None:
        _template_repo = InMemoryContentTemplateRepository()
    if _publish_repo is None:
        _publish_repo = InMemoryPublishRequestRepository()
    if _history_repo is None:
        _history_repo = InMemoryPublishHistoryRepository()
    if _version_repo is None:
        _version_repo = InMemoryContentVersionRepository()
    if _review_repo is None:
        _review_repo = InMemoryEditorialReviewRepository()
    if _comment_repo is None:
        _comment_repo = InMemoryReviewCommentRepository()
    if _decision_repo is None:
        _decision_repo = InMemoryReviewDecisionRepository()
    if _a11y_check_repo is None:
        _a11y_check_repo = InMemoryA11yCheckRepository()
    if _a11y_report_repo is None:
        _a11y_report_repo = InMemoryA11yValidationReportRepository()
    if _a11y_remediation_repo is None:
        _a11y_remediation_repo = InMemoryA11yRemediationRepository()

    return {
        "program_repo": _program_repo,
        "course_repo": _course_repo,
        "lab_repo": _lab_repo,
        "lab_template_repo": _lab_template_repo,
        "asset_repo": _asset_repo,
        "collection_repo": _collection_repo,
        "template_repo": _template_repo,
        "publish_repo": _publish_repo,
        "history_repo": _history_repo,
        "version_repo": _version_repo,
        "review_repo": _review_repo,
        "comment_repo": _comment_repo,
        "decision_repo": _decision_repo,
        "a11y_check_repo": _a11y_check_repo,
        "a11y_report_repo": _a11y_report_repo,
        "a11y_remediation_repo": _a11y_remediation_repo,
    }


def _get_course_design_service() -> Any:
    from ..services.course_designer_service import CourseDesignerService
    repos = _get_repos()
    return CourseDesignerService(repos["program_repo"], repos["course_repo"])


def _get_lesson_builder_service() -> Any:
    from ..services.lesson_builder_service import LessonBuilderService
    repos = _get_repos()
    return LessonBuilderService(repos["course_repo"])


def _get_virtual_lab_service() -> Any:
    from ..services.virtual_lab_service import VirtualLabService
    repos = _get_repos()
    return VirtualLabService(repos["lab_repo"], repos["lab_template_repo"])


def _get_multimedia_service() -> Any:
    from ..services.multimedia_service import MultimediaService
    repos = _get_repos()
    return MultimediaService(repos["asset_repo"], repos["collection_repo"])


def _get_template_studio_service() -> Any:
    from ..services.template_studio_service import TemplateStudioService
    repos = _get_repos()
    return TemplateStudioService(repos["template_repo"])


def _get_publishing_service() -> Any:
    from ..services.publishing_center_service import PublishingCenterService
    repos = _get_repos()
    return PublishingCenterService(repos["publish_repo"], repos["history_repo"], repos["version_repo"])


def _get_review_service() -> Any:
    from ..services.review_center_service import ReviewCenterService
    repos = _get_repos()
    return ReviewCenterService(repos["review_repo"], repos["comment_repo"], repos["decision_repo"])


def _get_a11y_service() -> Any:
    from ..services.a11y_validator_service import A11yValidatorService
    repos = _get_repos()
    return A11yValidatorService(repos["a11y_check_repo"], repos["a11y_report_repo"], repos["a11y_remediation_repo"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class ProgramRequest(BaseModel):
    name: str
    description: str = ""
    department: str = ""
    status: str = "draft"


class CourseRequest(BaseModel):
    name: str
    description: str = ""
    program_id: str = ""
    created_by: str = ""
    status: str = "draft"
    learning_objectives: list[str] = Field(default_factory=list)
    competencies: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    a11y_notes: str = ""
    estimated_hours: float = 0.0


class UnitRequest(BaseModel):
    name: str


class ModuleRequest(BaseModel):
    name: str


class LessonRequest(BaseModel):
    name: str
    estimated_minutes: int = 30
    learning_objectives: list[str] = Field(default_factory=list)


class ContentBlockRequest(BaseModel):
    block_type: str = "text"
    content: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    accessible: bool = True
    localized: bool = False


class ActivityRequest(BaseModel):
    activity_type: str = "mcq"
    title: str = ""
    description: str = ""
    content: dict[str, Any] = Field(default_factory=dict)
    scoring: dict[str, Any] = Field(default_factory=dict)


class VirtualLabRequest(BaseModel):
    name: str
    description: str = ""
    lab_type: str = "hands_on"
    learning_objectives: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    expected_outcomes: list[str] = Field(default_factory=list)
    reflection_questions: list[str] = Field(default_factory=list)
    assessment_criteria: dict[str, Any] = Field(default_factory=dict)
    a11y_instructions: str = ""
    estimated_minutes: int = 60
    status: str = "draft"


class LabStepRequest(BaseModel):
    title: str
    instructions: str = ""
    hints: list[str] = Field(default_factory=list)
    expected_result: str = ""
    validation_rules: dict[str, Any] = Field(default_factory=dict)


class LabTemplateRequest(BaseModel):
    name: str
    template_type: str = ""
    description: str = ""
    steps_template: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultimediaAssetRequest(BaseModel):
    name: str
    asset_type: str = "image"
    description: str = ""
    file_path: str = ""
    alt_text: str = ""
    caption: str = ""
    transcript: str = ""
    accessible: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class AssetCollectionRequest(BaseModel):
    name: str
    description: str = ""
    asset_ids: list[str] = Field(default_factory=list)


class TemplateRequest(BaseModel):
    name: str
    template_type: str = "lesson"
    description: str = ""
    structure: dict[str, Any] = Field(default_factory=dict)
    author: str = ""
    inherit_from: Optional[str] = None


class TemplateInstanceRequest(BaseModel):
    customizations: dict[str, Any] = Field(default_factory=dict)
    created_by: str = ""


class PublishRequestModel(BaseModel):
    content_id: str
    content_type: str
    requested_by: str
    release_notes: str = ""
    version: int = 1


class ValidationResultsRequest(BaseModel):
    total: int = 0
    passed: int = 0
    failed: int = 0


class ReviewRequest(BaseModel):
    content_id: str
    content_type: str
    submitter: str


class ReviewCommentRequest(BaseModel):
    author: str
    comment: str = ""
    severity: Optional[str] = None


class ReviewDecisionRequest(BaseModel):
    reviewer: str
    decision: str = "approved"
    comments: str = ""


# ===================================================================
# Program endpoints
# ===================================================================

@router.post("/programs", status_code=201)
async def create_program(request: ProgramRequest) -> dict[str, Any]:
    service = _get_course_design_service()
    try:
        return service.create_program(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/programs")
async def list_programs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_course_design_service()
    return service.list_programs(page=page, per_page=per_page, status=status)


@router.get("/programs/{program_id}")
async def get_program(program_id: str) -> dict[str, Any]:
    service = _get_course_design_service()
    program = service.get_program(program_id)
    if not program:
        raise HTTPException(status_code=404, detail=f"Program '{program_id}' not found")
    return program


@router.put("/programs/{program_id}")
async def update_program(program_id: str, request: ProgramRequest) -> dict[str, Any]:
    service = _get_course_design_service()
    try:
        result = service.update_program(program_id, request.model_dump(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail=f"Program '{program_id}' not found")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/programs/{program_id}")
async def delete_program(program_id: str) -> SuccessResponse:
    service = _get_course_design_service()
    try:
        service.delete_program(program_id)
        return SuccessResponse(message=f"Program '{program_id}' deleted")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.put("/programs/{program_id}/status")
async def update_program_status(program_id: str, status: str = Query(...)) -> dict[str, Any]:
    service = _get_course_design_service()
    try:
        result = service.update_program_status(program_id, status)
        if not result:
            raise HTTPException(status_code=404, detail=f"Program '{program_id}' not found")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


# ===================================================================
# Course Design endpoints
# ===================================================================

@router.post("/courses", status_code=201)
async def create_course(request: CourseRequest) -> dict[str, Any]:
    service = _get_course_design_service()
    try:
        return service.create_course(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/courses")
async def list_courses(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_course_design_service()
    return service.list_courses(page=page, per_page=per_page, status=status)


@router.get("/courses/{course_id}")
async def get_course(course_id: str) -> dict[str, Any]:
    service = _get_course_design_service()
    course = service.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course '{course_id}' not found")
    return course


@router.put("/courses/{course_id}")
async def update_course(course_id: str, request: CourseRequest) -> dict[str, Any]:
    service = _get_course_design_service()
    try:
        result = service.update_course(course_id, request.model_dump(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail=f"Course '{course_id}' not found")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/courses/{course_id}")
async def delete_course(course_id: str) -> SuccessResponse:
    service = _get_course_design_service()
    try:
        service.delete_course(course_id)
        return SuccessResponse(message=f"Course '{course_id}' deleted")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.put("/courses/{course_id}/status")
async def update_course_status(course_id: str, status: str = Query(...)) -> dict[str, Any]:
    service = _get_course_design_service()
    try:
        result = service.update_course_status(course_id, status)
        if not result:
            raise HTTPException(status_code=404, detail=f"Course '{course_id}' not found")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/courses/{course_id}/hierarchy")
async def get_course_hierarchy(course_id: str) -> dict[str, Any]:
    service = _get_course_design_service()
    try:
        return service.get_course_hierarchy(course_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/courses/search/{query}")
async def search_courses(
    query: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    service = _get_course_design_service()
    return service.search_courses(query, page=page, per_page=per_page)


@router.get("/programs/{program_id}/courses")
async def get_courses_by_program(program_id: str) -> dict[str, Any]:
    service = _get_course_design_service()
    courses = service.get_courses_by_program(program_id)
    return {"program_id": program_id, "courses": courses}


# ===================================================================
# Unit / Module / Lesson endpoints
# ===================================================================

@router.post("/courses/{course_id}/units", status_code=201)
async def add_unit(course_id: str, request: UnitRequest) -> dict[str, Any]:
    service = _get_course_design_service()
    try:
        return service.add_unit_to_course(course_id, request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/courses/{course_id}/units/{unit_id}/modules", status_code=201)
async def add_module(course_id: str, unit_id: str, request: ModuleRequest) -> dict[str, Any]:
    service = _get_course_design_service()
    try:
        return service.add_module_to_unit(course_id, unit_id, request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/courses/{course_id}/units/{unit_id}/modules/{module_id}/lessons", status_code=201)
async def add_lesson(
    course_id: str, unit_id: str, module_id: str, request: LessonRequest
) -> dict[str, Any]:
    service = _get_lesson_builder_service()
    try:
        return service.add_lesson_to_module(course_id, unit_id, module_id, request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/courses/{course_id}/lessons/{lesson_id}")
async def get_lesson(course_id: str, lesson_id: str) -> dict[str, Any]:
    service = _get_lesson_builder_service()
    try:
        return service.get_lesson(course_id, lesson_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/courses/{course_id}/lessons/{lesson_id}")
async def delete_lesson(course_id: str, lesson_id: str) -> SuccessResponse:
    service = _get_lesson_builder_service()
    try:
        service.delete_lesson(course_id, lesson_id)
        return SuccessResponse(message=f"Lesson '{lesson_id}' deleted")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/courses/{course_id}/lessons/{lesson_id}/blocks", status_code=201)
async def add_content_block(
    course_id: str, lesson_id: str, request: ContentBlockRequest
) -> dict[str, Any]:
    service = _get_lesson_builder_service()
    try:
        return service.add_content_block(course_id, lesson_id, request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.put("/courses/{course_id}/lessons/{lesson_id}/blocks/{block_id}")
async def update_content_block(
    course_id: str, lesson_id: str, block_id: str, request: ContentBlockRequest
) -> dict[str, Any]:
    service = _get_lesson_builder_service()
    try:
        return service.update_content_block(course_id, lesson_id, block_id, request.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/courses/{course_id}/lessons/{lesson_id}/blocks/{block_id}")
async def remove_content_block(course_id: str, lesson_id: str, block_id: str) -> SuccessResponse:
    service = _get_lesson_builder_service()
    try:
        result = service.remove_content_block(course_id, lesson_id, block_id)
        if not result:
            raise HTTPException(status_code=404, detail="Block not found")
        return SuccessResponse(message="Content block removed")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/courses/{course_id}/lessons/{lesson_id}/activities", status_code=201)
async def add_activity(
    course_id: str, lesson_id: str, request: ActivityRequest
) -> dict[str, Any]:
    service = _get_lesson_builder_service()
    try:
        return service.add_activity(course_id, lesson_id, request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.put("/courses/{course_id}/lessons/{lesson_id}/activities/{activity_id}")
async def update_activity(
    course_id: str, lesson_id: str, activity_id: str, request: ActivityRequest
) -> dict[str, Any]:
    service = _get_lesson_builder_service()
    try:
        return service.update_activity(course_id, lesson_id, activity_id, request.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/courses/{course_id}/lessons/{lesson_id}/activities/{activity_id}")
async def remove_activity(course_id: str, lesson_id: str, activity_id: str) -> SuccessResponse:
    service = _get_lesson_builder_service()
    try:
        result = service.remove_activity(course_id, lesson_id, activity_id)
        if not result:
            raise HTTPException(status_code=404, detail="Activity not found")
        return SuccessResponse(message="Activity removed")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/courses/{course_id}/lessons/{lesson_id}/duplicate")
async def duplicate_lesson(
    course_id: str, lesson_id: str, new_name: str = Query("")
) -> dict[str, Any]:
    service = _get_lesson_builder_service()
    try:
        return service.duplicate_lesson(course_id, lesson_id, new_name=new_name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


# ===================================================================
# Virtual Lab endpoints
# ===================================================================

@router.post("/labs", status_code=201)
async def create_lab(request: VirtualLabRequest) -> dict[str, Any]:
    service = _get_virtual_lab_service()
    try:
        return service.create_lab(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/labs")
async def list_labs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_virtual_lab_service()
    return service.list_labs(page=page, per_page=per_page, status=status)


@router.get("/labs/{lab_id}")
async def get_lab(lab_id: str) -> dict[str, Any]:
    service = _get_virtual_lab_service()
    lab = service.get_lab(lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail=f"Lab '{lab_id}' not found")
    return lab


@router.put("/labs/{lab_id}")
async def update_lab(lab_id: str, request: VirtualLabRequest) -> dict[str, Any]:
    service = _get_virtual_lab_service()
    try:
        result = service.update_lab(lab_id, request.model_dump(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail=f"Lab '{lab_id}' not found")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/labs/{lab_id}")
async def delete_lab(lab_id: str) -> SuccessResponse:
    service = _get_virtual_lab_service()
    try:
        service.delete_lab(lab_id)
        return SuccessResponse(message=f"Lab '{lab_id}' deleted")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/labs/{lab_id}/steps", status_code=201)
async def add_lab_step(lab_id: str, request: LabStepRequest) -> dict[str, Any]:
    service = _get_virtual_lab_service()
    try:
        return service.add_step(lab_id, request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.put("/labs/{lab_id}/steps/{step_id}")
async def update_lab_step(
    lab_id: str, step_id: str, request: LabStepRequest
) -> dict[str, Any]:
    service = _get_virtual_lab_service()
    try:
        return service.update_step(lab_id, step_id, request.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/labs/{lab_id}/steps/{step_id}")
async def remove_lab_step(lab_id: str, step_id: str) -> SuccessResponse:
    service = _get_virtual_lab_service()
    try:
        result = service.remove_step(lab_id, step_id)
        if not result:
            raise HTTPException(status_code=404, detail="Step not found")
        return SuccessResponse(message="Step removed")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/labs/search/{query}")
async def search_labs(
    query: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    service = _get_virtual_lab_service()
    return service.search_labs(query, page=page, per_page=per_page)


# ===================================================================
# Lab Template endpoints
# ===================================================================

@router.post("/lab-templates", status_code=201)
async def create_lab_template(request: LabTemplateRequest) -> dict[str, Any]:
    service = _get_virtual_lab_service()
    try:
        return service.create_template(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/lab-templates")
async def list_lab_templates() -> list[dict[str, Any]]:
    service = _get_virtual_lab_service()
    return service.list_templates()


@router.get("/lab-templates/{template_id}")
async def get_lab_template(template_id: str) -> dict[str, Any]:
    service = _get_virtual_lab_service()
    template = service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    return template


@router.delete("/lab-templates/{template_id}")
async def delete_lab_template(template_id: str) -> SuccessResponse:
    service = _get_virtual_lab_service()
    try:
        service.delete_template(template_id)
        return SuccessResponse(message=f"Template '{template_id}' deleted")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/lab-templates/{template_id}/create-lab", status_code=201)
async def create_lab_from_template(
    template_id: str, lab_name: str = Query(...)
) -> dict[str, Any]:
    service = _get_virtual_lab_service()
    try:
        return service.create_lab_from_template(template_id, lab_name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


# ===================================================================
# Multimedia Asset endpoints
# ===================================================================

@router.post("/assets", status_code=201)
async def create_asset(request: MultimediaAssetRequest) -> dict[str, Any]:
    service = _get_multimedia_service()
    try:
        return service.create_asset(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/assets")
async def list_assets(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    asset_type: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_multimedia_service()
    return service.list_assets(page=page, per_page=per_page, asset_type=asset_type)


@router.get("/assets/{asset_id}")
async def get_asset(asset_id: str) -> dict[str, Any]:
    service = _get_multimedia_service()
    asset = service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found")
    return asset


@router.put("/assets/{asset_id}")
async def update_asset(asset_id: str, request: MultimediaAssetRequest) -> dict[str, Any]:
    service = _get_multimedia_service()
    try:
        result = service.update_asset(asset_id, request.model_dump(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/assets/{asset_id}")
async def delete_asset(asset_id: str) -> SuccessResponse:
    service = _get_multimedia_service()
    try:
        service.delete_asset(asset_id)
        return SuccessResponse(message=f"Asset '{asset_id}' deleted")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/assets/{asset_id}/validate")
async def validate_asset(asset_id: str) -> dict[str, Any]:
    service = _get_multimedia_service()
    try:
        return service.validate_asset(asset_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/assets/search/{query}")
async def search_assets(
    query: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    service = _get_multimedia_service()
    return service.search_assets(query, page=page, per_page=per_page)


# ===================================================================
# Asset Collection endpoints
# ===================================================================

@router.post("/asset-collections", status_code=201)
async def create_asset_collection(request: AssetCollectionRequest) -> dict[str, Any]:
    service = _get_multimedia_service()
    try:
        return service.create_collection(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/asset-collections")
async def list_asset_collections() -> list[dict[str, Any]]:
    service = _get_multimedia_service()
    return service.list_collections()


@router.get("/asset-collections/{collection_id}")
async def get_asset_collection(collection_id: str) -> dict[str, Any]:
    service = _get_multimedia_service()
    collection = service.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection '{collection_id}' not found")
    return collection


@router.delete("/asset-collections/{collection_id}")
async def delete_asset_collection(collection_id: str) -> SuccessResponse:
    service = _get_multimedia_service()
    try:
        service.delete_collection(collection_id)
        return SuccessResponse(message=f"Collection '{collection_id}' deleted")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/asset-collections/{collection_id}/assets/{asset_id}")
async def add_asset_to_collection(collection_id: str, asset_id: str) -> dict[str, Any]:
    service = _get_multimedia_service()
    try:
        return service.add_asset_to_collection(collection_id, asset_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/asset-collections/{collection_id}/assets/{asset_id}")
async def remove_asset_from_collection(collection_id: str, asset_id: str) -> SuccessResponse:
    service = _get_multimedia_service()
    try:
        result = service.remove_asset_from_collection(collection_id, asset_id)
        if not result:
            raise HTTPException(status_code=404, detail="Asset not in collection")
        return SuccessResponse(message="Asset removed from collection")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/asset-collections/{collection_id}/validate")
async def validate_collection_assets(collection_id: str) -> dict[str, Any]:
    service = _get_multimedia_service()
    try:
        return service.validate_collection_assets(collection_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ===================================================================
# Content Template endpoints
# ===================================================================

@router.post("/templates", status_code=201)
async def create_template(request: TemplateRequest) -> dict[str, Any]:
    service = _get_template_studio_service()
    try:
        return service.create_template(request.model_dump(), author=request.author)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/templates")
async def list_templates(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    template_type: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_template_studio_service()
    return service.list_templates(page=page, per_page=per_page, template_type=template_type)


@router.get("/templates/{template_id}")
async def get_template(template_id: str) -> dict[str, Any]:
    service = _get_template_studio_service()
    template = service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    return template


@router.put("/templates/{template_id}")
async def update_template(
    template_id: str,
    request: TemplateRequest,
    changes: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_template_studio_service()
    try:
        change_list = [changes] if changes else None
        result = service.update_template(template_id, request.model_dump(exclude_unset=True), changes=change_list)
        if not result:
            raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/templates/{template_id}")
async def delete_template(template_id: str) -> SuccessResponse:
    service = _get_template_studio_service()
    try:
        service.delete_template(template_id)
        return SuccessResponse(message=f"Template '{template_id}' deleted")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/templates/{template_id}/versions")
async def get_template_versions(template_id: str) -> dict[str, Any]:
    service = _get_template_studio_service()
    try:
        history = service.get_version_history(template_id)
        return {"template_id": template_id, "versions": history}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/templates/{template_id}/with-inheritance")
async def get_template_with_inheritance(template_id: str) -> dict[str, Any]:
    service = _get_template_studio_service()
    try:
        return service.get_template_with_inheritance(template_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/templates/{template_id}/instances", status_code=201)
async def create_template_instance(
    template_id: str, request: TemplateInstanceRequest
) -> dict[str, Any]:
    service = _get_template_studio_service()
    try:
        return service.create_instance(template_id, request.customizations, created_by=request.created_by)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/templates/{template_id}/instances")
async def get_template_instances(template_id: str) -> dict[str, Any]:
    service = _get_template_studio_service()
    try:
        instances = service.get_instances(template_id)
        return {"template_id": template_id, "instances": instances}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ===================================================================
# Publishing endpoints
# ===================================================================

@router.post("/publish/requests", status_code=201)
async def request_publish(request: PublishRequestModel) -> dict[str, Any]:
    service = _get_publishing_service()
    try:
        return service.request_publish(
            content_id=request.content_id,
            content_type=request.content_type,
            requested_by=request.requested_by,
            release_notes=request.release_notes,
            version=request.version,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/publish/requests")
async def list_publish_requests(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_publishing_service()
    return service.list_publish_requests(page=page, per_page=per_page, status=status)


@router.get("/publish/requests/{request_id}")
async def get_publish_request(request_id: str) -> dict[str, Any]:
    service = _get_publishing_service()
    req = service.get_publish_request(request_id)
    if not req:
        raise HTTPException(status_code=404, detail=f"Request '{request_id}' not found")
    return req


@router.put("/publish/requests/{request_id}/validate")
async def start_validation(request_id: str) -> dict[str, Any]:
    service = _get_publishing_service()
    try:
        return service.start_validation(request_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.put("/publish/requests/{request_id}/validation-results")
async def set_validation_results(
    request_id: str, results: ValidationResultsRequest
) -> dict[str, Any]:
    service = _get_publishing_service()
    try:
        return service.set_validation_results(request_id, results.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.put("/publish/requests/{request_id}/a11y-results")
async def set_a11y_results(
    request_id: str, results: ValidationResultsRequest
) -> dict[str, Any]:
    service = _get_publishing_service()
    try:
        return service.set_a11y_results(request_id, results.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.put("/publish/requests/{request_id}/sign-and-publish")
async def sign_and_publish(request_id: str, digital_signature: str = Query(...)) -> dict[str, Any]:
    service = _get_publishing_service()
    try:
        return service.sign_and_publish(request_id, digital_signature)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.put("/publish/requests/{request_id}/reject")
async def reject_publish(request_id: str, reason: str = Query("")) -> dict[str, Any]:
    service = _get_publishing_service()
    try:
        return service.reject_publish(request_id, reason)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.put("/publish/requests/{request_id}/rollback")
async def rollback_publish(request_id: str, reason: str = Query("")) -> dict[str, Any]:
    service = _get_publishing_service()
    try:
        return service.rollback_publish(request_id, reason)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/publish/content/{content_id}/history")
async def get_publish_history(content_id: str) -> dict[str, Any]:
    service = _get_publishing_service()
    history = service.get_publish_history(content_id)
    return {"content_id": content_id, "history": history}


@router.get("/publish/content/{content_id}/versions")
async def get_content_versions(content_id: str) -> dict[str, Any]:
    service = _get_publishing_service()
    versions = service.get_content_versions(content_id)
    return {"content_id": content_id, "versions": versions}


@router.get("/publish/content/{content_id}/latest-version")
async def get_latest_version(content_id: str) -> dict[str, Any]:
    service = _get_publishing_service()
    version = service.get_latest_version(content_id)
    if not version:
        raise HTTPException(status_code=404, detail=f"No versions found for content '{content_id}'")
    return version


# ===================================================================
# Review endpoints
# ===================================================================

@router.post("/reviews", status_code=201)
async def create_review(request: ReviewRequest) -> dict[str, Any]:
    service = _get_review_service()
    try:
        return service.create_review(request.content_id, request.content_type, request.submitter)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/reviews")
async def list_reviews(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    stage: Optional[str] = Query(None),
) -> dict[str, Any]:
    service = _get_review_service()
    return service.list_reviews(page=page, per_page=per_page, stage=stage)


@router.get("/reviews/{review_id}")
async def get_review(review_id: str) -> dict[str, Any]:
    service = _get_review_service()
    review = service.get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail=f"Review '{review_id}' not found")
    return review


@router.get("/reviews/content/{content_id}")
async def get_review_by_content(content_id: str) -> dict[str, Any]:
    service = _get_review_service()
    review = service.get_review_by_content(content_id)
    if not review:
        raise HTTPException(status_code=404, detail=f"No review found for content '{content_id}'")
    return review


@router.put("/reviews/{review_id}/advance")
async def advance_review(review_id: str) -> dict[str, Any]:
    service = _get_review_service()
    try:
        return service.advance_review(review_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.put("/reviews/{review_id}/stage")
async def set_review_stage(review_id: str, stage: str = Query(...)) -> dict[str, Any]:
    service = _get_review_service()
    try:
        return service.set_stage(review_id, stage)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/reviews/{review_id}/comments", status_code=201)
async def add_review_comment(
    review_id: str, request: ReviewCommentRequest
) -> dict[str, Any]:
    service = _get_review_service()
    try:
        return service.add_comment(review_id, request.author, request.comment, severity=request.severity)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/reviews/{review_id}/comments")
async def get_review_comments(review_id: str) -> dict[str, Any]:
    service = _get_review_service()
    comments = service.get_comments(review_id)
    return {"review_id": review_id, "comments": comments}


@router.post("/reviews/{review_id}/decisions", status_code=201)
async def add_review_decision(
    review_id: str, request: ReviewDecisionRequest
) -> dict[str, Any]:
    service = _get_review_service()
    try:
        return service.add_decision(review_id, request.reviewer, request.decision, comments=request.comments)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/reviews/{review_id}/decisions")
async def get_review_decisions(review_id: str) -> dict[str, Any]:
    service = _get_review_service()
    decisions = service.get_decisions(review_id)
    return {"review_id": review_id, "decisions": decisions}


@router.get("/reviews/{review_id}/progress")
async def get_review_progress(review_id: str) -> dict[str, Any]:
    service = _get_review_service()
    try:
        return service.get_review_progress(review_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ===================================================================
# A11y Validation endpoints
# ===================================================================

@router.post("/a11y/validate/{content_id}", status_code=201)
async def run_a11y_validation(content_id: str) -> dict[str, Any]:
    service = _get_a11y_service()
    try:
        return service.run_checks(content_id, {"content_id": content_id})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/a11y/reports/{report_id}")
async def get_a11y_report(report_id: str) -> dict[str, Any]:
    service = _get_a11y_service()
    report = service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found")
    return report


@router.get("/a11y/content/{content_id}/report")
async def get_a11y_report_by_content(content_id: str) -> dict[str, Any]:
    service = _get_a11y_service()
    report = service.get_report_by_content(content_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"No report found for content '{content_id}'")
    return report


@router.get("/a11y/reports")
async def list_a11y_reports(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    service = _get_a11y_service()
    return service.list_reports(page=page, per_page=per_page)


@router.get("/a11y/reports/{report_id}/checks")
async def get_a11y_checks(report_id: str) -> dict[str, Any]:
    service = _get_a11y_service()
    checks = service.get_checks_for_report(report_id)
    return {"report_id": report_id, "checks": checks}


@router.get("/a11y/remediations/open")
async def get_open_remediations() -> dict[str, Any]:
    service = _get_a11y_service()
    remediations = service.get_open_remediations()
    return {"remediations": remediations, "total": len(remediations)}


@router.get("/a11y/reports/{report_id}/remediations")
async def get_remediations_for_report(report_id: str) -> dict[str, Any]:
    service = _get_a11y_service()
    remediations = service.get_remediations_for_report(report_id)
    return {"report_id": report_id, "remediations": remediations}


@router.put("/a11y/remediations/{remediation_id}")
async def update_remediation(
    remediation_id: str, data: dict[str, Any]
) -> dict[str, Any]:
    service = _get_a11y_service()
    try:
        result = service.update_remediation(remediation_id, data)
        if not result:
            raise HTTPException(status_code=404, detail=f"Remediation '{remediation_id}' not found")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.put("/a11y/remediations/{remediation_id}/assign")
async def assign_remediation(
    remediation_id: str, assignee: str = Query(...)
) -> dict[str, Any]:
    service = _get_a11y_service()
    try:
        result = service.assign_remediation(remediation_id, assignee)
        if not result:
            raise HTTPException(status_code=404, detail=f"Remediation '{remediation_id}' not found")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.put("/a11y/remediations/{remediation_id}/complete")
async def complete_remediation(remediation_id: str) -> dict[str, Any]:
    service = _get_a11y_service()
    try:
        result = service.complete_remediation(remediation_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Remediation '{remediation_id}' not found")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/a11y/content/{content_id}/compliance-summary")
async def get_compliance_summary(content_id: str) -> dict[str, Any]:
    service = _get_a11y_service()
    return service.get_compliance_summary(content_id)
