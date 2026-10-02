"""Regression tests for entity classes that were imported only under
``if TYPE_CHECKING:`` while being constructed at runtime.

Every service in this file carries ``from __future__ import annotations``, so
the guarded imports are *correct* for annotation purposes and no type checker
reports anything: ``ResearchProject`` in a signature resolves fine.

At runtime, though, a bare ``ResearchProject(...)`` looks the name up in the
module globals, the ``if TYPE_CHECKING:`` block never executed, and the call
raised ``NameError: name 'ResearchProject' is not defined`` on first use:

    from app.ecosystem.services.library_service import LibraryService
    LibraryService(repo).add_bookmark(...)   # NameError: name 'Bookmark' ...

This stayed invisible for two independent reasons:

1. ``app/api/v1/router.py`` wraps every ``include_router`` in
   ``try: ... except (ImportError, AttributeError): pass``, so an area that
   cannot be imported is silently never registered rather than reported.
2. ``backend/tests/unit/ecosystem/test_marketplace.py`` supplied the missing
   class by hand -- ``lib_mod.Bookmark = Bookmark`` -- so the one path that
   *was* exercised passed with a monkeypatch standing in for the import.

Both are removed: the entity imports are real runtime imports, and the
monkeypatch is gone. These tests call the real services against the real
in-memory repositories -- a ``MagicMock`` fabricates any attribute on demand,
which is precisely why the defect survived a green suite.
"""

from __future__ import annotations

import importlib
import pathlib

import pytest

import app

_MIN_EXPECTED_MODULES = 30
_BOOKMARK_PAGE = 10

# Scoped to the two areas this repair covers. `pkgutil.walk_packages` is not
# used: it imports while discovering, which trips an unrelated pre-existing
# SQLAlchemy declarative-mapper problem in `app.services.database`.
_AREAS = ("collaboration", "ecosystem")
_EXTRA = ("app.lms.domain.models.lms_models",)
_APP_ROOT = pathlib.Path(app.__file__).parent


