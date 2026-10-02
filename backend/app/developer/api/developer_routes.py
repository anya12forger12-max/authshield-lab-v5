"""FastAPI routes for the Developer Platform module."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/developer", tags=["developer"])


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class SdKCreateRequest(BaseModel):
    """Request body for creating an SDK."""

    name: str = ""
    version: str = "1.0"
    description: str = ""
    author: str = ""
    compatibility_version: str = "1.0"
    modules: list[str] = Field(default_factory=list)
    min_platform_version: str = "1.0"


class SdKResponse(BaseModel):
    """Standard SDK response envelope."""

    id: str
    name: str
    version: str
    description: str
    author: str
    compatibility_version: str
    modules: list[str]
    deprecated: bool
    min_platform_version: str
    created_at: str


class ExtensionCreateRequest(BaseModel):
    """Request body for creating an extension."""

    name: str = ""
    version: str = "1.0.0"
    author: str = ""
    description: str = ""
    extension_type: str = "plugin"
    permissions: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    compatibility: str = ">=1.0"


class ExtensionResponse(BaseModel):
    """Standard extension response envelope."""

    id: str
    name: str
    version: str
    author: str
    description: str
    extension_type: str
    status: str
    permissions: list[str]
    dependencies: list[str]
    compatibility: str


class WorkflowCreateRequest(BaseModel):
    """Request body for creating a workflow."""

    name: str = ""
    description: str = ""
    workflow_type: str = "custom"
    schedule: str = ""
    enabled: bool = True


class WorkflowResponse(BaseModel):
    """Standard workflow response envelope."""

    id: str
    name: str
    description: str
    workflow_type: str
    status: str
    enabled: bool
    schedule: str
    created_at: str


class StepCreateRequest(BaseModel):
    """Request body for adding a step to a workflow."""

    step_type: str = "action"
    action: str = ""
    params: dict = Field(default_factory=dict)
    order: int = 0
    on_failure: str = "stop"


class EndpointRegisterRequest(BaseModel):
    """Request body for registering an API endpoint."""

    path: str = ""
    method: str = "GET"
    description: str = ""
    category: str = "general"
    version: str = "1.0"
    deprecated: bool = False
    auth_required: bool = True


class EndpointResponse(BaseModel):
    """Standard endpoint response envelope."""

    id: str
    path: str
    method: str
    description: str
    category: str
    version: str
    deprecated: bool
    auth_required: bool


class ValidationReportResponse(BaseModel):
    """Standard validation report response."""

    id: str
    name: str
    target_type: str
    overall_status: str
    score: float
    generated_at: str


class ManifestCreateRequest(BaseModel):
    """Request body for creating a package manifest."""

    name: str = ""
    version: str = "1.0.0"
    author: str = ""
    description: str = ""
    package_type: str = "extension"
    dependencies: list[str] = Field(default_factory=list)
    license: str = "MIT"
    compatibility: str = ">=1.0"


class BuildConfigRequest(BaseModel):
    """Request body for creating a build configuration."""

    manifest_id: str = ""
    sources: list[str] = Field(default_factory=list)
    include_docs: bool = True
    include_tests: bool = False
    output_format: str = "zip"


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    success: bool = True


# ---------------------------------------------------------------------------
# Lazy-initialized service singletons
# ---------------------------------------------------------------------------

_sdk_service = None
_extension_service = None
_automation_service = None
_api_explorer_service = None
_validation_service = None
_package_service = None
_developer_tools_service = None


def _get_sdk_service():  # type: ignore[no-untyped-def]
    global _sdk_service
    if _sdk_service is None:
        from app.developer.services.sdk_service import SdKService
        _sdk_service = SdKService()
    return _sdk_service


def _get_extension_service():  # type: ignore[no-untyped-def]
    global _extension_service
    if _extension_service is None:
        from app.developer.services.extension_service import ExtensionService
        _extension_service = ExtensionService()
    return _extension_service


def _get_automation_service():  # type: ignore[no-untyped-def]
    global _automation_service
    if _automation_service is None:
        from app.developer.services.automation_service import AutomationService
        _automation_service = AutomationService()
    return _automation_service


def _get_api_explorer_service():  # type: ignore[no-untyped-def]
    global _api_explorer_service
    if _api_explorer_service is None:
        from app.developer.services.api_explorer_service import ApiExplorerService
        _api_explorer_service = ApiExplorerService()
    return _api_explorer_service


def _get_validation_service():  # type: ignore[no-untyped-def]
    global _validation_service
    if _validation_service is None:
        from app.developer.services.validation_service import ValidationService
        _validation_service = ValidationService()
    return _validation_service


def _get_package_service():  # type: ignore[no-untyped-def]
    global _package_service
    if _package_service is None:
        from app.developer.services.package_service import PackageService
        _package_service = PackageService()
    return _package_service


def _get_developer_tools_service():  # type: ignore[no-untyped-def]
    global _developer_tools_service
    if _developer_tools_service is None:
        from app.developer.services.developer_tools_service import DeveloperToolsService
        _developer_tools_service = DeveloperToolsService()
    return _developer_tools_service


# ---------------------------------------------------------------------------
# SDK Routes
# ---------------------------------------------------------------------------


@router.post("/sdks", response_model=SdKResponse, status_code=201)
async def create_sdk(body: SdKCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Create a new SDK."""
    from app.developer.domain.entities.sdk import SdKVersion

    version_enum = SdKVersion(body.version) if body.version in [v.value for v in SdKVersion] else SdKVersion.V1
    sdk = _get_sdk_service().create_sdk(
        name=body.name,
        version=version_enum,
        description=body.description,
        author=body.author,
        compatibility_version=body.compatibility_version,
        modules=body.modules,
        min_platform_version=body.min_platform_version,
    )
    return sdk.to_dict()


