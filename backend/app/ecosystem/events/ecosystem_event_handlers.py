"""Ecosystem event handlers."""

from __future__ import annotations

from typing import Any

from ..domain.events.ecosystem_events import (
    PackageInstalled,
    PackageRemoved,
    LibraryItemAdded,
    ResearchProjectCreated,
    DistributionExported,
    DistributionImported,
    OrganizationCreated,
)


_event_log: list[dict[str, Any]] = []


def handle_package_installed(event: PackageInstalled) -> None:
    _event_log.append({
        "type": "PackageInstalled",
        "package_id": event.package_id,
        "package_name": event.package_name,
        "version": event.version,
        "installed_by": event.installed_by,
        "occurred_at": event.occurred_at.isoformat(),
    })


def handle_package_removed(event: PackageRemoved) -> None:
    _event_log.append({
        "type": "PackageRemoved",
        "package_id": event.package_id,
        "package_name": event.package_name,
        "version": event.version,
        "removed_by": event.removed_by,
        "occurred_at": event.occurred_at.isoformat(),
    })


def handle_library_item_added(event: LibraryItemAdded) -> None:
    _event_log.append({
        "type": "LibraryItemAdded",
        "item_id": event.item_id,
        "title": event.title,
        "item_type": event.item_type,
        "added_by": event.added_by,
        "occurred_at": event.occurred_at.isoformat(),
    })


def handle_research_project_created(event: ResearchProjectCreated) -> None:
    _event_log.append({
        "type": "ResearchProjectCreated",
        "project_id": event.project_id,
        "title": event.title,
        "created_by": event.created_by,
        "occurred_at": event.occurred_at.isoformat(),
    })


def handle_distribution_exported(event: DistributionExported) -> None:
    _event_log.append({
        "type": "DistributionExported",
        "package_id": event.package_id,
        "package_name": event.package_name,
        "exported_by": event.exported_by,
        "occurred_at": event.occurred_at.isoformat(),
    })


def handle_distribution_imported(event: DistributionImported) -> None:
    _event_log.append({
        "type": "DistributionImported",
        "package_id": event.package_id,
        "package_name": event.package_name,
        "imported_by": event.imported_by,
        "status": event.status,
        "occurred_at": event.occurred_at.isoformat(),
    })


def handle_organization_created(event: OrganizationCreated) -> None:
    _event_log.append({
        "type": "OrganizationCreated",
        "org_id": event.org_id,
        "org_name": event.org_name,
        "org_type": event.org_type,
        "created_by": event.created_by,
        "occurred_at": event.occurred_at.isoformat(),
    })


def dispatch(event: PackageInstalled | PackageRemoved | LibraryItemAdded | ResearchProjectCreated | DistributionExported | DistributionImported | OrganizationCreated) -> None:
    handlers = {
        PackageInstalled: handle_package_installed,
        PackageRemoved: handle_package_removed,
        LibraryItemAdded: handle_library_item_added,
        ResearchProjectCreated: handle_research_project_created,
        DistributionExported: handle_distribution_exported,
        DistributionImported: handle_distribution_imported,
        OrganizationCreated: handle_organization_created,
    }
    handler = handlers.get(type(event))
    if handler:
        handler(event)


def get_event_log() -> list[dict[str, Any]]:
    return _event_log.copy()


def clear_event_log() -> None:
    _event_log.clear()
