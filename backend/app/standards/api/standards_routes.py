"""FastAPI routes for the Standards module."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/standards", tags=["standards"])


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class FrameworkCreateRequest(BaseModel):
    """Request body for creating a framework."""

    name: str = ""
    version: str = "1.0"
    description: str = ""
    status: str = "active"


class FrameworkUpdateRequest(BaseModel):
    """Request body for updating a framework."""

    name: str | None = None
    description: str | None = None
    status: str | None = None


class CompetencyCreateRequest(BaseModel):
    """Request body for adding a competency."""

    name: str = ""
    description: str = ""
    domain_id: str = ""
    level: str = ""
    skills: list[str] = Field(default_factory=list)


class DomainCreateRequest(BaseModel):
    """Request body for adding a domain."""

    name: str = ""
    description: str = ""


class CategoryCreateRequest(BaseModel):
    """Request body for adding a category."""

    name: str = ""
    description: str = ""


class LearningObjectiveCreateRequest(BaseModel):
    """Request body for adding a learning objective."""

    competency_id: str = ""
    description: str = ""
    level: str = ""


class SkillCreateRequest(BaseModel):
    """Request body for adding a skill."""

    name: str = ""
    description: str = ""
    parent_id: str | None = None
    aliases: list[str] = Field(default_factory=list)
    category: str = ""


class KnowledgeAreaCreateRequest(BaseModel):
    """Request body for adding a knowledge area."""

    name: str = ""
    description: str = ""


class ReferenceCreateRequest(BaseModel):
    """Request body for adding a reference."""

    title: str = ""
    url: str = ""
    reference_type: str = ""


class MappingCreateRequest(BaseModel):
    """Request body for creating a mapping."""

    source_id: str = ""
    source_type: str = ""
    target_id: str = ""
    target_type: str = ""
    coverage_level: str = "partial"
    confidence: float = 0.0
    instructor_notes: str = ""


class MappingUpdateRequest(BaseModel):
    """Request body for updating a mapping."""

    coverage_level: str | None = None
    confidence: float | None = None
    instructor_notes: str | None = None
    review_status: str | None = None


class BulkMappingRequest(BaseModel):
    """Request body for bulk mapping."""

    source_ids: list[str] = Field(default_factory=list)
    target_ids: list[str] = Field(default_factory=list)
    source_type: str = ""
    target_type: str = ""


class TaxonomyCreateRequest(BaseModel):
    """Request body for creating a taxonomy."""

    name: str = ""
    description: str = ""
    version: str = "1.0"


class TaxonomySkillCreateRequest(BaseModel):
    """Request body for adding a skill to a taxonomy."""

    name: str = ""
    description: str = ""
    category: str = ""
    parent_id: str | None = None
    aliases: list[str] = Field(default_factory=list)
    level: str = ""


class RelationshipCreateRequest(BaseModel):
    """Request body for adding a skill relationship."""

    source_skill_id: str = ""
    target_skill_id: str = ""
    relationship_type: str = ""
    weight: float = 1.0


class EvidenceCollectionCreateRequest(BaseModel):
    """Request body for creating an evidence collection."""

    name: str = ""
    framework_id: str = ""


class EvidenceItemCreateRequest(BaseModel):
    """Request body for adding an evidence item."""

    evidence_type: str = "assessment_result"
    description: str = ""
    source_id: str = ""
    source_type: str = ""


class ReviewCreateRequest(BaseModel):
    """Request body for creating a readiness review."""

    name: str = ""
    framework_id: str = ""
    created_by: str = ""


class ReviewAdvanceRequest(BaseModel):
    """Request body for advancing a readiness review."""

    actor: str = ""
    comments: str = ""


class DashboardGenerateRequest(BaseModel):
    """Request body for generating a quality dashboard."""

    curriculum_balance: float = 0.0
    competency_distribution: dict[str, float] = Field(default_factory=dict)
    skills_progression: dict[str, float] = Field(default_factory=dict)
    assessment_distribution: dict[str, float] = Field(default_factory=dict)
    a11y_health: float = 0.0
    doc_quality: float = 0.0
    localization_readiness: float = 0.0
    content_freshness: float = 0.0
    review_completion: float = 0.0


class ComparisonRequest(BaseModel):
    """Request body for comparing frameworks."""

    framework_a_id: str = ""
    framework_b_id: str = ""


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    success: bool = True


# ---------------------------------------------------------------------------
# Lazy-initialized service singletons
# ---------------------------------------------------------------------------

_framework_service = None
_mapping_service = None
_taxonomy_service = None
_evidence_service = None
_quality_service = None
_comparison_service = None


def _get_framework_service():  # type: ignore[no-untyped-def]
    global _framework_service
    if _framework_service is None:
        from app.standards.services.framework_service import FrameworkService
        _framework_service = FrameworkService()
    return _framework_service


def _get_mapping_service():  # type: ignore[no-untyped-def]
    global _mapping_service
    if _mapping_service is None:
        from app.standards.services.mapping_service import MappingService
        _mapping_service = MappingService()
    return _mapping_service


def _get_taxonomy_service():  # type: ignore[no-untyped-def]
    global _taxonomy_service
    if _taxonomy_service is None:
        from app.standards.services.skills_taxonomy_service import SkillsTaxonomyService
        _taxonomy_service = SkillsTaxonomyService()
    return _taxonomy_service


def _get_evidence_service():  # type: ignore[no-untyped-def]
    global _evidence_service
    if _evidence_service is None:
        from app.standards.services.evidence_service import EvidenceService
        _evidence_service = EvidenceService()
    return _evidence_service


def _get_quality_service():  # type: ignore[no-untyped-def]
    global _quality_service
    if _quality_service is None:
        from app.standards.services.quality_service import QualityService
        _quality_service = QualityService()
    return _quality_service


def _get_comparison_service():  # type: ignore[no-untyped-def]
    global _comparison_service
    if _comparison_service is None:
        from app.standards.services.comparison_service import ComparisonService
        _comparison_service = ComparisonService()
    return _comparison_service


# ---------------------------------------------------------------------------
# Framework Routes
# ---------------------------------------------------------------------------


@router.post("/frameworks", status_code=201)
async def create_framework(body: FrameworkCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Create a new competency framework."""
    fw = _get_framework_service().create_framework(
        name=body.name,
        version=body.version,
        description=body.description,
        status=body.status,
    )
    return fw.to_dict()


