"""Repository interfaces for the ecosystem module."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.marketplace import LocalPackage, InstallationRecord, PackageSearch
    from ...domain.entities.library import LibraryItem, Bookmark, Annotation, Citation
    from ...domain.entities.research import ResearchProject, LiteratureEntry, ResearchNote, KnowledgeMap, ReadingList, Bibliography
    from ...domain.entities.institution import Organization, Department, AcademicProgram, InstructorAssignment, ResourceAllocation
    from ...domain.entities.content_distribution import DistributionPackage, DistributionManifest, ImportRecord, SyncOperation


class MarketplaceRepository(ABC):
    @abstractmethod
    def add_package(self, package: LocalPackage) -> None: ...

    @abstractmethod
    def get_package(self, package_id: str) -> LocalPackage | None: ...

    @abstractmethod
    def find_by_name(self, name: str) -> list[LocalPackage]: ...

    @abstractmethod
    def search(self, search: PackageSearch) -> list[LocalPackage]: ...

    @abstractmethod
    def update_package(self, package: LocalPackage) -> None: ...

    @abstractmethod
    def remove_package(self, package_id: str) -> None: ...

    @abstractmethod
    def all_packages(self) -> list[LocalPackage]: ...

    @abstractmethod
    def add_installation(self, record: InstallationRecord) -> None: ...

    @abstractmethod
    def get_installation(self, record_id: str) -> InstallationRecord | None: ...

    @abstractmethod
    def find_installations_by_package(self, package_id: str) -> list[InstallationRecord]: ...


class LibraryRepository(ABC):
    @abstractmethod
    def add_item(self, item: LibraryItem) -> None: ...

    @abstractmethod
    def get_item(self, item_id: str) -> LibraryItem | None: ...

    @abstractmethod
    def search_items(self, query: str = "", item_type: str = "", tag: str = "") -> list[LibraryItem]: ...

    @abstractmethod
    def update_item(self, item: LibraryItem) -> None: ...

    @abstractmethod
    def remove_item(self, item_id: str) -> None: ...

    @abstractmethod
    def all_items(self) -> list[LibraryItem]: ...

    @abstractmethod
    def add_bookmark(self, bookmark: Bookmark) -> None: ...

    @abstractmethod
    def add_annotation(self, annotation: Annotation) -> None: ...

    @abstractmethod
    def add_citation(self, citation: Citation) -> None: ...

    @abstractmethod
    def get_bookmarks_for_item(self, item_id: str) -> list[Bookmark]: ...

    @abstractmethod
    def get_annotations_for_item(self, item_id: str) -> list[Annotation]: ...

    @abstractmethod
    def get_citations_for_item(self, item_id: str) -> list[Citation]: ...


class ResearchRepository(ABC):
    @abstractmethod
    def add_project(self, project: ResearchProject) -> None: ...

    @abstractmethod
    def get_project(self, project_id: str) -> ResearchProject | None: ...

    @abstractmethod
    def update_project(self, project: ResearchProject) -> None: ...

    @abstractmethod
    def remove_project(self, project_id: str) -> None: ...

    @abstractmethod
    def all_projects(self) -> list[ResearchProject]: ...

    @abstractmethod
    def add_literature_entry(self, entry: LiteratureEntry) -> None: ...

    @abstractmethod
    def get_literature_entry(self, entry_id: str) -> LiteratureEntry | None: ...

    @abstractmethod
    def update_literature_entry(self, entry: LiteratureEntry) -> None: ...

    @abstractmethod
    def remove_literature_entry(self, entry_id: str) -> None: ...

    @abstractmethod
    def get_literature_for_project(self, project_id: str) -> list[LiteratureEntry]: ...

    @abstractmethod
    def add_note(self, note: ResearchNote) -> None: ...

    @abstractmethod
    def get_notes_for_entry(self, entry_id: str) -> list[ResearchNote]: ...

    @abstractmethod
    def add_knowledge_map(self, km: KnowledgeMap) -> None: ...

    @abstractmethod
    def get_knowledge_map(self, map_id: str) -> KnowledgeMap | None: ...

    @abstractmethod
    def get_knowledge_maps_for_project(self, project_id: str) -> list[KnowledgeMap]: ...

    @abstractmethod
    def add_reading_list(self, rl: ReadingList) -> None: ...

    @abstractmethod
    def get_reading_lists_for_project(self, project_id: str) -> list[ReadingList]: ...

    @abstractmethod
    def add_bibliography(self, bib: Bibliography) -> None: ...

    @abstractmethod
    def get_bibliographies_for_project(self, project_id: str) -> list[Bibliography]: ...


class InstitutionRepository(ABC):
    @abstractmethod
    def add_organization(self, org: Organization) -> None: ...

    @abstractmethod
    def get_organization(self, org_id: str) -> Organization | None: ...

    @abstractmethod
    def update_organization(self, org: Organization) -> None: ...

    @abstractmethod
    def remove_organization(self, org_id: str) -> None: ...

    @abstractmethod
    def all_organizations(self) -> list[Organization]: ...

    @abstractmethod
    def add_department(self, dept: Department) -> None: ...

    @abstractmethod
    def get_department(self, dept_id: str) -> Department | None: ...

    @abstractmethod
    def update_department(self, dept: Department) -> None: ...

    @abstractmethod
    def remove_department(self, dept_id: str) -> None: ...

    @abstractmethod
    def get_departments_for_org(self, org_id: str) -> list[Department]: ...

    @abstractmethod
    def add_program(self, prog: AcademicProgram) -> None: ...

    @abstractmethod
    def get_program(self, prog_id: str) -> AcademicProgram | None: ...

    @abstractmethod
    def update_program(self, prog: AcademicProgram) -> None: ...

    @abstractmethod
    def get_programs_for_department(self, dept_id: str) -> list[AcademicProgram]: ...

    @abstractmethod
    def add_assignment(self, assignment: InstructorAssignment) -> None: ...

    @abstractmethod
    def get_assignments_for_instructor(self, instructor_id: str) -> list[InstructorAssignment]: ...

    @abstractmethod
    def add_allocation(self, allocation: ResourceAllocation) -> None: ...

    @abstractmethod
    def get_allocations_for_org(self, org_id: str) -> list[ResourceAllocation]: ...


class DistributionRepository(ABC):
    @abstractmethod
    def add_package(self, pkg: DistributionPackage) -> None: ...

    @abstractmethod
    def get_package(self, package_id: str) -> DistributionPackage | None: ...

    @abstractmethod
    def update_package(self, pkg: DistributionPackage) -> None: ...

    @abstractmethod
    def all_packages(self) -> list[DistributionPackage]: ...

    @abstractmethod
    def add_manifest(self, manifest: DistributionManifest) -> None: ...

    @abstractmethod
    def get_manifest_for_package(self, package_id: str) -> DistributionManifest | None: ...

    @abstractmethod
    def add_import_record(self, record: ImportRecord) -> None: ...

    @abstractmethod
    def get_import_records(self) -> list[ImportRecord]: ...

    @abstractmethod
    def add_sync_operation(self, op: SyncOperation) -> None: ...

    @abstractmethod
    def get_sync_operations(self) -> list[SyncOperation]: ...
