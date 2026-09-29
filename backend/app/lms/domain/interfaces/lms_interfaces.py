"""LMS repository interfaces (abstract base classes)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


class IClassroomRepository(ABC):
    """Interface for classroom data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, classroom_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(
        self, page: int = 1, per_page: int = 20, status: Optional[str] = None
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def update(self, classroom_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, classroom_id: str) -> bool:
        ...

    @abstractmethod
    def search(self, query: str, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        ...

    @abstractmethod
    def add_member(self, classroom_id: str, member_data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def remove_member(self, classroom_id: str, user_id: str) -> bool:
        ...

    @abstractmethod
    def get_members(self, classroom_id: str) -> list[Any]:
        ...


class IEnrollmentRepository(ABC):
    """Interface for enrollment data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, enrollment_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        course_id: Optional[str] = None,
        learner_id: Optional[str] = None,
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def update(self, enrollment_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, enrollment_id: str) -> bool:
        ...

    @abstractmethod
    def get_by_learner(self, learner_id: str) -> list[Any]:
        ...

    @abstractmethod
    def get_by_course(self, course_id: str) -> list[Any]:
        ...

    @abstractmethod
    def count_by_course(self, course_id: str) -> int:
        ...


class IGradebookRepository(ABC):
    """Interface for gradebook data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, entry_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_by_course(self, course_id: str) -> Any | None:
        ...

    @abstractmethod
    def add_grade_item(self, entry_id: str, item_data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def add_grade_entry(self, item_id: str, entry_data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_grade_entries(
        self, item_id: Optional[str] = None, learner_id: Optional[str] = None
    ) -> list[Any]:
        ...

    @abstractmethod
    def update(self, entry_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        ...


class ICompetencyRepository(ABC):
    """Interface for competency data persistence."""

    @abstractmethod
    def create_framework(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_framework(self, framework_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all_frameworks(self) -> list[Any]:
        ...

    @abstractmethod
    def create_competency(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_competency(self, competency_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all_competencies(self) -> list[Any]:
        ...

    @abstractmethod
    def update(self, competency_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, competency_id: str) -> bool:
        ...

    @abstractmethod
    def get_progress(
        self, learner_id: str, competency_id: Optional[str] = None
    ) -> list[Any]:
        ...

    @abstractmethod
    def create_progress(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def update_progress(self, progress_id: str, data: dict[str, Any]) -> Any | None:
        ...


class IAssessmentRepository(ABC):
    """Interface for assessment data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, assessment_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_by_course(self, course_id: str) -> list[Any]:
        ...

    @abstractmethod
    def update(self, assessment_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, assessment_id: str) -> bool:
        ...

    @abstractmethod
    def create_attempt(self, attempt_data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_attempts(
        self, assessment_id: str, learner_id: Optional[str] = None
    ) -> list[Any]:
        ...

    @abstractmethod
    def update_attempt(self, attempt_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def create_submission(self, submission_data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_submissions(self, attempt_id: str) -> list[Any]:
        ...

    @abstractmethod
    def create_question_group(self, group_data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_question_groups(self, assessment_id: str) -> list[Any]:
        ...


class ICalendarRepository(ABC):
    """Interface for calendar data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, calendar_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(self) -> list[Any]:
        ...

    @abstractmethod
    def update(self, calendar_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, calendar_id: str) -> bool:
        ...

    @abstractmethod
    def add_event(self, calendar_id: str, event_data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_events(self, calendar_id: str) -> list[Any]:
        ...

    @abstractmethod
    def remove_event(self, calendar_id: str, event_id: str) -> bool:
        ...

    @abstractmethod
    def create_term(self, term_data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_terms(self) -> list[Any]:
        ...

    @abstractmethod
    def create_important_date(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_important_dates(self) -> list[Any]:
        ...


class IPortfolioRepository(ABC):
    """Interface for portfolio data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, portfolio_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_by_learner(self, learner_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(self) -> list[Any]:
        ...

    @abstractmethod
    def update(self, portfolio_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, portfolio_id: str) -> bool:
        ...

    @abstractmethod
    def add_item(self, portfolio_id: str, item_data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_items(self, portfolio_id: str) -> list[Any]:
        ...

    @abstractmethod
    def remove_item(self, portfolio_id: str, item_id: str) -> bool:
        ...

    @abstractmethod
    def add_evidence(self, item_id: str, evidence_data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_evidence(self, item_id: str) -> list[Any]:
        ...
