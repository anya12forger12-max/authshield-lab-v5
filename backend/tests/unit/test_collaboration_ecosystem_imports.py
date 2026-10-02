"""Every collaboration and ecosystem module must be importable.

These packages addressed their siblings with bare absolute imports that do not
exist in the deployed layout::

    from domain.entities.research_workspace import ResearchProject
    from repositories.collaboration_repository_impl import (...)
    from services.marketplace_service import MarketplaceService

``app.collaboration.domain`` and ``app.collaboration.repositories`` are the
real locations, so each of those raised ``ModuleNotFoundError`` at import.
Nothing in the unit suite caught it because ``app/api/v1/router.py`` wraps
every ``include_router`` in ``try: ... except (ImportError, AttributeError):
pass`` -- a dead module is silently skipped, so the affected areas simply
disappeared from the route table while the suite stayed green.

``pytest`` collection imports the test modules, not the application packages,
so this asserts the imports directly instead of relying on a green run.
"""

from __future__ import annotations

import importlib

import pytest

MODULES = [
    # collaboration
    "app.collaboration.api.collaboration_routes",
    "app.collaboration.domain.interfaces",
    "app.collaboration.events.collaboration_event_handlers",
    "app.collaboration.repositories.collaboration_repository_impl",
    "app.collaboration.services.academic_hub_service",
    "app.collaboration.services.curriculum_exchange_service",
    "app.collaboration.services.knowledge_base_service",
    "app.collaboration.services.package_validation_service",
    "app.collaboration.services.peer_review_service",
    "app.collaboration.services.research_service",
    "app.collaboration.validators.collaboration_validator",
    # ecosystem
    "app.ecosystem.api.ecosystem_routes",
    "app.ecosystem.domain.interfaces",
    "app.ecosystem.events.ecosystem_event_handlers",
    "app.ecosystem.repositories.ecosystem_repository_impl",
    "app.ecosystem.services.distribution_service",
    "app.ecosystem.services.governance_validation_service",
    "app.ecosystem.services.institution_service",
    "app.ecosystem.services.library_service",
    "app.ecosystem.services.marketplace_service",
    "app.ecosystem.services.research_service",
    "app.ecosystem.validators.ecosystem_validator",
]


@pytest.mark.parametrize("module", MODULES)
def test_module_imports(module: str) -> None:
    importlib.import_module(module)


def test_repository_interfaces_are_available_at_runtime() -> None:
    """The in-memory repositories subclass their interfaces, so those imports
    cannot stay under ``TYPE_CHECKING``: as base classes they are resolved at
    runtime, and keeping them type-only raised ``NameError`` on import."""
    from app.collaboration.repositories.collaboration_repository_impl import (
        InMemoryAcademicHubRepository,
    )
    from app.collaboration.domain.interfaces import AcademicHubRepository

    assert issubclass(InMemoryAcademicHubRepository, AcademicHubRepository)


def test_research_service_creates_a_project() -> None:
    """Regression: ``create_project`` imported its entity function-locally from
    the nonexistent ``domain`` package, so the call raised
    ``ModuleNotFoundError`` (HTTP 500) instead of creating anything."""
    # The real in-memory repository, not a mock: a mock fabricates any method
    # on demand, which is how the missing-method crashes stayed hidden behind a
    # green suite for many rounds.
    from app.collaboration.repositories.collaboration_repository_impl import (
        InMemoryResearchWorkspaceRepository,
    )
    from app.collaboration.services.research_service import ResearchService

    repo = InMemoryResearchWorkspaceRepository()
    project = ResearchService(repo).create_project(
        name="Trial",
        description="d",
        principal_investigator="pi",
    )
    assert project.name == "Trial"
    # It really persisted through the real repository, not just returned.
    assert repo.get_project(project.id) is project
