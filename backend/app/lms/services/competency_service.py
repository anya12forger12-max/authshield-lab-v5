"""Competency tracking service for the LMS module."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.competency import CompetencyLevel, CompetencyStatus
from ..domain.events.lms_events import CompetencyAchieved
from ..domain.interfaces.lms_interfaces import ICompetencyRepository
from ..validators.lms_validator import validate_competency_data

logger = logging.getLogger(__name__)


class CompetencyService:
    """Service for managing competency frameworks, competencies, and learner progress."""

    def __init__(self, competency_repo: ICompetencyRepository) -> None:
        self._repo = competency_repo

    # ------------------------------------------------------------------
    # Framework management
    # ------------------------------------------------------------------

    def create_framework(self, data: dict[str, Any]) -> dict[str, Any]:
        name = data.get("name", "")
        if not name or not str(name).strip():
            raise ValueError("Framework name is required.")
        return self._repo.create_framework(data)

    def get_framework(self, framework_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_framework(framework_id)

    def list_frameworks(self) -> list[dict[str, Any]]:
        return self._repo.get_all_frameworks()

    # ------------------------------------------------------------------
    # Competency management
    # ------------------------------------------------------------------

    def create_competency(self, data: dict[str, Any]) -> dict[str, Any]:
        validation = validate_competency_data(data)
        if not validation.is_valid:
            raise ValueError(f"Validation failed: {validation.to_dict()}")
        return self._repo.create_competency(data)

    def get_competency(self, competency_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_competency(competency_id)

    def list_competencies(self) -> list[dict[str, Any]]:
        return self._repo.get_all_competencies()

    def update_competency(
        self, competency_id: str, data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        existing = self._repo.get_competency(competency_id)
        if not existing:
            raise ValueError(f"Competency '{competency_id}' not found.")

        merged = {**existing, **data}
        validation = validate_competency_data(merged)
        if not validation.is_valid:
            raise ValueError(f"Validation failed: {validation.to_dict()}")

        return self._repo.update(competency_id, data)

    def delete_competency(self, competency_id: str) -> bool:
        if not self._repo.get_competency(competency_id):
            raise ValueError(f"Competency '{competency_id}' not found.")
        return self._repo.delete(competency_id)

    # ------------------------------------------------------------------
    # Learner progress tracking
    # ------------------------------------------------------------------

    def get_learner_progress(
        self, learner_id: str, competency_id: Optional[str] = None
    ) -> list[dict[str, Any]]:
        return self._repo.get_progress(learner_id, competency_id)

    def start_competency(self, learner_id: str, competency_id: str) -> dict[str, Any]:
        existing_progress = self._repo.get_progress(learner_id, competency_id)
        if existing_progress:
            progress = existing_progress[0]
            if progress.get("status") == "not_started":
                return self._repo.update_progress(progress["id"], {"status": "in_progress"}) or progress
            raise ValueError(f"Learner already has competency in '{progress.get('status')}' status.")

        return self._repo.create_progress(
            {
                "learner_id": learner_id,
                "competency_id": competency_id,
                "status": "in_progress",
            }
        )

    def achieve_competency(
        self,
        learner_id: str,
        competency_id: str,
        assessor_id: Optional[str] = None,
        evidence: Optional[str] = None,
    ) -> dict[str, Any]:
        existing_progress = self._repo.get_progress(learner_id, competency_id)
        if not existing_progress:
            raise ValueError("Learner has not started this competency.")

        progress = existing_progress[0]
        current_status = progress.get("status", "not_started")
        if current_status in ("achieved", "mastered"):
            raise ValueError(f"Competency already in '{current_status}' status.")

        now = datetime.now(timezone.utc).isoformat()
        update_data: dict[str, Any] = {
            "status": "achieved",
            "assessed_at": now,
        }
        if assessor_id:
            update_data["assessor_id"] = assessor_id
        if evidence:
            current_evidence = json.loads(progress.get("evidence_json", "[]"))
            current_evidence.append(evidence)
            update_data["evidence_json"] = json.dumps(current_evidence)

        updated = self._repo.update_progress(progress["id"], update_data)

        event = CompetencyAchieved(
            progress_id=progress["id"],
            learner_id=learner_id,
            competency_id=competency_id,
            status="achieved",
        )
        logger.info(
            "competency_achieved",
            extra={"progress_id": progress["id"], "event_id": event.event_id},
        )
        return updated or progress

    def master_competency(
        self,
        learner_id: str,
        competency_id: str,
        assessor_id: Optional[str] = None,
        evidence: Optional[str] = None,
    ) -> dict[str, Any]:
        existing_progress = self._repo.get_progress(learner_id, competency_id)
        if not existing_progress:
            raise ValueError("Learner has not started this competency.")

        progress = existing_progress[0]
        current_status = progress.get("status", "not_started")
        if current_status == "mastered":
            raise ValueError("Competency is already mastered.")
        if current_status not in ("in_progress", "achieved"):
            raise ValueError(f"Cannot master competency in '{current_status}' status.")

        now = datetime.now(timezone.utc).isoformat()
        update_data: dict[str, Any] = {
            "status": "mastered",
            "assessed_at": now,
        }
        if assessor_id:
            update_data["assessor_id"] = assessor_id
        if evidence:
            current_evidence = json.loads(progress.get("evidence_json", "[]"))
            current_evidence.append(evidence)
            update_data["evidence_json"] = json.dumps(current_evidence)

        updated = self._repo.update_progress(progress["id"], update_data)

        event = CompetencyAchieved(
            progress_id=progress["id"],
            learner_id=learner_id,
            competency_id=competency_id,
            status="mastered",
        )
        logger.info(
            "competency_mastered",
            extra={"progress_id": progress["id"], "event_id": event.event_id},
        )
        return updated or progress

    def add_evidence(
        self, learner_id: str, competency_id: str, evidence_text: str
    ) -> dict[str, Any]:
        if not evidence_text.strip():
            raise ValueError("Evidence text cannot be empty.")

        existing_progress = self._repo.get_progress(learner_id, competency_id)
        if not existing_progress:
            raise ValueError("Learner has not started this competency.")

        progress = existing_progress[0]
        current_evidence = json.loads(progress.get("evidence_json", "[]"))
        current_evidence.append(evidence_text.strip())
        updated = self._repo.update_progress(
            progress["id"], {"evidence_json": json.dumps(current_evidence)}
        )
        return updated or progress

    def get_competency_stats(self, competency_id: str) -> dict[str, Any]:
        all_progress = []
        for p in self._repo.get_progress("", None):
            if p.get("competency_id") == competency_id:
                all_progress.append(p)

        total = len(all_progress)
        status_counts: dict[str, int] = {}
        for p in all_progress:
            s = p.get("status", "not_started")
            status_counts[s] = status_counts.get(s, 0) + 1

        return {
            "competency_id": competency_id,
            "total_learners": total,
            "status_counts": status_counts,
            "achieved_count": status_counts.get("achieved", 0),
            "mastered_count": status_counts.get("mastered", 0),
        }

    def get_learner_summary(self, learner_id: str) -> dict[str, Any]:
        all_progress = self._get_all_progress_for_learner(learner_id)
        total = len(all_progress)
        achieved = sum(1 for p in all_progress if p.get("status") in ("achieved", "mastered"))
        mastered = sum(1 for p in all_progress if p.get("status") == "mastered")

        return {
            "learner_id": learner_id,
            "total_competencies": total,
            "achieved": achieved,
            "mastered": mastered,
            "in_progress": sum(1 for p in all_progress if p.get("status") == "in_progress"),
            "mastery_rate": round((mastered / total * 100.0), 2) if total > 0 else 0.0,
        }

    def _get_all_progress_for_learner(self, learner_id: str) -> list[dict[str, Any]]:
        all_progress = self._repo.get_progress(learner_id, None)
        return all_progress
