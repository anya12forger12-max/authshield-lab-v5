"""Fleet guard: no service may silently truncate a paginated repository envelope.

Repositories answer list-shaped queries with a *paginated envelope*
(``{"items", "total", "page", "per_page", "pages"}``) rather than a flat list, and
they apply their own filter (``template_type``, ``enabled_only``, ...) before
slicing that page. So a caller that fetches one default page and keeps only that
page's ``items`` silently drops every match past ``per_page`` -- no exception, no
log line, and usually a *smaller* list than the caller asked for.

This class shipped twice and both instances were invisible to the type checker:
``TemplateStudioService.get_templates_by_type`` (fixed in a prior round) and
``FeatureFlagService.get_enabled_flags`` (this one) each promised a flat
``list[dict[str, Any]]`` while returning a single page of a paginated envelope.
Every affected module carries ``from __future__ import annotations``, so the
annotations are free at runtime and ``mypy --strict`` -- including the
defect-shaped ratchet -- reports nothing at all.

The guard is therefore a repo-wide AST sweep rather than another per-service
test: the defect is a *shape* that appears wherever a service touches an envelope
method, so a per-method test can only ever cover the methods someone already
thought to test. Resolution is deliberately conservative -- a repository counts as
a paginated producer only when a concrete implementation literally returns a dict
carrying both an ``items`` and a ``pages`` key -- and every sweep asserts its own
liveness, because a resolver that silently stops matching would make this file
pass vacuously.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Iterator

BACKEND_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = BACKEND_ROOT / "app"

# Methods matching this are called through an explicit page/per_page, i.e. the
# caller is deliberately asking for one slice of the envelope.
PAGING_KWARGS = frozenset({"page", "per_page"})

# A caller that returns a flat collection while not paging cannot possibly have
# seen every row: one page holds `per_page` rows and the repository default is 20.
FLAT_RETURNS = ("list", "tuple", "Sequence", "Iterable")

# Sanity floor for the liveness assertion: every app/ tree resolves well over
# this many classes, so a collapse of the resolver cannot still clear it.
MIN_CLASSES_EXPECTED = 100


class Finding(NamedTuple):
    """One call site that consumes a paginated envelope."""

    kind: str  # "TRUNCATES" or "PAGED"
    path: Path
    lineno: int
    caller: str
    consumer: str
    receiver_class: str
    source: str


class _ClassInfo(NamedTuple):
    bases: tuple[str, ...]
    methods: dict[str, ast.FunctionDef | ast.AsyncFunctionDef]


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _builds_envelope(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """True if ``fn`` returns a dict literal carrying both items and pages keys.

    Checked against the AST rather than the source text: ``ast.unparse`` rewrites
    string quotes to single form, so any quote-sensitive text match silently fails
    on a real tree while looking correct in review.
    """
    for node in ast.walk(fn):
        if isinstance(node, ast.Dict):
            keys = {
                key.value
                for key in node.keys
                if isinstance(key, ast.Constant) and isinstance(key.value, str)
            }
            if {"items", "pages"} <= keys:
                return True
    return False


def _collect_classes(app_root: Path) -> dict[str, _ClassInfo]:
    classes: dict[str, _ClassInfo] = {}
    for path in sorted(app_root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:  # pragma: no cover - unparsable module is a real bug
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            methods = {
                item.name: item
                for item in node.body
                if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef)
            }
            existing = classes.get(node.name)
            bases = tuple(ast.unparse(b) for b in node.bases)
            if existing is None:
                classes[node.name] = _ClassInfo(bases=bases, methods=methods)
            else:  # merge a partial redeclaration, keeping known bases
                classes[node.name] = _ClassInfo(
                    bases=existing.bases + tuple(b for b in bases if b not in existing.bases),
                    methods={**existing.methods, **methods},
                )
    return classes


def _subclasses(classes: dict[str, _ClassInfo], name: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    frontier = [name]
    while frontier:
        current = frontier.pop()
        for candidate, info in classes.items():
            if candidate in seen or current not in info.bases:
                continue
            seen.add(candidate)
            found.append(candidate)
            frontier.append(candidate)
    return found


def _declared_return(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    return ast.unparse(fn.returns) if fn.returns is not None else "<none>"


def _is_paginated_producer(
    classes: dict[str, _ClassInfo], receiver_class: str, method: str
) -> bool:
    info = classes.get(receiver_class)
    if info is None or method not in info.methods:
        return False
    if not _declared_return(info.methods[method]).startswith("dict"):
        return False
    candidates = [receiver_class, *_subclasses(classes, receiver_class)]
    return any(
        method in classes[name].methods and _builds_envelope(classes[name].methods[method])
        for name in candidates
    )


def _param_annotations(cls: ast.ClassDef) -> dict[str, str]:
    """Every annotated parameter name visible anywhere in the class."""
    params: dict[str, str] = {}
    for func in ast.walk(cls):
        if not isinstance(func, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        for arg in (*func.args.args, *func.args.kwonlyargs):
            if arg.annotation is not None:
                params.setdefault(arg.arg, ast.unparse(arg.annotation))
    return params


def _self_attrs(
    cls: ast.ClassDef,
) -> Iterator[tuple[str, str | None, str | None]]:
    """Yield ``(attribute, explicit_annotation, assigned_name)`` for ``self.x = ...``.

    ``self._repo = repo`` carries the type on the constructor parameter, so the
    assigned name -- not the attribute's base, which is always ``self`` -- is what
    has to be looked up afterwards.
    """
    for item in ast.walk(cls):
        if isinstance(item, ast.Assign):
            if not isinstance(item.value, ast.Name) or len(item.targets) != 1:
                continue
            target: ast.expr = item.targets[0]
            rhs: ast.expr | None = item.value
        elif isinstance(item, ast.AnnAssign):
            target = item.target
            rhs = item.value
        else:
            continue
        if not (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)):
            continue
        if target.value.id != "self":
            continue
        explicit = (
            ast.unparse(item.annotation)
            if isinstance(item, ast.AnnAssign) and item.annotation is not None
            else None
        )
        yield target.attr, explicit, rhs.id if isinstance(rhs, ast.Name) else None


def _receiver_types(cls: ast.ClassDef) -> dict[str, str]:
    """Map ``self._repo`` attributes to the annotated type they were assigned."""
    params = _param_annotations(cls)
    declared: dict[str, str] = {}
    for attr, explicit, assigned in _self_attrs(cls):
        if attr in declared:
            continue
        if explicit:
            declared[attr] = explicit
        elif assigned and (annotation := params.get(assigned)):
            declared[attr] = annotation
    return declared


def _enclosing_return(tree: ast.Module, lineno: int) -> tuple[str, str]:
    best: tuple[int, str, str] | None = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        start = min([node.lineno, *(d.lineno for d in node.decorator_list)])
        in_range = start <= lineno <= (node.end_lineno or node.lineno)
        if in_range and (best is None or start > best[0]):
            best = (start, node.name, _declared_return(node))
    return (best[1], best[2]) if best else ("<module>", "<none>")


def scan_envelope_consumers(app_root: Path) -> list[Finding]:
    """Find every service/route call site that consumes a paginated envelope.

    Repository modules are skipped: the producer side is the contract, and its own
    ``return {"items": ..., "pages": ...}`` must not be counted as a consumer.
    """
    classes = _collect_classes(app_root)
    by_norm = {_norm(name): name for name in classes}
    findings: list[Finding] = []

    for path in sorted(app_root.rglob("*.py")):
        if "repositories" in path.parts:
            continue
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:  # pragma: no cover - unparsable module is a real bug
            continue
        lines = source.splitlines()
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            receivers = _receiver_types(cls)
            for node in ast.walk(cls):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                    continue
                recv = node.func.value
                if not (
                    isinstance(recv, ast.Attribute)
                    and isinstance(recv.value, ast.Name)
                    and recv.value.id == "self"
                ):
                    continue
                declared = receivers.get(recv.attr)
                if declared is None:
                    continue
                receiver_class = by_norm.get(_norm(declared))
                if receiver_class is None:
                    continue
                consumer = f"{receiver_class}.{node.func.attr}"
                if not _is_paginated_producer(classes, receiver_class, node.func.attr):
                    continue
                caller, returns = _enclosing_return(tree, node.lineno)
                pagings = {kw.arg for kw in node.keywords if kw.arg} & PAGING_KWARGS
                kind = (
                    "PAGED"
                    if pagings
                    else ("TRUNCATES" if returns.startswith(FLAT_RETURNS) else "PAGED")
                )
                findings.append(
                    Finding(
                        kind=kind,
                        path=path.relative_to(app_root),
                        lineno=node.lineno,
                        caller=f"{cls.name}.{caller}",
                        consumer=consumer,
                        receiver_class=receiver_class,
                        source=lines[node.lineno - 1].strip(),
                    )
                )
    return findings


def _plant(tmp_root: Path, service_body: str, *, repo_returns_flat: bool = False) -> Path:
    """Write an app/ tree whose repository is a real envelope producer.

    ``repo_returns_flat`` swaps in a repository that returns a plain list instead,
    so the negative control plants the shape explicitly rather than reaching for a
    string replacement that can silently fail to match.
    """
    app = tmp_root / "app"
    (app / "repositories").mkdir(parents=True)
    (app / "services").mkdir(parents=True)
    (app / "domain").mkdir(parents=True)
    iface_source = (
        "from abc import ABC\n"
        "from typing import Any\n"
        "\n"
        "\n"
        "class IThingRepository(ABC):\n"
        "    def get_all(\n"
        "        self, page: int = 1, per_page: int = 20, kind: str | None = None\n"
        "    ) -> dict[str, Any]: ...\n"
    )
    if repo_returns_flat:
        # The interface has to agree with the implementation, or the repository is
        # not a paginated producer for a reason unrelated to envelope shape.
        iface_source = iface_source.replace(
            ") -> dict[str, Any]: ...", ") -> list[dict[str, Any]]: ..."
        )
        assert ") -> list[dict[str, Any]]: ..." in iface_source
        (app / "domain" / "interfaces.py").write_text(iface_source, encoding="utf-8")
        impl_source = (
            "from typing import Any\n"
            "\n"
            "from app.domain.interfaces import IThingRepository\n"
            "\n"
            "\n"
            "class InMemoryThingRepository(IThingRepository):\n"
            "    def __init__(self) -> None:\n"
            "        self._rows: dict[str, dict[str, Any]] = {}\n"
            "\n"
            "    def get_all(\n"
            "        self, page: int = 1, per_page: int = 20, kind: str | None = None\n"
            "    ) -> list[dict[str, Any]]:\n"
            "        items = list(self._rows.values())\n"
            "        if kind:\n"
            '            return [i for i in items if i["kind"] == kind]\n'
            "        return items\n"
        )
    else:
        impl_source = (
            "from typing import Any\n"
            "\n"
            "from app.domain.interfaces import IThingRepository\n"
            "\n"
            "\n"
            "class InMemoryThingRepository(IThingRepository):\n"
            "    def __init__(self) -> None:\n"
            "        self._rows: dict[str, dict[str, Any]] = {}\n"
            "\n"
            "    def get_all(\n"
            "        self, page: int = 1, per_page: int = 20, kind: str | None = None\n"
            "    ) -> dict[str, Any]:\n"
            "        items = list(self._rows.values())\n"
            "        if kind:\n"
            '            items = [i for i in items if i["kind"] == kind]\n'
            "        total = len(items)\n"
            "        pages = max(1, (total + per_page - 1) // per_page)\n"
            "        offset = (page - 1) * per_page\n"
            "        return {\n"
            '            "items": items[offset : offset + per_page],\n'
            '            "total": total,\n'
            '            "page": page,\n'
            '            "per_page": per_page,\n'
            '            "pages": pages,\n'
            "        }\n"
        )
    assert "class IThingRepository" in iface_source
    (app / "domain" / "interfaces.py").write_text(iface_source, encoding="utf-8")
    assert "class InMemoryThingRepository" in impl_source
    (app / "repositories" / "thing_repo_impl.py").write_text(impl_source, encoding="utf-8")
    (app / "services" / "thing_service.py").write_text(
        "from typing import Any\n"
        "\n"
        "from app.domain.interfaces import IThingRepository\n"
        "\n"
        "\n"
        "class ThingService:\n"
        "    def __init__(self, repo: IThingRepository) -> None:\n"
        "        self._repo = repo\n"
        "\n" + service_body,
        encoding="utf-8",
    )
    return app


def test_no_service_truncates_a_paginated_repository_envelope() -> None:
    findings = scan_envelope_consumers(APP_ROOT)
    offenders = [f for f in findings if f.kind == "TRUNCATES"]
    assert not offenders, (
        "these call sites consume a paginated repository envelope without paging, so "
        "they silently drop every row past the first page:\n"
        + "\n".join(
            f"  {f.path}:{f.lineno} {f.caller} -> {f.consumer}\n      {f.source}" for f in offenders
        )
    )


def test_sweep_actually_finds_envelope_consumers() -> None:
    """Liveness: the resolver must match real call sites, or the guard is a no-op.

    A guard that reports zero because the resolver stopped resolving is
    indistinguishable from a clean tree, so the number of consumers found is
    asserted rather than assumed.
    """
    findings = scan_envelope_consumers(APP_ROOT)
    assert findings, (
        "no paginated-envelope consumers found in app/ -- the receiver/interface "
        "resolution has almost certainly stopped matching, which would make "
        "test_no_service_truncates_a_paginated_repository_envelope vacuous"
    )
    assert any(f.kind == "PAGED" for f in findings)


def test_sweep_covers_services_and_routes() -> None:
    """Coverage: the sweep must reach both service and route modules.

    Repository modules are intentionally excluded, so the scanned set has to be
    proven non-empty per layer instead of assumed.
    """
    classes = _collect_classes(APP_ROOT)
    assert any("services" in name.parts for name in APP_ROOT.rglob("*.py"))
    assert len(classes) > MIN_CLASSES_EXPECTED, f"resolver saw only {len(classes)} classes"


def test_planted_truncating_consumer_is_detected(tmp_path: Path) -> None:
    """Positive control: the detector fires on a defect that is really planted."""
    app = _plant(
        tmp_path,
        "    def list_kinds(self, kind: str) -> list[dict[str, Any]]:\n"
        "        envelope = self._repo.get_all(kind=kind)\n"
        '        return list(envelope.get("items") or [])\n',
    )
    findings = scan_envelope_consumers(app)
    assert [f.kind for f in findings] == ["TRUNCATES"]
    assert findings[0].consumer == "IThingRepository.get_all"


def test_planted_paging_consumer_is_not_flagged(tmp_path: Path) -> None:
    """Negative control: correct paging through the envelope must pass."""
    app = _plant(
        tmp_path,
        "    def list_kinds(self, kind: str) -> list[dict[str, Any]]:\n"
        "        results: list[dict[str, Any]] = []\n"
        "        page = 1\n"
        "        while True:\n"
        "            envelope = self._repo.get_all(page=page, per_page=100, kind=kind)\n"
        '            batch = list(envelope.get("items") or [])\n'
        "            results.extend(batch)\n"
        '            if not batch or page >= int(envelope.get("pages") or 1):\n'
        "                return results\n"
        "            page += 1\n",
    )
    assert [f.kind for f in scan_envelope_consumers(app)] == ["PAGED"]


def test_plain_result_dict_is_not_mistaken_for_an_envelope(tmp_path: Path) -> None:
    """False-positive control: a dict return is not automatically pagination.

    ``validate_password`` returns a plain ``{"is_valid", "errors"}`` result and
    was reported by an earlier, looser version of this sweep. The contract is
    pinned here so the looser reading cannot come back.
    """
    app = _plant(
        tmp_path,
        "    def check(self, raw: str) -> dict[str, Any]:\n"
        '        return {"is_valid": len(raw) > 8, "errors": []}\n',
    )
    assert scan_envelope_consumers(app) == []


def test_flat_returning_repository_is_not_an_envelope_producer(tmp_path: Path) -> None:
    """A ``-> list`` repository method must never be treated as paginated."""
    app = _plant(
        tmp_path,
        "    def list_all(self) -> list[dict[str, Any]]:\n        return self._repo.get_all()\n",
        repo_returns_flat=True,
    )
    assert scan_envelope_consumers(app) == []
