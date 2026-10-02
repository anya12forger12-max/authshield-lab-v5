from __future__ import annotations

from abc import ABC, abstractmethod

from app.quality.domain.entities.accessibility_a11y import A11yAudit, A11yProfile, A11yScorecard, KeyboardShortcut
from app.quality.domain.entities.diagnostics import DiagnosticBundle, DiagnosticCheck
from app.quality.domain.entities.maintainability import BuildHealth, TechnicalDebtItem
from app.quality.domain.entities.observability import ApplicationMetric, ObservabilitySnapshot
from app.quality.domain.entities.performance import Benchmark, BenchmarkHistory, PerformanceReport
from app.quality.domain.entities.quality import ModuleHealth, QualityDashboard, QualityScore
from app.quality.domain.entities.release import Release, ReleaseNote, ReleaseReadiness
from app.quality.domain.entities.testing import CoverageReport, TestCase, TestSuite


class QualityScoreRepository(ABC):
    @abstractmethod
    def save(self, score: QualityScore) -> QualityScore: ...

    @abstractmethod
    def find_by_category(self, category: str) -> list[QualityScore]: ...

    @abstractmethod
    def find_all(self) -> list[QualityScore]: ...


class QualityDashboardRepository(ABC):
    @abstractmethod
    def save(self, dashboard: QualityDashboard) -> QualityDashboard: ...

    @abstractmethod
    def find_latest(self) -> QualityDashboard | None: ...


class ModuleHealthRepository(ABC):
    @abstractmethod
    def save(self, health: ModuleHealth) -> ModuleHealth: ...

    @abstractmethod
    def find_by_module(self, module_name: str) -> ModuleHealth | None: ...

    @abstractmethod
    def find_all(self) -> list[ModuleHealth]: ...


class TestCaseRepository(ABC):
    @abstractmethod
    def save(self, test_case: TestCase) -> TestCase: ...

    @abstractmethod
    def find_by_id(self, test_id: str) -> TestCase | None: ...

    @abstractmethod
    def find_by_type(self, test_type: str) -> list[TestCase]: ...

    @abstractmethod
    def find_by_module(self, module: str) -> list[TestCase]: ...

    @abstractmethod
    def find_all(self) -> list[TestCase]: ...


class TestSuiteRepository(ABC):
    @abstractmethod
    def save(self, suite: TestSuite) -> TestSuite: ...

    @abstractmethod
    def find_by_id(self, suite_id: str) -> TestSuite | None: ...

    @abstractmethod
    def find_all(self) -> list[TestSuite]: ...


class CoverageReportRepository(ABC):
    @abstractmethod
    def save(self, report: CoverageReport) -> CoverageReport: ...

    @abstractmethod
    def find_latest(self) -> CoverageReport | None: ...


class ApplicationMetricRepository(ABC):
    @abstractmethod
    def save(self, metric: ApplicationMetric) -> ApplicationMetric: ...

    @abstractmethod
    def find_by_name(self, name: str) -> list[ApplicationMetric]: ...

    @abstractmethod
    def find_all(self) -> list[ApplicationMetric]: ...


class ObservabilitySnapshotRepository(ABC):
    @abstractmethod
    def save(self, snapshot: ObservabilitySnapshot) -> ObservabilitySnapshot: ...

    @abstractmethod
    def find_latest(self) -> ObservabilitySnapshot | None: ...


class DiagnosticCheckRepository(ABC):
    @abstractmethod
    def save(self, check: DiagnosticCheck) -> DiagnosticCheck: ...

    @abstractmethod
    def find_by_category(self, category: str) -> list[DiagnosticCheck]: ...


class DiagnosticBundleRepository(ABC):
    @abstractmethod
    def save(self, bundle: DiagnosticBundle) -> DiagnosticBundle: ...

    @abstractmethod
    def find_by_id(self, bundle_id: str) -> DiagnosticBundle | None: ...

    @abstractmethod
    def find_all(self) -> list[DiagnosticBundle]: ...


class A11yProfileRepository(ABC):
    @abstractmethod
    def save(self, profile: A11yProfile) -> A11yProfile: ...

    @abstractmethod
    def find_by_name(self, name: str) -> A11yProfile | None: ...

    @abstractmethod
    def find_all(self) -> list[A11yProfile]: ...


class A11yAuditRepository(ABC):
    @abstractmethod
    def save(self, audit: A11yAudit) -> A11yAudit: ...

    @abstractmethod
    def find_by_id(self, audit_id: str) -> A11yAudit | None: ...

    @abstractmethod
    def find_all(self) -> list[A11yAudit]: ...


class A11yScorecardRepository(ABC):
    @abstractmethod
    def save(self, scorecard: A11yScorecard) -> A11yScorecard: ...

    @abstractmethod
    def find_by_category(self, category: str) -> list[A11yScorecard]: ...

    @abstractmethod
    def find_all(self) -> list[A11yScorecard]: ...


class KeyboardShortcutRepository(ABC):
    @abstractmethod
    def save(self, shortcut: KeyboardShortcut) -> KeyboardShortcut: ...

    @abstractmethod
    def find_by_action(self, action: str) -> KeyboardShortcut | None: ...

    @abstractmethod
    def find_all(self) -> list[KeyboardShortcut]: ...


class BenchmarkRepository(ABC):
    @abstractmethod
    def save(self, benchmark: Benchmark) -> Benchmark: ...

    @abstractmethod
    def find_by_name(self, name: str) -> list[Benchmark]: ...

    @abstractmethod
    def find_all(self) -> list[Benchmark]: ...


class PerformanceReportRepository(ABC):
    @abstractmethod
    def save(self, report: PerformanceReport) -> PerformanceReport: ...

    @abstractmethod
    def find_by_id(self, report_id: str) -> PerformanceReport | None: ...

    @abstractmethod
    def find_all(self) -> list[PerformanceReport]: ...


class BenchmarkHistoryRepository(ABC):
    @abstractmethod
    def save(self, history: BenchmarkHistory) -> BenchmarkHistory: ...

    @abstractmethod
    def find_by_benchmark_name(self, name: str) -> BenchmarkHistory | None: ...


class TechnicalDebtItemRepository(ABC):
    @abstractmethod
    def save(self, item: TechnicalDebtItem) -> TechnicalDebtItem: ...

    @abstractmethod
    def find_by_category(self, category: str) -> list[TechnicalDebtItem]: ...

    @abstractmethod
    def find_all(self) -> list[TechnicalDebtItem]: ...


class BuildHealthRepository(ABC):
    @abstractmethod
    def save(self, build: BuildHealth) -> BuildHealth: ...

    @abstractmethod
    def find_by_status(self, status: str) -> list[BuildHealth]: ...

    @abstractmethod
    def find_all(self) -> list[BuildHealth]: ...


class ReleaseRepository(ABC):
    @abstractmethod
    def save(self, release: Release) -> Release: ...

    @abstractmethod
    def find_by_id(self, release_id: str) -> Release | None: ...

    @abstractmethod
    def find_by_version(self, version: str) -> Release | None: ...

    @abstractmethod
    def find_all(self) -> list[Release]: ...


class ReleaseReadinessRepository(ABC):
    @abstractmethod
    def save(self, readiness: ReleaseReadiness) -> ReleaseReadiness: ...

    @abstractmethod
    def find_by_release_id(self, release_id: str) -> ReleaseReadiness | None: ...


class ReleaseNoteRepository(ABC):
    @abstractmethod
    def save(self, note: ReleaseNote) -> ReleaseNote: ...

    @abstractmethod
    def find_by_release_id(self, release_id: str) -> list[ReleaseNote]: ...
