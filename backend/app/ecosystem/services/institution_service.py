"""Institution service."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..domain.interfaces import InstitutionRepository
    from ..domain.entities.institution import (
        Organization, Department, AcademicProgram,
        InstructorAssignment, ResourceAllocation,
    )


class InstitutionService:
    def __init__(self, repo: InstitutionRepository) -> None:
        self._repo = repo

    def create_organization(self, name: str, org_type: str, settings: dict | None = None) -> Organization:
        org = Organization(name=name, org_type=org_type, settings=settings)
        self._repo.add_organization(org)
        return org

    def get_organization(self, org_id: str) -> Organization | None:
        return self._repo.get_organization(org_id)

    def update_organization(self, org_id: str, name: str | None = None, org_type: str | None = None, settings: dict | None = None) -> Organization:
        org = self._repo.get_organization(org_id)
        if not org:
            raise ValueError(f"Organization {org_id} not found")
        if name is not None:
            org.name = name
        if org_type is not None:
            org.org_type = org_type
        if settings is not None:
            org.settings = settings
        self._repo.update_organization(org)
        return org

    def delete_organization(self, org_id: str) -> None:
        self._repo.remove_organization(org_id)

    def list_organizations(self) -> list[Organization]:
        return self._repo.all_organizations()

    def add_department(self, org_id: str, name: str, description: str = "") -> Department:
        dept = Department(org_id=org_id, name=name, description=description)
        self._repo.add_department(dept)
        org = self._repo.get_organization(org_id)
        if org:
            org.departments.append(dept.id)
            self._repo.update_organization(org)
        return dept

    def get_department(self, dept_id: str) -> Department | None:
        return self._repo.get_department(dept_id)

    def update_department(self, dept_id: str, name: str | None = None, description: str | None = None) -> Department:
        dept = self._repo.get_department(dept_id)
        if not dept:
            raise ValueError(f"Department {dept_id} not found")
        if name is not None:
            dept.name = name
        if description is not None:
            dept.description = description
        self._repo.update_department(dept)
        return dept

    def delete_department(self, dept_id: str) -> None:
        self._repo.remove_department(dept_id)

    def get_departments_for_org(self, org_id: str) -> list[Department]:
        return self._repo.get_departments_for_org(org_id)

    def create_program(self, department_id: str, name: str, description: str = "", duration_months: int = 0, competencies: list[str] | None = None) -> AcademicProgram:
        prog = AcademicProgram(
            department_id=department_id, name=name, description=description,
            duration_months=duration_months, competencies=competencies,
        )
        self._repo.add_program(prog)
        return prog

    def get_program(self, prog_id: str) -> AcademicProgram | None:
        return self._repo.get_program(prog_id)

    def update_program(self, prog_id: str, name: str | None = None, description: str | None = None, status: str | None = None) -> AcademicProgram:
        prog = self._repo.get_program(prog_id)
        if not prog:
            raise ValueError(f"Program {prog_id} not found")
        if name is not None:
            prog.name = name
        if description is not None:
            prog.description = description
        if status is not None:
            prog.status = status
        self._repo.update_program(prog)
        return prog

    def get_programs_for_department(self, dept_id: str) -> list[AcademicProgram]:
        return self._repo.get_programs_for_department(dept_id)

    def assign_instructor(self, instructor_id: str, program_id: str, course_id: str = "", term: str = "") -> InstructorAssignment:
        assignment = InstructorAssignment(instructor_id=instructor_id, program_id=program_id, course_id=course_id, term=term)
        self._repo.add_assignment(assignment)
        return assignment

    def get_instructor_assignments(self, instructor_id: str) -> list[InstructorAssignment]:
        return self._repo.get_assignments_for_instructor(instructor_id)

    def allocate_resource(self, resource_type: str, amount: float, unit: str = "", allocated_to: str = "", purpose: str = "") -> ResourceAllocation:
        alloc = ResourceAllocation(resource_type=resource_type, amount=amount, unit=unit, allocated_to=allocated_to, purpose=purpose)
        self._repo.add_allocation(alloc)
        return alloc

    def get_allocations(self, org_id: str) -> list[ResourceAllocation]:
        return self._repo.get_allocations_for_org(org_id)
