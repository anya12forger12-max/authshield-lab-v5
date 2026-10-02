from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.quality.domain.entities.accessibility_a11y import A11yAudit, A11yProfile, A11yScorecard, KeyboardShortcut
from app.quality.domain.entities.diagnostics import DiagnosticBundle
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
from app.quality.repositories.quality_repository_impl import (
    InMemoryA11yAuditRepository,
    InMemoryA11yProfileRepository,
    InMemoryA11yScorecardRepository,
    InMemoryApplicationMetricRepository,
    InMemoryBenchmarkHistoryRepository,
    InMemoryBenchmarkRepository,
    InMemoryBuildHealthRepository,
    InMemoryCoverageReportRepository,
    InMemoryDiagnosticBundleRepository,
    InMemoryDiagnosticCheckRepository,
    InMemoryKeyboardShortcutRepository,
    InMemoryModuleHealthRepository,
    InMemoryObservabilitySnapshotRepository,
    InMemoryPerformanceReportRepository,
    InMemoryQualityDashboardRepository,
    InMemoryQualityScoreRepository,
    InMemoryReleaseNoteRepository,
    InMemoryReleaseReadinessRepository,
    InMemoryReleaseRepository,
    InMemoryTechnicalDebtItemRepository,
    InMemoryTestCaseRepository,
    InMemoryTestSuiteRepository,
)
from app.quality.services.accessibility_service import AccessibilityService
from app.quality.services.diagnostics_service import DiagnosticsService
from app.quality.services.maintainability_service import MaintainabilityService
from app.quality.services.observability_service import ObservabilityService
from app.quality.services.performance_service import PerformanceService
from app.quality.services.quality_dashboard_service import QualityDashboardService
from app.quality.services.release_service import ReleaseService
from app.quality.services.test_platform_service import TestPlatformService

router = APIRouter(prefix="/quality", tags=["quality"])

_quality_score_repo: QualityScoreRepository = InMemoryQualityScoreRepository()
_quality_dash_repo: QualityDashboardRepository = InMemoryQualityDashboardRepository()
_module_health_repo: ModuleHealthRepository = InMemoryModuleHealthRepository()
_test_case_repo: TestCaseRepository = InMemoryTestCaseRepository()
_suite_repo: TestSuiteRepository = InMemoryTestSuiteRepository()
_coverage_repo: CoverageReportRepository = InMemoryCoverageReportRepository()
_metric_repo: ApplicationMetricRepository = InMemoryApplicationMetricRepository()
_snapshot_repo: ObservabilitySnapshotRepository = InMemoryObservabilitySnapshotRepository()
_diag_check_repo: DiagnosticCheckRepository = InMemoryDiagnosticCheckRepository()
_diag_bundle_repo: DiagnosticBundleRepository = InMemoryDiagnosticBundleRepository()
_a11y_profile_repo: A11yProfileRepository = InMemoryA11yProfileRepository()
_a11y_audit_repo: A11yAuditRepository = InMemoryA11yAuditRepository()
_a11y_scorecard_repo: A11yScorecardRepository = InMemoryA11yScorecardRepository()
_shortcut_repo: KeyboardShortcutRepository = InMemoryKeyboardShortcutRepository()
_benchmark_repo: BenchmarkRepository = InMemoryBenchmarkRepository()
_perf_report_repo: PerformanceReportRepository = InMemoryPerformanceReportRepository()
_benchmark_history_repo: BenchmarkHistoryRepository = InMemoryBenchmarkHistoryRepository()
_debt_repo: TechnicalDebtItemRepository = InMemoryTechnicalDebtItemRepository()
_build_repo: BuildHealthRepository = InMemoryBuildHealthRepository()
_release_repo: ReleaseRepository = InMemoryReleaseRepository()
_readiness_repo: ReleaseReadinessRepository = InMemoryReleaseReadinessRepository()
_note_repo: ReleaseNoteRepository = InMemoryReleaseNoteRepository()

_dashboard_svc = QualityDashboardService(_quality_score_repo, _quality_dash_repo, _module_health_repo)
_test_svc = TestPlatformService(_test_case_repo, _suite_repo, _coverage_repo)
_observability_svc = ObservabilityService(_metric_repo, _snapshot_repo)
_diagnostics_svc = DiagnosticsService(_diag_check_repo, _diag_bundle_repo)
_accessibility_svc = AccessibilityService(_a11y_profile_repo, _a11y_audit_repo, _a11y_scorecard_repo, _shortcut_repo)
_performance_svc = PerformanceService(_benchmark_repo, _perf_report_repo, _benchmark_history_repo)
_maintainability_svc = MaintainabilityService(_debt_repo, _build_repo)
_release_svc = ReleaseService(_release_repo, _readiness_repo, _note_repo)


