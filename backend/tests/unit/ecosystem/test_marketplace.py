"""Tests for ecosystem entities and services — LocalPackage, LibraryItem, ResearchProject, MarketplaceService, LibraryService."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.ecosystem.domain.entities.marketplace import (
    InstallationRecord,
    LocalPackage,
    PackageCategory,
    PackageSearch,
)
from app.ecosystem.domain.entities.library import LibraryItem, LibraryItemType
from app.ecosystem.domain.entities.research import ResearchProject, ResearchStatus
from app.ecosystem.services.marketplace_service import MarketplaceService


class TestLocalPackage:
    def test_default_values(self):
        p = LocalPackage(name="Pkg", version="1.0", author="Auth", description="Desc", category=PackageCategory.plugin)
        assert p.name == "Pkg"
        assert p.installed is False
        assert p.favorite is False
        assert p.rating == 0

    def test_custom_package(self):
        p = LocalPackage(
            name="SecPack", version="2.0", author="Alice", description="Security",
            category=PackageCategory.course, tags=["security"], file_size=1024
        )
        assert len(p.tags) == 1
        assert p.file_size == 1024


class TestPackageSearch:
    def test_default_values(self):
        s = PackageSearch()
        assert s.query == ""
        assert s.limit == 20
        assert s.offset == 0

    def test_search_with_category(self):
        s = PackageSearch(query="security", category=PackageCategory.plugin, sort_by="rating")
        assert s.query == "security"
        assert s.sort_by == "rating"


class TestInstallationRecord:
    def test_create(self):
        rec = InstallationRecord(package_id="p1", installed_by="user1", version="1.0")
        assert rec.package_id == "p1"
        assert rec.status.value == "installed"

    def test_custom_config(self):
        rec = InstallationRecord(package_id="p1", installed_by="user1", version="1.0", config={"key": "val"})
        assert rec.config["key"] == "val"


class TestLibraryItem:
    def test_defaults(self):
        item = LibraryItem(title="Book", author="Author", item_type=LibraryItemType.book)
        assert item.title == "Book"
        assert item.bookmarked is False

    def test_page_count(self):
        item = LibraryItem(title="Doc", author="A", item_type=LibraryItemType.documentation, page_count=200)
        assert item.page_count == 200


class TestResearchProject:
    def test_defaults(self):
        p = ResearchProject(title="Test Project")
        assert p.status == ResearchStatus.active

    def test_custom_status(self):
        p = ResearchProject(title="Completed", status=ResearchStatus.completed)
        assert p.status == ResearchStatus.completed


class TestMarketplaceService:
    def test_search_packages(self):
        repo = MagicMock()
        repo.search = MagicMock(return_value=[])
        service = MarketplaceService(repo)
        result = service.search_packages(PackageSearch())
        assert result == []

    def test_filter_by_category(self):
        repo = MagicMock()
        repo.all_packages = MagicMock(return_value=[
            LocalPackage(name="A", version="1.0", author="X", description="D", category=PackageCategory.course),
            LocalPackage(name="B", version="1.0", author="X", description="D", category=PackageCategory.plugin),
        ])
        service = MarketplaceService(repo)
        result = service.filter_by_category("course")
        assert len(result) == 1
        assert result[0].name == "A"

    def test_install_package_raises_on_missing(self):
        repo = MagicMock()
        repo.get_package = MagicMock(return_value=None)
        service = MarketplaceService(repo)
        with pytest.raises(ValueError, match="Package"):
            service.install_package("bad", "user")

    def test_rate_package(self):
        repo = MagicMock()
        p = LocalPackage(name="P", version="1.0", author="A", description="D", category=PackageCategory.plugin)
        p.rating = 3
        p.review_count = 2
        repo.get_package = MagicMock(return_value=p)
        repo.update_package = MagicMock()
        service = MarketplaceService(repo)
        result = service.rate_package(p.id, 5)
        assert result.rating == 4

    def test_rate_package_out_of_range(self):
        repo = MagicMock()
        p = LocalPackage(name="P", version="1.0", author="A", description="D", category=PackageCategory.plugin)
        repo.get_package = MagicMock(return_value=p)
        service = MarketplaceService(repo)
        with pytest.raises(ValueError, match="Rating"):
            service.rate_package(p.id, 6)

    def test_toggle_favorite(self):
        repo = MagicMock()
        p = LocalPackage(name="P", version="1.0", author="A", description="D", category=PackageCategory.plugin)
        repo.get_package = MagicMock(return_value=p)
        repo.update_package = MagicMock()
        service = MarketplaceService(repo)
        result = service.toggle_favorite(p.id)
        assert result.favorite is True

    def test_get_favorites(self):
        repo = MagicMock()
        p = LocalPackage(name="P", version="1.0", author="A", description="D", category=PackageCategory.plugin)
        p.favorite = True
        repo.all_packages = MagicMock(return_value=[p])
        service = MarketplaceService(repo)
        result = service.get_favorites()
        assert len(result) == 1

    def test_validate_package_integrity(self):
        repo = MagicMock()
        p = LocalPackage(name="P", version="1.0", author="A", description="D", category=PackageCategory.plugin)
        p.checksum = "a" * 32
        p.signature = "b" * 16
        service = MarketplaceService(repo)
        assert service.validate_package_integrity(p) is True

    def test_validate_package_integrity_fails(self):
        repo = MagicMock()
        p = LocalPackage(name="P", version="1.0", author="A", description="D", category=PackageCategory.plugin)
        p.checksum = "ab"
        p.signature = "cd"
        service = MarketplaceService(repo)
        assert service.validate_package_integrity(p) is False


class TestLibraryService:
    def test_add_and_get_item(self):
        from app.ecosystem.services.library_service import LibraryService
        repo = MagicMock()
        service = LibraryService(repo)
        item = LibraryItem(title="Book", author="A", item_type=LibraryItemType.book)
        repo.get_item = MagicMock(return_value=item)
        result = service.get_item(item.id)
        assert result.title == "Book"

    def test_search_items(self):
        from app.ecosystem.services.library_service import LibraryService
        repo = MagicMock()
        repo.search_items = MagicMock(return_value=[])
        service = LibraryService(repo)
        result = service.search_items("math")
        assert result == []

    def test_add_bookmark(self):
        from app.ecosystem.services.library_service import LibraryService
        repo = MagicMock()
        repo.add_bookmark = MagicMock()
        service = LibraryService(repo)
        bm = service.add_bookmark("i1", "u1", note="good", page=10)
        assert bm.item_id == "i1"
        assert bm.page == 10

    def test_generate_bibliography_apa(self):
        from app.ecosystem.services.library_service import LibraryService
        repo = MagicMock()
        item = LibraryItem(title="Test", author="Author", item_type=LibraryItemType.book)
        item.created_at = __import__("datetime").datetime(2024, 1, 1)
        repo.get_item = MagicMock(return_value=item)
        service = LibraryService(repo)
        result = service.generate_bibliography([item.id], format="apa")
        assert "Author" in result
        assert "Test" in result
