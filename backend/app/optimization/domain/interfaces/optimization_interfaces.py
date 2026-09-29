"""Optimization repository interfaces (abstract base classes)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


class IPerformanceMetricRepository(ABC):
    """Interface for performance metric persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, metric_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        category: Optional[str] = None,
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def update(self, metric_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, metric_id: str) -> bool:
        ...

    @abstractmethod
    def get_by_category(self, category: str) -> list[Any]:
        ...

    @abstractmethod
    def get_latest(self, name: str) -> Any | None:
        ...


class IBenchmarkRepository(ABC):
    """Interface for benchmark result persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, benchmark_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        category: Optional[str] = None,
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def get_by_name(self, name: str) -> list[Any]:
        ...

    @abstractmethod
    def delete(self, benchmark_id: str) -> bool:
        ...


class IDashboardRepository(ABC):
    """Interface for optimization dashboard persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, dashboard_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_latest(self) -> Any | None:
        ...

    @abstractmethod
    def get_all(self, limit: int = 10) -> list[Any]:
        ...

    @abstractmethod
    def delete(self, dashboard_id: str) -> bool:
        ...


class IFeatureFlagRepository(ABC):
    """Interface for feature flag persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, flag_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_by_name(self, name: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        category: Optional[str] = None,
        enabled_only: bool = False,
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def update(self, flag_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, flag_id: str) -> bool:
        ...


class IConfigProfileRepository(ABC):
    """Interface for configuration profile persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, profile_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        target_audience: Optional[str] = None,
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def update(self, profile_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, profile_id: str) -> bool:
        ...


class ICompatibilityRepository(ABC):
    """Interface for compatibility report persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, report_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(self, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        ...

    @abstractmethod
    def delete(self, report_id: str) -> bool:
        ...


class ISustainabilityRepository(ABC):
    """Interface for sustainability metrics persistence."""

    @abstractmethod
    def create_metric(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_metric_by_id(self, metric_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all_metrics(self) -> list[Any]:
        ...

    @abstractmethod
    def update_metric(self, metric_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete_metric(self, metric_id: str) -> bool:
        ...

    @abstractmethod
    def create_debt_item(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_debt_item_by_id(self, item_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all_debt_items(self, resolved: Optional[bool] = None) -> list[Any]:
        ...

    @abstractmethod
    def update_debt_item(self, item_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete_debt_item(self, item_id: str) -> bool:
        ...


class IReleaseRepository(ABC):
    """Interface for release governance persistence."""

    @abstractmethod
    def create_workflow(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_workflow_by_id(self, workflow_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_workflow_by_release_id(self, release_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all_workflows(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def update_workflow(self, workflow_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def create_approval(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_approvals_for_workflow(self, workflow_id: str) -> list[Any]:
        ...

    @abstractmethod
    def update_approval(self, approval_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def create_gate(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_gates_for_release(self, release_id: str) -> list[Any]:
        ...

    @abstractmethod
    def update_gate(self, gate_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def create_checklist_item(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_checklist_for_release(self, release_id: str) -> list[Any]:
        ...

    @abstractmethod
    def update_checklist_item(self, item_id: str, data: dict[str, Any]) -> Any | None:
        ...


class IAIAssistantRepository(ABC):
    """Interface for AI assistant data persistence."""

    @abstractmethod
    def create_suggestion(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_suggestion_by_id(self, suggestion_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all_suggestions(
        self,
        page: int = 1,
        per_page: int = 20,
        suggestion_type: Optional[str] = None,
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def update_suggestion(
        self, suggestion_id: str, data: dict[str, Any]
    ) -> Any | None:
        ...

    @abstractmethod
    def delete_suggestion(self, suggestion_id: str) -> bool:
        ...

    @abstractmethod
    def create_audit(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_audit_by_id(self, audit_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_audits_for_content(self, content_id: str) -> list[Any]:
        ...

    @abstractmethod
    def update_audit(self, audit_id: str, data: dict[str, Any]) -> Any | None:
        ...


class IDiagnosticTraceRepository(ABC):
    """Interface for diagnostic trace persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, trace_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(self, limit: int = 50) -> list[Any]:
        ...

    @abstractmethod
    def update(self, trace_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, trace_id: str) -> bool:
        ...
