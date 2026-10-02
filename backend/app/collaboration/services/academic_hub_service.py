"""Academic hub service – projects, packages, reviews, publications, dashboard."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..domain.interfaces import AcademicHubRepository
    from ..domain.entities.academic_hub import (
        InstitutionalProject,
        SharedCurriculumPackage,
        ImportedResource,
        ReviewRequest,
        PublicationQueueItem,
        VersionHistory,
        AcademicHubDashboard,
    )


class AcademicHubService:
    def __init__(self, repo: AcademicHubRepository) -> None:
        self._repo = repo

    def create_project(
        self,
        name: str,
        description: str,
        department: str,
        lead: str,
        members: list[str] | None = None,
    ) -> InstitutionalProject:
        from ..domain.entities.academic_hub import InstitutionalProject
        project = InstitutionalProject(
            name=name,
            description=description,
            department=department,
            lead=lead,
            members=members,
        )
        self._repo.add_project(project)
        self._record_version(project.id, "InstitutionalProject", "1.0.0", ["Created"], lead)
        return project

    def get_project(self, project_id: str) -> InstitutionalProject | None:
        return self._repo.get_project(project_id)

    def update_project(
        self,
        project_id: str,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
        members: list[str] | None = None,
    ) -> InstitutionalProject:
        project = self._repo.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if status is not None:
            project.status = status
        if members is not None:
            project.members = members
        project.updated_at = datetime.now(timezone.utc)
        self._repo.update_project(project)
        changes = [f"Updated at {project.updated_at.isoformat()}"]
        self._record_version(project.id, "InstitutionalProject", project.version if hasattr(project, 'version') else "1.1.0", changes, project.lead)
        return project

    def delete_project(self, project_id: str) -> None:
        self._repo.remove_project(project_id)

    def list_projects(self) -> list[InstitutionalProject]:
        return self._repo.all_projects()

    def share_curriculum_package(
        self,
        title: str,
        source_institution: str,
        version: str,
        content_type: str,
        checksum: str,
        signature: str,
        compatibility: str,
        accessibility_report: dict | None = None,
        localization_report: dict | None = None,
    ) -> SharedCurriculumPackage:
        from ..domain.entities.academic_hub import SharedCurriculumPackage
        pkg = SharedCurriculumPackage(
            title=title,
            source_institution=source_institution,
            version=version,
            content_type=content_type,
            checksum=checksum,
            signature=signature,
            compatibility=compatibility,
            accessibility_report=accessibility_report,
            localization_report=localization_report,
        )
        self._repo.add_shared_package(pkg)
        return pkg

    def get_shared_package(self, package_id: str) -> SharedCurriculumPackage | None:
        return self._repo.get_shared_package(package_id)

    def list_shared_packages(self) -> list[SharedCurriculumPackage]:
        return self._repo.all_shared_packages()

    def import_resource(
        self,
        package_id: str,
        imported_by: str,
        status: str = "pending",
        validation_results: dict | None = None,
    ) -> ImportedResource:
        from ..domain.entities.academic_hub import ImportedResource
        resource = ImportedResource(
            package_id=package_id,
            imported_by=imported_by,
            status=status,
            validation_results=validation_results,
        )
        self._repo.add_imported_resource(resource)
        return resource

    def get_imported_resource(self, resource_id: str) -> ImportedResource | None:
        return self._repo.get_imported_resource(resource_id)

    def list_imported_resources(self) -> list[ImportedResource]:
        return self._repo.all_imported_resources()

    def create_review_request(
        self,
        title: str,
        request_type: str,
        submitter: str,
        assignees: list[str] | None = None,
        due_date: str = "",
    ) -> ReviewRequest:
        from ..domain.entities.academic_hub import ReviewRequest, ReviewStatus
        request = ReviewRequest(
            title=title,
            request_type=request_type,
            submitter=submitter,
            assignees=assignees,
            due_date=due_date,
        )
        self._repo.add_review_request(request)
        return request

    def update_review_status(self, request_id: str, status: str) -> ReviewRequest:
        request = self._repo.get_review_request(request_id)
        if not request:
            raise ValueError(f"Review request {request_id} not found")
        request.status = status
        self._repo.update_review_request(request)
        return request

    def list_review_requests(self) -> list[ReviewRequest]:
        return self._repo.all_review_requests()

    def queue_publication(
        self,
        content_id: str,
        content_type: str,
        title: str,
        version: str,
        submitted_by: str,
    ) -> PublicationQueueItem:
        from ..domain.entities.academic_hub import PublicationQueueItem
        item = PublicationQueueItem(
            content_id=content_id,
            content_type=content_type,
            title=title,
            version=version,
            submitted_by=submitted_by,
        )
        self._repo.add_publication_item(item)
        return item

    def update_publication_status(self, item_id: str, status: str) -> PublicationQueueItem:
        item = self._repo.get_publication_item(item_id)
        if not item:
            raise ValueError(f"Publication item {item_id} not found")
        item.status = status
        self._repo.update_publication_item(item)
        return item

    def list_publication_items(self) -> list[PublicationQueueItem]:
        return self._repo.all_publication_items()

    def get_version_history(self, entity_id: str) -> list[VersionHistory]:
        return self._repo.get_version_history_for_entity(entity_id)

    def get_dashboard(self) -> AcademicHubDashboard:
        from ..domain.entities.academic_hub import AcademicHubDashboard
        projects = self._repo.all_projects()
        packages = self._repo.all_shared_packages()
        resources = self._repo.all_imported_resources()
        reviews = self._repo.all_review_requests()
        publications = self._repo.all_publication_items()
        now = datetime.now(timezone.utc)
        pending = sum(1 for r in reviews if r.status.value in ("draft", "in_review"))
        pubs_this_month = sum(
            1 for p in publications
            if p.submitted_at.year == now.year and p.submitted_at.month == now.month
        )
        return AcademicHubDashboard(
            total_projects=len(projects),
            shared_packages=len(packages),
            imported_resources=len(resources),
            pending_reviews=pending,
            publications_this_month=pubs_this_month,
        )

    def _record_version(
        self,
        entity_id: str,
        entity_type: str,
        version: str,
        changes: list[str],
        author: str,
    ) -> None:
        from ..domain.entities.academic_hub import VersionHistory
        entry = VersionHistory(
            entity_id=entity_id,
            entity_type=entity_type,
            version=version,
            changes=changes,
            author=author,
        )
        self._repo.add_version_history(entry)
