"""Every declarative ORM model in one shared registry must be valid.

Two defects hid behind a fully green suite, because nothing under ``app/``
imports these modules at runtime -- so ``import app.main`` succeeded, the app
booted, and all 952 tests passed while both were live.

1. ``ArticleVersionModel`` and ``ArticleCitationModel`` were declared with a bare
   ``Base`` -- no ``UUIDPrimaryKeyMixin``, no ``primary_key=True`` column -- so
   their tables had no primary key. That is an *import-time* failure, raised
   while the class is being registered::

       sqlalchemy.exc.ArgumentError: Mapper Mapper[ArticleVersionModel(
           collab_article_versions)] could not assemble any primary key columns

   ``app.collaboration.domain.models`` therefore could not be imported at all.

2. The ``app.ecosystem.domain.models`` relationships referenced their targets by
   bare string (``relationship("CitationModel")``). Twelve class names exist
   twice across packages in this one registry, so ``configure_mappers()``
   aborted with ``InvalidRequestError: Multiple classes found for path
   "CitationModel"`` -- and would abort again for the next ambiguous name. Those
   references are now fully qualified.

Both are registry-wide: ``configure_mappers()`` and ``Base.metadata.create_all()``
(the latter is ``init_db()``, called from the FastAPI lifespan) operate over
*every* mapped class, not just the ones a request touches.

These tests import every ``models`` module first, then assert the whole registry
is valid, so neither class of defect can come back unnoticed.
"""

from __future__ import annotations

import importlib
import pathlib
import pkgutil
from typing import Any

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Mapper, configure_mappers

import app
from app.shared.base_model import Base


def _model_module_names() -> tuple[list[str], list[str]]:
    """Every ``app.*`` module whose leaf name mentions ``models``.

    Returns the names plus any module that could not even be walked. Letting the
    walk abort would silently shrink the list, turning a broken model module into
    a quietly smaller sweep, so failures are collected and asserted on instead.
    """
    errors: list[str] = []

    def onerror(name: str) -> None:
        errors.append(name)

    discovered = [
        module.name
        for module in pkgutil.walk_packages(app.__path__, prefix="app.", onerror=onerror)
        if "models" in module.name.rsplit(".", 1)[-1]
    ]
    return sorted(set(discovered) | set(errors)), sorted(errors)


def _model_modules_on_disk() -> set[str]:
    """The same set derived from the filesystem, as an independent cross-check.

    This mirrors the walk filter exactly (``models`` in the leaf name) without
    importing anything, so it is unaffected by a module that fails to import.
    Comparing the two proves the sweep neither missed a module nor invented one,
    and it adapts to each repo's own size instead of a hardcoded count.
    """
    root = pathlib.Path(app.__path__[0])
    names: set[str] = set()
    for path in root.rglob("*.py"):
        parts = list(path.relative_to(root).with_suffix("").parts)
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        if parts and "models" in parts[-1]:
            names.add(".".join(["app", *parts]))
    return names


MODEL_MODULES, UNWALKABLE = _model_module_names()
COLLABORATION_MODELS = "app.collaboration.domain.models"
HAS_COLLABORATION = COLLABORATION_MODELS in MODEL_MODULES
MODELS_ON_DISK = _model_modules_on_disk()


def _mappers() -> list[Mapper[Any]]:
    return sorted(Base.registry.mappers, key=lambda mapper: mapper.class_.__name__)


@pytest.fixture(scope="module", autouse=True)
def _register_every_model() -> None:
    """Import every ``models`` module so every mapper reaches the registry."""
    for name in MODEL_MODULES:
        importlib.import_module(name)


def test_model_modules_are_discovered() -> None:
    """Guard the guard: the sweep must match what is actually on disk."""
    assert MODELS_ON_DISK, "no model modules found on disk -- wrong root?"
    assert sorted(MODELS_ON_DISK) == MODEL_MODULES
    assert "app.shared.models" in MODEL_MODULES


def test_every_model_package_is_walkable() -> None:
    """A package that cannot be walked is a broken model area, not an empty one."""
    assert UNWALKABLE == []


@pytest.mark.parametrize("module_name", MODEL_MODULES)
def test_every_model_module_imports(module_name: str) -> None:
    """A model module that cannot be imported is an invisible dead area.

    ``app/api/v1/router.py`` swallows ``ImportError`` around every
    ``include_router``, so a module that fails to import makes its whole area
    vanish from the route table without a trace.
    """
    importlib.import_module(module_name)


def test_every_declarative_model_has_a_primary_key() -> None:
    missing = [mapper.class_.__name__ for mapper in _mappers() if not list(mapper.primary_key)]
    assert missing == []


def test_configure_mappers_succeeds() -> None:
    """Registry-wide configuration; raises if any mapper cannot assemble a PK."""
    configure_mappers()
    assert _mappers()


def test_create_all_builds_every_registered_table() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    created = set(inspect(engine).get_table_names())
    expected = set(Base.metadata.tables)
    assert expected, "no tables were registered at all"
    assert expected <= created
    if HAS_COLLABORATION:
        assert "collab_article_versions" in created
        assert "collab_article_citations" in created


@pytest.mark.skipif(
    not HAS_COLLABORATION,
    reason="this repo has no collaboration model package",
)
@pytest.mark.parametrize("model_name", ["ArticleVersionModel", "ArticleCitationModel"])
def test_article_models_use_the_shared_uuid_primary_key(model_name: str) -> None:
    models = importlib.import_module(COLLABORATION_MODELS)
    mapper = inspect(getattr(models, model_name))
    assert [column.name for column in mapper.primary_key] == ["id"]
    assert mapper.columns["id"].default is not None
