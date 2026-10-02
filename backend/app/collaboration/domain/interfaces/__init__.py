"""Repository interfaces for the collaboration module."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.academic_hub import (
        InstitutionalProject,
        SharedCurriculumPackage,
        ImportedResource,
        ReviewRequest,
        PublicationQueueItem,
        VersionHistory,
    )
    from ...domain.entities.curriculum_exchange import (
        ExchangePackage,
        ExchangeManifest,
        PackageValidationReport,
        ExchangeHistory,
    )
    from ...domain.entities.research_workspace import (
        ResearchProject,
        LiteratureCollection,
        LiteratureEntry,
        ResearchNote,
        Citation,
        KnowledgeMap,
        ReadingList,
        Bibliography,
    )
    from ...domain.entities.peer_review import (
        PeerReview,
        ReviewComment,
        ReviewDecision,
        ReviewRevision,
        ReviewHistory,
    )
    from ...domain.entities.knowledge_base import (
        KnowledgeArticle,
        KnowledgeCategory,
        ArticleVersion,
        ArticleCitation,
    )


class AcademicHubRepository(ABC):
    @abstractmethod
    def add_project(self, project: InstitutionalProject) -> None: ...

    @abstractmethod
    def get_project(self, project_id: str) -> InstitutionalProject | None: ...

    @abstractmethod
    def update_project(self, project: InstitutionalProject) -> None: ...

    @abstractmethod
    def remove_project(self, project_id: str) -> None: ...

    @abstractmethod
    def all_projects(self) -> list[InstitutionalProject]: ...

    @abstractmethod
    def add_shared_package(self, package: SharedCurriculumPackage) -> None: ...

    @abstractmethod
    def get_shared_package(self, package_id: str) -> SharedCurriculumPackage | None: ...

    @abstractmethod
    def all_shared_packages(self) -> list[SharedCurriculumPackage]: ...

    @abstractmethod
    def add_imported_resource(self, resource: ImportedResource) -> None: ...

    @abstractmethod
    def get_imported_resource(self, resource_id: str) -> ImportedResource | None: ...

    @abstractmethod
    def all_imported_resources(self) -> list[ImportedResource]: ...

    @abstractmethod
    def add_review_request(self, request: ReviewRequest) -> None: ...

    @abstractmethod
    def get_review_request(self, request_id: str) -> ReviewRequest | None: ...

    @abstractmethod
    def update_review_request(self, request: ReviewRequest) -> None: ...

    @abstractmethod
    def all_review_requests(self) -> list[ReviewRequest]: ...

    @abstractmethod
    def add_publication_item(self, item: PublicationQueueItem) -> None: ...

    @abstractmethod
    def get_publication_item(self, item_id: str) -> PublicationQueueItem | None: ...

    @abstractmethod
    def update_publication_item(self, item: PublicationQueueItem) -> None: ...

    @abstractmethod
    def all_publication_items(self) -> list[PublicationQueueItem]: ...

    @abstractmethod
    def add_version_history(self, entry: VersionHistory) -> None: ...

    @abstractmethod
    def get_version_history_for_entity(self, entity_id: str) -> list[VersionHistory]: ...


class CurriculumExchangeRepository(ABC):
    @abstractmethod
    def add_package(self, package: ExchangePackage) -> None: ...

    @abstractmethod
    def get_package(self, package_id: str) -> ExchangePackage | None: ...

    @abstractmethod
    def update_package(self, package: ExchangePackage) -> None: ...

    @abstractmethod
    def remove_package(self, package_id: str) -> None: ...

    @abstractmethod
    def all_packages(self) -> list[ExchangePackage]: ...

    @abstractmethod
    def add_manifest(self, manifest: ExchangeManifest) -> None: ...

    @abstractmethod
    def get_manifest_for_package(self, package_id: str) -> ExchangeManifest | None: ...

    @abstractmethod
    def add_validation_report(self, report: PackageValidationReport) -> None: ...

    @abstractmethod
    def get_validation_report(self, report_id: str) -> PackageValidationReport | None: ...

    @abstractmethod
    def get_validation_reports_for_package(self, package_id: str) -> list[PackageValidationReport]: ...

    @abstractmethod
    def add_history(self, entry: ExchangeHistory) -> None: ...

    @abstractmethod
    def get_history_for_package(self, package_id: str) -> list[ExchangeHistory]: ...


class ResearchWorkspaceRepository(ABC):
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
    def add_literature_collection(self, collection: LiteratureCollection) -> None: ...

    @abstractmethod
    def get_literature_collection(self, collection_id: str) -> LiteratureCollection | None: ...

    @abstractmethod
    def update_literature_collection(self, collection: LiteratureCollection) -> None: ...

    @abstractmethod
    def get_literature_collections_for_project(self, project_id: str) -> list[LiteratureCollection]: ...

    @abstractmethod
    def add_literature_entry(self, entry: LiteratureEntry) -> None: ...

    @abstractmethod
    def get_literature_entry(self, entry_id: str) -> LiteratureEntry | None: ...

    @abstractmethod
    def update_literature_entry(self, entry: LiteratureEntry) -> None: ...

    @abstractmethod
    def remove_literature_entry(self, entry_id: str) -> None: ...

    @abstractmethod
    def add_note(self, note: ResearchNote) -> None: ...

    @abstractmethod
    def get_notes_for_entry(self, entry_id: str) -> list[ResearchNote]: ...

    @abstractmethod
    def add_citation(self, citation: Citation) -> None: ...

    @abstractmethod
    def get_citations_for_entry(self, entry_id: str) -> list[Citation]: ...

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


class PeerReviewRepository(ABC):
    @abstractmethod
    def add_review(self, review: PeerReview) -> None: ...

    @abstractmethod
    def get_review(self, review_id: str) -> PeerReview | None: ...

    @abstractmethod
    def update_review(self, review: PeerReview) -> None: ...

    @abstractmethod
    def remove_review(self, review_id: str) -> None: ...

    @abstractmethod
    def all_reviews(self) -> list[PeerReview]: ...

    @abstractmethod
    def add_comment(self, comment: ReviewComment) -> None: ...

    @abstractmethod
    def get_comments_for_review(self, review_id: str) -> list[ReviewComment]: ...

    @abstractmethod
    def add_decision(self, decision: ReviewDecision) -> None: ...

    @abstractmethod
    def get_decisions_for_review(self, review_id: str) -> list[ReviewDecision]: ...

    @abstractmethod
    def add_revision(self, revision: ReviewRevision) -> None: ...

    @abstractmethod
    def get_revisions_for_review(self, review_id: str) -> list[ReviewRevision]: ...

    @abstractmethod
    def add_history(self, history: ReviewHistory) -> None: ...

    @abstractmethod
    def get_history_for_review(self, review_id: str) -> ReviewHistory | None: ...

    @abstractmethod
    def update_history(self, history: ReviewHistory) -> None: ...


class KnowledgeBaseRepository(ABC):
    @abstractmethod
    def add_article(self, article: KnowledgeArticle) -> None: ...

    @abstractmethod
    def get_article(self, article_id: str) -> KnowledgeArticle | None: ...

    @abstractmethod
    def update_article(self, article: KnowledgeArticle) -> None: ...

    @abstractmethod
    def remove_article(self, article_id: str) -> None: ...

    @abstractmethod
    def all_articles(self) -> list[KnowledgeArticle]: ...

    @abstractmethod
    def add_category(self, category: KnowledgeCategory) -> None: ...

    @abstractmethod
    def get_category(self, category_id: str) -> KnowledgeCategory | None: ...

    @abstractmethod
    def update_category(self, category: KnowledgeCategory) -> None: ...

    @abstractmethod
    def remove_category(self, category_id: str) -> None: ...

    @abstractmethod
    def all_categories(self) -> list[KnowledgeCategory]: ...

    @abstractmethod
    def add_version(self, version: ArticleVersion) -> None: ...

    @abstractmethod
    def get_versions_for_article(self, article_id: str) -> list[ArticleVersion]: ...

    @abstractmethod
    def add_citation(self, citation: ArticleCitation) -> None: ...

    @abstractmethod
    def get_citations_for_article(self, article_id: str) -> list[ArticleCitation]: ...
