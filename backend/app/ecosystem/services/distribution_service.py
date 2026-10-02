"""Distribution service."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

from ..domain.entities.content_distribution import (
    DistributionPackage, DistributionManifest, DistributionItem,
    ImportRecord, SyncOperation,
)

if TYPE_CHECKING:
    from ..domain.interfaces import DistributionRepository


class DistributionService:
    def __init__(self, repo: DistributionRepository) -> None:
        self._repo = repo

    def create_package(self, name: str, description: str = "", content_type: str = "", version: str = "1.0.0", created_by: str = "") -> DistributionPackage:
        pkg = DistributionPackage(
            name=name, description=description, content_type=content_type,
            version=version, created_by=created_by,
        )
        self._repo.add_package(pkg)
        return pkg

    def export_package(self, package_id: str) -> DistributionManifest:
        pkg = self._repo.get_package(package_id)
        if not pkg:
            raise ValueError(f"Distribution package {package_id} not found")
        raw = f"{pkg.id}:{pkg.name}:{pkg.version}".encode()
        pkg.checksum = hashlib.sha256(raw).hexdigest()
        pkg.signature = f"sig:{pkg.checksum[:16]}"
        pkg.exported = True
        self._repo.update_package(pkg)
        manifest = DistributionManifest(package_id=package_id)
        manifest.total_size = 0
        self._repo.add_manifest(manifest)
        return manifest

    def import_package(self, package_id: str, imported_by: str) -> ImportRecord:
        pkg = self._repo.get_package(package_id)
        if not pkg:
            raise ValueError(f"Distribution package {package_id} not found")
        pkg.imported = True
        self._repo.update_package(pkg)
        record = ImportRecord(package_id=package_id, imported_by=imported_by, status="imported")
        self._repo.add_import_record(record)
        return record

    def add_manifest_item(self, package_id: str, name: str, path: str, size: int = 0, checksum: str = "", item_type: str = "file") -> DistributionManifest:
        manifest = self._repo.get_manifest_for_package(package_id)
        if not manifest:
            manifest = DistributionManifest(package_id=package_id)
            self._repo.add_manifest(manifest)
        item = DistributionItem(name=name, path=path, size=size, checksum=checksum, item_type=item_type)
        manifest.items.append(item)
        manifest.total_size += size
        return manifest

    def start_sync(self, name: str, source: str, destination: str) -> SyncOperation:
        op = SyncOperation(name=name, source=source, destination=destination, status="in_progress")
        self._repo.add_sync_operation(op)
        return op

    def complete_sync(self, operation_id: str, items_processed: int, items_conflict: int) -> SyncOperation:
        ops = self._repo.get_sync_operations()
        for op in ops:
            if op.id == operation_id:
                op.status = "completed"
                op.items_processed = items_processed
                op.items_conflict = items_conflict
                op.completed_at = op.started_at
                return op
        raise ValueError(f"Sync operation {operation_id} not found")

    def detect_conflicts(self, package_id: str) -> list[str]:
        existing = self._repo.all_packages()
        pkg = self._repo.get_package(package_id)
        if not pkg:
            return []
        conflicts: list[str] = []
        for ep in existing:
            if ep.name == pkg.name and ep.id != pkg.id:
                conflicts.append(f"Name conflict: {ep.name}")
            if ep.id == pkg.id:
                continue
        return conflicts

    def get_package(self, package_id: str) -> DistributionPackage | None:
        return self._repo.get_package(package_id)

    def list_packages(self) -> list[DistributionPackage]:
        return self._repo.all_packages()

    def get_manifest(self, package_id: str) -> DistributionManifest | None:
        return self._repo.get_manifest_for_package(package_id)

    def get_import_records(self) -> list[ImportRecord]:
        return self._repo.get_import_records()

    def get_sync_operations(self) -> list[SyncOperation]:
        return self._repo.get_sync_operations()
