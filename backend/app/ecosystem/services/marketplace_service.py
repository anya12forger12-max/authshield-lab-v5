"""Marketplace service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..domain.entities.marketplace import LocalPackage, PackageSearch, InstallationRecord

if TYPE_CHECKING:
    from ..domain.interfaces import MarketplaceRepository


class MarketplaceService:
    def __init__(self, repo: MarketplaceRepository) -> None:
        self._repo = repo

    def install_package(self, package_id: str, installed_by: str, config: dict | None = None) -> InstallationRecord:
        pkg = self._repo.get_package(package_id)
        if not pkg:
            raise ValueError(f"Package {package_id} not found")
        record = InstallationRecord(
            package_id=package_id,
            installed_by=installed_by,
            version=pkg.version,
            status="installed",
            config=config or {},
        )
        self._repo.add_installation(record)
        pkg.installed = True
        pkg.installed_at = record.installed_at
        self._repo.update_package(pkg)
        return record

    def uninstall_package(self, package_id: str) -> None:
        pkg = self._repo.get_package(package_id)
        if not pkg:
            raise ValueError(f"Package {package_id} not found")
        for rec in self._repo.find_installations_by_package(package_id):
            rec.status = "uninstalled"
        pkg.installed = False
        pkg.installed_at = None
        self._repo.update_package(pkg)

    def search_packages(self, search: PackageSearch) -> list[LocalPackage]:
        return self._repo.search(search)

    def filter_by_category(self, category: str) -> list[LocalPackage]:
        return [p for p in self._repo.all_packages() if p.category.value == category]

    def rate_package(self, package_id: str, rating: int) -> LocalPackage:
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        pkg = self._repo.get_package(package_id)
        if not pkg:
            raise ValueError(f"Package {package_id} not found")
        total = pkg.rating * pkg.review_count
        pkg.review_count += 1
        pkg.rating = round((total + rating) / pkg.review_count)
        self._repo.update_package(pkg)
        return pkg

    def toggle_favorite(self, package_id: str) -> LocalPackage:
        pkg = self._repo.get_package(package_id)
        if not pkg:
            raise ValueError(f"Package {package_id} not found")
        pkg.favorite = not pkg.favorite
        self._repo.update_package(pkg)
        return pkg

    def get_favorites(self) -> list[LocalPackage]:
        return [p for p in self._repo.all_packages() if p.favorite]

    def validate_package_integrity(self, package: LocalPackage) -> bool:
        if not package.checksum or not package.signature:
            return False
        return len(package.checksum) >= 32 and len(package.signature) >= 16

    def get_installed_packages(self) -> list[LocalPackage]:
        return [p for p in self._repo.all_packages() if p.installed]
