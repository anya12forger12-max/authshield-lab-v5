"""In-memory implementations of collaboration repositories for offline/local use."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..domain.interfaces import (
    AcademicHubRepository,
    CurriculumExchangeRepository,
    ResearchWorkspaceRepository,
    PeerReviewRepository,
    KnowledgeBaseRepository,
)

if TYPE_CHECKING:
    from ..domain.entities.academic_hub import (
        InstitutionalProject,
        SharedCurriculumPackage,
        ImportedResource,
        ReviewRequest,
        PublicationQueueItem,
        VersionHistory,
    )
    from ..domain.entities.curriculum_exchange import (
        ExchangePackage,
        ExchangeManifest,
        PackageValidationReport,
        ExchangeHistory,
    )
    from ..domain.entities.research_workspace import (
        ResearchProject,
        LiteratureCollection,
        LiteratureEntry,
        ResearchNote,
        Citation,
        KnowledgeMap,
        ReadingList,
        Bibliography,
    )
    from ..domain.entities.peer_review import (
        PeerReview,
        ReviewComment,
        ReviewDecision,
        ReviewRevision,
        ReviewHistory,
    )
    from ..domain.entities.knowledge_base import (
        KnowledgeArticle,
        KnowledgeCategory,
        ArticleVersion,
        ArticleCitation,
    )


class InMemoryAcademicHubRepository(AcademicHubRepository):
    def __init__(self) -> None:
        self._projects: dict[str, InstitutionalProject] = {}
        self._shared_packages: dict[str, SharedCurriculumPackage] = {}
        self._imported_resources: dict[str, ImportedResource] = {}
        self._review_requests: dict[str, ReviewRequest] = {}
        self._publication_items: dict[str, PublicationQueueItem] = {}
        self._version_history: dict[str, list[VersionHistory]] = {}

    def add_project(self, project: InstitutionalProject) -> None:
        self._projects[project.id] = project

    def get_project(self, project_id: str) -> InstitutionalProject | None:
        return self._projects.get(project_id)

    def update_project(self, project: InstitutionalProject) -> None:
        self._projects[project.id] = project

    def remove_project(self, project_id: str) -> None:
        self._projects.pop(project_id, None)

    def all_projects(self) -> list[InstitutionalProject]:
        return list(self._projects.values())

    def add_shared_package(self, package: SharedCurriculumPackage) -> None:
        self._shared_packages[package.id] = package

    def get_shared_package(self, package_id: str) -> SharedCurriculumPackage | None:
        return self._shared_packages.get(package_id)

    def all_shared_packages(self) -> list[SharedCurriculumPackage]:
        return list(self._shared_packages.values())

    def add_imported_resource(self, resource: ImportedResource) -> None:
        self._imported_resources[resource.id] = resource

    def get_imported_resource(self, resource_id: str) -> ImportedResource | None:
        return self._imported_resources.get(resource_id)

    def all_imported_resources(self) -> list[ImportedResource]:
        return list(self._imported_resources.values())

    def add_review_request(self, request: ReviewRequest) -> None:
        self._review_requests[request.id] = request

    def get_review_request(self, request_id: str) -> ReviewRequest | None:
        return self._review_requests.get(request_id)

    def update_review_request(self, request: ReviewRequest) -> None:
        self._review_requests[request.id] = request

    def all_review_requests(self) -> list[ReviewRequest]:
        return list(self._review_requests.values())

    def add_publication_item(self, item: PublicationQueueItem) -> None:
        self._publication_items[item.id] = item

    def get_publication_item(self, item_id: str) -> PublicationQueueItem | None:
        return self._publication_items.get(item_id)

    def update_publication_item(self, item: PublicationQueueItem) -> None:
        self._publication_items[item.id] = item

    def all_publication_items(self) -> list[PublicationQueueItem]:
        return list(self._publication_items.values())

    def add_version_history(self, entry: VersionHistory) -> None:
        history = self._version_history.setdefault(entry.entity_id, [])
        history.append(entry)

    def get_version_history_for_entity(self, entity_id: str) -> list[VersionHistory]:
        return list(self._version_history.get(entity_id, []))


class InMemoryCurriculumExchangeRepository(CurriculumExchangeRepository):
    def __init__(self) -> None:
        self._packages: dict[str, ExchangePackage] = {}
        self._manifests: dict[str, ExchangeManifest] = {}
        self._validation_reports: dict[str, PackageValidationReport] = {}
        self._history: dict[str, list[ExchangeHistory]] = {}

    def add_package(self, package: ExchangePackage) -> None:
        self._packages[package.id] = package

    def get_package(self, package_id: str) -> ExchangePackage | None:
        return self._packages.get(package_id)

    def update_package(self, package: ExchangePackage) -> None:
        self._packages[package.id] = package

    def remove_package(self, package_id: str) -> None:
        self._packages.pop(package_id, None)

    def all_packages(self) -> list[ExchangePackage]:
        return list(self._packages.values())

    def add_manifest(self, manifest: ExchangeManifest) -> None:
        self._manifests[manifest.id] = manifest

    def get_manifest_for_package(self, package_id: str) -> ExchangeManifest | None:
        for m in self._manifests.values():
            if m.package_id == package_id:
                return m
        return None

    def add_validation_report(self, report: PackageValidationReport) -> None:
        self._validation_reports[report.id] = report

    def get_validation_report(self, report_id: str) -> PackageValidationReport | None:
        return self._validation_reports.get(report_id)

    def get_validation_reports_for_package(self, package_id: str) -> list[PackageValidationReport]:
        return [r for r in self._validation_reports.values() if r.package_id == package_id]

    def add_history(self, entry: ExchangeHistory) -> None:
        history = self._history.setdefault(entry.package_id, [])
        history.append(entry)

    def get_history_for_package(self, package_id: str) -> list[ExchangeHistory]:
        return list(self._history.get(package_id, []))


class InMemoryResearchWorkspaceRepository(ResearchWorkspaceRepository):
    def __init__(self) -> None:
        self._projects: dict[str, ResearchProject] = {}
        self._collections: dict[str, LiteratureCollection] = {}
        self._entries: dict[str, LiteratureEntry] = {}
        self._notes: dict[str, list[ResearchNote]] = {}
        self._citations: dict[str, list[Citation]] = {}
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

    def add_literature_collection(self, collection: LiteratureCollection) -> None:
        self._collections[collection.id] = collection

    def get_literature_collection(self, collection_id: str) -> LiteratureCollection | None:
        return self._collections.get(collection_id)

    def update_literature_collection(self, collection: LiteratureCollection) -> None:
        self._collections[collection.id] = collection

    def get_literature_collections_for_project(self, project_id: str) -> list[LiteratureCollection]:
        return [c for c in self._collections.values() if c.project_id == project_id]

    def add_literature_entry(self, entry: LiteratureEntry) -> None:
        self._entries[entry.id] = entry

    def get_literature_entry(self, entry_id: str) -> LiteratureEntry | None:
        return self._entries.get(entry_id)

    def update_literature_entry(self, entry: LiteratureEntry) -> None:
        self._entries[entry.id] = entry

    def remove_literature_entry(self, entry_id: str) -> None:
        self._entries.pop(entry_id, None)

    def add_note(self, note: ResearchNote) -> None:
        notes = self._notes.setdefault(note.entry_id, [])
        notes.append(note)

    def get_notes_for_entry(self, entry_id: str) -> list[ResearchNote]:
        return list(self._notes.get(entry_id, []))

    def add_citation(self, citation: Citation) -> None:
        citations = self._citations.setdefault(citation.source_id, [])
        citations.append(citation)

    def get_citations_for_entry(self, entry_id: str) -> list[Citation]:
        return list(self._citations.get(entry_id, []))

    def add_knowledge_map(self, km: KnowledgeMap) -> None:
        self._knowledge_maps[km.id] = km

    def get_knowledge_map(self, map_id: str) -> KnowledgeMap | None:
        return self._knowledge_maps.get(map_id)

    def update_knowledge_map(self, km: KnowledgeMap) -> None:
        self._knowledge_maps[km.id] = km

    def get_knowledge_maps_for_project(self, project_id: str) -> list[KnowledgeMap]:
        return [km for km in self._knowledge_maps.values() if km.project_id == project_id]

    def add_reading_list(self, rl: ReadingList) -> None:
        self._reading_lists[rl.id] = rl

    def get_reading_lists_for_project(self, project_id: str) -> list[ReadingList]:
        return [r for r in self._reading_lists.values() if r.project_id == project_id]

    def add_bibliography(self, bib: Bibliography) -> None:
        self._bibliographies[bib.id] = bib

    def get_bibliographies_for_project(self, project_id: str) -> list[Bibliography]:
        return [b for b in self._bibliographies.values() if b.project_id == project_id]


class InMemoryPeerReviewRepository(PeerReviewRepository):
    def __init__(self) -> None:
        self._reviews: dict[str, PeerReview] = {}
        self._comments: dict[str, list[ReviewComment]] = {}
        self._decisions: dict[str, list[ReviewDecision]] = {}
        self._revisions: dict[str, list[ReviewRevision]] = {}
        self._histories: dict[str, ReviewHistory] = {}

    def add_review(self, review: PeerReview) -> None:
        self._reviews[review.id] = review

    def get_review(self, review_id: str) -> PeerReview | None:
        return self._reviews.get(review_id)

    def update_review(self, review: PeerReview) -> None:
        self._reviews[review.id] = review

    def remove_review(self, review_id: str) -> None:
        self._reviews.pop(review_id, None)

    def all_reviews(self) -> list[PeerReview]:
        return list(self._reviews.values())

    def add_comment(self, comment: ReviewComment) -> None:
        comments = self._comments.setdefault(comment.review_id, [])
        comments.append(comment)

    def get_comments_for_review(self, review_id: str) -> list[ReviewComment]:
        return list(self._comments.get(review_id, []))

    def add_decision(self, decision: ReviewDecision) -> None:
        decisions = self._decisions.setdefault(decision.review_id, [])
        decisions.append(decision)

    def get_decisions_for_review(self, review_id: str) -> list[ReviewDecision]:
        return list(self._decisions.get(review_id, []))

    def add_revision(self, revision: ReviewRevision) -> None:
        revisions = self._revisions.setdefault(revision.review_id, [])
        revisions.append(revision)

    def get_revisions_for_review(self, review_id: str) -> list[ReviewRevision]:
        return list(self._revisions.get(review_id, []))

    def add_history(self, history: ReviewHistory) -> None:
        self._histories[history.review_id] = history

    def get_history_for_review(self, review_id: str) -> ReviewHistory | None:
        return self._histories.get(review_id)

    def update_history(self, history: ReviewHistory) -> None:
        self._histories[history.review_id] = history


class InMemoryKnowledgeBaseRepository(KnowledgeBaseRepository):
    def __init__(self) -> None:
        self._articles: dict[str, KnowledgeArticle] = {}
        self._categories: dict[str, KnowledgeCategory] = {}
        self._versions: dict[str, list[ArticleVersion]] = {}
        self._citations: dict[str, list[ArticleCitation]] = {}

    def add_article(self, article: KnowledgeArticle) -> None:
        self._articles[article.id] = article

    def get_article(self, article_id: str) -> KnowledgeArticle | None:
        return self._articles.get(article_id)

    def update_article(self, article: KnowledgeArticle) -> None:
        self._articles[article.id] = article

    def remove_article(self, article_id: str) -> None:
        self._articles.pop(article_id, None)

    def all_articles(self) -> list[KnowledgeArticle]:
        return list(self._articles.values())

    def add_category(self, category: KnowledgeCategory) -> None:
        self._categories[category.id] = category

    def get_category(self, category_id: str) -> KnowledgeCategory | None:
        return self._categories.get(category_id)

    def update_category(self, category: KnowledgeCategory) -> None:
        self._categories[category.id] = category

    def remove_category(self, category_id: str) -> None:
        self._categories.pop(category_id, None)

    def all_categories(self) -> list[KnowledgeCategory]:
        return list(self._categories.values())

    def add_version(self, version: ArticleVersion) -> None:
        versions = self._versions.setdefault(version.article_id, [])
        versions.append(version)

    def get_versions_for_article(self, article_id: str) -> list[ArticleVersion]:
        return list(self._versions.get(article_id, []))

    def add_citation(self, citation: ArticleCitation) -> None:
        citations = self._citations.setdefault(citation.source_id, [])
        citations.append(citation)

    def get_citations_for_article(self, article_id: str) -> list[ArticleCitation]:
        return list(self._citations.get(article_id, []))
