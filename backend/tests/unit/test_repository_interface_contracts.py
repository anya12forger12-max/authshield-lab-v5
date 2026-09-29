"""Regression tests for repository-interface contract defects.

Every one of these services called a repository method that existed on
neither the ABC nor (mostly) the concrete in-memory implementation, so the
call raised ``AttributeError`` at runtime:

* ``CompetencyService.start_competency`` used to call
  ``update_progress("", {}) or create_competency_progress(...)``. No progress
  record is ever keyed ``""``, so the left side always returned ``None`` and
  the right side did not exist -- the first call *always* raised. It now
  calls ``create_progress`` directly.
* ``PerformanceService.get_benchmarks(None)`` called ``find_all()``, which
  was declared on no implementation.
* ``IDiagnosticTraceRepository`` had no ``update()`` at all, so
  ``add_span_to_trace`` raised.

These tests drive the **real** in-memory repositories on purpose. A
``MagicMock()`` repository fabricates any attribute on demand, which is
precisely why these crashes survived a fully green unit suite.
"""

from __future__ import annotations

import pytest

from app.lms.repositories.lms_repository_impl import InMemoryCompetencyRepository
from app.lms.services.competency_service import CompetencyService
from app.optimization.repositories.optimization_repository_impl import (
    InMemoryDiagnosticTraceRepository,
)
from app.quality.repositories.quality_repository_impl import (
    InMemoryBenchmarkHistoryRepository,
    InMemoryBenchmarkRepository,
    InMemoryPerformanceReportRepository,
)
from app.quality.services.performance_service import PerformanceService


@pytest.fixture
def competency_service() -> CompetencyService:
    return CompetencyService(InMemoryCompetencyRepository())  # type: ignore[arg-type]


@pytest.fixture
def performance_service() -> PerformanceService:
    return PerformanceService(
        InMemoryBenchmarkRepository(),  # type: ignore[arg-type]
        InMemoryPerformanceReportRepository(),  # type: ignore[arg-type]
        InMemoryBenchmarkHistoryRepository(),  # type: ignore[arg-type]
    )


class TestCompetencyStart:
    def test_first_call_succeeds(self, competency_service):
        # Regression: every call raised AttributeError because
        # update_progress("", {}) always returned None and
        # create_competency_progress did not exist.
        progress = competency_service.start_competency("learner-1", "comp-1")
        assert progress["learner_id"] == "learner-1"
        assert progress["competency_id"] == "comp-1"
        assert progress["status"] == "in_progress"

    def test_record_is_persisted_and_reachable(self, competency_service):
        created = competency_service.start_competency("learner-1", "comp-1")
        repo = competency_service._repo
        stored = repo.get_progress("learner-1", "comp-1")
        assert len(stored) == 1
        assert stored[0]["id"] == created["id"]

    def test_second_call_is_rejected_not_duplicated(self, competency_service):
        competency_service.start_competency("learner-1", "comp-1")
        # The service deliberately refuses to restart an in-progress record.
        with pytest.raises(ValueError, match="already has competency"):
            competency_service.start_competency("learner-1", "comp-1")
        # ...and it did not create a second record.
        assert len(competency_service._repo.get_progress("learner-1", "comp-1")) == 1


class TestBenchmarkFindAll:
    def test_find_all_is_implemented(self, performance_service):
        # Regression: BenchmarkRepository had no find_all().
        assert performance_service.get_benchmarks(None) == []

    def test_find_all_reflects_saved_benchmarks(self, performance_service):
        repo = performance_service._benchmark_repo
        benchmark = repo.save(type("B", (), {"id": "b1", "name": "b"})())
        found = performance_service.get_benchmarks(None)
        assert [b.id for b in found] == [benchmark.id]


class TestDiagnosticTraceUpdate:
    def test_update_exists_on_the_interface(self):
        repo = InMemoryDiagnosticTraceRepository()
        # Regression: no update() existed anywhere on the interface.
        assert hasattr(repo, "update")

    def test_update_round_trips(self):
        repo = InMemoryDiagnosticTraceRepository()
        created = repo.create({"name": "trace", "spans_json": "[]", "total_duration_ms": 0})
        updated = repo.update(created["id"], {"spans_json": '[{"a":1}]'})
        assert updated is not None
        assert updated["spans_json"] == '[{"a":1}]'

    def test_update_missing_id_returns_none(self):
        repo = InMemoryDiagnosticTraceRepository()
        assert repo.update("does-not-exist", {"spans_json": "[]"}) is None
