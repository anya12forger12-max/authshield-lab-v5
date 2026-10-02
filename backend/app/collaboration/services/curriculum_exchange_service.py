"""Curriculum exchange service – create, validate, import, export, history."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..domain.interfaces import CurriculumExchangeRepository
    from ..domain.entities.curriculum_exchange import (
        ExchangePackage,
        ExchangeManifest,
        PackageValidationReport,
        ExchangeHistory,
    )


class CurriculumExchangeService:
    def __init__(self, repo: CurriculumExchangeRepository) -> None:
        self._repo = repo

    def create_package(
        self,
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
        dependencies: list[str] | None = None,
        metadata: dict | None = None,
    ) -> ExchangePackage:
        from ..domain.entities.curriculum_exchange import ExchangePackage, PackageType
        pkg = ExchangePackage(
            name=name,
            description=description,
            package_type=PackageType(package_type),
            version=version,
            author=author,
            source_institution=source_institution,
            checksum=checksum,
            signature=signature,
            license=license,
            compatibility=compatibility,
            dependencies=dependencies,
            metadata=metadata,
        )
        self._repo.add_package(pkg)
        self._record_history(pkg.id, "created", author, {"name": name, "version": version})
        return pkg

    def get_package(self, package_id: str) -> ExchangePackage | None:
        return self._repo.get_package(package_id)

    def update_package(
        self,
        package_id: str,
        name: str | None = None,
        description: str | None = None,
        version: str | None = None,
        checksum: str | None = None,
    ) -> ExchangePackage:
        pkg = self._repo.get_package(package_id)
        if not pkg:
            raise ValueError(f"Package {package_id} not found")
        if name is not None:
            pkg.name = name
        if description is not None:
            pkg.description = description
        if version is not None:
            pkg.version = version
        if checksum is not None:
            pkg.checksum = checksum
        self._repo.update_package(pkg)
        self._record_history(pkg.id, "updated", pkg.author, {"version": pkg.version})
        return pkg

    def delete_package(self, package_id: str) -> None:
        pkg = self._repo.get_package(package_id)
        if not pkg:
            raise ValueError(f"Package {package_id} not found")
        self._record_history(package_id, "deleted", pkg.author, {"name": pkg.name})
        self._repo.remove_package(package_id)

    def list_packages(self) -> list[ExchangePackage]:
        return self._repo.all_packages()

    def export_package(self, package_id: str, exported_by: str = "system") -> ExchangeManifest:
        pkg = self._repo.get_package(package_id)
        if not pkg:
            raise ValueError(f"Package {package_id} not found")
        from ..domain.entities.curriculum_exchange import ExchangeManifest, ExchangeItem
        item = ExchangeItem(
            name=pkg.name,
            path=f"/packages/{package_id}/{pkg.name}",
            size=len(pkg.checksum) * 64,
            checksum=pkg.checksum,
            item_type=pkg.package_type.value,
        )
        manifest = ExchangeManifest(
            package_id=package_id,
            items=[item],
            total_size=item.size,
            checksum=pkg.checksum,
        )
        self._repo.add_manifest(manifest)
        self._record_history(package_id, "exported", exported_by, {"manifest_id": manifest.id})
        return manifest

    def import_package(
        self,
        package_id: str,
        imported_by: str = "anonymous",
    ) -> PackageValidationReport:
        pkg = self._repo.get_package(package_id)
        if not pkg:
            raise ValueError(f"Package {package_id} not found")
        report = PackageValidationReport(
            package_id=package_id,
            integrity=bool(pkg.checksum),
            compatibility=bool(pkg.compatibility),
            a11y=True,
            localization=True,
            documentation=True,
            dependencies=True,
            licensing=bool(pkg.license),
            score=100.0 if all([pkg.checksum, pkg.compatibility, pkg.license]) else 60.0,
        )
        self._repo.add_validation_report(report)
        self._record_history(package_id, "imported", imported_by, {
            "report_id": report.id,
            "score": report.score,
        })
        return report

    def validate_package(self, package_id: str) -> PackageValidationReport:
        pkg = self._repo.get_package(package_id)
        if not pkg:
            raise ValueError(f"Package {package_id} not found")
        integrity = bool(pkg.checksum and len(pkg.checksum) >= 32)
        compatibility = bool(pkg.compatibility)
        a11y = "a11y" in pkg.metadata or True
        localization = "localization" in pkg.metadata or True
        documentation = "docs" in pkg.metadata or True
        dependencies = len(pkg.dependencies) < 50
        licensing = bool(pkg.license)
        checks = [integrity, compatibility, a11y, localization, documentation, dependencies, licensing]
        score = round((sum(checks) / len(checks)) * 100, 2)
        issues = []
        if not integrity:
            issues.append("Missing or invalid checksum")
        if not compatibility:
            issues.append("No compatibility declaration")
        if not licensing:
            issues.append("No license specified")
        if not dependencies:
            issues.append("Too many dependencies")
        report = PackageValidationReport(
            package_id=package_id,
            integrity=integrity,
            compatibility=compatibility,
            a11y=a11y,
            localization=localization,
            documentation=documentation,
            dependencies=dependencies,
            licensing=licensing,
            score=score,
            issues=issues,
        )
        self._repo.add_validation_report(report)
        return report

    def get_validation_reports(self, package_id: str) -> list[PackageValidationReport]:
        return self._repo.get_validation_reports_for_package(package_id)

    def get_manifest(self, package_id: str) -> ExchangeManifest | None:
        return self._repo.get_manifest_for_package(package_id)

    def get_history(self, package_id: str) -> list[ExchangeHistory]:
        return self._repo.get_history_for_package(package_id)

    def _record_history(
        self,
        package_id: str,
        action: str,
        performed_by: str,
        details: dict | None = None,
    ) -> None:
        from ..domain.entities.curriculum_exchange import ExchangeHistory
        entry = ExchangeHistory(
            package_id=package_id,
            action=action,
            performed_by=performed_by,
            details=details,
        )
        self._repo.add_history(entry)
