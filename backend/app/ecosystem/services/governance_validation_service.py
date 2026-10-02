"""Governance & validation service."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..domain.entities.marketplace import LocalPackage
    from ..domain.entities.content_distribution import DistributionPackage


class GovernanceValidationService:
    def validate_package(self, package: LocalPackage) -> dict[str, bool]:
        return {
            "integrity": self.validate_integrity(package),
            "compatibility": self.validate_compatibility(package),
            "accessibility": self.validate_accessibility(package),
            "documentation": self.validate_documentation(package),
            "licensing": self.validate_licensing(package),
        }

    def validate_integrity(self, package: LocalPackage) -> bool:
        if not package.checksum or not package.signature:
            return False
        return len(package.checksum) >= 32 and package.signature.startswith("sig:")

    def validate_compatibility(self, package: LocalPackage) -> bool:
        if not package.compatibility:
            return False
        compatible_versions = ["1.0", "1.1", "2.0", "3.0"]
        return any(v in package.compatibility for v in compatible_versions)

    def validate_accessibility(self, package: LocalPackage) -> bool:
        a11y_tags = {"a11y", "accessibility", "wcag", "aria", "screen-reader"}
        tags_set = set(t.lower() for t in package.tags)
        return bool(tags_set & a11y_tags) or "a11y" in package.name.lower()

    def validate_documentation(self, package: LocalPackage) -> bool:
        docs_keywords = {"doc", "docs", "documentation", "guide", "manual", "readme"}
        combined = f"{package.name} {package.description}".lower()
        return any(kw in combined for kw in docs_keywords)

    def validate_licensing(self, package: LocalPackage) -> bool:
        if not package.license:
            return False
        valid_licenses = {"mit", "apache-2.0", "gpl-3.0", "bsd-3-clause", "cc-by-4.0", "cc-by-sa-4.0", "unlicense"}
        return package.license.lower() in valid_licenses

    def validate_distribution_package(self, pkg: DistributionPackage) -> dict[str, bool]:
        return {
            "has_checksum": bool(pkg.checksum),
            "has_signature": bool(pkg.signature),
            "has_content_type": bool(pkg.content_type),
            "has_version": bool(pkg.version),
        }
