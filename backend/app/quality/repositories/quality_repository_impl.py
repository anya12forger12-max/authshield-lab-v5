"""In-memory implementations of all quality repository interfaces."""

from __future__ import annotations

from typing import Any

from app.quality.domain.entities.accessibility_a11y import (
    A11yAudit,
    A11yProfile,
    A11yScorecard,
    KeyboardShortcut,
)
from app.quality.domain.entities.diagnostics import DiagnosticBundle, DiagnosticCheck
from app.quality.domain.entities.maintainability import BuildHealth, TechnicalDebtItem
from app.quality.domain.entities.observability import ApplicationMetric, ObservabilitySnapshot
from app.quality.domain.entities.performance import Benchmark, BenchmarkHistory, PerformanceReport
from app.quality.domain.entities.quality import ModuleHealth, QualityDashboard, QualityScore
from app.quality.domain.entities.release import Release, ReleaseNote, ReleaseReadiness
from app.quality.domain.entities.testing import CoverageReport, TestCase, TestSuite
from app.quality.domain.interfaces.repositories import (
    A11yAuditRepository,
    A11yProfileRepository,
    A11yScorecardRepository,
    ApplicationMetricRepository,
    BenchmarkHistoryRepository,
    BenchmarkRepository,
    BuildHealthRepository,
    CoverageReportRepository,
    DiagnosticBundleRepository,
    DiagnosticCheckRepository,
    KeyboardShortcutRepository,
    ModuleHealthRepository,
    ObservabilitySnapshotRepository,
    PerformanceReportRepository,
    QualityDashboardRepository,
    QualityScoreRepository,
    ReleaseNoteRepository,
    ReleaseReadinessRepository,
    ReleaseRepository,
    TechnicalDebtItemRepository,
    TestCaseRepository,
    TestSuiteRepository,
)


class InMemoryQualityScoreRepository(QualityScoreRepository):
    def __init__(self) -> None:
        self._data: dict[str, QualityScore] = {}

    def save(self, score: QualityScore) -> QualityScore:
        self._data[score.id] = score
        return score

    def find_by_category(self, category: str) -> list[QualityScore]:
        return [s for s in self._data.values() if s.category == category]

    def find_all(self) -> list[QualityScore]:
        return list(self._data.values())


class InMemoryQualityDashboardRepository(QualityDashboardRepository):
    def __init__(self) -> None:
        self._data: dict[str, QualityDashboard] = {}

    def save(self, dashboard: QualityDashboard) -> QualityDashboard:
        self._data[dashboard.id] = dashboard
        return dashboard

    def find_latest(self) -> QualityDashboard | None:
        if not self._data:
            return None
        return max(self._data.values(), key=lambda d: d.generated_at)


class InMemoryModuleHealthRepository(ModuleHealthRepository):
    def __init__(self) -> None:
        self._data: dict[str, ModuleHealth] = {}

    def save(self, health: ModuleHealth) -> ModuleHealth:
        self._data[health.module_name] = health
        return health

    def find_by_module(self, module_name: str) -> ModuleHealth | None:
        return self._data.get(module_name)

    def find_all(self) -> list[ModuleHealth]:
        return list(self._data.values())


class InMemoryTestCaseRepository(TestCaseRepository):
    def __init__(self) -> None:
        self._data: dict[str, TestCase] = {}

    def save(self, test_case: TestCase) -> TestCase:
        self._data[test_case.id] = test_case
        return test_case

    def find_by_id(self, test_id: str) -> TestCase | None:
        return self._data.get(test_id)

    def find_by_type(self, test_type: str) -> list[TestCase]:
        return [t for t in self._data.values() if t.test_type.value == test_type]

    def find_by_module(self, module: str) -> list[TestCase]:
        return [t for t in self._data.values() if t.module == module]

    def find_all(self) -> list[TestCase]:
        return list(self._data.values())


class InMemoryTestSuiteRepository(TestSuiteRepository):
    def __init__(self) -> None:
        self._data: dict[str, TestSuite] = {}

    def save(self, suite: TestSuite) -> TestSuite:
        self._data[suite.id] = suite
        return suite

    def find_by_id(self, suite_id: str) -> TestSuite | None:
        return self._data.get(suite_id)

    def find_all(self) -> list[TestSuite]:
        return list(self._data.values())