def _not_found(entity: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{entity} not found")


# Quality Dashboard Routes


@router.get("/dashboard", response_model=QualityDashboard)
def get_latest_dashboard() -> QualityDashboard:
    dash = _dashboard_svc.get_latest_dashboard()
    if not dash:
        raise _not_found("Dashboard")
    return dash


@router.post("/dashboard/generate", response_model=QualityDashboard)
def generate_dashboard() -> QualityDashboard:
    return _dashboard_svc.generate_dashboard()


@router.get("/dashboard/scores", response_model=list[QualityScore])
def list_scores() -> list[QualityScore]:
    return _dashboard_svc.aggregate_scores()


@router.post("/dashboard/scores", response_model=QualityScore)
def add_score(score: QualityScore) -> QualityScore:
    return _dashboard_svc.add_score(score)


@router.get("/dashboard/modules", response_model=list[ModuleHealth])
def list_module_health() -> list[ModuleHealth]:
    return _dashboard_svc.get_module_health()


# Test Platform Routes


@router.get("/tests", response_model=list[TestCase])
def list_test_cases() -> list[TestCase]:
    return _test_svc._test_case_repo.find_all()


@router.post("/tests", response_model=TestCase)
def create_test_case(tc: TestCase) -> TestCase:
    return _test_svc.create_test_case(tc)


@router.get("/tests/{test_id}", response_model=TestCase)
def get_test_case(test_id: str) -> TestCase:
    tc = _test_svc.get_test_case(test_id)
    if not tc:
        raise _not_found("TestCase")
    return tc


@router.get("/suites", response_model=list[TestSuite])
def list_suites() -> list[TestSuite]:
    return _test_svc.get_all_suites()


@router.post("/suites", response_model=TestSuite)
def create_suite(suite: TestSuite) -> TestSuite:
    return _test_svc.create_suite(suite)


@router.post("/suites/run", response_model=TestSuite)
def run_suite(suite: TestSuite) -> TestSuite:
    return _test_svc.run_suite(suite)


@router.get("/coverage", response_model=CoverageReport)
def get_latest_coverage() -> CoverageReport:
    cr = _test_svc.get_latest_coverage()
    if not cr:
        raise _not_found("CoverageReport")
    return cr


@router.post("/coverage", response_model=CoverageReport)
def track_coverage(report: CoverageReport) -> CoverageReport:
    return _test_svc.track_coverage(report)


# Observability Routes


@router.get("/metrics", response_model=list[ApplicationMetric])
def list_metrics(name: str | None = None) -> list[ApplicationMetric]:
    return _observability_svc.get_metrics(name)


@router.post("/metrics", response_model=ApplicationMetric)
def collect_metric(metric: ApplicationMetric) -> ApplicationMetric:
    return _observability_svc.collect_metric(metric)


@router.get("/snapshots/latest", response_model=ObservabilitySnapshot)
def get_latest_snapshot() -> ObservabilitySnapshot:
    snap = _observability_svc.get_latest_snapshot()
    if not snap:
        raise _not_found("ObservabilitySnapshot")
    return snap


# Diagnostics Routes


@router.get("/diagnostics/bundles", response_model=list[DiagnosticBundle])
def list_bundles() -> list[DiagnosticBundle]:
    return _diagnostics_svc.get_all_bundles()


@router.post("/diagnostics/bundles", response_model=DiagnosticBundle)
def create_bundle(bundle: DiagnosticBundle) -> DiagnosticBundle:
    return _diagnostics_svc.generate_bundle(
        name=bundle.name,
        checks=bundle.checks,
        platform=bundle.platform,
        version=bundle.version,
        includes_sensitive=bundle.includes_sensitive,
    )


@router.get("/diagnostics/bundles/{bundle_id}", response_model=DiagnosticBundle)
def get_bundle(bundle_id: str) -> DiagnosticBundle:
    bundle = _diagnostics_svc.get_bundle(bundle_id)
    if not bundle:
        raise _not_found("DiagnosticBundle")
    return bundle


# Accessibility Routes


@router.get("/a11y/profiles", response_model=list[A11yProfile])
def list_profiles() -> list[A11yProfile]:
    return _accessibility_svc.get_all_profiles()


@router.post("/a11y/profiles", response_model=A11yProfile)
def create_profile(profile: A11yProfile) -> A11yProfile:
    return _accessibility_svc.create_profile(profile)


@router.get("/a11y/audits", response_model=list[A11yAudit])
def list_audits() -> list[A11yAudit]:
    return _accessibility_svc.get_all_audits()


@router.post("/a11y/audits", response_model=A11yAudit)
def run_audit(audit: A11yAudit) -> A11yAudit:
    return _accessibility_svc.run_audit(audit)


@router.get("/a11y/scorecards", response_model=list[A11yScorecard])
def list_scorecards() -> list[A11yScorecard]:
    return _a11y_scorecard_repo.find_all()


@router.post("/a11y/scorecards", response_model=A11yScorecard)
def create_scorecard(scorecard: A11yScorecard) -> A11yScorecard:
    return _accessibility_svc.create_scorecard(scorecard)


@router.get("/a11y/shortcuts", response_model=list[KeyboardShortcut])
def list_shortcuts() -> list[KeyboardShortcut]:
    return _accessibility_svc.get_all_shortcuts()


@router.post("/a11y/shortcuts", response_model=KeyboardShortcut)
def add_shortcut(shortcut: KeyboardShortcut) -> KeyboardShortcut:
    return _accessibility_svc.add_shortcut(shortcut)


# Performance Routes


@router.get("/benchmarks", response_model=list[Benchmark])
def list_benchmarks(name: str | None = None) -> list[Benchmark]:
    return _performance_svc.get_benchmarks(name)


@router.post("/benchmarks", response_model=Benchmark)
def run_benchmark(benchmark: Benchmark) -> Benchmark:
    return _performance_svc.run_benchmark(benchmark)


@router.get("/benchmarks/history/{name}", response_model=BenchmarkHistory)
def get_benchmark_history(name: str) -> BenchmarkHistory:
    history = _performance_svc.get_history(name)
    if not history:
        raise _not_found("BenchmarkHistory")
    return history


@router.get("/reports", response_model=list[PerformanceReport])
def list_performance_reports() -> list[PerformanceReport]:
    return _performance_svc.get_all_reports()


@router.post("/reports", response_model=PerformanceReport)
def create_performance_report(report: PerformanceReport) -> PerformanceReport:
    return _performance_svc.generate_report(report.name, report.benchmarks)


# Maintainability Routes


@router.get("/debt", response_model=list[TechnicalDebtItem])
def list_debt() -> list[TechnicalDebtItem]:
    return _maintainability_svc.get_all_debt_items()


@router.post("/debt", response_model=TechnicalDebtItem)
def add_debt_item(item: TechnicalDebtItem) -> TechnicalDebtItem:
    return _maintainability_svc.add_debt_item(item)


@router.get("/builds", response_model=list[BuildHealth])
def list_builds() -> list[BuildHealth]:
    return _maintainability_svc.get_all_builds()


@router.post("/builds", response_model=BuildHealth)
def record_build(build: BuildHealth) -> BuildHealth:
    return _maintainability_svc.record_build(build)


# Release Routes


@router.get("/releases", response_model=list[Release])
def list_releases() -> list[Release]:
    return _release_svc.get_all_releases()


@router.post("/releases", response_model=Release)
def create_release(release: Release) -> Release:
    return _release_svc.create_release(release)


@router.get("/releases/{release_id}", response_model=Release)
def get_release(release_id: str) -> Release:
    release = _release_svc.get_release(release_id)
    if not release:
        raise _not_found("Release")
    return release


@router.post("/releases/{release_id}/readiness", response_model=ReleaseReadiness)
def check_release_readiness(release_id: str) -> ReleaseReadiness:
    return _release_svc.check_readiness(release_id)


@router.get("/releases/{release_id}/readiness", response_model=ReleaseReadiness)
def get_release_readiness(release_id: str) -> ReleaseReadiness:
    readiness = _release_svc.get_release_readiness(release_id)
    if not readiness:
        raise _not_found("ReleaseReadiness")
    return readiness


@router.get("/releases/{release_id}/notes", response_model=list[ReleaseNote])
def get_release_notes(release_id: str) -> list[ReleaseNote]:
    return _release_svc.get_notes_for_release(release_id)


@router.post("/releases/{release_id}/notes", response_model=ReleaseNote)
def add_release_note(release_id: str, note: ReleaseNote) -> ReleaseNote:
    note.release_id = release_id
    return _release_svc.add_note(note)