@router.get("/frameworks")
async def list_frameworks() -> list[dict]:  # type: ignore[no-untyped-def]
    """List all frameworks."""
    return [f.to_dict() for f in _get_framework_service().list_frameworks()]


@router.get("/frameworks/{framework_id}")
async def get_framework(framework_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Get a framework by ID."""
    fw = _get_framework_service().get_framework(framework_id)
    if fw is None:
        raise HTTPException(status_code=404, detail="Framework not found")
    return fw.to_dict()


@router.put("/frameworks/{framework_id}")
async def update_framework(framework_id: str, body: FrameworkUpdateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Update a framework."""
    fw = _get_framework_service().update_framework(
        framework_id=framework_id,
        name=body.name,
        description=body.description,
        status=body.status,
    )
    if fw is None:
        raise HTTPException(status_code=404, detail="Framework not found")
    return fw.to_dict()


@router.delete("/frameworks/{framework_id}", response_model=MessageResponse)
async def delete_framework(framework_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Delete a framework."""
    deleted = _get_framework_service().delete_framework(framework_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Framework not found")
    return {"message": "Framework deleted", "success": True}


@router.post("/frameworks/{framework_id}/competencies", status_code=201)
async def add_competency(framework_id: str, body: CompetencyCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Add a competency to a framework."""
    comp = _get_framework_service().add_competency(
        framework_id=framework_id,
        name=body.name,
        description=body.description,
        domain_id=body.domain_id,
        level=body.level,
        skills=body.skills,
    )
    if comp is None:
        raise HTTPException(status_code=404, detail="Framework not found")
    return comp.to_dict()


@router.get("/frameworks/{framework_id}/competencies")
async def list_competencies(framework_id: str) -> list[dict]:  # type: ignore[no-untyped-def]
    """List competencies for a framework."""
    return [c.to_dict() for c in _get_framework_service().list_competencies(framework_id)]


@router.delete("/frameworks/{framework_id}/competencies/{competency_id}", response_model=MessageResponse)
async def remove_competency(framework_id: str, competency_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Remove a competency from a framework."""
    removed = _get_framework_service().remove_competency(framework_id, competency_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Competency not found")
    return {"message": "Competency removed", "success": True}


@router.post("/frameworks/{framework_id}/domains", status_code=201)
async def add_domain(framework_id: str, body: DomainCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Add a domain to a framework."""
    dom = _get_framework_service().add_domain(
        framework_id=framework_id,
        name=body.name,
        description=body.description,
    )
    if dom is None:
        raise HTTPException(status_code=404, detail="Framework not found")
    return dom.to_dict()


@router.get("/frameworks/{framework_id}/domains")
async def list_domains(framework_id: str) -> list[dict]:  # type: ignore[no-untyped-def]
    """List domains for a framework."""
    return [d.to_dict() for d in _get_framework_service().list_domains(framework_id)]


@router.post("/frameworks/{framework_id}/categories", status_code=201)
async def add_category(framework_id: str, body: CategoryCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Add a category to a framework."""
    cat = _get_framework_service().add_category(
        framework_id=framework_id,
        name=body.name,
        description=body.description,
    )
    if cat is None:
        raise HTTPException(status_code=404, detail="Framework not found")
    return cat.to_dict()


@router.get("/frameworks/{framework_id}/categories")
async def list_categories(framework_id: str) -> list[dict]:  # type: ignore[no-untyped-def]
    """List categories for a framework."""
    return [c.to_dict() for c in _get_framework_service().list_categories(framework_id)]


@router.post("/frameworks/{framework_id}/learning-objectives", status_code=201)
async def add_learning_objective(framework_id: str, body: LearningObjectiveCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Add a learning objective to a framework."""
    obj = _get_framework_service().add_learning_objective(
        framework_id=framework_id,
        competency_id=body.competency_id,
        description=body.description,
        level=body.level,
    )
    if obj is None:
        raise HTTPException(status_code=404, detail="Framework not found")
    return obj.to_dict()


@router.get("/frameworks/{framework_id}/learning-objectives")
async def list_learning_objectives(framework_id: str) -> list[dict]:  # type: ignore[no-untyped-def]
    """List learning objectives for a framework."""
    return [o.to_dict() for o in _get_framework_service().list_learning_objectives(framework_id)]


@router.post("/frameworks/{framework_id}/skills", status_code=201)
async def add_skill(framework_id: str, body: SkillCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Add a skill to a framework."""
    skill = _get_framework_service().add_skill(
        framework_id=framework_id,
        name=body.name,
        description=body.description,
        parent_id=body.parent_id,
        aliases=body.aliases,
        category=body.category,
    )
    if skill is None:
        raise HTTPException(status_code=404, detail="Framework not found")
    return skill.to_dict()


@router.get("/frameworks/{framework_id}/skills")
async def list_skills(framework_id: str) -> list[dict]:  # type: ignore[no-untyped-def]
    """List skills for a framework."""
    return [s.to_dict() for s in _get_framework_service().list_skills(framework_id)]


@router.get("/skills/search")
async def search_skills(query: str = "") -> list[dict]:  # type: ignore[no-untyped-def]
    """Search skills across all frameworks."""
    return [s.to_dict() for s in _get_framework_service().search_skills(query)]


@router.post("/frameworks/{framework_id}/knowledge-areas", status_code=201)
async def add_knowledge_area(framework_id: str, body: KnowledgeAreaCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Add a knowledge area to a framework."""
    area = _get_framework_service().add_knowledge_area(
        framework_id=framework_id,
        name=body.name,
        description=body.description,
    )
    if area is None:
        raise HTTPException(status_code=404, detail="Framework not found")
    return area.to_dict()


@router.get("/frameworks/{framework_id}/knowledge-areas")
async def list_knowledge_areas(framework_id: str) -> list[dict]:  # type: ignore[no-untyped-def]
    """List knowledge areas for a framework."""
    return [a.to_dict() for a in _get_framework_service().list_knowledge_areas(framework_id)]


@router.post("/frameworks/{framework_id}/references", status_code=201)
async def add_reference(framework_id: str, body: ReferenceCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Add a reference to a framework."""
    ref = _get_framework_service().add_reference(
        framework_id=framework_id,
        title=body.title,
        url=body.url,
        reference_type=body.reference_type,
    )
    if ref is None:
        raise HTTPException(status_code=404, detail="Framework not found")
    return ref.to_dict()


@router.get("/frameworks/{framework_id}/references")
async def list_references(framework_id: str) -> list[dict]:  # type: ignore[no-untyped-def]
    """List references for a framework."""
    return [r.to_dict() for r in _get_framework_service().list_references(framework_id)]


@router.post("/frameworks/import", status_code=201)
async def import_framework(body: dict) -> dict:  # type: ignore[no-untyped-def]
    """Import a framework from JSON data."""
    fw = _get_framework_service().import_framework(body)
    return fw.to_dict()


@router.get("/frameworks/{framework_id}/export")
async def export_framework(framework_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Export a framework as JSON data."""
    data = _get_framework_service().export_framework(framework_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Framework not found")
    return data


@router.post("/frameworks/compare")
async def compare_frameworks(body: ComparisonRequest) -> dict:  # type: ignore[no-untyped-def]
    """Compare two frameworks."""
    return _get_framework_service().compare_frameworks(
        body.framework_a_id,
        body.framework_b_id,
    )


# ---------------------------------------------------------------------------
# Mapping Routes
# ---------------------------------------------------------------------------


@router.post("/mappings", status_code=201)
async def create_mapping(body: MappingCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Create a curriculum mapping."""
    mapping = _get_mapping_service().create_mapping(
        source_id=body.source_id,
        source_type=body.source_type,
        target_id=body.target_id,
        target_type=body.target_type,
        coverage_level=body.coverage_level,
        confidence=body.confidence,
        instructor_notes=body.instructor_notes,
    )
    return mapping.to_dict()


@router.get("/mappings")
async def list_mappings() -> list[dict]:  # type: ignore[no-untyped-def]
    """List all mappings."""
    return [m.to_dict() for m in _get_mapping_service().list_mappings()]


@router.get("/mappings/{mapping_id}")
async def get_mapping(mapping_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Get a mapping by ID."""
    mapping = _get_mapping_service().get_mapping(mapping_id)
    if mapping is None:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return mapping.to_dict()


@router.put("/mappings/{mapping_id}")
async def update_mapping(mapping_id: str, body: MappingUpdateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Update a mapping."""
    mapping = _get_mapping_service().update_mapping(
        mapping_id=mapping_id,
        coverage_level=body.coverage_level,
        confidence=body.confidence,
        instructor_notes=body.instructor_notes,
        review_status=body.review_status,
    )
    if mapping is None:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return mapping.to_dict()


@router.delete("/mappings/{mapping_id}", response_model=MessageResponse)
async def delete_mapping(mapping_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Delete a mapping."""
    deleted = _get_mapping_service().delete_mapping(mapping_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return {"message": "Mapping deleted", "success": True}


@router.post("/mappings/bulk", status_code=201)
async def bulk_mapping(body: BulkMappingRequest) -> dict:  # type: ignore[no-untyped-def]
    """Run bulk mapping."""
    result = _get_mapping_service().bulk_map(
        source_ids=body.source_ids,
        target_ids=body.target_ids,
        source_type=body.source_type,
        target_type=body.target_type,
    )
    return result.to_dict()


@router.get("/frameworks/{framework_id}/coverage")
async def compute_coverage(framework_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Compute coverage for a framework."""
    try:
        report = _get_mapping_service().compute_coverage(framework_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return report.to_dict()


@router.get("/frameworks/{framework_id}/gaps")
async def identify_gaps(framework_id: str) -> list[dict]:  # type: ignore[no-untyped-def]
    """Identify gaps in a framework's mappings."""
    try:
        gaps = _get_mapping_service().identify_gaps(framework_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return [g.to_dict() for g in gaps]


# ---------------------------------------------------------------------------
# Skills Taxonomy Routes
# ---------------------------------------------------------------------------


@router.post("/taxonomies", status_code=201)
async def create_taxonomy(body: TaxonomyCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Create a new skills taxonomy."""
    tax = _get_taxonomy_service().create_taxonomy(
        name=body.name,
        description=body.description,
        version=body.version,
    )
    return tax.to_dict()


@router.get("/taxonomies")
async def list_taxonomies() -> list[dict]:  # type: ignore[no-untyped-def]
    """List all taxonomies."""
    return [t.to_dict() for t in _get_taxonomy_service().list_taxonomies()]


@router.get("/taxonomies/{taxonomy_id}")
async def get_taxonomy(taxonomy_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Get a taxonomy by ID."""
    tax = _get_taxonomy_service().get_taxonomy(taxonomy_id)
    if tax is None:
        raise HTTPException(status_code=404, detail="Taxonomy not found")
    return tax.to_dict()


@router.delete("/taxonomies/{taxonomy_id}", response_model=MessageResponse)
async def delete_taxonomy(taxonomy_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Delete a taxonomy."""
    deleted = _get_taxonomy_service().delete_taxonomy(taxonomy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Taxonomy not found")
    return {"message": "Taxonomy deleted", "success": True}


@router.post("/taxonomies/{taxonomy_id}/skills", status_code=201)
async def add_taxonomy_skill(taxonomy_id: str, body: TaxonomySkillCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Add a skill to a taxonomy."""
    skill = _get_taxonomy_service().add_skill(
        taxonomy_id=taxonomy_id,
        name=body.name,
        description=body.description,
        category=body.category,
        parent_id=body.parent_id,
        aliases=body.aliases,
        level=body.level,
    )
    if skill is None:
        raise HTTPException(status_code=404, detail="Taxonomy not found")
    return skill.to_dict()


@router.get("/taxonomies/{taxonomy_id}/skills")
async def list_taxonomy_skills(taxonomy_id: str) -> list[dict]:  # type: ignore[no-untyped-def]
    """List skills in a taxonomy."""
    return [s.to_dict() for s in _get_taxonomy_service().list_skills(taxonomy_id)]


@router.get("/taxonomy-skills/search")
async def search_taxonomy_skills(query: str = "") -> list[dict]:  # type: ignore[no-untyped-def]
    """Search taxonomy skills."""
    return [s.to_dict() for s in _get_taxonomy_service().search_skills(query)]


@router.post("/taxonomies/{taxonomy_id}/relationships", status_code=201)
async def add_relationship(taxonomy_id: str, body: RelationshipCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Add a relationship between skills."""
    rel = _get_taxonomy_service().add_relationship(
        source_skill_id=body.source_skill_id,
        target_skill_id=body.target_skill_id,
        relationship_type=body.relationship_type,
        weight=body.weight,
        taxonomy_id=taxonomy_id,
    )
    return rel.to_dict()


@router.get("/taxonomies/{taxonomy_id}/relationships")
async def list_relationships(taxonomy_id: str) -> list[dict]:  # type: ignore[no-untyped-def]
    """List relationships in a taxonomy."""
    return [r.to_dict() for r in _get_taxonomy_service().list_relationships(taxonomy_id)]


# ---------------------------------------------------------------------------
# Evidence Routes
# ---------------------------------------------------------------------------


@router.post("/evidence/collections", status_code=201)
async def create_evidence_collection(body: EvidenceCollectionCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Create an evidence collection."""
    collection = _get_evidence_service().create_collection(
        name=body.name,
        framework_id=body.framework_id,
    )
    return collection.to_dict()


@router.get("/evidence/collections")
async def list_evidence_collections() -> list[dict]:  # type: ignore[no-untyped-def]
    """List all evidence collections."""
    return [c.to_dict() for c in _get_evidence_service().list_collections()]


@router.get("/evidence/collections/{collection_id}")
async def get_evidence_collection(collection_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Get an evidence collection by ID."""
    collection = _get_evidence_service().get_collection(collection_id)
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection.to_dict()


@router.post("/evidence/collections/{collection_id}/items", status_code=201)
async def add_evidence_item(collection_id: str, body: EvidenceItemCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Add an evidence item to a collection."""
    item = _get_evidence_service().add_evidence(
        collection_id=collection_id,
        evidence_type=body.evidence_type,
        description=body.description,
        source_id=body.source_id,
        source_type=body.source_type,
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    return item.to_dict()


@router.get("/evidence/collections/{collection_id}/items")
async def list_evidence_items(collection_id: str) -> list[dict]:  # type: ignore[no-untyped-def]
    """List evidence items in a collection."""
    return [i.to_dict() for i in _get_evidence_service().list_evidence_items(collection_id)]


@router.post("/evidence/items/{item_id}/review")
async def review_evidence(item_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Mark an evidence item as reviewed."""
    item = _get_evidence_service().review_evidence(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Evidence item not found")
    return item.to_dict()


@router.get("/evidence/search")
async def search_evidence(query: str = "") -> list[dict]:  # type: ignore[no-untyped-def]
    """Search evidence items."""
    return [r.to_dict() for r in _get_evidence_service().search_evidence(query)]


@router.get("/evidence/types")
async def get_evidence_types() -> list[str]:  # type: ignore[no-untyped-def]
    """Get valid evidence types."""
    return _get_evidence_service().get_evidence_types()


@router.get("/evidence/collections/{collection_id}/stats")
async def get_evidence_stats(collection_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Get stats for an evidence collection."""
    stats = _get_evidence_service().get_collection_stats(collection_id)
    if stats is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    return stats


# ---------------------------------------------------------------------------
# Quality / Readiness Routes
# ---------------------------------------------------------------------------


@router.post("/quality/dashboards", status_code=201)
async def generate_dashboard(body: DashboardGenerateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Generate an academic quality dashboard."""
    dashboard = _get_quality_service().generate_dashboard(
        curriculum_balance=body.curriculum_balance,
        competency_distribution=body.competency_distribution,
        skills_progression=body.skills_progression,
        assessment_distribution=body.assessment_distribution,
        a11y_health=body.a11y_health,
        doc_quality=body.doc_quality,
        localization_readiness=body.localization_readiness,
        content_freshness=body.content_freshness,
        review_completion=body.review_completion,
    )
    return dashboard.to_dict()


@router.get("/quality/dashboards/latest")
async def get_latest_dashboard() -> dict:  # type: ignore[no-untyped-def]
    """Get the latest quality dashboard."""
    dashboard = _get_quality_service().get_latest_dashboard()
    if dashboard is None:
        raise HTTPException(status_code=404, detail="No dashboards found")
    return dashboard.to_dict()


@router.get("/quality/dashboards")
async def list_dashboards() -> list[dict]:  # type: ignore[no-untyped-def]
    """List all quality dashboards."""
    return [d.to_dict() for d in _get_quality_service().list_dashboards()]


@router.post("/readiness-reviews", status_code=201)
async def create_readiness_review(body: ReviewCreateRequest) -> dict:  # type: ignore[no-untyped-def]
    """Create a readiness review."""
    review = _get_quality_service().create_review(
        name=body.name,
        framework_id=body.framework_id,
        created_by=body.created_by,
    )
    return review.to_dict()


@router.get("/readiness-reviews")
async def list_readiness_reviews() -> list[dict]:  # type: ignore[no-untyped-def]
    """List all readiness reviews."""
    return [r.to_dict() for r in _get_quality_service().list_reviews()]


@router.get("/readiness-reviews/{review_id}")
async def get_readiness_review(review_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Get a readiness review by ID."""
    review = _get_quality_service().get_review(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review.to_dict()


@router.post("/readiness-reviews/{review_id}/advance")
async def advance_readiness_review(review_id: str, body: ReviewAdvanceRequest) -> dict:  # type: ignore[no-untyped-def]
    """Advance a readiness review to the next stage."""
    review = _get_quality_service().advance_review(
        review_id=review_id,
        actor=body.actor,
        comments=body.comments,
    )
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found or cannot advance")
    return review.to_dict()


@router.post("/readiness-reviews/{review_id}/reject")
async def reject_readiness_review(review_id: str, body: ReviewAdvanceRequest) -> dict:  # type: ignore[no-untyped-def]
    """Reject a readiness review back to the previous stage."""
    review = _get_quality_service().reject_review(
        review_id=review_id,
        actor=body.actor,
        comments=body.comments,
    )
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found or cannot reject")
    return review.to_dict()


@router.post("/frameworks/{framework_id}/validate-outcomes")
async def validate_outcomes(framework_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Validate learning outcomes for a framework."""
    try:
        validation = _get_quality_service().validate_learning_outcomes(framework_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return validation.to_dict()


# ---------------------------------------------------------------------------
# Comparison Routes
# ---------------------------------------------------------------------------


@router.post("/comparisons", status_code=201)
async def create_comparison(body: ComparisonRequest) -> dict:  # type: ignore[no-untyped-def]
    """Compare two frameworks."""
    try:
        comparison = _get_comparison_service().compare(
            framework_a_id=body.framework_a_id,
            framework_b_id=body.framework_b_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return comparison.to_dict()


@router.get("/comparisons")
async def list_comparisons() -> list[dict]:  # type: ignore[no-untyped-def]
    """List all framework comparisons."""
    return [c.to_dict() for c in _get_comparison_service().list_comparisons()]


@router.get("/comparisons/{comparison_id}")
async def get_comparison(comparison_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Get a comparison by ID."""
    comp = _get_comparison_service().get_comparison(comparison_id)
    if comp is None:
        raise HTTPException(status_code=404, detail="Comparison not found")
    return comp.to_dict()


@router.post("/comparisons/migration-report")
async def generate_migration_report(body: ComparisonRequest) -> dict:  # type: ignore[no-untyped-def]
    """Generate a migration report between two frameworks."""
    try:
        report = _get_comparison_service().generate_migration_report(
            framework_a_id=body.framework_a_id,
            framework_b_id=body.framework_b_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return report