class InMemoryCoverageReportRepository(CoverageReportRepository):
    def __init__(self) -> None:
        self._data: dict[str, CoverageReport] = {}

    def save(self, report: CoverageReport) -> CoverageReport:
        self._data[report.id] = report
        return report

    def find_latest(self) -> CoverageReport | None:
        if not self._data:
            return None
        return max(self._data.values(), key=lambda r: r.generated_at)


class InMemoryApplicationMetricRepository(ApplicationMetricRepository):
    def __init__(self) -> None:
        self._data: dict[str, ApplicationMetric] = {}

    def save(self, metric: ApplicationMetric) -> ApplicationMetric:
        self._data[metric.id] = metric
        return metric

    def find_by_name(self, name: str) -> list[ApplicationMetric]:
        return [m for m in self._data.values() if m.name == name]

    def find_all(self) -> list[ApplicationMetric]:
        return list(self._data.values())


class InMemoryObservabilitySnapshotRepository(ObservabilitySnapshotRepository):
    def __init__(self) -> None:
        self._data: dict[str, ObservabilitySnapshot] = {}

    def save(self, snapshot: ObservabilitySnapshot) -> ObservabilitySnapshot:
        self._data[snapshot.id] = snapshot
        return snapshot

    def find_latest(self) -> ObservabilitySnapshot | None:
        if not self._data:
            return None
        return max(self._data.values(), key=lambda s: s.captured_at)


class InMemoryDiagnosticCheckRepository(DiagnosticCheckRepository):
    def __init__(self) -> None:
        self._data: dict[str, DiagnosticCheck] = {}

    def save(self, check: DiagnosticCheck) -> DiagnosticCheck:
        self._data[check.id] = check
        return check

    def find_by_category(self, category: str) -> list[DiagnosticCheck]:
        return [c for c in self._data.values() if c.category == category]


class InMemoryDiagnosticBundleRepository(DiagnosticBundleRepository):
    def __init__(self) -> None:
        self._data: dict[str, DiagnosticBundle] = {}

    def save(self, bundle: DiagnosticBundle) -> DiagnosticBundle:
        self._data[bundle.id] = bundle
        return bundle

    def find_by_id(self, bundle_id: str) -> DiagnosticBundle | None:
        return self._data.get(bundle_id)

    def find_all(self) -> list[DiagnosticBundle]:
        return list(self._data.values())


class InMemoryA11yProfileRepository(A11yProfileRepository):
    def __init__(self) -> None:
        self._data: dict[str, A11yProfile] = {}

    def save(self, profile: A11yProfile) -> A11yProfile:
        self._data[profile.id] = profile
        return profile

    def find_by_name(self, name: str) -> A11yProfile | None:
        for p in self._data.values():
            if p.name == name:
                return p
        return None

    def find_all(self) -> list[A11yProfile]:
        return list(self._data.values())


class InMemoryA11yAuditRepository(A11yAuditRepository):
    def __init__(self) -> None:
        self._data: dict[str, A11yAudit] = {}

    def save(self, audit: A11yAudit) -> A11yAudit:
        self._data[audit.id] = audit
        return audit

    def find_by_id(self, audit_id: str) -> A11yAudit | None:
        return self._data.get(audit_id)

    def find_all(self) -> list[A11yAudit]:
        return list(self._data.values())


class InMemoryA11yScorecardRepository(A11yScorecardRepository):
    def __init__(self) -> None:
        self._data: dict[str, A11yScorecard] = {}

    def save(self, scorecard: A11yScorecard) -> A11yScorecard:
        self._data[scorecard.id] = scorecard
        return scorecard

    def find_by_category(self, category: str) -> list[A11yScorecard]:
        return [s for s in self._data.values() if s.category == category]

    def find_all(self) -> list[A11yScorecard]:
        return list(self._data.values())


