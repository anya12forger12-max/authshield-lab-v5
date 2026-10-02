"""No module may use a name at runtime that it binds only under TYPE_CHECKING.

Why this needs a dedicated guard: every one of these modules carries
`from __future__ import annotations`, so the annotation resolves for a type
checker and mypy reports nothing at all, while the name is simply absent at
import time. The first call raises `NameError`. That is exactly how six service
files shipped entity classes that were constructed from names existing only for
the type checker.

Detection is scope-aware, and each of the following was arrived at by a first
implementation getting it wrong -- the synthetic tests at the bottom of this
module pin every one of them, so this guard cannot silently stop working:

* Annotations are strings under `from __future__ import annotations`, so they
  are not runtime uses. Counting them flags every abstract signature in the
  interfaces packages. They *are* runtime uses in a module without that import,
  so the annotations are visited and filtered, not skipped outright.
* A name the module also imports function-locally is bound in the scope that
  uses it, so it is fine.
* A use is covered by a runtime binding in *any enclosing scope*, so bindings
  must be resolved per scope chain rather than per module.
* Visiting a statement's whole subtree and then visiting that subtree's nested
  scopes again visits each method twice, the second time outside its own scope,
  which silently discards every function-local binding.
"""

from __future__ import annotations

import ast
import builtins
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[2] / "app"

# A healthy application package is far larger than this; the floor only exists
# so that an empty or mis-resolved sweep cannot be mistaken for a clean one.
_MIN_MODULES = 100

_BUILTINS = set(dir(builtins))


def _is_type_checking(test: ast.expr) -> bool:
    if isinstance(test, ast.Name):
        return test.id == "TYPE_CHECKING"
    return isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"


def _branch_bindings(node: ast.If | ast.Try, *, include_type_checking: bool) -> set[str]:
    """Bindings introduced by every body of one branching statement."""
    blocks: list[list[ast.stmt]] = [node.body, node.orelse]
    finalbody = getattr(node, "finalbody", [])
    if finalbody:
        blocks.append(finalbody)
    blocks.extend(handler.body for handler in getattr(node, "handlers", []))

    total: set[str] = set()
    for block in blocks:
        total |= _statement_bindings(block, include_type_checking=include_type_checking)
    return total


def _statement_bindings(
    statements: list[ast.stmt], *, include_type_checking: bool = False
) -> set[str]:
    """Names bound by the statements of one scope, without entering nested scopes."""
    bound: set[str] = set()
    for node in statements:
        if isinstance(node, ast.If):
            if _is_type_checking(node.test):
                if include_type_checking:
                    bound |= _statement_bindings(node.body)
            else:
                bound |= _branch_bindings(node, include_type_checking=include_type_checking)
        elif isinstance(node, ast.Try):
            bound |= _branch_bindings(node, include_type_checking=include_type_checking)
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            bound.add(node.name)
        elif isinstance(node, ast.Import | ast.ImportFrom):
            bound.update((alias.asname or alias.name).split(".")[0] for alias in node.names)
        elif isinstance(node, ast.Assign):
            bound.update(t.id for t in node.targets if isinstance(t, ast.Name))
        elif isinstance(node, ast.AnnAssign | ast.AugAssign | ast.For | ast.AsyncFor):
            if isinstance(node.target, ast.Name):
                bound.add(node.target.id)
        elif isinstance(node, ast.With | ast.AsyncWith):
            bound.update(
                item.optional_vars.id
                for item in node.items
                if isinstance(item.optional_vars, ast.Name)
            )
    return bound


def _walrus_bindings(expression: ast.expr) -> set[str]:
    """A lambda body is a single expression: only `:=` targets bind in it."""
    return {
        node.target.id
        for node in ast.walk(expression)
        if isinstance(node, ast.NamedExpr) and isinstance(node.target, ast.Name)
    }


def _positional_arguments(
    node: ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda,
) -> list[ast.arg | None]:
    """Regular, keyword-only and star arguments; `*args`/`**kwargs` may be None."""
    arguments = node.args
    return [
        *arguments.posonlyargs,
        *arguments.args,
        *arguments.kwonlyargs,
        arguments.vararg,
        arguments.kwarg,
    ]


