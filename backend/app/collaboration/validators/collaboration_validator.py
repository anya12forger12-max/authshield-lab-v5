"""Collaboration validators for projects, packages, reviews, and knowledge base."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..domain.entities.academic_hub import InstitutionalProject, SharedCurriculumPackage
    from ..domain.entities.curriculum_exchange import ExchangePackage
    from ..domain.entities.peer_review import PeerReview
    from ..domain.entities.knowledge_base import KnowledgeArticle


class CollaborationValidator:
    _NAME_PATTERN = re.compile(r"^[a-zA-Z0-9\s_\-\.]{1,255}$")
    _SEMVER_PATTERN = re.compile(
        r"^\d+\.\d+\.\d+(-[a-z0-9]+(\.[a-z0-9]+)*)?(\+[a-z0-9]+)?$"
    )
    _VALID_PROJECT_STATUSES = {"active", "paused", "completed"}
    _VALID_REVIEW_STATUSES = {"draft", "in_review", "approved", "rejected"}
    _VALID_CONTENT_TYPES = {
        "course", "lesson", "module", "assessment", "simulation",
        "documentation", "template", "learning_path",
    }

    def validate_project_name(self, name: str) -> bool:
        return bool(name and self._NAME_PATTERN.match(name))

    def validate_semver(self, version: str) -> bool:
        return bool(version and self._SEMVER_PATTERN.match(version))

    def validate_institutional_project(self, project: InstitutionalProject) -> list[str]:
        errors: list[str] = []
        if not self.validate_project_name(project.name):
            errors.append(f"Invalid project name: {project.name}")
        if not project.description:
            errors.append("Description is required")
        if not project.department:
            errors.append("Department is required")
        if not project.lead:
            errors.append("Lead is required")
        if project.status.value not in self._VALID_PROJECT_STATUSES:
            errors.append(f"Invalid status: {project.status}")
        if len(project.members) > 200:
            errors.append("Too many members (max 200)")
        return errors

    def validate_shared_curriculum_package(self, pkg: SharedCurriculumPackage) -> list[str]:
        errors: list[str] = []
        if not pkg.title:
            errors.append("Title is required")
        if not pkg.source_institution:
            errors.append("Source institution is required")
        if not self.validate_semver(pkg.version):
            errors.append(f"Invalid semver: {pkg.version}")
        if not pkg.content_type:
            errors.append("Content type is required")
        if not pkg.checksum:
            errors.append("Checksum is required")
        if len(pkg.checksum) < 32:
            errors.append("Checksum too short (min 32 chars)")
        if not pkg.signature:
            errors.append("Signature is required")
        return errors

    def validate_exchange_package(self, pkg: ExchangePackage) -> list[str]:
        errors: list[str] = []
        if not pkg.name:
            errors.append("Package name is required")
        if not self.validate_semver(pkg.version):
            errors.append(f"Invalid semver: {pkg.version}")
        if not pkg.author:
            errors.append("Author is required")
        if not pkg.source_institution:
            errors.append("Source institution is required")
        if not pkg.checksum:
            errors.append("Checksum is required")
        if len(pkg.checksum) < 32:
            errors.append("Checksum too short (min 32 chars)")
        if not pkg.signature:
            errors.append("Signature is required")
        if not pkg.license:
            errors.append("License is required")
        if not pkg.compatibility:
            errors.append("Compatibility is required")
        if len(pkg.dependencies) > 50:
            errors.append("Too many dependencies (max 50)")
        return errors

    def validate_peer_review(self, review: PeerReview) -> list[str]:
        errors: list[str] = []
        if not review.title:
            errors.append("Title is required")
        if not review.content_id:
            errors.append("Content ID is required")
        if not review.content_type:
            errors.append("Content type is required")
        if review.content_type not in self._VALID_CONTENT_TYPES:
            errors.append(f"Invalid content type: {review.content_type}")
        if not review.submitter:
            errors.append("Submitter is required")
        return errors

    def validate_knowledge_article(self, article: KnowledgeArticle) -> list[str]:
        errors: list[str] = []
        if not article.title:
            errors.append("Title is required")
        if len(article.title) > 500:
            errors.append("Title too long (max 500 chars)")
        if not article.content:
            errors.append("Content is required")
        if not article.category:
            errors.append("Category is required")
        if not article.author:
            errors.append("Author is required")
        if len(article.tags) > 30:
            errors.append("Too many tags (max 30)")
        if article.version < 1:
            errors.append("Version must be >= 1")
        return errors

    def validate_review_request(self, title: str, request_type: str, submitter: str) -> list[str]:
        errors: list[str] = []
        if not title:
            errors.append("Title is required")
        if not request_type:
            errors.append("Request type is required")
        if not submitter:
            errors.append("Submitter is required")
        return errors

    def validate_publication_item(
        self,
        content_id: str,
        content_type: str,
        title: str,
        version: str,
        submitted_by: str,
    ) -> list[str]:
        errors: list[str] = []
        if not content_id:
            errors.append("Content ID is required")
        if not content_type:
            errors.append("Content type is required")
        if not title:
            errors.append("Title is required")
        if not self.validate_semver(version):
            errors.append(f"Invalid semver: {version}")
        if not submitted_by:
            errors.append("Submitted by is required")
        return errors

    def validate_search_query(self, query: str) -> bool:
        return bool(query and len(query.strip()) >= 2 and len(query) <= 500)

    def validate_category_name(self, name: str) -> bool:
        return bool(name and len(name) <= 255 and self._NAME_PATTERN.match(name))
