"""In-memory repository implementations for all optimization interfaces."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.interfaces.optimization_interfaces import (
    IAIAssistantRepository,
    IBenchmarkRepository,
    ICompatibilityRepository,
    IConfigProfileRepository,
    IDashboardRepository,
    IDiagnosticTraceRepository,
    IFeatureFlagRepository,
    IPerformanceMetricRepository,
    IReleaseRepository,
    ISustainabilityRepository,
)

logger = logging.getLogger(__name__)


class InMemoryPerformanceMetricRepository(IPerformanceMetricRepository):
    """In-memory implementation of the performance metric repository."""

    def __init__(self) -> None:
        self._metrics: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        metric_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        metric = {
            "id": metric_id,
            "name": data.get("name", ""),
            "category": data.get("category", ""),
            "value": data.get("value", 0.0),
            "unit": data.get("unit", ""),
            "timestamp": data.get("timestamp", now),
            "threshold": data.get("threshold", 0.0),
            "passed": data.get("passed", True),
            "created_at": now,
            "updated_at": now,
        }
        self._metrics[metric_id] = metric
        return metric

    def get_by_id(self, metric_id: str) -> dict[str, Any] | None:
        return self._metrics.get(metric_id)

    def get_all(
        self, page: int = 1, per_page: int = 20, category: Optional[str] = None
    ) -> dict[str, Any]:
        items = list(self._metrics.values())
        if category:
            items = [m for m in items if m.get("category") == category]
        items.sort(key=lambda m: m.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        page_items = items[offset: offset + per_page]
        return {"items": page_items, "total": total, "page": page, "per_page": per_page, "pages": pages}

    def update(self, metric_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        metric = self._metrics.get(metric_id)
        if not metric:
            return None
        for key in ("name", "category", "value", "unit", "threshold", "passed"):
            if key in data:
                metric[key] = data[key]
        metric["updated_at"] = datetime.now(timezone.utc).isoformat()
        return metric

    def delete(self, metric_id: str) -> bool:
        return self._metrics.pop(metric_id, None) is not None

    def get_by_category(self, category: str) -> list[dict[str, Any]]:
        return [m for m in self._metrics.values() if m.get("category") == category]

    def get_latest(self, name: str) -> dict[str, Any] | None:
        matches = [m for m in self._metrics.values() if m.get("name") == name]
        if not matches:
            return None
        return max(matches, key=lambda m: m.get("created_at", ""))


class InMemoryBenchmarkRepository(IBenchmarkRepository):
    """In-memory implementation of the benchmark repository."""

    def __init__(self) -> None:
        self._benchmarks: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        bench_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        benchmark = {
            "id": bench_id,
            "name": data.get("name", ""),
            "category": data.get("category", ""),
            "value": data.get("value", 0.0),
            "unit": data.get("unit", ""),
            "threshold": data.get("threshold", 0.0),
            "passed": data.get("passed", True),
            "baseline_value": data.get("baseline_value", 0.0),
            "regression_pct": data.get("regression_pct", 0.0),
            "measured_at": data.get("measured_at", now),
            "created_at": now,
        }
        self._benchmarks[bench_id] = benchmark
        return benchmark

    def get_by_id(self, benchmark_id: str) -> dict[str, Any] | None:
        return self._benchmarks.get(benchmark_id)

    def get_all(
        self, page: int = 1, per_page: int = 20, category: Optional[str] = None
    ) -> dict[str, Any]:
        items = list(self._benchmarks.values())
        if category:
            items = [b for b in items if b.get("category") == category]
        items.sort(key=lambda b: b.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        page_items = items[offset: offset + per_page]
        return {"items": page_items, "total": total, "page": page, "per_page": per_page, "pages": pages}

    def get_by_name(self, name: str) -> list[dict[str, Any]]:
        return [b for b in self._benchmarks.values() if b.get("name") == name]

    def delete(self, benchmark_id: str) -> bool:
        return self._benchmarks.pop(benchmark_id, None) is not None


class InMemoryDashboardRepository(IDashboardRepository):
    """In-memory implementation of the dashboard repository."""

    def __init__(self) -> None:
        self._dashboards: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        dash_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        dashboard = dict(data)
        dashboard["id"] = dash_id
        dashboard.setdefault("created_at", now)
        self._dashboards[dash_id] = dashboard
        return dashboard

    def get_by_id(self, dashboard_id: str) -> dict[str, Any] | None:
        return self._dashboards.get(dashboard_id)

    def get_latest(self) -> dict[str, Any] | None:
        if not self._dashboards:
            return None
        return max(self._dashboards.values(), key=lambda d: d.get("created_at", ""))

    def get_all(self, limit: int = 10) -> list[dict[str, Any]]:
        items = sorted(self._dashboards.values(), key=lambda d: d.get("created_at", ""), reverse=True)
        return items[:limit]

    def delete(self, dashboard_id: str) -> bool:
        return self._dashboards.pop(dashboard_id, None) is not None


class InMemoryFeatureFlagRepository(IFeatureFlagRepository):
    """In-memory implementation of the feature flag repository."""

    def __init__(self) -> None:
        self._flags: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        flag_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        flag = {
            "id": flag_id,
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "enabled": data.get("enabled", False),
            "category": data.get("category", ""),
            "default_value": data.get("default_value", False),
            "rollout_date": data.get("rollout_date", ""),
            "removal_date": data.get("removal_date", ""),
            "created_at": now,
            "updated_at": now,
        }
        self._flags[flag_id] = flag
        return flag

    def get_by_id(self, flag_id: str) -> dict[str, Any] | None:
        return self._flags.get(flag_id)

    def get_by_name(self, name: str) -> dict[str, Any] | None:
        for flag in self._flags.values():
            if flag.get("name") == name:
                return flag
        return None

    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        category: Optional[str] = None,
        enabled_only: bool = False,
    ) -> dict[str, Any]:
        items = list(self._flags.values())
        if category:
            items = [f for f in items if f.get("category") == category]
        if enabled_only:
            items = [f for f in items if f.get("enabled", False)]
        items.sort(key=lambda f: f.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        page_items = items[offset: offset + per_page]
        return {"items": page_items, "total": total, "page": page, "per_page": per_page, "pages": pages}

    def update(self, flag_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        flag = self._flags.get(flag_id)
        if not flag:
            return None
        for key in ("name", "description", "enabled", "category", "default_value", "rollout_date", "removal_date"):
            if key in data:
                flag[key] = data[key]
        flag["updated_at"] = datetime.now(timezone.utc).isoformat()
        return flag

    def delete(self, flag_id: str) -> bool:
        return self._flags.pop(flag_id, None) is not None


class InMemoryConfigProfileRepository(IConfigProfileRepository):
    """In-memory implementation of the config profile repository."""

    def __init__(self) -> None:
        self._profiles: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        profile_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        profile = {
            "id": profile_id,
            "name": data.get("name", ""),
            "target_audience": data.get("target_audience", ""),
            "settings": data.get("settings", {}),
            "created_at": now,
            "updated_at": now,
            "version": data.get("version", "1.0"),
        }
        self._profiles[profile_id] = profile
        return profile

    def get_by_id(self, profile_id: str) -> dict[str, Any] | None:
        return self._profiles.get(profile_id)

    def get_all(
        self, page: int = 1, per_page: int = 20, target_audience: Optional[str] = None
    ) -> dict[str, Any]:
        items = list(self._profiles.values())
        if target_audience:
            items = [p for p in items if p.get("target_audience") == target_audience]
        items.sort(key=lambda p: p.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        page_items = items[offset: offset + per_page]
        return {"items": page_items, "total": total, "page": page, "per_page": per_page, "pages": pages}

    def update(self, profile_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        profile = self._profiles.get(profile_id)
        if not profile:
            return None
        for key in ("name", "target_audience", "settings", "version"):
            if key in data:
                profile[key] = data[key]
        profile["updated_at"] = datetime.now(timezone.utc).isoformat()
        return profile

    def delete(self, profile_id: str) -> bool:
        return self._profiles.pop(profile_id, None) is not None


class InMemoryCompatibilityRepository(ICompatibilityRepository):
    """In-memory implementation of the compatibility repository."""

    def __init__(self) -> None:
        self._reports: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        report_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        report = dict(data)
        report["id"] = report_id
        report.setdefault("generated_at", now)
        report.setdefault("created_at", now)
        self._reports[report_id] = report
        return report

    def get_by_id(self, report_id: str) -> dict[str, Any] | None:
        return self._reports.get(report_id)

    def get_all(self, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        items = list(self._reports.values())
        items.sort(key=lambda r: r.get("generated_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        page_items = items[offset: offset + per_page]
        return {"items": page_items, "total": total, "page": page, "per_page": per_page, "pages": pages}

    def delete(self, report_id: str) -> bool:
        return self._reports.pop(report_id, None) is not None


class InMemorySustainabilityRepository(ISustainabilityRepository):
    """In-memory implementation of the sustainability repository."""

    def __init__(self) -> None:
        self._metrics: dict[str, dict[str, Any]] = {}
        self._debt_items: dict[str, dict[str, Any]] = {}

    def create_metric(self, data: dict[str, Any]) -> dict[str, Any]:
        metric_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        metric = dict(data)
        metric["id"] = metric_id
        metric.setdefault("created_at", now)
        self._metrics[metric_id] = metric
        return metric

    def get_metric_by_id(self, metric_id: str) -> dict[str, Any] | None:
        return self._metrics.get(metric_id)

    def get_all_metrics(self) -> list[dict[str, Any]]:
        return list(self._metrics.values())

    def update_metric(self, metric_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        metric = self._metrics.get(metric_id)
        if not metric:
            return None
        metric.update(data)
        return metric

    def delete_metric(self, metric_id: str) -> bool:
        return self._metrics.pop(metric_id, None) is not None

    def create_debt_item(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "category": data.get("category", ""),
            "description": data.get("description", ""),
            "severity": data.get("severity", "low"),
            "estimated_hours": data.get("estimated_hours", 0.0),
            "created_at": now,
            "resolved": data.get("resolved", False),
            "resolved_at": data.get("resolved_at"),
        }
        self._debt_items[item_id] = item
        return item

    def get_debt_item_by_id(self, item_id: str) -> dict[str, Any] | None:
        return self._debt_items.get(item_id)

    def get_all_debt_items(self, resolved: Optional[bool] = None) -> list[dict[str, Any]]:
        items = list(self._debt_items.values())
        if resolved is not None:
            items = [i for i in items if i.get("resolved", False) == resolved]
        return items

    def update_debt_item(self, item_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        item = self._debt_items.get(item_id)
        if not item:
            return None
        for key in ("category", "description", "severity", "estimated_hours", "resolved", "resolved_at"):
            if key in data:
                item[key] = data[key]
        return item

    def delete_debt_item(self, item_id: str) -> bool:
        return self._debt_items.pop(item_id, None) is not None


class InMemoryReleaseRepository(IReleaseRepository):
    """In-memory implementation of the release governance repository."""

    def __init__(self) -> None:
        self._workflows: dict[str, dict[str, Any]] = {}
        self._approvals: dict[str, dict[str, Any]] = {}
        self._gates: dict[str, dict[str, Any]] = {}
        self._checklist: dict[str, dict[str, Any]] = {}

    def create_workflow(self, data: dict[str, Any]) -> dict[str, Any]:
        wf_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        workflow = dict(data)
        workflow["id"] = wf_id
        workflow.setdefault("created_at", now)
        self._workflows[wf_id] = workflow
        return workflow

    def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        return self._workflows.get(workflow_id)

    def get_workflow_by_release_id(self, release_id: str) -> dict[str, Any] | None:
        for wf in self._workflows.values():
            if wf.get("release_id") == release_id:
                return wf
        return None

    def get_all_workflows(self, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        items = list(self._workflows.values())
        items.sort(key=lambda w: w.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        page_items = items[offset: offset + per_page]
        return {"items": page_items, "total": total, "page": page, "per_page": per_page, "pages": pages}

    def update_workflow(self, workflow_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        wf = self._workflows.get(workflow_id)
        if not wf:
            return None
        for key in ("current_stage", "stage_history", "completed_at", "created_by", "version"):
            if key in data:
                wf[key] = data[key]
        return wf

    def create_approval(self, data: dict[str, Any]) -> dict[str, Any]:
        approval_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        approval = dict(data)
        approval["id"] = approval_id
        approval.setdefault("created_at", now)
        self._approvals[approval_id] = approval
        return approval

    def get_approvals_for_workflow(self, workflow_id: str) -> list[dict[str, Any]]:
        return [a for a in self._approvals.values() if a.get("workflow_id") == workflow_id]

    def update_approval(self, approval_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        approval = self._approvals.get(approval_id)
        if not approval:
            return None
        for key in ("approved", "comments", "approved_at"):
            if key in data:
                approval[key] = data[key]
        return approval

    def create_gate(self, data: dict[str, Any]) -> dict[str, Any]:
        gate_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        gate = dict(data)
        gate["id"] = gate_id
        gate.setdefault("created_at", now)
        self._gates[gate_id] = gate
        return gate

    def get_gates_for_release(self, release_id: str) -> list[dict[str, Any]]:
        return [g for g in self._gates.values() if g.get("release_id") == release_id]

    def update_gate(self, gate_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        gate = self._gates.get(gate_id)
        if not gate:
            return None
        for key in ("passed", "evidence", "checked_at"):
            if key in data:
                gate[key] = data[key]
        return gate

    def create_checklist_item(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = dict(data)
        item["id"] = item_id
        item.setdefault("created_at", now)
        self._checklist[item_id] = item
        return item

    def get_checklist_for_release(self, release_id: str) -> list[dict[str, Any]]:
        return [c for c in self._checklist.values() if c.get("release_id") == release_id]

    def update_checklist_item(self, item_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        item = self._checklist.get(item_id)
        if not item:
            return None
        for key in ("completed", "completed_at", "assignee", "due_date"):
            if key in data:
                item[key] = data[key]
        return item


class InMemoryAIAssistantRepository(IAIAssistantRepository):
    """In-memory implementation of the AI assistant repository."""

    def __init__(self) -> None:
        self._suggestions: dict[str, dict[str, Any]] = {}
        self._audits: dict[str, dict[str, Any]] = {}

    def create_suggestion(self, data: dict[str, Any]) -> dict[str, Any]:
        sug_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        suggestion = dict(data)
        suggestion["id"] = sug_id
        suggestion.setdefault("created_at", now)
        self._suggestions[sug_id] = suggestion
        return suggestion

    def get_suggestion_by_id(self, suggestion_id: str) -> dict[str, Any] | None:
        return self._suggestions.get(suggestion_id)

    def get_all_suggestions(
        self,
        page: int = 1,
        per_page: int = 20,
        suggestion_type: Optional[str] = None,
    ) -> dict[str, Any]:
        items = list(self._suggestions.values())
        if suggestion_type:
            items = [s for s in items if s.get("suggestion_type") == suggestion_type]
        items.sort(key=lambda s: s.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        page_items = items[offset: offset + per_page]
        return {"items": page_items, "total": total, "page": page, "per_page": per_page, "pages": pages}

    def update_suggestion(self, suggestion_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        sug = self._suggestions.get(suggestion_id)
        if not sug:
            return None
        for key in ("reviewed", "accepted", "reviewed_at", "content", "confidence"):
            if key in data:
                sug[key] = data[key]
        return sug

    def delete_suggestion(self, suggestion_id: str) -> bool:
        return self._suggestions.pop(suggestion_id, None) is not None

    def create_audit(self, data: dict[str, Any]) -> dict[str, Any]:
        audit_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        audit = dict(data)
        audit["id"] = audit_id
        audit.setdefault("created_at", now)
        self._audits[audit_id] = audit
        return audit

    def get_audit_by_id(self, audit_id: str) -> dict[str, Any] | None:
        return self._audits.get(audit_id)

    def get_audits_for_content(self, content_id: str) -> list[dict[str, Any]]:
        return [a for a in self._audits.values() if a.get("content_id") == content_id]

    def update_audit(self, audit_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        audit = self._audits.get(audit_id)
        if not audit:
            return None
        for key in ("instructor_reviewed", "reviewed_at"):
            if key in data:
                audit[key] = data[key]
        return audit


class InMemoryDiagnosticTraceRepository(IDiagnosticTraceRepository):
    """In-memory implementation of the diagnostic trace repository."""

    def __init__(self) -> None:
        self._traces: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        trace_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        trace = dict(data)
        trace["id"] = trace_id
        trace.setdefault("created_at", now)
        self._traces[trace_id] = trace
        return trace

    def get_by_id(self, trace_id: str) -> dict[str, Any] | None:
        return self._traces.get(trace_id)

    def get_all(self, limit: int = 50) -> list[dict[str, Any]]:
        items = sorted(self._traces.values(), key=lambda t: t.get("created_at", ""), reverse=True)
        return items[:limit]

    def update(self, trace_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        trace = self._traces.get(trace_id)
        if not trace:
            return None
        for key in ("spans_json", "total_duration_ms", "updated_at"):
            if key in data:
                trace[key] = data[key]
        return trace

    def delete(self, trace_id: str) -> bool:
        return self._traces.pop(trace_id, None) is not None