class _UnboundNameVisitor(ast.NodeVisitor):
    def __init__(self, guarded: set[str], *, lazy_annotations: bool) -> None:
        self.guarded = guarded
        self.lazy = lazy_annotations
        self.annotations: set[int] = set()
        self.scopes: list[set[str]] = [_BUILTINS]
        self.found: dict[str, int] = {}

    def _bound(self) -> set[str]:
        return set().union(*self.scopes)

    def _enter(self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> None:
        self.scopes.append(self._bound() | _statement_bindings(node.body))
        for statement in node.body:
            self.visit(statement)
        self.scopes.pop()

    def _defaults(self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda) -> None:
        # Decorators and default values are evaluated in the enclosing scope.
        # A lambda has no `decorator_list`, hence the getattr.
        for decorator in getattr(node, "decorator_list", []):
            self.visit(decorator)
        arguments = node.args
        for default in [*arguments.defaults, *arguments.kw_defaults]:
            if default is not None:
                self.visit(default)

    def _annotations(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        # Annotations must be visited too: `visit_FunctionDef` does not fall
        # through to generic_visit, so skipping them would make this detector
        # blind in a module lacking `from __future__ import annotations`, where a
        # TYPE_CHECKING-only annotation is a genuine import-time NameError.
        # Where that future import *is* present they resolve to strings, and the
        # annotation set filters them out, which is the intended behaviour.
        for argument in _positional_arguments(node):
            if argument is not None and argument.annotation is not None:
                self.visit(argument.annotation)
        if node.returns is not None:
            self.visit(node.returns)

    def visit_Name(self, node: ast.Name) -> None:
        if not isinstance(node.ctx, ast.Load):
            return
        if self.lazy and id(node) in self.annotations:
            return
        if node.id in self.guarded and node.id not in self._bound():
            self.found.setdefault(node.id, node.lineno)

    def visit_If(self, node: ast.If) -> None:
        if _is_type_checking(node.test):
            return  # the guarded branch never executes
        for statement in [*node.body, *node.orelse]:
            self.visit(statement)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._defaults(node)
        self._annotations(node)
        self._enter(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        # ast.NodeVisitor dispatches on the node class name, so this spelling is
        # the protocol's requirement rather than a mixed-case slip.
        self._defaults(node)
        self._annotations(node)
        self._enter(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self._defaults(node)  # a lambda has defaults but no annotations
        self.scopes.append(self._bound() | _walrus_bindings(node.body))
        self.visit(node.body)
        self.scopes.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in [*node.bases, *(keyword.value for keyword in node.keywords)]:
            self.visit(base)
        self._enter(node)

    def run(self, tree: ast.Module) -> None:
        if self.lazy:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    for argument in _positional_arguments(node):
                        if argument is not None and argument.annotation is not None:
                            self._mark(argument.annotation)
                    if node.returns is not None:
                        self._mark(node.returns)
                elif isinstance(node, ast.AnnAssign) and node.annotation is not None:
                    self._mark(node.annotation)
        for statement in tree.body:
            self.visit(statement)

    def _mark(self, annotation: ast.expr) -> None:
        self.annotations.update(id(child) for child in ast.walk(annotation))


def _unresolved_runtime_names(source: str) -> dict[str, int]:
    """Names `source` uses at runtime that no enclosing scope binds."""
    tree = ast.parse(source)
    lazy = any(
        isinstance(node, ast.ImportFrom)
        and node.module == "__future__"
        and any(alias.name == "annotations" for alias in node.names)
        for node in tree.body
    )
    guarded = _statement_bindings(
        [node for node in tree.body if isinstance(node, ast.If) and _is_type_checking(node.test)],
        include_type_checking=True,
    )
    guarded -= _statement_bindings(tree.body)
    if not guarded:
        return {}
    visitor = _UnboundNameVisitor(guarded, lazy_annotations=lazy)
    visitor.run(tree)
    return visitor.found


def _application_modules() -> list[Path]:
    return sorted(path for path in APP_ROOT.rglob("*.py") if path.is_file())


def test_detector_flags_a_name_used_only_under_type_checking() -> None:
    """A planted defect must be caught, so this guard can never go vacuous."""
    source = (
        "from __future__ import annotations\n"
        "from typing import TYPE_CHECKING\n"
        "if TYPE_CHECKING:\n"
        "    from .entities import Widget\n"
        "def build() -> Widget:\n"
        "    return Widget()\n"
    )
    assert _unresolved_runtime_names(source) == {"Widget": 6}


def test_detector_ignores_a_lazy_annotation() -> None:
    source = (
        "from __future__ import annotations\n"
        "from typing import TYPE_CHECKING\n"
        "if TYPE_CHECKING:\n"
        "    from .entities import Widget\n"
        "def build() -> Widget: ...\n"
    )
    assert _unresolved_runtime_names(source) == {}


def test_detector_flags_an_annotation_when_annotations_are_not_lazy() -> None:
    """Without the future import the annotation is evaluated, so it is a real use."""
    source = (
        "from typing import TYPE_CHECKING\n"
        "if TYPE_CHECKING:\n"
        "    from .entities import Widget\n"
        "def build() -> Widget: ...\n"
    )
    assert _unresolved_runtime_names(source) == {"Widget": 4}


def test_detector_honours_a_function_local_import() -> None:
    source = (
        "from __future__ import annotations\n"
        "from typing import TYPE_CHECKING\n"
        "if TYPE_CHECKING:\n"
        "    from .entities import Widget\n"
        "def build():\n"
        "    from .entities import Widget\n"
        "    return Widget()\n"
    )
    assert _unresolved_runtime_names(source) == {}


def test_detector_flags_a_use_outside_the_locally_imported_function() -> None:
    """The binding must be in an *enclosing* scope, not merely present somewhere."""
    source = (
        "from __future__ import annotations\n"
        "from typing import TYPE_CHECKING\n"
        "if TYPE_CHECKING:\n"
        "    from .entities import Widget\n"
        "def build():\n"
        "    from .entities import Widget\n"
        "    return Widget()\n"
        "def other():\n"
        "    return Widget()\n"
    )
    assert _unresolved_runtime_names(source) == {"Widget": 9}


def test_detector_catches_the_real_crash_shape() -> None:
    """The shipped shape: an entity imported for typing, built at runtime."""
    source = (
        "from __future__ import annotations\n"
        "from typing import TYPE_CHECKING\n"
        "if TYPE_CHECKING:\n"
        "    from .domain.entities.exchange import ExchangePackage\n"
        "class Service:\n"
        "    def __init__(self, repo) -> None:\n"
        "        self._repo = repo\n"
        "    def import_package(self, package_id: str) -> ExchangePackage:\n"
        "        package = self._repo.get_package(package_id)\n"
        "        return ExchangePackage(id=package_id)\n"
    )
    # Line 9 binds `package`; the first `ExchangePackage` *use* is the return.
    assert _unresolved_runtime_names(source) == {"ExchangePackage": 10}


def test_detector_resolves_an_enclosing_class_binding() -> None:
    """A class-level import binds every method that lexically encloses it."""
    source = (
        "from __future__ import annotations\n"
        "from typing import TYPE_CHECKING\n"
        "if TYPE_CHECKING:\n"
        "    from .entities import Widget\n"
        "class Service:\n"
        "    from .entities import Widget\n"
        "    def build(self):\n"
        "        return Widget()\n"
    )
    assert _unresolved_runtime_names(source) == {}


def test_application_has_modules_to_scan() -> None:
    """Coverage proof: an empty sweep must never be mistaken for a clean sweep."""
    modules = _application_modules()
    assert len(modules) > _MIN_MODULES, f"expected the app package, found {len(modules)}"


def test_no_module_uses_a_type_checking_only_name() -> None:
    """One aggregate sweep rather than one case per module.

    Parametrising over several hundred modules would inflate the suite's test
    count by more than half, which buries real regressions in noise. The failure
    message names every offending module and line, so a single case is easier to
    act on as well.
    """
    offenders: list[str] = []
    for module in _application_modules():
        unresolved = _unresolved_runtime_names(module.read_text(encoding="utf-8"))
        if unresolved:
            offenders.append(
                f"  {module.relative_to(APP_ROOT)}: "
                + ", ".join(f"{name} (line {line})" for name, line in sorted(unresolved.items()))
            )
    assert not offenders, (
        f"{len(offenders)} module(s) use these names at runtime but bind them only "
        "under TYPE_CHECKING, so the first call raises NameError:\n" + "\n".join(offenders)
    )
