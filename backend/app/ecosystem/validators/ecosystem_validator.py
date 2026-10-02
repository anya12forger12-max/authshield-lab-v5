"""Ecosystem validators for package & content integrity."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..domain.entities.marketplace import LocalPackage
    from ..domain.entities.library import LibraryItem
    from ..domain.entities.research import ResearchProject
    from ..domain.entities.institution import Organization
    from ..domain.entities.content_distribution import DistributionPackage


class EcosystemValidator:
    def validate_package_name(self, name: str) -> bool:
        return bool(re.match(r"^[a-z0-9_\-\.]{1,100}$", name))

    def validate_semver(self, version: str) -> bool:
        return bool(re.match(r"^\d+\.\d+\.\d+(-[a-z0-9]+(\.[a-z0-9]+)*)?(\+[a-z0-9]+)?$", version))

    def validate_package(self, package: LocalPackage) -> list[str]:
        errors: list[str] = []
        if not self.validate_package_name(package.name):
            errors.append(f"Invalid package name: {package.name}")
        if not self.validate_semver(package.version):
            errors.append(f"Invalid semver: {package.version}")
        if not package.author:
            errors.append("Author is required")
        if len(package.tags) > 20:
            errors.append("Too many tags (max 20)")
        return errors

    def validate_library_item(self, item: LibraryItem) -> list[str]:
        errors: list[str] = []
        if not item.title:
            errors.append("Title is required")
        if not item.author:
            errors.append("Author is required")
        if item.page_count < 0:
            errors.append("Page count cannot be negative")
        return errors

    def validate_project(self, project: ResearchProject) -> list[str]:
        errors: list[str] = []
        if not project.title:
            errors.append("Title is required")
        return errors

    def validate_organization(self, org: Organization) -> list[str]:
        errors: list[str] = []
        if not org.name:
            errors.append("Name is required")
        return errors

    def validate_distribution_package(self, pkg: DistributionPackage) -> list[str]:
        errors: list[str] = []
        if not self.validate_package_name(pkg.name):
            errors.append(f"Invalid distribution name: {pkg.name}")
        if not self.validate_semver(pkg.version):
            errors.append(f"Invalid semver: {pkg.version}")
        return errors
