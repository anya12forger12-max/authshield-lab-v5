"""In-memory implementation of ecosystem repositories for offline/local use."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..domain.interfaces import (
    MarketplaceRepository, LibraryRepository, ResearchRepository,
    InstitutionRepository, DistributionRepository,
)

if TYPE_CHECKING:
    from ..domain.entities.marketplace import LocalPackage, InstallationRecord, PackageSearch
    from ..domain.entities.library import LibraryItem, Bookmark, Annotation, Citation
    from ..domain.entities.research import ResearchProject, LiteratureEntry, ResearchNote, KnowledgeMap, ReadingList, Bibliography
    from ..domain.entities.institution import Organization, Department, AcademicProgram, InstructorAssignment, ResourceAllocation
    from ..domain.entities.content_distribution import DistributionPackage, DistributionManifest, ImportRecord, SyncOperation


class InMemoryMarketplaceRepository(MarketplaceRepository):
    def __init__(self) -> None:
        self._packages: dict[str, LocalPackage] = {}
        self._installations: dict[str, InstallationRecord] = {}

    def add_package(self, package: LocalPackage) -> None:
        self._packages[package.id] = package

    def get_package(self, package_id: str) -> LocalPackage | None:
        return self._packages.get(package_id)

    def find_by_name(self, name: str) -> list[LocalPackage]:
        return [p for p in self._packages.values() if p.name == name]

    def search(self, search: PackageSearch) -> list[LocalPackage]:
        results = list(self._packages.values())
        if search.query:
            q = search.query.lower()
            results = [p for p in results if q in p.name.lower() or q in p.description.lower()]
        if search.category:
            results = [p for p in results if p.category == search.category]
        if search.tags:
            results = [p for p in results if any(t in p.tags for t in search.tags)]
        reverse = search.sort_by.startswith("-")
        key = search.sort_by.lstrip("-")
        if key == "name":
            results.sort(key=lambda p: p.name, reverse=reverse)
        elif key == "rating":
            results.sort(key=lambda p: p.rating, reverse=True)
        elif key == "created_at":
            results.sort(key=lambda p: p.created_at, reverse=True)
        return results[search.offset:search.offset + search.limit]

    def update_package(self, package: LocalPackage) -> None:
        self._packages[package.id] = package

    def remove_package(self, package_id: str) -> None:
        self._packages.pop(package_id, None)

    def all_packages(self) -> list[LocalPackage]:
        return list(self._packages.values())

    def add_installation(self, record: InstallationRecord) -> None:
        self._installations[record.id] = record

    def get_installation(self, record_id: str) -> InstallationRecord | None:
        return self._installations.get(record_id)

    def find_installations_by_package(self, package_id: str) -> list[InstallationRecord]:
        return [r for r in self._installations.values() if r.package_id == package_id]


class InMemoryLibraryRepository(LibraryRepository):
    def __init__(self) -> None:
        self._items: dict[str, LibraryItem] = {}
        self._bookmarks: dict[str, Bookmark] = {}
        self._annotations: dict[str, Annotation] = {}
        self._citations: dict[str, Citation] = {}

    def add_item(self, item: LibraryItem) -> None:
        self._items[item.id] = item

    def get_item(self, item_id: str) -> LibraryItem | None:
        return self._items.get(item_id)

    def search_items(self, query: str = "", item_type: str = "", tag: str = "") -> list[LibraryItem]:
        results = list(self._items.values())
        if query:
            q = query.lower()
            results = [i for i in results if q in i.title.lower() or q in i.description.lower()]
        if item_type:
            results = [i for i in results if i.item_type.value == item_type]
        if tag:
            results = [i for i in results if tag in i.tags]
        return results

    def update_item(self, item: LibraryItem) -> None:
        self._items[item.id] = item

    def remove_item(self, item_id: str) -> None:
        self._items.pop(item_id, None)
        self._bookmarks = {k: v for k, v in self._bookmarks.items() if v.item_id != item_id}
        self._annotations = {k: v for k, v in self._annotations.items() if v.item_id != item_id}
        self._citations = {k: v for k, v in self._citations.items() if v.source_item_id != item_id and v.target_item_id != item_id}

    def all_items(self) -> list[LibraryItem]:
        return list(self._items.values())

    def add_bookmark(self, bookmark: Bookmark) -> None:
        self._bookmarks[bookmark.id] = bookmark

    def add_annotation(self, annotation: Annotation) -> None:
        self._annotations[annotation.id] = annotation

    def add_citation(self, citation: Citation) -> None:
        self._citations[citation.id] = citation

    def get_bookmarks_for_item(self, item_id: str) -> list[Bookmark]:
        return [b for b in self._bookmarks.values() if b.item_id == item_id]

    def get_annotations_for_item(self, item_id: str) -> list[Annotation]:
        return [a for a in self._annotations.values() if a.item_id == item_id]

    def get_citations_for_item(self, item_id: str) -> list[Citation]:
        return [c for c in self._citations.values() if c.source_item_id == item_id or c.target_item_id == item_id]


class InMemoryResearchRepository(ResearchRepository):
    def __init__(self) -> None:
        self._projects: dict[str, ResearchProject] = {}
        self._literature: dict[str, LiteratureEntry] = {}
        self._notes: dict[str, ResearchNote] = {}
        self._knowledge_maps: dict[str, KnowledgeMap] = {}
        self._reading_lists: dict[str, ReadingList] = {}
        self._bibliographies: dict[str, Bibliography] = {}

    def add_project(self, project: ResearchProject) -> None:
        self._projects[project.id] = project

    def get_project(self, project_id: str) -> ResearchProject | None:
        return self._projects.get(project_id)

    def update_project(self, project: ResearchProject) -> None:
        self._projects[project.id] = project

    def remove_project(self, project_id: str) -> None:
        self._projects.pop(project_id, None)

    def all_projects(self) -> list[ResearchProject]:
        return list(self._projects.values())

    def add_literature_entry(self, entry: LiteratureEntry) -> None:
        self._literature[entry.id] = entry

    def get_literature_entry(self, entry_id: str) -> LiteratureEntry | None:
        return self._literature.get(entry_id)

    def update_literature_entry(self, entry: LiteratureEntry) -> None:
        self._literature[entry.id] = entry

    def remove_literature_entry(self, entry_id: str) -> None:
        self._literature.pop(entry_id, None)

    def get_literature_for_project(self, project_id: str) -> list[LiteratureEntry]:
        return [e for e in self._literature.values() if e.project_id == project_id]

    def add_note(self, note: ResearchNote) -> None:
        self._notes[note.id] = note

    def get_notes_for_entry(self, entry_id: str) -> list[ResearchNote]:
        return [n for n in self._notes.values() if n.entry_id == entry_id]

    def add_knowledge_map(self, km: KnowledgeMap) -> None:
        self._knowledge_maps[km.id] = km

    def get_knowledge_map(self, map_id: str) -> KnowledgeMap | None:
        return self._knowledge_maps.get(map_id)

    def get_knowledge_maps_for_project(self, project_id: str) -> list[KnowledgeMap]:
        return [km for km in self._knowledge_maps.values() if km.project_id == project_id]

    def add_reading_list(self, rl: ReadingList) -> None:
        self._reading_lists[rl.id] = rl

    def get_reading_lists_for_project(self, project_id: str) -> list[ReadingList]:
        return [rl for rl in self._reading_lists.values() if rl.project_id == project_id]

    def add_bibliography(self, bib: Bibliography) -> None:
        self._bibliographies[bib.id] = bib

    def get_bibliographies_for_project(self, project_id: str) -> list[Bibliography]:
        return [b for b in self._bibliographies.values() if b.project_id == project_id]


class InMemoryInstitutionRepository(InstitutionRepository):
    def __init__(self) -> None:
        self._orgs: dict[str, Organization] = {}
        self._departments: dict[str, Department] = {}
        self._programs: dict[str, AcademicProgram] = {}
        self._assignments: dict[str, InstructorAssignment] = {}
        self._allocations: dict[str, ResourceAllocation] = {}

    def add_organization(self, org: Organization) -> None:
        self._orgs[org.id] = org

    def get_organization(self, org_id: str) -> Organization | None:
        return self._orgs.get(org_id)

    def update_organization(self, org: Organization) -> None:
        self._orgs[org.id] = org

    def remove_organization(self, org_id: str) -> None:
        self._orgs.pop(org_id, None)

    def all_organizations(self) -> list[Organization]:
        return list(self._orgs.values())

    def add_department(self, dept: Department) -> None:
        self._departments[dept.id] = dept

    def get_department(self, dept_id: str) -> Department | None:
        return self._departments.get(dept_id)

    def update_department(self, dept: Department) -> None:
        self._departments[dept.id] = dept

    def remove_department(self, dept_id: str) -> None:
        self._departments.pop(dept_id, None)

    def get_departments_for_org(self, org_id: str) -> list[Department]:
        return [d for d in self._departments.values() if d.org_id == org_id]

    def add_program(self, prog: AcademicProgram) -> None:
        self._programs[prog.id] = prog

    def get_program(self, prog_id: str) -> AcademicProgram | None:
        return self._programs.get(prog_id)

    def update_program(self, prog: AcademicProgram) -> None:
        self._programs[prog.id] = prog

    def get_programs_for_department(self, dept_id: str) -> list[AcademicProgram]:
        return [p for p in self._programs.values() if p.department_id == dept_id]

    def add_assignment(self, assignment: InstructorAssignment) -> None:
        self._assignments[assignment.id] = assignment

    def get_assignments_for_instructor(self, instructor_id: str) -> list[InstructorAssignment]:
        return [a for a in self._assignments.values() if a.instructor_id == instructor_id]

    def add_allocation(self, allocation: ResourceAllocation) -> None:
        self._allocations[allocation.id] = allocation

    def get_allocations_for_org(self, org_id: str) -> list[ResourceAllocation]:
        return [a for a in self._allocations.values()]


class InMemoryDistributionRepository(DistributionRepository):
    def __init__(self) -> None:
        self._packages: dict[str, DistributionPackage] = {}
        self._manifests: dict[str, DistributionManifest] = {}
        self._imports: dict[str, ImportRecord] = {}
        self._sync_ops: dict[str, SyncOperation] = {}

    def add_package(self, pkg: DistributionPackage) -> None:
        self._packages[pkg.id] = pkg

    def get_package(self, package_id: str) -> DistributionPackage | None:
        return self._packages.get(package_id)

    def update_package(self, pkg: DistributionPackage) -> None:
        self._packages[pkg.id] = pkg

    def all_packages(self) -> list[DistributionPackage]:
        return list(self._packages.values())

    def add_manifest(self, manifest: DistributionManifest) -> None:
        self._manifests[manifest.id] = manifest

    def get_manifest_for_package(self, package_id: str) -> DistributionManifest | None:
        for m in self._manifests.values():
            if m.package_id == package_id:
                return m
        return None

    def add_import_record(self, record: ImportRecord) -> None:
        self._imports[record.id] = record

    def get_import_records(self) -> list[ImportRecord]:
        return list(self._imports.values())

    def add_sync_operation(self, op: SyncOperation) -> None:
        self._sync_ops[op.id] = op

    def get_sync_operations(self) -> list[SyncOperation]:
        return list(self._sync_ops.values())
