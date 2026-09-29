"""In-memory repository implementations for all LMS repository interfaces."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.interfaces.lms_interfaces import (
    IAssessmentRepository,
    ICalendarRepository,
    IClassroomRepository,
    ICompetencyRepository,
    IEnrollmentRepository,
    IGradebookRepository,
    IPortfolioRepository,
)

logger = logging.getLogger(__name__)


class InMemoryClassroomRepository(IClassroomRepository):
    """In-memory implementation of the classroom repository."""

    def __init__(self) -> None:
        self._classrooms: dict[str, dict[str, Any]] = {}
        self._members: dict[str, list[dict[str, Any]]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        classroom_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        classroom = {
            "id": classroom_id,
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "capacity": data.get("capacity", 30),
            "instructor_id": data.get("instructor_id", ""),
            "status": data.get("status", "active"),
            "created_at": now,
            "updated_at": now,
        }
        self._classrooms[classroom_id] = classroom
        self._members[classroom_id] = []
        logger.info("classroom_created", extra={"classroom_id": classroom_id})
        return classroom

    def get_by_id(self, classroom_id: str) -> dict[str, Any] | None:
        classroom = self._classrooms.get(classroom_id)
        if classroom:
            classroom["members"] = self._members.get(classroom_id, [])
        return classroom

    def get_all(
        self, page: int = 1, per_page: int = 20, status: Optional[str] = None
    ) -> dict[str, Any]:
        items = list(self._classrooms.values())
        if status:
            items = [c for c in items if c["status"] == status]
        items.sort(key=lambda c: c.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        page_items = items[offset : offset + per_page]
        for item in page_items:
            item["members"] = self._members.get(item["id"], [])
        return {"items": page_items, "total": total, "page": page, "per_page": per_page, "pages": pages}

    def update(self, classroom_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        classroom = self._classrooms.get(classroom_id)
        if not classroom:
            return None
        for key in ("name", "description", "capacity", "instructor_id", "status"):
            if key in data:
                classroom[key] = data[key]
        classroom["updated_at"] = datetime.now(timezone.utc).isoformat()
        return classroom

    def delete(self, classroom_id: str) -> bool:
        if classroom_id in self._classrooms:
            del self._classrooms[classroom_id]
            self._members.pop(classroom_id, None)
            return True
        return False

    def search(self, query: str, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        query_lower = query.lower()
        items = [
            c for c in self._classrooms.values()
            if query_lower in c.get("name", "").lower()
            or query_lower in c.get("description", "").lower()
        ]
        items.sort(key=lambda c: c.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        page_items = items[offset : offset + per_page]
        return {"items": page_items, "total": total, "page": page, "per_page": per_page, "pages": pages}

    def add_member(self, classroom_id: str, member_data: dict[str, Any]) -> dict[str, Any]:
        members = self._members.setdefault(classroom_id, [])
        member = {
            "user_id": member_data.get("user_id", ""),
            "role": member_data.get("role", "learner"),
            "joined_at": datetime.now(timezone.utc).isoformat(),
            "status": member_data.get("status", "active"),
        }
        members.append(member)
        return member

    def remove_member(self, classroom_id: str, user_id: str) -> bool:
        members = self._members.get(classroom_id, [])
        for m in members:
            if m["user_id"] == user_id and m["status"] == "active":
                m["status"] = "removed"
                return True
        return False

    def get_members(self, classroom_id: str) -> list[dict[str, Any]]:
        return [
            m for m in self._members.get(classroom_id, [])
            if m["status"] == "active"
        ]


class InMemoryEnrollmentRepository(IEnrollmentRepository):
    """In-memory implementation of the enrollment repository."""

    def __init__(self) -> None:
        self._enrollments: dict[str, dict[str, Any]] = {}
        self._waitlist: dict[str, list[dict[str, Any]]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        enrollment_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        enrollment = {
            "id": enrollment_id,
            "learner_id": data.get("learner_id", ""),
            "course_id": data.get("course_id", ""),
            "status": data.get("status", "pending"),
            "enrolled_at": now,
            "completed_at": None,
            "grade": None,
        }
        self._enrollments[enrollment_id] = enrollment
        return enrollment

    def get_by_id(self, enrollment_id: str) -> dict[str, Any] | None:
        return self._enrollments.get(enrollment_id)

    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        course_id: Optional[str] = None,
        learner_id: Optional[str] = None,
    ) -> dict[str, Any]:
        items = list(self._enrollments.values())
        if status:
            items = [e for e in items if e["status"] == status]
        if course_id:
            items = [e for e in items if e["course_id"] == course_id]
        if learner_id:
            items = [e for e in items if e["learner_id"] == learner_id]
        items.sort(key=lambda e: e.get("enrolled_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        page_items = items[offset : offset + per_page]
        return {"items": page_items, "total": total, "page": page, "per_page": per_page, "pages": pages}

    def update(self, enrollment_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        enrollment = self._enrollments.get(enrollment_id)
        if not enrollment:
            return None
        for key in ("status", "grade", "completed_at"):
            if key in data:
                enrollment[key] = data[key]
        return enrollment

    def delete(self, enrollment_id: str) -> bool:
        return self._enrollments.pop(enrollment_id, None) is not None

    def get_by_learner(self, learner_id: str) -> list[dict[str, Any]]:
        return [e for e in self._enrollments.values() if e["learner_id"] == learner_id]

    def get_by_course(self, course_id: str) -> list[dict[str, Any]]:
        return [e for e in self._enrollments.values() if e["course_id"] == course_id]

    def count_by_course(self, course_id: str) -> int:
        return len([
            e for e in self._enrollments.values()
            if e["course_id"] == course_id and e["status"] == "active"
        ])


class InMemoryGradebookRepository(IGradebookRepository):
    """In-memory implementation of the gradebook repository."""

    def __init__(self) -> None:
        self._gradebooks: dict[str, dict[str, Any]] = {}
        self._grade_items: dict[str, list[dict[str, Any]]] = {}
        self._grade_entries: dict[str, list[dict[str, Any]]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        entry_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        entry = {
            "id": entry_id,
            "course_id": data.get("course_id", ""),
            "created_at": now,
            "updated_at": now,
        }
        self._gradebooks[entry_id] = entry
        self._grade_items[entry_id] = []
        return entry

    def get_by_id(self, entry_id: str) -> dict[str, Any] | None:
        entry = self._gradebooks.get(entry_id)
        if entry:
            entry["items"] = self._grade_items.get(entry_id, [])
        return entry

    def get_by_course(self, course_id: str) -> dict[str, Any] | None:
        for entry in self._gradebooks.values():
            if entry["course_id"] == course_id:
                entry["items"] = self._grade_items.get(entry["id"], [])
                return entry
        return None

    def add_grade_item(self, entry_id: str, item_data: dict[str, Any]) -> dict[str, Any]:
        item_id = item_data.get("id", str(uuid.uuid4()))
        item = {
            "id": item_id,
            "gradebook_id": entry_id,
            "name": item_data.get("name", ""),
            "category": item_data.get("category", "assignment"),
            "points_possible": item_data.get("points_possible", 100.0),
            "weight": item_data.get("weight", 1.0),
            "due_date": item_data.get("due_date"),
        }
        self._grade_items.setdefault(entry_id, []).append(item)
        self._grade_entries[item_id] = []
        return item

    def add_grade_entry(self, item_id: str, entry_data: dict[str, Any]) -> dict[str, Any]:
        entry_id = entry_data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        entry = {
            "id": entry_id,
            "grade_item_id": item_id,
            "learner_id": entry_data.get("learner_id", ""),
            "score": entry_data.get("score", 0.0),
            "graded_at": now,
            "feedback": entry_data.get("feedback"),
            "graded_by": entry_data.get("graded_by"),
        }
        self._grade_entries.setdefault(item_id, []).append(entry)
        return entry

    def get_grade_entries(
        self, item_id: Optional[str] = None, learner_id: Optional[str] = None
    ) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        if item_id:
            entries = list(self._grade_entries.get(item_id, []))
        else:
            for item_entries in self._grade_entries.values():
                entries.extend(item_entries)
        if learner_id:
            entries = [e for e in entries if e["learner_id"] == learner_id]
        return entries

    def update(self, entry_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        entry = self._gradebooks.get(entry_id)
        if not entry:
            return None
        if "course_id" in data:
            entry["course_id"] = data["course_id"]
        entry["updated_at"] = datetime.now(timezone.utc).isoformat()
        return entry

    def delete(self, entry_id: str) -> bool:
        if entry_id in self._gradebooks:
            del self._gradebooks[entry_id]
            items = self._grade_items.pop(entry_id, [])
            for item in items:
                self._grade_entries.pop(item["id"], None)
            return True
        return False


class InMemoryCompetencyRepository(ICompetencyRepository):
    """In-memory implementation of the competency repository."""

    def __init__(self) -> None:
        self._frameworks: dict[str, dict[str, Any]] = {}
        self._competencies: dict[str, dict[str, Any]] = {}
        self._progress: dict[str, dict[str, Any]] = {}

    def create_framework(self, data: dict[str, Any]) -> dict[str, Any]:
        fw_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        framework = {
            "id": fw_id,
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "version": data.get("version", "1.0"),
            "competencies": [],
            "created_at": now,
            "updated_at": now,
        }
        self._frameworks[fw_id] = framework
        return framework

    def get_framework(self, framework_id: str) -> dict[str, Any] | None:
        return self._frameworks.get(framework_id)

    def get_all_frameworks(self) -> list[dict[str, Any]]:
        return list(self._frameworks.values())

    def create_competency(self, data: dict[str, Any]) -> dict[str, Any]:
        comp_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        competency = {
            "id": comp_id,
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "domain": data.get("domain", ""),
            "level": data.get("level", "beginner"),
            "framework_id": data.get("framework_id"),
            "created_at": now,
            "updated_at": now,
        }
        self._competencies[comp_id] = competency
        fw_id = data.get("framework_id")
        if fw_id and fw_id in self._frameworks:
            self._frameworks[fw_id]["competencies"].append(comp_id)
        return competency

    def get_competency(self, competency_id: str) -> dict[str, Any] | None:
        return self._competencies.get(competency_id)

    def get_all_competencies(self) -> list[dict[str, Any]]:
        return list(self._competencies.values())

    def update(self, competency_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        competency = self._competencies.get(competency_id)
        if not competency:
            return None
        for key in ("name", "description", "domain", "level"):
            if key in data:
                competency[key] = data[key]
        competency["updated_at"] = datetime.now(timezone.utc).isoformat()
        return competency

    def delete(self, competency_id: str) -> bool:
        competency = self._competencies.pop(competency_id, None)
        if not competency:
            return False
        fw_id = competency.get("framework_id")
        if fw_id and fw_id in self._frameworks:
            fw = self._frameworks[fw_id]
            fw["competencies"] = [c for c in fw["competencies"] if c != competency_id]
        to_delete = [pid for pid, p in self._progress.items() if p["competency_id"] == competency_id]
        for pid in to_delete:
            del self._progress[pid]
        return True

    def get_progress(
        self, learner_id: str, competency_id: Optional[str] = None
    ) -> list[dict[str, Any]]:
        results = [
            p for p in self._progress.values()
            if p["learner_id"] == learner_id
        ]
        if competency_id:
            results = [p for p in results if p["competency_id"] == competency_id]
        return results

    def create_progress(self, data: dict[str, Any]) -> dict[str, Any]:
        progress_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        progress = {
            "id": progress_id,
            "learner_id": data.get("learner_id"),
            "competency_id": data.get("competency_id"),
            "status": data.get("status", "not_started"),
            "evidence_json": data.get("evidence_json"),
            "assessed_at": data.get("assessed_at"),
            "assessor_id": data.get("assessor_id"),
            "created_at": now,
            "updated_at": now,
        }
        self._progress[progress_id] = progress
        return progress

    def update_progress(self, progress_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        progress = self._progress.get(progress_id)
        if not progress:
            return None
        for key in ("status", "evidence_json", "assessed_at", "assessor_id"):
            if key in data:
                progress[key] = data[key]
        return progress


class InMemoryAssessmentRepository(IAssessmentRepository):
    """In-memory implementation of the assessment repository."""

    def __init__(self) -> None:
        self._assessments: dict[str, dict[str, Any]] = {}
        self._attempts: dict[str, list[dict[str, Any]]] = {}
        self._submissions: dict[str, list[dict[str, Any]]] = {}
        self._question_groups: dict[str, list[dict[str, Any]]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        assessment_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        assessment = {
            "id": assessment_id,
            "title": data.get("title", ""),
            "assessment_type": data.get("assessment_type", "quiz"),
            "course_id": data.get("course_id", ""),
            "passing_score": data.get("passing_score", 70.0),
            "time_limit_minutes": data.get("time_limit_minutes"),
            "attempts_allowed": data.get("attempts_allowed", 1),
            "status": data.get("status", "draft"),
            "created_at": now,
            "updated_at": now,
        }
        self._assessments[assessment_id] = assessment
        self._attempts[assessment_id] = []
        self._question_groups[assessment_id] = []
        return assessment

    def get_by_id(self, assessment_id: str) -> dict[str, Any] | None:
        assessment = self._assessments.get(assessment_id)
        if assessment:
            assessment["attempts"] = self._attempts.get(assessment_id, [])
            assessment["question_groups"] = self._question_groups.get(assessment_id, [])
        return assessment

    def get_by_course(self, course_id: str) -> list[dict[str, Any]]:
        return [a for a in self._assessments.values() if a["course_id"] == course_id]

    def update(self, assessment_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        assessment = self._assessments.get(assessment_id)
        if not assessment:
            return None
        for key in ("title", "assessment_type", "passing_score", "time_limit_minutes", "attempts_allowed", "status"):
            if key in data:
                assessment[key] = data[key]
        assessment["updated_at"] = datetime.now(timezone.utc).isoformat()
        return assessment

    def delete(self, assessment_id: str) -> bool:
        if assessment_id in self._assessments:
            del self._assessments[assessment_id]
            self._attempts.pop(assessment_id, None)
            self._question_groups.pop(assessment_id, None)
            return True
        return False

    def create_attempt(self, attempt_data: dict[str, Any]) -> dict[str, Any]:
        attempt_id = attempt_data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        attempt = {
            "id": attempt_id,
            "assessment_id": attempt_data.get("assessment_id", ""),
            "learner_id": attempt_data.get("learner_id", ""),
            "attempt_number": attempt_data.get("attempt_number", 1),
            "started_at": now,
            "submitted_at": None,
            "score": None,
            "feedback": None,
        }
        assessment_id = attempt_data.get("assessment_id", "")
        self._attempts.setdefault(assessment_id, []).append(attempt)
        self._submissions[attempt_id] = []
        return attempt

    def get_attempts(
        self, assessment_id: str, learner_id: Optional[str] = None
    ) -> list[dict[str, Any]]:
        attempts = self._attempts.get(assessment_id, [])
        if learner_id:
            attempts = [a for a in attempts if a["learner_id"] == learner_id]
        return attempts

    def update_attempt(self, attempt_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        for attempt_list in self._attempts.values():
            for attempt in attempt_list:
                if attempt["id"] == attempt_id:
                    for key in ("score", "feedback", "submitted_at"):
                        if key in data:
                            attempt[key] = data[key]
                    return attempt
        return None

    def create_submission(self, submission_data: dict[str, Any]) -> dict[str, Any]:
        sub_id = submission_data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        submission = {
            "id": sub_id,
            "attempt_id": submission_data.get("attempt_id", ""),
            "content": submission_data.get("content", ""),
            "submitted_at": now,
            "attachments": submission_data.get("attachments", []),
        }
        attempt_id = submission_data.get("attempt_id", "")
        self._submissions.setdefault(attempt_id, []).append(submission)
        return submission

    def get_submissions(self, attempt_id: str) -> list[dict[str, Any]]:
        return list(self._submissions.get(attempt_id, []))

    def create_question_group(self, group_data: dict[str, Any]) -> dict[str, Any]:
        group_id = group_data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        group = {
            "id": group_id,
            "assessment_id": group_data.get("assessment_id", ""),
            "name": group_data.get("name", ""),
            "questions": group_data.get("questions", []),
            "weight": group_data.get("weight", 1.0),
            "created_at": now,
        }
        assessment_id = group_data.get("assessment_id", "")
        self._question_groups.setdefault(assessment_id, []).append(group)
        return group

    def get_question_groups(self, assessment_id: str) -> list[dict[str, Any]]:
        return list(self._question_groups.get(assessment_id, []))


class InMemoryCalendarRepository(ICalendarRepository):
    """In-memory implementation of the calendar repository."""

    def __init__(self) -> None:
        self._calendars: dict[str, dict[str, Any]] = {}
        self._events: dict[str, list[dict[str, Any]]] = {}
        self._terms: dict[str, dict[str, Any]] = {}
        self._important_dates: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        cal_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        calendar = {
            "id": cal_id,
            "name": data.get("name", ""),
            "year": data.get("year", datetime.now(timezone.utc).year),
            "created_at": now,
            "updated_at": now,
        }
        self._calendars[cal_id] = calendar
        self._events[cal_id] = []
        return calendar

    def get_by_id(self, calendar_id: str) -> dict[str, Any] | None:
        calendar = self._calendars.get(calendar_id)
        if calendar:
            calendar["events"] = self._events.get(calendar_id, [])
        return calendar

    def get_all(self) -> list[dict[str, Any]]:
        return list(self._calendars.values())

    def update(self, calendar_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        calendar = self._calendars.get(calendar_id)
        if not calendar:
            return None
        for key in ("name", "year"):
            if key in data:
                calendar[key] = data[key]
        calendar["updated_at"] = datetime.now(timezone.utc).isoformat()
        return calendar

    def delete(self, calendar_id: str) -> bool:
        if calendar_id in self._calendars:
            del self._calendars[calendar_id]
            self._events.pop(calendar_id, None)
            return True
        return False

    def add_event(self, calendar_id: str, event_data: dict[str, Any]) -> dict[str, Any]:
        event_id = event_data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        event = {
            "id": event_id,
            "calendar_id": calendar_id,
            "title": event_data.get("title", ""),
            "event_type": event_data.get("event_type", "class"),
            "start_time": event_data.get("start_time", now),
            "end_time": event_data.get("end_time", now),
            "recurring": event_data.get("recurring", False),
            "recurrence_rule": event_data.get("recurrence_rule"),
            "description": event_data.get("description"),
            "color": event_data.get("color", "#3B82F6"),
            "created_at": now,
        }
        self._events.setdefault(calendar_id, []).append(event)
        return event

    def get_events(self, calendar_id: str) -> list[dict[str, Any]]:
        return list(self._events.get(calendar_id, []))

    def remove_event(self, calendar_id: str, event_id: str) -> bool:
        events = self._events.get(calendar_id, [])
        for i, e in enumerate(events):
            if e["id"] == event_id:
                events.pop(i)
                return True
        return False

    def create_term(self, term_data: dict[str, Any]) -> dict[str, Any]:
        term_id = term_data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        term = {
            "id": term_id,
            "name": term_data.get("name", ""),
            "start_date": term_data.get("start_date", now),
            "end_date": term_data.get("end_date", now),
            "breaks": [],
            "created_at": now,
        }
        self._terms[term_id] = term
        return term

    def get_terms(self) -> list[dict[str, Any]]:
        return list(self._terms.values())

    def create_important_date(self, data: dict[str, Any]) -> dict[str, Any]:
        date_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        important_date = {
            "id": date_id,
            "title": data.get("title", ""),
            "date": data.get("date", now),
            "date_type": data.get("date_type", "enrollment_deadline"),
            "description": data.get("description"),
            "created_at": now,
        }
        self._important_dates[date_id] = important_date
        return important_date

    def get_important_dates(self) -> list[dict[str, Any]]:
        return list(self._important_dates.values())


class InMemoryPortfolioRepository(IPortfolioRepository):
    """In-memory implementation of the portfolio repository."""

    def __init__(self) -> None:
        self._portfolios: dict[str, dict[str, Any]] = {}
        self._items: dict[str, list[dict[str, Any]]] = {}
        self._evidence: dict[str, list[dict[str, Any]]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        portfolio_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        portfolio = {
            "id": portfolio_id,
            "learner_id": data.get("learner_id", ""),
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "created_at": now,
            "updated_at": now,
        }
        self._portfolios[portfolio_id] = portfolio
        self._items[portfolio_id] = []
        return portfolio

    def get_by_id(self, portfolio_id: str) -> dict[str, Any] | None:
        portfolio = self._portfolios.get(portfolio_id)
        if portfolio:
            portfolio["items"] = self._items.get(portfolio_id, [])
        return portfolio

    def get_by_learner(self, learner_id: str) -> dict[str, Any] | None:
        for portfolio in self._portfolios.values():
            if portfolio["learner_id"] == learner_id:
                portfolio["items"] = self._items.get(portfolio["id"], [])
                return portfolio
        return None

    def get_all(self) -> list[dict[str, Any]]:
        return list(self._portfolios.values())

    def update(self, portfolio_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        portfolio = self._portfolios.get(portfolio_id)
        if not portfolio:
            return None
        for key in ("title", "description"):
            if key in data:
                portfolio[key] = data[key]
        portfolio["updated_at"] = datetime.now(timezone.utc).isoformat()
        return portfolio

    def delete(self, portfolio_id: str) -> bool:
        if portfolio_id in self._portfolios:
            del self._portfolios[portfolio_id]
            items = self._items.pop(portfolio_id, [])
            for item in items:
                self._evidence.pop(item["id"], None)
            return True
        return False

    def add_item(self, portfolio_id: str, item_data: dict[str, Any]) -> dict[str, Any]:
        item_id = item_data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "portfolio_id": portfolio_id,
            "title": item_data.get("title", ""),
            "description": item_data.get("description", ""),
            "item_type": item_data.get("item_type", "project"),
            "created_at": now,
            "metadata": item_data.get("metadata", {}),
        }
        self._items.setdefault(portfolio_id, []).append(item)
        self._evidence[item_id] = []
        return item

    def get_items(self, portfolio_id: str) -> list[dict[str, Any]]:
        return list(self._items.get(portfolio_id, []))

    def remove_item(self, portfolio_id: str, item_id: str) -> bool:
        items = self._items.get(portfolio_id, [])
        for i, item in enumerate(items):
            if item["id"] == item_id:
                items.pop(i)
                self._evidence.pop(item_id, None)
                return True
        return False

    def add_evidence(self, item_id: str, evidence_data: dict[str, Any]) -> dict[str, Any]:
        ev_id = evidence_data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        evidence = {
            "id": ev_id,
            "item_id": item_id,
            "competency_id": evidence_data.get("competency_id", ""),
            "description": evidence_data.get("description", ""),
            "date_earned": now,
        }
        self._evidence.setdefault(item_id, []).append(evidence)
        return evidence

    def get_evidence(self, item_id: str) -> list[dict[str, Any]]:
        return list(self._evidence.get(item_id, []))
