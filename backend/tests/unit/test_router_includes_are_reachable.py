"""Every router the API v1 aggregator tries to include must actually be mounted.

``app/api/v1/router.py`` registers each area inside::

    try:
        from ...<area>.api.routes import router as <area>_router
        api_v1_router.include_router(<area>_router)
    except (ImportError, AttributeError):
        pass

That ``except: pass`` converts a hard failure into silence. A broken relative
import inside an area's models or validators makes the whole module
unimportable, the ``ImportError`` is swallowed, and the area simply disappears
from the route table while the test suite stays green -- 91 of 93 collaboration
and ecosystem endpoints once went missing this way, and the entire ``/policies
area was absent in three repos for the same reason.

A static check cannot catch this: a base class imported only under
``TYPE_CHECKING`` is invisible to a type checker, and a passing test count says
nothing about how many paths are mounted. The honest check is to resolve every
declared include and count the surface on the *running* app.
"""

from __future__ import annotations

import ast
import importlib
import pathlib

import pytest
from fastapi.routing import APIRoute, APIRouter

ROUTER_FILE = pathlib.Path(__file__).resolve().parents[2] / "app/api/v1/router.py"
API_V1_PREFIX = "/api/v1"

# Areas this aggregator is expected to register. Asserting the exact set is what
# stops "the surface is healthy" from being satisfied by deleting an include.
EXPECTED_AREAS = {
    "health",
    "auth",
    "users",
    "sessions",
    "audit",
    "defenses",
    "content",
    "content_studio",
    "lms",
    "simulation",
    "standards",
    "certification",
    "developer",
    "production",
    "quality",
    "ecosystem",
    "optimization",
    "collaboration",
    "analytics",
}

# Areas whose surface must stay mounted. Without these floors the whole
# guarantee could be satisfied by dropping the include_router calls, which is
# the opposite of the fix. Keys are the include aliases; ``defenses_router``
# serves the ``/policies`` paths.
MINIMUM_AREA_PATHS = {
    "defenses": 5,
    "collaboration": 30,
    "ecosystem": 20,
}


def _resolve(from_node: ast.ImportFrom) -> str:
    """Absolute module name for a (possibly relative) import inside the aggregator."""
    package = "app.api.v1"
    if from_node.level:
        base = package.split(".")
        if from_node.level > len(base):
            msg = f"relative import escapes the package: level={from_node.level}"
            raise AssertionError(msg)
        base = base[: len(base) - (from_node.level - 1)]
        prefix = ".".join(base)
        module = f"{prefix}.{from_node.module}" if from_node.module else prefix
    else:
        module = from_node.module or ""
    return module


def _declared_includes() -> list[tuple[str, str, str]]:
    """``(module, attribute, area)`` for every ``router as <area>_router`` import."""
    tree = ast.parse(ROUTER_FILE.read_text())
    found: list[tuple[str, str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        for alias in node.names:
            # ``from ...x import router as x_router`` -> asname carries the area.
            bound = alias.asname or alias.name
            if not bound.endswith("_router"):
                continue
            found.append((_resolve(node), alias.name, bound[: -len("_router")]))
    return found


INCLUDES = _declared_includes()


def _mounted_paths() -> set[str]:
    from app.main import app

    return {route.path for route in app.routes if isinstance(route, APIRoute)}


def test_the_includes_are_discovered() -> None:
    """Guard the guard: a parser bug must not report an empty, passing sweep."""
    assert INCLUDES, "no router includes parsed -- the AST walk is broken"
    assert {area for _, _, area in INCLUDES} == EXPECTED_AREAS


@pytest.mark.parametrize(("module", "attribute", "area"), INCLUDES, ids=[i[2] for i in INCLUDES])
def test_declared_router_module_imports(module: str, attribute: str, area: str) -> None:
    """The import the aggregator attempts must not raise."""
    imported = importlib.import_module(module)
    router = getattr(imported, attribute, None)
    assert isinstance(router, APIRouter), f"{area}: {module}.{attribute} is not an APIRouter"
    assert router.routes, f"{area}: {module}.{attribute} exposes no routes"


@pytest.mark.parametrize(("module", "attribute", "area"), INCLUDES, ids=[i[2] for i in INCLUDES])
def test_declared_router_is_mounted_on_the_app(module: str, attribute: str, area: str) -> None:
    """Each included router's routes must be present on the running application."""
    router: APIRouter = getattr(importlib.import_module(module), attribute)
    mounted = _mounted_paths()
    # APIRouter bakes its own prefix into each route's ``path`` at registration,
    # so ``route.path`` is already the child path and only the parent prefix is
    # still to be applied.
    missing = [
        f"{API_V1_PREFIX}{route.path}"
        for route in router.routes
        if isinstance(route, APIRoute) and f"{API_V1_PREFIX}{route.path}" not in mounted
    ]
    assert not missing, f"{area}: {len(missing)} route(s) not mounted, e.g. {missing[:3]}"


def test_no_router_is_mounted_at_a_doubled_prefix() -> None:
    """``APIRouter(prefix='/api/v1')`` plus a child ``/api/v1/<area>`` doubles up."""
    doubled = sorted(p for p in _mounted_paths() if p.startswith(f"{API_V1_PREFIX}{API_V1_PREFIX}"))
    assert not doubled, f"{len(doubled)} path(s) mounted at a doubled prefix: {doubled[:3]}"


@pytest.mark.parametrize(("area", "minimum"), sorted(MINIMUM_AREA_PATHS.items()))
def test_area_surface_is_not_reachable_by_deleting_the_include(area: str, minimum: int) -> None:
    """Floor on the mounted surface for the areas that once vanished silently."""
    prefixes = {
        f"{API_V1_PREFIX}{getattr(importlib.import_module(m), a).prefix}"
        for m, a, name in INCLUDES
        if name == area
    }
    assert prefixes, f"no declared include for the {area} area"
    mounted = _mounted_paths()
    matching = (
        path for path in mounted if any(path.startswith(p + "/") or path == p for p in prefixes)
    )
    count = sum(1 for _ in matching)
    assert count >= minimum, f"{area}: only {count} path(s) mounted, expected >= {minimum}"
