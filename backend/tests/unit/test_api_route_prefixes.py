"""Regression test for doubled API route prefixes.

``api_v1_router`` is created as ``APIRouter(prefix="/api/v1")`` and the
feature routers are included into it. Thirteen of those sub-routers *also*
declared their own ``prefix="/api/v1/<area>"``, so FastAPI concatenated the
two and mounted every one of their endpoints at::

    /api/v1/api/v1/analytics/...
    /api/v1/api/v1/collaboration/...
    /api/v1/api/v1/ecosystem/...

544 of this fork's 582 distinct paths were therefore unreachable at their
documented paths. The routers that got it right (authentication, users,
sessions, audit) declared ``prefix="/auth"`` etc. with no version segment,
and the frontend only ever called ``/api/v1/auth/*`` -- so nothing depended
on the doubled form and the fix is purely additive reachability.

The collaboration and ecosystem areas were doubly broken: their route
modules additionally imported sibling packages through bare absolute paths
(``from repositories...``, ``from services...``) that do not exist, so they
raised ``ModuleNotFoundError`` on import, every ``include_router`` was
swallowed by the ``try/except (ImportError, AttributeError)`` in
``app/api/v1/router.py``, and only 2 of their 93 paths were mounted at all.
"""

from __future__ import annotations

import pytest
from fastapi.routing import APIRoute

from app.api.v1.router import api_v1_router

DOUBLED = "/api/v1/api/v1"


def _paths() -> list[str]:
    # APIRouter.routes is list[BaseRoute]; only APIRoute carries a path.
    return [r.path for r in api_v1_router.routes if isinstance(r, APIRoute)]


class TestRoutePrefixes:
    def test_no_route_is_mounted_at_a_doubled_prefix(self):
        doubled = [p for p in _paths() if DOUBLED in p]
        assert doubled == [], f"{len(doubled)} routes mounted at {DOUBLED}: {doubled[:5]}"

    def test_routers_are_included_at_all(self):
        # A large surface is registered; this guards against the prefix fix
        # being "solved" by dropping the includes.
        assert len(_paths()) > 700

    @pytest.mark.parametrize(
        "area",
        [
            "analytics",
            "lms",
            "simulation",
            "developer",
            "quality",
            "production",
            "optimization",
            "standards",
            "content-studio",
            "certification",
            # Broken by the bare-absolute-import defect fixed alongside this:
            # their route modules could not import, so these areas mounted
            # almost nothing at all.
            "collaboration",
            "ecosystem",
        ],
    )
    def test_each_area_is_reachable_under_its_documented_prefix(self, area):
        assert any(p.startswith(f"/api/v1/{area}/") for p in _paths()), (
            f"no routes under /api/v1/{area}/"
        )

    def test_collaboration_and_ecosystem_surface_is_actually_mounted(self):
        paths = _paths()
        collab = [p for p in paths if p.startswith("/api/v1/collaboration/")]
        ecosystem = [p for p in paths if p.startswith("/api/v1/ecosystem/")]
        # Guards against a "fix" that silently drops the whole surface.
        assert len(collab) > 30
        assert len(ecosystem) > 20

    def test_working_areas_are_unchanged(self):
        paths = _paths()
        assert any(p.startswith("/api/v1/auth/") for p in paths)
        assert any(p.startswith("/api/v1/users") for p in paths)