def _module_names_under(rel_dir: str) -> list[str]:
    base = _APP_ROOT / rel_dir
    out: list[str] = []
    for path in sorted(base.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        mod = "app." + str(path.relative_to(_APP_ROOT).with_suffix("")).replace("/", ".")
        out.append(mod)
    return out


ALL_MODULES = sorted(_module_names_under(_AREAS[0]) + _module_names_under(_AREAS[1]) + list(_EXTRA))


def test_sweep_actually_enumerated_the_areas() -> None:
    """Guard the guard: a discovery bug would make the sweep below vacuous."""
    assert len(ALL_MODULES) > _MIN_EXPECTED_MODULES, len(ALL_MODULES)
    assert any(m.startswith("app.collaboration.") for m in ALL_MODULES)
    assert any(m.startswith("app.ecosystem.") for m in ALL_MODULES)


@pytest.mark.parametrize("module_name", ALL_MODULES)
def test_every_app_module_imports(module_name: str) -> None:
    """Every module must import without a NameError from a guarded import."""
    importlib.import_module(module_name)


def test_library_service_constructs_real_entities() -> None:
    """`Bookmark()` was the exact NameError behind the removed monkeypatch."""
    from app.ecosystem.repositories.ecosystem_repository_impl import (
        InMemoryLibraryRepository,
    )
    from app.ecosystem.services.library_service import LibraryService

    repo = InMemoryLibraryRepository()

    bookmark = LibraryService(repo).add_bookmark("i1", "u1", note="good", page=_BOOKMARK_PAGE)

    assert type(bookmark).__name__ == "Bookmark"
    assert bookmark.item_id == "i1"
    assert bookmark.page == _BOOKMARK_PAGE
    assert repo.get_bookmarks_for_item("i1") == [bookmark]


def test_institution_service_constructs_real_entities() -> None:
    """`Organization()`, `Department()`, ... all resolved only via TYPE_CHECKING."""
    from app.ecosystem.repositories.ecosystem_repository_impl import (
        InMemoryInstitutionRepository,
    )
    from app.ecosystem.services.institution_service import InstitutionService

    repo = InMemoryInstitutionRepository()
    service = InstitutionService(repo)

    org = service.create_organization("Acme", "university")
    department = service.add_department(org.id, "Research")

    assert type(org).__name__ == "Organization"
    assert type(department).__name__ == "Department"
    assert repo.get_organization(org.id) is not None


def test_organisation_type_stays_free_form_and_never_raises() -> None:
    """`Organization.org_type` is declared `OrgType` but assigned a raw `str`.

    Nothing ever reads ``org_type.value`` -- the only ``.value`` read in the
    ecosystem repository is ``LibraryItem.item_type.value`` -- so the value is
    genuinely free-form and the API accepts any string. Coercing it with
    ``OrgType(org_type)`` would turn an unvalidated value into an unhandled
    ``ValueError`` (HTTP 500) for any caller passing e.g. ``"school"``.

    This test pins the *safe* behaviour so the type mismatch cannot later be
    "fixed" by adding an unguarded coercion.
    """
    from app.ecosystem.domain.entities.institution import OrgType
    from app.ecosystem.repositories.ecosystem_repository_impl import (
        InMemoryInstitutionRepository,
    )
    from app.ecosystem.services.institution_service import InstitutionService

    repo = InMemoryInstitutionRepository()

    known = InstitutionService(repo).create_organization("Acme", "university")
    assert known.org_type == "university"
    assert OrgType(known.org_type) is OrgType.university

    # A value outside the enum must still be accepted rather than raising.
    free_form = InstitutionService(repo).create_organization("Other", "school")
    assert free_form.org_type == "school"


def test_distribution_service_constructs_real_entities() -> None:
    """`DistributionPackage()`, `SyncOperation()`, ... six previously fatal names."""
    from app.ecosystem.repositories.ecosystem_repository_impl import (
        InMemoryDistributionRepository,
    )
    from app.ecosystem.services.distribution_service import DistributionService

    repo = InMemoryDistributionRepository()

    package = DistributionService(repo).create_package(
        name="Pkg", description="d", content_type="file", version="1.0.0", created_by="u"
    )

    assert type(package).__name__ == "DistributionPackage"
    assert repo.get_package(package.id) is not None


def test_ecosystem_research_service_constructs_real_entities() -> None:
    """Eight runtime-constructed names in one module."""
    from app.ecosystem.repositories.ecosystem_repository_impl import (
        InMemoryResearchRepository,
    )
    from app.ecosystem.services.research_service import ResearchService

    repo = InMemoryResearchRepository()

    project = ResearchService(repo).create_project("Proj", "desc")

    assert type(project).__name__ == "ResearchProject"
    assert repo.get_project(project.id) is not None


def test_package_validation_services_construct_real_reports() -> None:
    """`PackageValidationReport()` in both the service and the exchange flow."""
    from app.collaboration.repositories.collaboration_repository_impl import (
        InMemoryCurriculumExchangeRepository,
    )
    from app.collaboration.services.curriculum_exchange_service import (
        CurriculumExchangeService,
    )

    repo = InMemoryCurriculumExchangeRepository()
    service = CurriculumExchangeService(repo)

    package = service.create_package(
        name="Pkg",
        description="d",
        package_type="course",
        version="1.0.0",
        author="a",
        source_institution="i",
        checksum="a" * 64,
        signature="sig",
        license="CC-BY",
        compatibility=">=1.0",
    )
    report = service.validate_package(package.id)

    assert type(report).__name__ == "PackageValidationReport"


def test_collaboration_and_ecosystem_areas_are_registered() -> None:
    """The point of the repair: both areas exist on the real router."""
    from fastapi.routing import APIRoute

    from app.api.v1.router import api_v1_router

    mounted = {r.path for r in api_v1_router.routes if isinstance(r, APIRoute)}

    assert any(p.startswith("/api/v1/collaboration") for p in mounted), sorted(mounted)[:10]
    assert any(p.startswith("/api/v1/ecosystem") for p in mounted)
    assert not any(p.startswith("/api/v1/api/v1/") for p in mounted)


def test_service_modules_import_entity_names_at_runtime() -> None:
    """Belt-and-braces: the promoted names are real module globals.

    The call-through tests above would catch a regression, but this states the
    invariant directly and localises a future failure to a single module.
    """
    expectations = {
        "app.collaboration.services.curriculum_exchange_service": "PackageValidationReport",
        "app.collaboration.services.package_validation_service": "PackageValidationReport",
        "app.ecosystem.services.distribution_service": "DistributionPackage",
        "app.ecosystem.services.institution_service": "Organization",
        "app.ecosystem.services.library_service": "Bookmark",
        "app.ecosystem.services.marketplace_service": "InstallationRecord",
        "app.ecosystem.services.research_service": "ResearchProject",
    }

    missing: dict[str, list[str]] = {}
    for module_name, attribute in expectations.items():
        module = importlib.import_module(module_name)
        absent = [attribute] if not hasattr(module, attribute) else []
        if absent:
            missing[module_name] = absent

    assert not missing, missing


def test_repository_interfaces_stay_out_of_runtime_globals() -> None:
    """Interfaces remain annotation-only on purpose.

    Their in-memory implementations are themselves ``TYPE_CHECKING``-gated, so
    promoting the interface imports would create a runtime import cycle and
    would break ``mypy --strict``. Only entity classes are promoted.
    """
    from app.ecosystem.services import library_service

    assert not hasattr(library_service, "ILibraryRepository")
