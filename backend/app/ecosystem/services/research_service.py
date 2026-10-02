"""Research service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..domain.entities.research import (
    ResearchProject, LiteratureEntry, ResearchNote, KnowledgeMap,
    KnowledgeConcept, KnowledgeLink, ReadingList, Bibliography,
)

if TYPE_CHECKING:
    from ..domain.interfaces import ResearchRepository


class ResearchService:
    def __init__(self, repo: ResearchRepository) -> None:
        self._repo = repo

    def create_project(self, title: str, description: str = "") -> ResearchProject:
        project = ResearchProject(title=title, description=description)
        self._repo.add_project(project)
        return project

    def get_project(self, project_id: str) -> ResearchProject | None:
        return self._repo.get_project(project_id)

    def update_project(self, project_id: str, title: str | None = None, description: str | None = None, status: str | None = None) -> ResearchProject:
        project = self._repo.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        if title is not None:
            project.title = title
        if description is not None:
            project.description = description
        if status is not None:
            project.status = status
        self._repo.update_project(project)
        return project

    def delete_project(self, project_id: str) -> None:
        self._repo.remove_project(project_id)

    def list_projects(self) -> list[ResearchProject]:
        return self._repo.all_projects()

    def add_literature(self, project_id: str, title: str, author: str = "", year: int = 0, source: str = "", abstract: str = "", keywords: list[str] | None = None, notes: str = "") -> LiteratureEntry:
        entry = LiteratureEntry(
            project_id=project_id, title=title, author=author, year=year,
            source=source, abstract=abstract, keywords=keywords, notes=notes,
        )
        self._repo.add_literature_entry(entry)
        return entry

    def update_literature_status(self, entry_id: str, status: str) -> LiteratureEntry:
        entry = self._repo.get_literature_entry(entry_id)
        if not entry:
            raise ValueError(f"Entry {entry_id} not found")
        entry.read_status = status
        self._repo.update_literature_entry(entry)
        return entry

    def delete_literature(self, entry_id: str) -> None:
        self._repo.remove_literature_entry(entry_id)

    def get_literature_for_project(self, project_id: str) -> list[LiteratureEntry]:
        return self._repo.get_literature_for_project(project_id)

    def add_note(self, entry_id: str, content: str) -> ResearchNote:
        note = ResearchNote(entry_id=entry_id, content=content)
        self._repo.add_note(note)
        return note

    def get_notes_for_entry(self, entry_id: str) -> list[ResearchNote]:
        return self._repo.get_notes_for_entry(entry_id)

    def create_knowledge_map(self, project_id: str, name: str) -> KnowledgeMap:
        km = KnowledgeMap(project_id=project_id, name=name)
        self._repo.add_knowledge_map(km)
        return km

    def add_concept(self, map_id: str, name: str, description: str = "", category: str = "") -> KnowledgeConcept:
        km = self._repo.get_knowledge_map(map_id)
        if not km:
            raise ValueError(f"Knowledge map {map_id} not found")
        concept = KnowledgeConcept(map_id=map_id, name=name, description=description, category=category)
        km.concepts.append(concept)
        self._repo.add_knowledge_map(km)
        return concept

    def add_link(self, source_id: str, target_id: str, relationship: str = "", weight: float = 1.0) -> KnowledgeLink:
        link = KnowledgeLink(source_id=source_id, target_id=target_id, relationship=relationship, weight=weight)
        for km in self._repo.get_knowledge_maps_for_project(""):
            if any(c.id == source_id or c.id == target_id for c in km.concepts):
                km.links.append(link)
                self._repo.add_knowledge_map(km)
                break
        return link

    def get_knowledge_maps(self, project_id: str) -> list[KnowledgeMap]:
        return self._repo.get_knowledge_maps_for_project(project_id)

    def create_reading_list(self, project_id: str, name: str, entries: list[str] | None = None) -> ReadingList:
        rl = ReadingList(project_id=project_id, name=name, entries=entries)
        self._repo.add_reading_list(rl)
        return rl

    def get_reading_lists(self, project_id: str) -> list[ReadingList]:
        return self._repo.get_reading_lists_for_project(project_id)

    def create_bibliography(self, project_id: str, name: str = "default", entries: list[str] | None = None, format: str = "apa") -> Bibliography:
        bib = Bibliography(project_id=project_id, name=name, entries=entries, format=format)
        self._repo.add_bibliography(bib)
        return bib

    def get_bibliographies(self, project_id: str) -> list[Bibliography]:
        return self._repo.get_bibliographies_for_project(project_id)
