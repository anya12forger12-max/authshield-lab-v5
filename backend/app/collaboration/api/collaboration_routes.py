"""Collaboration API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..domain.entities.academic_hub import ProjectStatus, ReviewStatus
from ..domain.entities.peer_review import ReviewStage, ReviewDecisionType
from ..repositories.collaboration_repository_impl import (
    InMemoryAcademicHubRepository,
    InMemoryCurriculumExchangeRepository,
    InMemoryResearchWorkspaceRepository,
    InMemoryPeerReviewRepository,
    InMemoryKnowledgeBaseRepository,
)
from ..services.academic_hub_service import AcademicHubService
from ..services.curriculum_exchange_service import CurriculumExchangeService
from ..services.research_service import ResearchService
from ..services.peer_review_service import PeerReviewService
from ..services.knowledge_base_service import KnowledgeBaseService
from ..services.package_validation_service import PackageValidationService
from ..validators.collaboration_validator import CollaborationValidator

router = APIRouter(prefix="/collaboration", tags=["collaboration"])

_academic_repo = InMemoryAcademicHubRepository()
_exchange_repo = InMemoryCurriculumExchangeRepository()
_research_repo = InMemoryResearchWorkspaceRepository()
_review_repo = InMemoryPeerReviewRepository()
_kb_repo = InMemoryKnowledgeBaseRepository()

academic_service = AcademicHubService(_academic_repo)
exchange_service = CurriculumExchangeService(_exchange_repo)
research_service = ResearchService(_research_repo)
review_service = PeerReviewService(_review_repo)
kb_service = KnowledgeBaseService(_kb_repo)
validation_service = PackageValidationService(_exchange_repo)
validator = CollaborationValidator()


# ── Academic Hub ──────────────────────────────────────────────────────────

@router.get("/hub/projects")
def list_projects():
    return [vars(p) for p in academic_service.list_projects()]


@router.post("/hub/projects")
def create_project(
    name: str,
    description: str,
    department: str,
    lead: str,
    members: list[str] = [],
):
    if not validator.validate_project_name(name):
        raise HTTPException(400, "Invalid project name")
    project = academic_service.create_project(name, description, department, lead, members)
    return vars(project)


@router.get("/hub/projects/{project_id}")
def get_project(project_id: str):
    project = academic_service.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return vars(project)


@router.put("/hub/projects/{project_id}")
def update_project(
    project_id: str,
    name: str = "",
    description: str = "",
    status: str = "",
):
    try:
        project = academic_service.update_project(
            project_id,
            name=name if name else None,
            description=description if description else None,
            status=status if status else None,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(project)


@router.delete("/hub/projects/{project_id}")
def delete_project(project_id: str):
    academic_service.delete_project(project_id)
    return {"status": "deleted"}


@router.get("/hub/shared-packages")
def list_shared_packages():
    return [vars(p) for p in academic_service.list_shared_packages()]


@router.post("/hub/shared-packages")
def share_curriculum_package(
    title: str,
    source_institution: str,
    version: str,
    content_type: str,
    checksum: str,
    signature: str,
    compatibility: str,
):
    if not validator.validate_semver(version):
        raise HTTPException(400, "Invalid semver version")
    pkg = academic_service.share_curriculum_package(
        title, source_institution, version, content_type,
        checksum, signature, compatibility,
    )
    return vars(pkg)


@router.get("/hub/shared-packages/{package_id}")
def get_shared_package(package_id: str):
    pkg = academic_service.get_shared_package(package_id)
    if not pkg:
        raise HTTPException(404, "Shared package not found")
    return vars(pkg)


@router.get("/hub/imported-resources")
def list_imported_resources():
    return [vars(r) for r in academic_service.list_imported_resources()]


@router.post("/hub/imported-resources")
def import_resource(
    package_id: str,
    imported_by: str = "anonymous",
    status: str = "pending",
):
    resource = academic_service.import_resource(package_id, imported_by, status)
    return vars(resource)


@router.get("/hub/review-requests")
def list_review_requests():
    return [vars(r) for r in academic_service.list_review_requests()]


@router.post("/hub/review-requests")
def create_review_request(
    title: str,
    request_type: str,
    submitter: str,
    assignees: list[str] = [],
    due_date: str = "",
):
    errors = validator.validate_review_request(title, request_type, submitter)
    if errors:
        raise HTTPException(400, "; ".join(errors))
    request = academic_service.create_review_request(title, request_type, submitter, assignees, due_date)
    return vars(request)


@router.put("/hub/review-requests/{request_id}/status")
def update_review_status(request_id: str, status: str):
    try:
        request = academic_service.update_review_status(request_id, status)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(request)


@router.get("/hub/publications")
def list_publications():
    return [vars(p) for p in academic_service.list_publication_items()]


@router.post("/hub/publications")
def queue_publication(
    content_id: str,
    content_type: str,
    title: str,
    version: str,
    submitted_by: str,
):
    errors = validator.validate_publication_item(content_id, content_type, title, version, submitted_by)
    if errors:
        raise HTTPException(400, "; ".join(errors))
    if not validator.validate_semver(version):
        raise HTTPException(400, "Invalid semver version")
    item = academic_service.queue_publication(content_id, content_type, title, version, submitted_by)
    return vars(item)


@router.put("/hub/publications/{item_id}/status")
def update_publication_status(item_id: str, status: str):
    try:
        item = academic_service.update_publication_status(item_id, status)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(item)


@router.get("/hub/dashboard")
def get_dashboard():
    dashboard = academic_service.get_dashboard()
    return vars(dashboard)


@router.get("/hub/version-history/{entity_id}")
def get_version_history(entity_id: str):
    return [vars(v) for v in academic_service.get_version_history(entity_id)]


# ── Curriculum Exchange ───────────────────────────────────────────────────

@router.get("/exchange/packages")
def list_exchange_packages():
    return [vars(p) for p in exchange_service.list_packages()]


@router.post("/exchange/packages")
def create_exchange_package(
    name: str,
    description: str,
    package_type: str,
    version: str,
    author: str,
    source_institution: str,
    checksum: str,
    signature: str,
    license: str,
    compatibility: str,
    dependencies: list[str] = [],
    metadata: dict = {},
):
    if not validator.validate_semver(version):
        raise HTTPException(400, "Invalid semver version")
    pkg = exchange_service.create_package(
        name, description, package_type, version, author,
        source_institution, checksum, signature, license,
        compatibility, dependencies, metadata,
    )
    return vars(pkg)


@router.get("/exchange/packages/{package_id}")
def get_exchange_package(package_id: str):
    pkg = exchange_service.get_package(package_id)
    if not pkg:
        raise HTTPException(404, "Exchange package not found")
    return vars(pkg)


@router.put("/exchange/packages/{package_id}")
def update_exchange_package(
    package_id: str,
    name: str = "",
    description: str = "",
    version: str = "",
):
    try:
        pkg = exchange_service.update_package(
            package_id,
            name=name if name else None,
            description=description if description else None,
            version=version if version else None,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(pkg)


@router.delete("/exchange/packages/{package_id}")
def delete_exchange_package(package_id: str):
    try:
        exchange_service.delete_package(package_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"status": "deleted"}


@router.post("/exchange/packages/{package_id}/export")
def export_package(package_id: str, exported_by: str = "anonymous"):
    try:
        manifest = exchange_service.export_package(package_id, exported_by)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"manifest_id": manifest.id, "package_id": manifest.package_id, "total_size": manifest.total_size}


@router.post("/exchange/packages/{package_id}/import")
def import_exchange_package(package_id: str, imported_by: str = "anonymous"):
    try:
        report = exchange_service.import_package(package_id, imported_by)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(report)


@router.post("/exchange/packages/{package_id}/validate")
def validate_exchange_package(package_id: str):
    try:
        report = exchange_service.validate_package(package_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(report)


@router.get("/exchange/packages/{package_id}/validation-reports")
def get_validation_reports(package_id: str):
    return [vars(r) for r in exchange_service.get_validation_reports(package_id)]


@router.get("/exchange/packages/{package_id}/manifest")
def get_manifest(package_id: str):
    manifest = exchange_service.get_manifest(package_id)
    if not manifest:
        raise HTTPException(404, "Manifest not found")
    return vars(manifest)


@router.get("/exchange/packages/{package_id}/history")
def get_exchange_history(package_id: str):
    return [vars(h) for h in exchange_service.get_history(package_id)]


@router.post("/exchange/validate-batch")
def validate_batch(package_ids: list[str]):
    reports = validation_service.validate_batch(package_ids)
    return [vars(r) for r in reports]


# ── Research ──────────────────────────────────────────────────────────────

@router.get("/research/projects")
def list_research_projects():
    return [vars(p) for p in research_service.list_projects()]


@router.post("/research/projects")
def create_research_project(
    name: str,
    description: str,
    principal_investigator: str,
    team: list[str] = [],
):
    if not name:
        raise HTTPException(400, "Name is required")
    project = research_service.create_project(name, description, principal_investigator, team)
    return vars(project)


@router.get("/research/projects/{project_id}")
def get_research_project(project_id: str):
    project = research_service.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return vars(project)


@router.put("/research/projects/{project_id}")
def update_research_project(
    project_id: str,
    name: str = "",
    description: str = "",
    status: str = "",
):
    try:
        project = research_service.update_project(
            project_id,
            name=name if name else None,
            description=description if description else None,
            status=status if status else None,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(project)


@router.delete("/research/projects/{project_id}")
def delete_research_project(project_id: str):
    research_service.delete_project(project_id)
    return {"status": "deleted"}


@router.get("/research/projects/{project_id}/literature-collections")
def list_literature_collections(project_id: str):
    return [vars(c) for c in research_service.list_literature_collections(project_id)]


@router.post("/research/projects/{project_id}/literature-collections")
def create_literature_collection(project_id: str, name: str):
    collection = research_service.create_literature_collection(project_id, name)
    return vars(collection)


@router.post("/research/literature")
def add_literature_entry(
    title: str,
    author: str = "",
    year: int = 0,
    source: str = "",
    abstract: str = "",
    keywords: list[str] = [],
    notes: str = "",
):
    entry = research_service.add_literature_entry(title, author, year, source, abstract, keywords, notes)
    return vars(entry)


@router.get("/research/literature/{entry_id}")
def get_literature_entry(entry_id: str):
    entry = research_service.get_literature_entry(entry_id)
    if not entry:
        raise HTTPException(404, "Literature entry not found")
    return vars(entry)


@router.put("/research/literature/{entry_id}")
def update_literature_entry(
    entry_id: str,
    title: str = "",
    author: str = "",
    read_status: str = "",
):
    try:
        entry = research_service.update_literature_entry(
            entry_id,
            title=title if title else None,
            author=author if author else None,
            read_status=read_status if read_status else None,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(entry)


@router.delete("/research/literature/{entry_id}")
def delete_literature_entry(entry_id: str):
    research_service.delete_literature_entry(entry_id)
    return {"status": "deleted"}


@router.post("/research/literature/{entry_id}/notes")
def add_note(entry_id: str, content: str = "", created_by: str = "anonymous"):
    note = research_service.add_note(entry_id, content, created_by)
    return vars(note)


@router.get("/research/literature/{entry_id}/notes")
def get_notes_for_entry(entry_id: str):
    return [vars(n) for n in research_service.get_notes_for_entry(entry_id)]


@router.post("/research/citations")
def add_citation(
    source_id: str,
    target_id: str,
    citation_type: str = "references",
    page: int = 0,
    note: str = "",
):
    citation = research_service.add_citation(source_id, target_id, citation_type, page, note)
    return vars(citation)


@router.get("/research/literature/{entry_id}/citations")
def get_citations_for_entry(entry_id: str):
    return [vars(c) for c in research_service.get_citations_for_entry(entry_id)]


@router.get("/research/projects/{project_id}/knowledge-maps")
def list_knowledge_maps(project_id: str):
    return [vars(m) for m in research_service.get_knowledge_maps(project_id)]


@router.post("/research/projects/{project_id}/knowledge-maps")
def create_knowledge_map(project_id: str, name: str):
    km = research_service.create_knowledge_map(project_id, name)
    return vars(km)


@router.post("/research/knowledge-maps/{map_id}/concepts")
def add_concept_to_map(
    map_id: str,
    name: str,
    description: str,
    category: str,
):
    try:
        concept = research_service.add_concept_to_map(map_id, name, description, category)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(concept)


@router.post("/research/knowledge-maps/{map_id}/links")
def add_link_to_map(
    map_id: str,
    source_id: str,
    target_id: str,
    relationship: str,
    weight: float = 1.0,
):
    try:
        link = research_service.add_link_to_map(map_id, source_id, target_id, relationship, weight)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"source_id": link.source_id, "target_id": link.target_id, "relationship": link.relationship, "weight": link.weight}


@router.get("/research/projects/{project_id}/reading-lists")
def list_reading_lists(project_id: str):
    return [vars(r) for r in research_service.get_reading_lists(project_id)]


@router.post("/research/projects/{project_id}/reading-lists")
def create_reading_list(project_id: str, name: str, item_ids: list[str] = []):
    rl = research_service.create_reading_list(project_id, name, item_ids)
    return vars(rl)


@router.get("/research/projects/{project_id}/bibliographies")
def list_bibliographies(project_id: str):
    return [vars(b) for b in research_service.get_bibliographies(project_id)]


@router.post("/research/projects/{project_id}/bibliographies")
def create_bibliography(project_id: str, name: str = "default", entries: list[str] = [], format: str = "apa"):
    bib = research_service.create_bibliography(project_id, name, entries, format)
    return vars(bib)


# ── Peer Review ───────────────────────────────────────────────────────────

@router.get("/reviews")
def list_reviews():
    return [vars(r) for r in review_service.list_reviews()]


@router.post("/reviews")
def create_review(
    title: str,
    content_id: str,
    content_type: str,
    submitter: str,
):
    errors = validator.validate_review_request(title, content_type, submitter)
    if errors:
        raise HTTPException(400, "; ".join(errors))
    review = review_service.create_review(title, content_id, content_type, submitter)
    return vars(review)


@router.get("/reviews/{review_id}")
def get_review(review_id: str):
    review = review_service.get_review(review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    return vars(review)


@router.post("/reviews/{review_id}/advance")
def advance_review_stage(review_id: str, actor: str = "system"):
    try:
        review = review_service.advance_stage(review_id, actor)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return vars(review)


@router.post("/reviews/{review_id}/comments")
def add_review_comment(
    review_id: str,
    author: str,
    comment: str,
    severity: str = "",
):
    try:
        c = review_service.add_comment(
            review_id, author, comment,
            severity=severity if severity else None,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(c)


@router.get("/reviews/{review_id}/comments")
def get_review_comments(review_id: str):
    return [vars(c) for c in review_service.get_comments(review_id)]


@router.post("/reviews/{review_id}/decisions")
def make_review_decision(
    review_id: str,
    reviewer: str,
    decision: str,
    comments: str = "",
):
    try:
        d = review_service.make_decision(review_id, reviewer, decision, comments)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(d)


@router.get("/reviews/{review_id}/decisions")
def get_review_decisions(review_id: str):
    return [vars(d) for d in review_service.get_decisions(review_id)]


@router.post("/reviews/{review_id}/revisions")
def add_review_revision(
    review_id: str,
    changes: list[str] = [],
    author: str = "",
):
    try:
        revision = review_service.add_revision(review_id, changes, author)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(revision)


@router.get("/reviews/{review_id}/revisions")
def get_review_revisions(review_id: str):
    return [vars(r) for r in review_service.get_revisions(review_id)]


@router.get("/reviews/{review_id}/history")
def get_review_history(review_id: str):
    history = review_service.get_history(review_id)
    if not history:
        raise HTTPException(404, "Review history not found")
    events = [{"stage": e.stage.value, "action": e.action, "actor": e.actor, "timestamp": e.timestamp.isoformat(), "details": e.details} for e in history.events]
    return {"review_id": history.review_id, "events": events}


# ── Knowledge Base ────────────────────────────────────────────────────────

@router.get("/knowledge/articles")
def list_articles():
    return [vars(a) for a in kb_service.list_articles()]


@router.post("/knowledge/articles")
def create_article(
    title: str,
    content: str,
    category: str,
    author: str,
    tags: list[str] = [],
):
    if not validator.validate_category_name(category):
        raise HTTPException(400, "Invalid category name")
    article = kb_service.create_article(title, content, category, author, tags)
    return vars(article)


@router.get("/knowledge/articles/{article_id}")
def get_article(article_id: str):
    article = kb_service.get_article(article_id)
    if not article:
        raise HTTPException(404, "Article not found")
    return vars(article)


@router.put("/knowledge/articles/{article_id}")
def update_article(
    article_id: str,
    title: str = "",
    content: str = "",
    category: str = "",
    tags: list[str] = [],
):
    try:
        article = kb_service.update_article(
            article_id,
            title=title if title else None,
            content=content if content else None,
            category=category if category else None,
            tags=tags if tags else None,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(article)


@router.delete("/knowledge/articles/{article_id}")
def delete_article(article_id: str):
    kb_service.delete_article(article_id)
    return {"status": "deleted"}


@router.post("/knowledge/articles/{article_id}/publish")
def publish_article(article_id: str):
    try:
        article = kb_service.publish_article(article_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(article)


@router.post("/knowledge/articles/{article_id}/archive")
def archive_article(article_id: str):
    try:
        article = kb_service.archive_article(article_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(article)


@router.get("/knowledge/search")
def search_articles(q: str = ""):
    if not validator.validate_search_query(q):
        raise HTTPException(400, "Invalid search query (min 2, max 500 chars)")
    return [vars(a) for a in kb_service.search_articles(q)]


@router.get("/knowledge/categories")
def list_categories():
    return [vars(c) for c in kb_service.list_categories()]


@router.post("/knowledge/categories")
def create_category(name: str, description: str = "", parent_id: str = ""):
    if not validator.validate_category_name(name):
        raise HTTPException(400, "Invalid category name")
    cat = kb_service.create_category(name, description, parent_id if parent_id else None)
    return vars(cat)


@router.get("/knowledge/categories/{category_id}")
def get_category(category_id: str):
    cat = kb_service.get_category(category_id)
    if not cat:
        raise HTTPException(404, "Category not found")
    return vars(cat)


@router.put("/knowledge/categories/{category_id}")
def update_category(category_id: str, name: str = "", description: str = ""):
    try:
        cat = kb_service.update_category(
            category_id,
            name=name if name else None,
            description=description if description else None,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(cat)


@router.delete("/knowledge/categories/{category_id}")
def delete_category(category_id: str):
    kb_service.delete_category(category_id)
    return {"status": "deleted"}


@router.get("/knowledge/articles/{article_id}/versions")
def get_article_versions(article_id: str):
    return [{"article_id": v.article_id, "version": v.version, "content": v.content, "author": v.author, "created_at": v.created_at.isoformat()} for v in kb_service.get_versions(article_id)]


@router.post("/knowledge/citations")
def add_article_citation(source_id: str, target_id: str, citation_type: str = "references"):
    citation = kb_service.add_citation(source_id, target_id, citation_type)
    return vars(citation)


@router.get("/knowledge/articles/{article_id}/citations")
def get_article_citations(article_id: str):
    return [vars(c) for c in kb_service.get_citations(article_id)]
