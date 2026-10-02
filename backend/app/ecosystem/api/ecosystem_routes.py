"""Ecosystem API routes."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from ..domain.entities.marketplace import (
    LocalPackage, PackageCategory, PackageSearch, InstallationRecord,
)
from ..domain.entities.library import LibraryItem, LibraryItemType
from ..domain.entities.research import ResearchProject, ResearchStatus
from ..domain.entities.institution import Organization, OrgType
from ..domain.entities.content_distribution import DistributionPackage
from ..repositories.ecosystem_repository_impl import (
    InMemoryMarketplaceRepository, InMemoryLibraryRepository,
    InMemoryResearchRepository, InMemoryInstitutionRepository,
    InMemoryDistributionRepository,
)
from ..services.marketplace_service import MarketplaceService
from ..services.library_service import LibraryService
from ..services.research_service import ResearchService
from ..services.institution_service import InstitutionService
from ..services.distribution_service import DistributionService
from ..validators.ecosystem_validator import EcosystemValidator

router = APIRouter(prefix="/ecosystem", tags=["ecosystem"])

_market_repo = InMemoryMarketplaceRepository()
_library_repo = InMemoryLibraryRepository()
_research_repo = InMemoryResearchRepository()
_institution_repo = InMemoryInstitutionRepository()
_distribution_repo = InMemoryDistributionRepository()

market_service = MarketplaceService(_market_repo)
library_service = LibraryService(_library_repo)
research_service = ResearchService(_research_repo)
institution_service = InstitutionService(_institution_repo)
distribution_service = DistributionService(_distribution_repo)
validator = EcosystemValidator()


@router.get("/packages")
def list_packages():
    return [vars(p) for p in _market_repo.all_packages()]


@router.post("/packages")
def create_package(
    name: str,
    version: str,
    author: str,
    description: str = "",
    category: str = "plugin",
    tags: list[str] = [],
):
    if not validator.validate_package_name(name):
        raise HTTPException(400, "Invalid package name")
    if not validator.validate_semver(version):
        raise HTTPException(400, "Invalid semver version")
    pkg = LocalPackage(
        name=name, version=version, author=author, description=description,
        category=PackageCategory(category), tags=tags,
    )
    _market_repo.add_package(pkg)
    return vars(pkg)


@router.get("/packages/{package_id}")
def get_package(package_id: str):
    pkg = _market_repo.get_package(package_id)
    if not pkg:
        raise HTTPException(404, "Package not found")
    return vars(pkg)


@router.post("/packages/{package_id}/install")
def install_package(package_id: str, installed_by: str = "anonymous"):
    record = market_service.install_package(package_id, installed_by)
    return vars(record)


@router.post("/packages/{package_id}/uninstall")
def uninstall_package(package_id: str):
    try:
        market_service.uninstall_package(package_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"status": "uninstalled"}


@router.post("/packages/{package_id}/rate")
def rate_package(package_id: str, rating: int = 5):
    try:
        pkg = market_service.rate_package(package_id, rating)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return vars(pkg)


@router.post("/packages/{package_id}/favorite")
def toggle_favorite(package_id: str):
    try:
        pkg = market_service.toggle_favorite(package_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(pkg)


@router.get("/packages/favorites")
def list_favorites():
    return [vars(p) for p in market_service.get_favorites()]


@router.get("/packages/installed")
def list_installed():
    return [vars(p) for p in market_service.get_installed_packages()]


@router.post("/packages/search")
def search_packages(query: str = "", category: str = "", sort_by: str = "name", limit: int = 20, offset: int = 0):
    cat = PackageCategory(category) if category else None
    search = PackageSearch(query=query, category=cat, sort_by=sort_by, limit=limit, offset=offset)
    return [vars(p) for p in market_service.search_packages(search)]


@router.get("/library")
def list_library_items():
    return [vars(i) for i in _library_repo.all_items()]


@router.post("/library")
def create_library_item(
    title: str, author: str, item_type: str,
    description: str = "", tags: list[str] = [],
):
    it = LibraryItemType(item_type)
    item = LibraryItem(title=title, author=author, item_type=it, description=description, tags=tags)
    lib_service = LibraryService(_library_repo)
    lib_service.add_item(item)
    return vars(item)


@router.get("/library/{item_id}")
def get_library_item(item_id: str):
    item = _library_repo.get_item(item_id)
    if not item:
        raise HTTPException(404, "Library item not found")
    return vars(item)


@router.delete("/library/{item_id}")
def delete_library_item(item_id: str):
    _library_repo.remove_item(item_id)
    return {"status": "deleted"}


@router.post("/library/{item_id}/bookmark")
def bookmark_item(item_id: str, user_id: str = "anonymous", note: str = ""):
    bm = library_service.add_bookmark(item_id, user_id, note)
    return vars(bm)


@router.post("/library/{item_id}/annotate")
def annotate_item(item_id: str, user_id: str = "anonymous", text: str = "", highlight: str = "", page: int = 0):
    ann = library_service.add_annotation(item_id, user_id, text, highlight, page)
    return vars(ann)


@router.get("/library/{item_id}/bookmarks")
def get_item_bookmarks(item_id: str):
    return [vars(b) for b in library_service.get_bookmarks_for_item(item_id)]


@router.get("/library/{item_id}/annotations")
def get_item_annotations(item_id: str):
    return [vars(a) for a in library_service.get_annotations_for_item(item_id)]


@router.get("/library/{item_id}/citations")
def get_item_citations(item_id: str):
    return [vars(c) for c in library_service.get_citations_for_item(item_id)]


@router.post("/library/citations")
def create_citation(source_item_id: str, target_item_id: str, citation_type: str = "references", page: int = 0, note: str = ""):
    cit = library_service.add_citation(source_item_id, target_item_id, citation_type, page, note)
    return vars(cit)


@router.get("/library/bibliography")
def generate_bibliography(item_ids: str, format: str = "apa"):
    ids = [x.strip() for x in item_ids.split(",") if x.strip()]
    text = library_service.generate_bibliography(ids, format)
    return {"bibliography": text}


@router.get("/research/projects")
def list_research_projects():
    return [vars(p) for p in research_service.list_projects()]


@router.post("/research/projects")
def create_research_project(title: str, description: str = ""):
    if not title:
        raise HTTPException(400, "Title is required")
    project = research_service.create_project(title, description)
    return vars(project)


@router.get("/research/projects/{project_id}")
def get_research_project(project_id: str):
    project = research_service.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return vars(project)


@router.put("/research/projects/{project_id}")
def update_research_project(project_id: str, title: str = "", description: str = "", status: str = ""):
    t = title if title else None
    d = description if description else None
    s = status if status else None
    try:
        project = research_service.update_project(project_id, t, d, s)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(project)


@router.delete("/research/projects/{project_id}")
def delete_research_project(project_id: str):
    research_service.delete_project(project_id)
    return {"status": "deleted"}


@router.post("/research/projects/{project_id}/literature")
def add_literature(project_id: str, title: str, author: str = "", year: int = 0, source: str = "", abstract: str = "", keywords: list[str] = []):
    entry = research_service.add_literature(project_id, title, author, year, source, abstract, keywords)
    return vars(entry)


@router.get("/research/literature/{entry_id}")
def get_literature_entry(entry_id: str):
    entry = _research_repo.get_literature_entry(entry_id)
    if not entry:
        raise HTTPException(404, "Literature entry not found")
    return vars(entry)


@router.delete("/research/literature/{entry_id}")
def delete_literature_entry(entry_id: str):
    research_service.delete_literature(entry_id)
    return {"status": "deleted"}


@router.post("/research/literature/{entry_id}/notes")
def add_note_to_entry(entry_id: str, content: str = ""):
    note = research_service.add_note(entry_id, content)
    return vars(note)


@router.get("/research/literature/{entry_id}/notes")
def get_notes_for_entry(entry_id: str):
    return [vars(n) for n in research_service.get_notes_for_entry(entry_id)]


@router.post("/research/projects/{project_id}/knowledge-maps")
def create_knowledge_map(project_id: str, name: str):
    km = research_service.create_knowledge_map(project_id, name)
    return vars(km)


@router.get("/research/projects/{project_id}/knowledge-maps")
def list_knowledge_maps(project_id: str):
    return [vars(m) for m in research_service.get_knowledge_maps(project_id)]


@router.post("/research/projects/{project_id}/reading-lists")
def create_reading_list(project_id: str, name: str, entries: list[str] = []):
    rl = research_service.create_reading_list(project_id, name, entries)
    return vars(rl)


@router.get("/research/projects/{project_id}/reading-lists")
def list_reading_lists(project_id: str):
    return [vars(r) for r in research_service.get_reading_lists(project_id)]


@router.post("/research/projects/{project_id}/bibliographies")
def create_bibliography(project_id: str, name: str = "default", entries: list[str] = [], format: str = "apa"):
    bib = research_service.create_bibliography(project_id, name, entries, format)
    return vars(bib)


@router.get("/research/projects/{project_id}/bibliographies")
def list_bibliographies(project_id: str):
    return [vars(b) for b in research_service.get_bibliographies(project_id)]


@router.get("/institution/organizations")
def list_organizations():
    return [vars(o) for o in institution_service.list_organizations()]


@router.post("/institution/organizations")
def create_organization(name: str, org_type: str = "university", settings: dict = {}):
    if not name:
        raise HTTPException(400, "Name is required")
    org = institution_service.create_organization(name, org_type, settings)
    return vars(org)


@router.get("/institution/organizations/{org_id}")
def get_organization(org_id: str):
    org = institution_service.get_organization(org_id)
    if not org:
        raise HTTPException(404, "Organization not found")
    return vars(org)


@router.put("/institution/organizations/{org_id}")
def update_organization(org_id: str, name: str = "", org_type: str = ""):
    try:
        org = institution_service.update_organization(
            org_id,
            name=name if name else None,
            org_type=org_type if org_type else None,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(org)


@router.delete("/institution/organizations/{org_id}")
def delete_organzation(org_id: str):
    institution_service.delete_organization(org_id)
    return {"status": "deleted"}


@router.post("/institution/organizations/{org_id}/departments")
def create_department(org_id: str, name: str, description: str = ""):
    dept = institution_service.add_department(org_id, name, description)
    return vars(dept)


@router.get("/institution/departments/{dept_id}")
def get_department(dept_id: str):
    dept = institution_service.get_department(dept_id)
    if not dept:
        raise HTTPException(404, "Department not found")
    return vars(dept)


@router.put("/institution/departments/{dept_id}")
def update_department(dept_id: str, name: str = "", description: str = ""):
    try:
        dept = institution_service.update_department(
            dept_id,
            name=name if name else None,
            description=description if description else None,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(dept)


@router.delete("/institution/departments/{dept_id}")
def delete_departments(dept_id: str):
    institution_service.delete_department(dept_id)
    return {"status": "deleted"}


@router.get("/institution/organizations/{org_id}/departments")
def list_departments_for_org(org_id: str):
    depts = institution_service.get_departments_for_org(org_id)
    return [vars(d) for d in depts]


@router.post("/institution/departments/{dept_id}/programs")
def create_program(dept_id: str, name: str, description: str = "", duration_months: int = 0, competencies: list[str] = []):
    prog = institution_service.create_program(dept_id, name, description, duration_months, competencies)
    return vars(prog)


@router.get("/institution/programs/{prog_id}")
def get_program(prog_id: str):
    prog = institution_service.get_program(prog_id)
    if not prog:
        raise HTTPException(404, "Program not found")
    return vars(prog)


@router.get("/institution/departments/{dept_id}/programs")
def list_programs_for_department(dept_id: str):
    return [vars(p) for p in institution_service.get_programs_for_department(dept_id)]


@router.put("/institution/programs/{prog_id}")
def update_program(prog_id: str, name: str = "", description: str = "", status: str = ""):
    try:
        prog = institution_service.update_program(
            prog_id,
            name=name if name else None,
            description=description if description else None,
            status=status if status else None,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    return vars(prog)


@router.post("/institution/assignments")
def create_assignment(instructor_id: str, program_id: str, course_id: str = "", term: str = ""):
    assignment = institution_service.assign_instructor(instructor_id, program_id, course_id, term)
    return vars(assignment)


@router.get("/instructor/{instructor_id}/assignments")
def get_assignments(instructor_id: str):
    return [vars(a) for a in institution_service.get_instructor_assignments(instructor_id)]


@router.post("/institution/resource-allocations")
def create_allocation(resource_type: str, amount: float, unit: str = "", allocated_to: str = "", purpose: str = ""):
    alloc = institution_service.allocate_resource(resource_type, amount, unit, allocated_to, purpose)
    return vars(alloc)


@router.get("/institution/resource-allocations")
def list_allocations():
    return [vars(a) for a in _institution_repo._allocations.values()]


@router.get("/distribution/packages")
def list_distribution_packages():
    return [vars(p) for p in distribution_service.list_packages()]


@router.post("/distribution/packages")
def create_distribution_package(name: str, description: str = "", content_type: str = "", version: str = "1.0.0", created_by: str = ""):
    if not validator.validate_package_name(name):
        raise HTTPException(400, "Invalid package name")
    if not validator.validate_semver(version):
        raise HTTPException(400, "Invalid semver")
    pkg = distribution_service.create_package(name, description, content_type, version, created_by)
    return vars(pkg)


@router.post("/distribution/packages/{package_id}/export")
def export_package(package_id: str):
    try:
        manifest = distribution_service.export_package(package_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"manifest_id": manifest.id, "total_size": manifest.total_size}


@router.post("/distribution/packages/{package_id}/import")
def import_package(package_id: str, imported_by: str = "anonymous"):
    conflicts = distribution_service.detect_conflicts(package_id)
    record = distribution_service.import_package(package_id, imported_by)
    return {"record_id": record.id, "status": record.status, "conflicts": conflicts}


@router.get("/distribution/imports")
def list_imports():
    return [vars(r) for r in distribution_service.get_import_records()]


@router.post("/distribution/sync")
def start_sync(name: str, source: str, destination: str):
    op = distribution_service.start_sync(name, source, destination)
    return vars(op)


@router.get("/distribution/sync")
def list_sync():
    return [vars(s) for s in distribution_service.get_sync_operations()]


@router.get("/validate/package/{package_id}")
def validate_package(package_id: str):
    from ..services.governance_validation_service import GovernanceValidationService
    pkg = _market_repo.get_package(package_id)
    if not pkg:
        raise HTTPException(404, "Package not found")
    gv = GovernanceValidationService()
    return gv.validate_package(pkg)
