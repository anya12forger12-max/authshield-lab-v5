"""Package validation service – validate integrity, compatibility, a11y, docs, dependencies, licensing."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from ..domain.entities.curriculum_exchange import ExchangePackage, PackageValidationReport

if TYPE_CHECKING:
    from ..domain.interfaces import CurriculumExchangeRepository


class PackageValidationService:
    _REQUIRED_FIELDS = ["name", "version", "author", "checksum", "signature", "license"]
    _MAX_DEPENDENCIES = 50

    def __init__(self, repo: CurriculumExchangeRepository) -> None:
        self._repo = repo

    def validate_package(self, package_id: str) -> PackageValidationReport:
        pkg = self._repo.get_package(package_id)
        if not pkg:
            raise ValueError(f"Package {package_id} not found")
        integrity = self._validate_integrity(pkg)
        compatibility = self._validate_compatibility(pkg)
        a11y = self._validate_accessibility(pkg)
        localization = self._validate_localization(pkg)
        documentation = self._validate_documentation(pkg)
        dependencies = self._validate_dependencies(pkg)
        licensing = self._validate_licensing(pkg)
        checks = {
            "integrity": integrity,
            "compatibility": compatibility,
            "a11y": a11y,
            "localization": localization,
            "documentation": documentation,
            "dependencies": dependencies,
            "licensing": licensing,
        }
        issues = self._collect_issues(pkg, checks)
        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        score = round((passed / total) * 100, 2) if total > 0 else 0.0
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

    def validate_batch(self, package_ids: list[str]) -> list[PackageValidationReport]:
        reports = []
        for pid in package_ids:
            try:
                report = self.validate_package(pid)
                reports.append(report)
            except ValueError:
                continue
        return reports

    def get_reports_for_package(self, package_id: str) -> list[PackageValidationReport]:
        return self._repo.get_validation_reports_for_package(package_id)

    def check_integrity(self, package_id: str) -> bool:
        pkg = self._repo.get_package(package_id)
        if not pkg:
            return False
        return self._validate_integrity(pkg)

    def check_compatibility(self, package_id: str) -> bool:
        pkg = self._repo.get_package(package_id)
        if not pkg:
            return False
        return self._validate_compatibility(pkg)

    def _validate_integrity(self, pkg: "ExchangePackage") -> bool:
        if not pkg.checksum:
            return False
        if len(pkg.checksum) < 32:
            return False
        if not pkg.signature:
            return False
        if len(pkg.signature) < 16:
            return False
        return True

    def _validate_compatibility(self, pkg: "ExchangePackage") -> bool:
        if not pkg.compatibility:
            return False
        valid_operators = [">=", "<=", "~=", "==", "^"]
        return any(op in pkg.compatibility for op in valid_operators) or len(pkg.compatibility) >= 3

    def _validate_accessibility(self, pkg: "ExchangePackage") -> bool:
        if "a11y" in pkg.metadata:
            return bool(pkg.metadata["a11y"])
        if "accessibility" in pkg.metadata:
            return bool(pkg.metadata["accessibility"])
        return True

    def _validate_localization(self, pkg: "ExchangePackage") -> bool:
        if "localization" in pkg.metadata:
            return bool(pkg.metadata["localization"])
        if "locales" in pkg.metadata:
            locales = pkg.metadata["locales"]
            return isinstance(locales, (list, dict)) and len(locales) > 0
        return True

    def _validate_documentation(self, pkg: "ExchangePackage") -> bool:
        if "docs" in pkg.metadata:
            return bool(pkg.metadata["docs"])
        if "documentation" in pkg.metadata:
            return bool(pkg.metadata["documentation"])
        if "readme" in pkg.metadata:
            return bool(pkg.metadata["readme"])
        return True

    def _validate_dependencies(self, pkg: "ExchangePackage") -> bool:
        if not isinstance(pkg.dependencies, list):
            return False
        if len(pkg.dependencies) > self._MAX_DEPENDENCIES:
            return False
        for dep in pkg.dependencies:
            if not isinstance(dep, str) or not dep.strip():
                return False
        return True

    def _validate_licensing(self, pkg: "ExchangePackage") -> bool:
        if not pkg.license:
            return False
        known_licenses = [
            "MIT", "Apache-2.0", "GPL-3.0", "BSD-2-Clause", "BSD-3-Clause",
            "ISC", "LGPL-3.0", "MPL-2.0", "Unlicense", "CC-BY-4.0",
            "CC-BY-SA-4.0", "CC0-1.0", "proprietary", "custom",
        ]
        return pkg.license in known_licenses or len(pkg.license) >= 3

    def _collect_issues(self, pkg: "ExchangePackage", checks: dict[str, bool]) -> list[str]:
        issues: list[str] = []
        if not checks["integrity"]:
            issues.append("Invalid or missing checksum/signature")
        if not checks["compatibility"]:
            issues.append("Missing or invalid compatibility declaration")
        if not checks["a11y"]:
            issues.append("Accessibility metadata indicates non-compliance")
        if not checks["localization"]:
            issues.append("Localization metadata missing or empty")
        if not checks["documentation"]:
            issues.append("Documentation metadata missing")
        if not checks["dependencies"]:
            dep_count = len(pkg.dependencies) if isinstance(pkg.dependencies, list) else 0
            if dep_count > self._MAX_DEPENDENCIES:
                issues.append(f"Too many dependencies ({dep_count} > {self._MAX_DEPENDENCIES})")
            else:
                issues.append("Invalid dependency entries found")
        if not checks["licensing"]:
            issues.append("Missing or unrecognized license")
        if not pkg.name:
            issues.append("Package name is empty")
        if not pkg.version:
            issues.append("Package version is empty")
        if not pkg.author:
            issues.append("Package author is empty")
        return issues