@router.get("/sdks", response_model=list[SdKResponse])
async def list_sdks() -> list[dict]:  # type: ignore[no-untyped-def]
    """List all SDKs."""
    return [sdk.to_dict() for sdk in _get_sdk_service().list_sdks()]


@router.get("/sdks/{sdk_id}", response_model=SdKResponse)
async def get_sdk(sdk_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Get an SDK by ID."""
    sdk = _get_sdk_service().get_sdk(sdk_id)
    if sdk is None:
        raise HTTPException(status_code=404, detail="SDK not found")
    return sdk.to_dict()


@router.delete("/sdks/{sdk_id}", response_model=MessageResponse)
async def delete_sdk(sdk_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Delete an SDK."""
    success = _get_sdk_service().delete_sdk(sdk_id)
    if not success:
        raise HTTPException(status_code=404, detail="SDK not found")
    return {"message": "SDK deleted", "success": True}


@router.post("/sdks/{sdk_id}/deprecate", response_model=SdKResponse)
async def deprecate_sdk(sdk_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Deprecate an SDK."""
    sdk = _get_sdk_service().deprecate_sdk(sdk_id)
    if sdk is None:
        raise HTTPException(status_code=404, detail="SDK not found")
    return sdk.to_dict()


@router.get("/sdks/{sdk_id}/compatibility")
async def check_sdk_compatibility(sdk_id: str, platform_version: str = "1.0") -> dict:  # type: ignore[no-untyped-def]
    """Check SDK compatibility with a platform version."""
    compatible = _get_sdk_service().check_compatibility(sdk_id, platform_version)
    return {"sdk_id": sdk_id, "platform_version": platform_version, "compatible": compatible}


# ---------------------------------------------------------------------------
# Extension Routes
# ---------------------------------------------------------------------------


@router.post("/extensions", response_model=ExtensionResponse, status_code=201)
async def create_extension(body: ExtensionCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Create a new extension."""
    from app.developer.domain.entities.extension import ExtensionType

    ext_type = ExtensionType(body.extension_type) if body.extension_type in [e.value for e in ExtensionType] else ExtensionType.PLUGIN
    ext = _get_extension_service().register_extension(
        name=body.name,
        version=body.version,
        author=body.author,
        description=body.description,
        extension_type=ext_type,
        permissions=body.permissions,
        dependencies=body.dependencies,
        compatibility=body.compatibility,
    )
    return ext.to_dict()


@router.get("/extensions", response_model=list[ExtensionResponse])
async def list_extensions() -> list[dict]:  # type: ignore[no-untyped-def]
    """List all extensions."""
    return [e.to_dict() for e in _get_extension_service().list_extensions()]


@router.get("/extensions/{extension_id}", response_model=ExtensionResponse)
async def get_extension(extension_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Get an extension by ID."""
    ext = _get_extension_service().get_extension(extension_id)
    if ext is None:
        raise HTTPException(status_code=404, detail="Extension not found")
    return ext.to_dict()


@router.get("/extensions/search/{query}")
async def search_extensions(query: str) -> list[dict]:  # type: ignore[no-untyped-def]
    """Search extensions by name or description."""
    return [e.to_dict() for e in _get_extension_service().search_extensions(query)]


@router.post("/extensions/{extension_id}/install")
async def install_extension(extension_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Install an extension."""
    record = _get_extension_service().install_extension(extension_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Extension not found or already installed")
    return record.to_dict()


@router.post("/extensions/{extension_id}/uninstall", response_model=MessageResponse)
async def uninstall_extension(extension_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Uninstall an extension."""
    success = _get_extension_service().uninstall_extension(extension_id)
    if not success:
        raise HTTPException(status_code=404, detail="Extension not found")
    return {"message": "Extension uninstalled", "success": True}


@router.post("/extensions/{extension_id}/enable", response_model=MessageResponse)
async def enable_extension(extension_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Enable a disabled extension."""
    success = _get_extension_service().enable_extension(extension_id)
    if not success:
        raise HTTPException(status_code=404, detail="Extension not found")
    return {"message": "Extension enabled", "success": True}


@router.post("/extensions/{extension_id}/disable", response_model=MessageResponse)
async def disable_extension(extension_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Disable an extension."""
    success = _get_extension_service().disable_extension(extension_id)
    if not success:
        raise HTTPException(status_code=404, detail="Extension not found")
    return {"message": "Extension disabled", "success": True}


@router.get("/extensions/{extension_id}/validate")
async def validate_extension(extension_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Validate an extension."""
    return _get_extension_service().validate_extension(extension_id)


@router.delete("/extensions/{extension_id}", response_model=MessageResponse)
async def delete_extension(extension_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Delete an extension."""
    success = _get_extension_service().delete_extension(extension_id)
    if not success:
        raise HTTPException(status_code=404, detail="Extension not found")
    return {"message": "Extension deleted", "success": True}


# ---------------------------------------------------------------------------
# Automation Workflow Routes
# ---------------------------------------------------------------------------


@router.post("/workflows", response_model=WorkflowResponse, status_code=201)
async def create_workflow(body: WorkflowCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Create a new automation workflow."""
    wf = _get_automation_service().create_workflow(
        name=body.name,
        description=body.description,
        workflow_type=body.workflow_type,
        schedule=body.schedule,
        enabled=body.enabled,
    )
    return wf.to_dict()


@router.get("/workflows", response_model=list[WorkflowResponse])
async def list_workflows() -> list[dict]:  # type: ignore[no-untyped-def]
    """List all workflows."""
    return [w.to_dict() for w in _get_automation_service().list_workflows()]


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Get a workflow by ID."""
    wf = _get_automation_service().get_workflow(workflow_id)
    if wf is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf.to_dict()


@router.post("/workflows/{workflow_id}/steps", status_code=201)
async def add_workflow_step(workflow_id: str, body: StepCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Add a step to a workflow."""
    step = _get_automation_service().add_step(
        workflow_id=workflow_id,
        step_type=body.step_type,
        action=body.action,
        params=body.params,
        order=body.order,
        on_failure=body.on_failure,
    )
    if step is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return step.to_dict()


@router.post("/workflows/{workflow_id}/run")
async def run_workflow(workflow_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Execute a workflow."""
    run = _get_automation_service().run_workflow(workflow_id)
    if run is None:
        raise HTTPException(status_code=400, detail="Workflow not found or already running")
    return run.to_dict()


@router.post("/workflows/{workflow_id}/cancel", response_model=MessageResponse)
async def cancel_workflow(workflow_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Cancel a running workflow."""
    success = _get_automation_service().cancel_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot cancel workflow")
    return {"message": "Workflow cancelled", "success": True}


@router.get("/workflows/{workflow_id}/stats")
async def get_workflow_stats(workflow_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Get execution statistics for a workflow."""
    return _get_automation_service().get_workflow_stats(workflow_id)


@router.delete("/workflows/{workflow_id}", response_model=MessageResponse)
async def delete_workflow(workflow_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Delete a workflow."""
    success = _get_automation_service().delete_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"message": "Workflow deleted", "success": True}


# ---------------------------------------------------------------------------
# API Explorer Routes
# ---------------------------------------------------------------------------


@router.post("/api-explorer/endpoints", status_code=201)
async def register_endpoint(body: EndpointRegisterRequest) -> dict:  # type: ignore[no-untyped-def]
    """Register a new API endpoint."""
    ep = _get_api_explorer_service().register_endpoint(
        path=body.path,
        method=body.method,
        description=body.description,
        category=body.category,
        version=body.version,
        deprecated=body.deprecated,
        auth_required=body.auth_required,
    )
    return ep.to_dict()


@router.get("/api-explorer/endpoints", response_model=list[EndpointResponse])
async def list_endpoints() -> list[dict]:  # type: ignore[no-untyped-def]
    """List all registered API endpoints."""
    return [ep.to_dict() for ep in _get_api_explorer_service().list_endpoints()]


@router.get("/api-explorer/endpoints/search/{query}")
async def search_endpoints(query: str) -> list[dict]:  # type: ignore[no-untyped-def]
    """Search API endpoints."""
    return [ep.to_dict() for ep in _get_api_explorer_service().search_endpoints(query)]


@router.get("/api-explorer/endpoints/{endpoint_id}")
async def get_endpoint(endpoint_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Get an API endpoint by ID."""
    ep = _get_api_explorer_service().get_endpoint(endpoint_id)
    if ep is None:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return ep.to_dict()


@router.get("/api-explorer/summary")
async def get_api_summary() -> dict:  # type: ignore[no-untyped-def]
    """Get a summary of all registered API endpoints."""
    return _get_api_explorer_service().get_api_summary()


@router.get("/api-explorer/schemas")
async def list_schemas() -> list[dict]:  # type: ignore[no-untyped-def]
    """List all API schemas."""
    return [s.to_dict() for s in _get_api_explorer_service().list_schemas()]


# ---------------------------------------------------------------------------
# Validation Routes
# ---------------------------------------------------------------------------


@router.post("/validation/validate-extension")
async def validate_extension(body: dict) -> dict:  # type: ignore[no-untyped-def]
    """Validate extension data."""
    report = _get_validation_service().validate_extension(body)
    return report.to_dict()


@router.post("/validation/validate-template")
async def validate_template(body: dict) -> dict:  # type: ignore[no-untyped-def]
    """Validate template data."""
    report = _get_validation_service().validate_template(body)
    return report.to_dict()


@router.post("/validation/validate-package")
async def validate_package(body: dict) -> dict:  # type: ignore[no-untyped-def]
    """Validate package data."""
    report = _get_validation_service().validate_package(body)
    return report.to_dict()


@router.post("/validation/compatibility")
async def validate_compatibility(
    source_version: str = "1.0.0",
    target_version: str = "2.0.0",
) -> dict:  # type: ignore[no-untyped-def]
    """Validate version compatibility."""
    report = _get_validation_service().validate_compatibility(source_version, target_version)
    return report.to_dict()


@router.get("/validation/reports", response_model=list[ValidationReportResponse])
async def list_validation_reports() -> list[dict]:  # type: ignore[no-untyped-def]
    """List all validation reports."""
    return [r.to_dict() for r in _get_validation_service().list_reports()]


@router.get("/validation/reports/{report_id}")
async def get_validation_report(report_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Get a validation report by ID."""
    report = _get_validation_service().get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.to_dict()


# ---------------------------------------------------------------------------
# Package Builder Routes
# ---------------------------------------------------------------------------


@router.post("/packages/manifests", status_code=201)
async def create_manifest(body: ManifestCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Create a package manifest."""
    manifest = _get_package_service().create_manifest(
        name=body.name,
        version=body.version,
        author=body.author,
        description=body.description,
        package_type=body.package_type,
        dependencies=body.dependencies,
        license=body.license,
        compatibility=body.compatibility,
    )
    return manifest.to_dict()


@router.get("/packages/manifests")
async def list_manifests() -> list[dict]:  # type: ignore[no-untyped-def]
    """List all package manifests."""
    return [m.to_dict() for m in _get_package_service().list_manifests()]


@router.get("/packages/manifests/{manifest_id}")
async def get_manifest(manifest_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Get a package manifest by ID."""
    manifest = _get_package_service().get_manifest(manifest_id)
    if manifest is None:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return manifest.to_dict()


@router.post("/packages/build")
async def build_package(body: BuildConfigRequest) -> dict:  # type: ignore[no-untyped-def]
    """Create a build config and build a package."""
    config = _get_package_service().create_build_config(
        manifest_id=body.manifest_id,
        sources=body.sources,
        include_docs=body.include_docs,
        include_tests=body.include_tests,
        output_format=body.output_format,
    )
    if config is None:
        raise HTTPException(status_code=404, detail="Manifest not found")
    result = _get_package_service().build_package(config.id)
    if result is None:
        raise HTTPException(status_code=500, detail="Build failed")
    return result.to_dict()


@router.get("/packages/build-results")
async def list_build_results() -> list[dict]:  # type: ignore[no-untyped-def]
    """List all build results."""
    return [r.to_dict() for r in _get_package_service().list_build_results()]


@router.post("/packages/manifests/{manifest_id}/install")
async def install_package(manifest_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Install a package from its manifest."""
    result = _get_package_service().install_package(manifest_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Install failed"))
    return result


@router.post("/packages/manifests/{manifest_id}/rollback")
async def rollback_package(manifest_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Roll back the last installation of a package."""
    result = _get_package_service().rollback_package(manifest_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Rollback failed"))
    return result


@router.get("/packages/manifests/{manifest_id}/validate")
async def validate_manifest(manifest_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Validate a package manifest."""
    return _get_package_service().validate_manifest(manifest_id)


# ---------------------------------------------------------------------------
# Developer Tools Routes
# ---------------------------------------------------------------------------


@router.get("/tools/api-stats")
async def get_api_stats() -> dict:  # type: ignore[no-untyped-def]
    """Get API browser statistics."""
    return _get_developer_tools_service().get_api_stats()


@router.get("/tools/schemas")
async def list_tool_schemas() -> list[dict]:  # type: ignore[no-untyped-def]
    """List schemas from the schema explorer."""
    return _get_developer_tools_service().list_schemas()


@router.get("/tools/config")
async def get_all_config() -> dict:  # type: ignore[no-untyped-def]
    """Get all configuration values."""
    return _get_developer_tools_service().list_config()


@router.get("/tools/logs")
async def get_logs(
    level: str | None = None,
    source: str | None = None,
    limit: int = 100,
) -> list[dict]:  # type: ignore[no-untyped-def]
    """Retrieve log entries."""
    return _get_developer_tools_service().get_logs(level=level, source=source, limit=limit)


@router.get("/tools/logs/stats")
async def get_log_stats() -> dict:  # type: ignore[no-untyped-def]
    """Get log statistics."""
    return _get_developer_tools_service().get_log_stats()


@router.get("/tools/dashboard")
async def get_dashboard() -> dict:  # type: ignore[no-untyped-def]
    """Get the developer tools dashboard."""
    return _get_developer_tools_service().get_dashboard()


@router.get("/tools/metrics")
async def get_metrics(name: str | None = None, limit: int = 100) -> list[dict]:  # type: ignore[no-untyped-def]
    """Get performance metrics."""
    return _get_developer_tools_service().get_metrics(name=name, limit=limit)


@router.get("/tools/metrics/summary/{metric_name}")
async def get_metric_summary(metric_name: str) -> dict:  # type: ignore[no-untyped-def]
    """Get summary statistics for a metric."""
    return _get_developer_tools_service().get_metric_summary(metric_name)