class InMemoryKeyboardShortcutRepository(KeyboardShortcutRepository):
    def __init__(self) -> None:
        self._data: dict[str, KeyboardShortcut] = {}

    def save(self, shortcut: KeyboardShortcut) -> KeyboardShortcut:
        self._data[shortcut.id] = shortcut
        return shortcut

    def find_by_action(self, action: str) -> KeyboardShortcut | None:
        for s in self._data.values():
            if s.action == action:
                return s
        return None

    def find_all(self) -> list[KeyboardShortcut]:
        return list(self._data.values())


class InMemoryBenchmarkRepository(BenchmarkRepository):
    def __init__(self) -> None:
        self._data: dict[str, Benchmark] = {}

    def save(self, benchmark: Benchmark) -> Benchmark:
        self._data[benchmark.id] = benchmark
        return benchmark

    def find_by_name(self, name: str) -> list[Benchmark]:
        return [b for b in self._data.values() if b.name == name]

    def find_all(self) -> list[Benchmark]:
        return list(self._data.values())


class InMemoryPerformanceReportRepository(PerformanceReportRepository):
    def __init__(self) -> None:
        self._data: dict[str, PerformanceReport] = {}

    def save(self, report: PerformanceReport) -> PerformanceReport:
        self._data[report.id] = report
        return report

    def find_by_id(self, report_id: str) -> PerformanceReport | None:
        return self._data.get(report_id)

    def find_all(self) -> list[PerformanceReport]:
        return list(self._data.values())


class InMemoryBenchmarkHistoryRepository(BenchmarkHistoryRepository):
    def __init__(self) -> None:
        self._data: dict[str, BenchmarkHistory] = {}

    def save(self, history: BenchmarkHistory) -> BenchmarkHistory:
        self._data[history.id] = history
        return history

    def find_by_benchmark_name(self, name: str) -> BenchmarkHistory | None:
        for h in self._data.values():
            if h.benchmark_name == name:
                return h
        return None


class InMemoryTechnicalDebtItemRepository(TechnicalDebtItemRepository):
    def __init__(self) -> None:
        self._data: dict[str, TechnicalDebtItem] = {}

    def save(self, item: TechnicalDebtItem) -> TechnicalDebtItem:
        self._data[item.id] = item
        return item

    def find_by_category(self, category: str) -> list[TechnicalDebtItem]:
        return [i for i in self._data.values() if i.category == category]

    def find_all(self) -> list[TechnicalDebtItem]:
        return list(self._data.values())


class InMemoryBuildHealthRepository(BuildHealthRepository):
    def __init__(self) -> None:
        self._data: dict[str, BuildHealth] = {}

    def save(self, build: BuildHealth) -> BuildHealth:
        self._data[build.id] = build
        return build

    def find_by_status(self, status: str) -> list[BuildHealth]:
        return [b for b in self._data.values() if b.status == status]

    def find_all(self) -> list[BuildHealth]:
        return list(self._data.values())


class InMemoryReleaseRepository(ReleaseRepository):
    def __init__(self) -> None:
        self._data: dict[str, Release] = {}

    def save(self, release: Release) -> Release:
        self._data[release.id] = release
        return release

    def find_by_id(self, release_id: str) -> Release | None:
        return self._data.get(release_id)

    def find_by_version(self, version: str) -> Release | None:
        for r in self._data.values():
            if r.version == version:
                return r
        return None

    def find_all(self) -> list[Release]:
        return list(self._data.values())


class InMemoryReleaseReadinessRepository(ReleaseReadinessRepository):
    def __init__(self) -> None:
        self._data: dict[str, ReleaseReadiness] = {}

    def save(self, readiness: ReleaseReadiness) -> ReleaseReadiness:
        self._data[readiness.id] = readiness
        return readiness

    def find_by_release_id(self, release_id: str) -> ReleaseReadiness | None:
        for r in self._data.values():
            if r.release_id == release_id:
                return r
        return None


class InMemoryReleaseNoteRepository(ReleaseNoteRepository):
    def __init__(self) -> None:
        self._data: dict[str, ReleaseNote] = {}

    def save(self, note: ReleaseNote) -> ReleaseNote:
        self._data[note.id] = note
        return note

    def find_by_release_id(self, release_id: str) -> list[ReleaseNote]:
        return [n for n in self._data.values() if n.release_id == release_id]
