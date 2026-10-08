"""Institution domain entities."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum


class OrgType(str, Enum):
    university = "university"
    enterprise = "enterprise"
    government = "government"
    training_center = "training_center"
    research_lab = "research_lab"


class ProgramStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


class Organization:
    def __init__(
        self,
        name: str,
        org_type: str,
        departments: list[str] | None = None,
        settings: dict | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.org_type = org_type
        self.departments = departments or []
        self.settings = settings or {}
        self.created_at = datetime.now(timezone.utc)


class Department:
    def __init__(
        self,
        org_id: str,
        name: str,
        description: str = "",
        instructors: list[str] | None = None,
        learners: list[str] | None = None,
        programs: list[str] | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.org_id = org_id
        self.name = name
        self.description = description
        self.instructors = instructors or []
        self.learners = learners or []
        self.programs = programs or []


class AcademicProgram:
    def __init__(
        self,
        department_id: str,
        name: str,
        description: str = "",
        duration_months: int = 0,
        competencies: list[str] | None = None,
        status: ProgramStatus = ProgramStatus.active,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.department_id = department_id
        self.name = name
        self.description = description
        self.duration_months = duration_months
        self.competencies = competencies or []
        self.status = status


class InstructorAssignment:
    def __init__(
        self,
        instructor_id: str,
        program_id: str,
        course_id: str = "",
        term: str = "",
    ) -> None:
        self.id = str(uuid.uuid4())
        self.instructor_id = instructor_id
        self.program_id = program_id
        self.course_id = course_id
        self.term = term
        self.assigned_at = datetime.now(timezone.utc)


class ResourceAllocation:
    def __init__(
        self,
        resource_type: str,
        amount: float,
        unit: str = "",
        allocated_to: str = "",
        purpose: str = "",
    ) -> None:
        self.id = str(uuid.uuid4())
        self.resource_type = resource_type
        self.amount = amount
        self.unit = unit
        self.allocated_to = allocated_to
        self.purpose = purpose
        self.allocated_at = datetime.now(timezone.utc)
