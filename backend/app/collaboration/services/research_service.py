"""Research workspace service – projects, literature, notes, knowledge maps, bibliographies."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..domain.entities.research_workspace import (
        Bibliography,
        Citation,
        KnowledgeMap,
        LiteratureCollection,
        LiteratureEntry,
        ReadingList,
        ResearchNote,
        ResearchProject,
    )
    from ..domain.interfaces import ResearchWorkspaceRepository


class ResearchService:
    def __init__(self, repo: ResearchWorkspaceRepository) -> None:
        self._repo = repo

    def create_project(
        self,
        name: str,
        description: str,
        principal_investigator: str,
        team: list[str] | None = None,
    ) -> "ResearchProject":
        from ..domain.entities.research_workspace import ResearchProject
        project = ResearchProject(
            name=name,
            description=description,
            principal_investigator=principal_investigator,
            team=team,
        )
        self._repo.add_project(project)
        return project

    def get_project(self, project_id: str) -> "ResearchProject | None":
        return self._repo.get_project(project_id)

    def update_project(
        self,
        project_id: str,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
        team: list[str] | None = None,
    ) -> "ResearchProject":
        project = self._repo.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if status is not None:
            project.status = status
        if team is not None:
            project.team = team
        project.updated_at = datetime.now(timezone.utc)
        self._repo.update_project(project)
        return project

    def delete_project(self, project_id: str) -> None:
        self._repo.remove_project(project_id)

    def list_projects(self) -> list:
        return self._repo.all_projects()

    def create_literature_collection(
        self,
        project_id: str,
        name: str,
    ) -> "LiteratureCollection":
        from ..domain.entities.research_workspace import LiteratureCollection
        collection = LiteratureCollection(project_id=project_id, name=name)
        self._repo.add_literature_collection(collection)
        return collection

    def get_literature_collection(self, collection_id: str):
        return self._repo.get_literature_collection(collection_id)

    def list_literature_collections(self, project_id: str) -> list:
        return self._repo.get_literature_collections_for_project(project_id)

    def add_literature_entry(
        self,
        title: str,
        author: str = "",
        year: int = 0,
        source: str = "",
        abstract: str = "",
        keywords: list[str] | None = None,
        notes: str = "",
    ) -> "LiteratureEntry":
        from ..domain.entities.research_workspace import LiteratureEntry
        entry = LiteratureEntry(
            title=title,
            author=author,
            year=year,
            source=source,
            abstract=abstract,
            keywords=keywords,
            notes=notes,
        )
        self._repo.add_literature_entry(entry)
        return entry

    def get_literature_entry(self, entry_id: str):
        return self._repo.get_literature_entry(entry_id)

    def update_literature_entry(
        self,
        entry_id: str,
        title: str | None = None,
        author: str | None = None,
        year: int | None = None,
        source: str | None = None,
        abstract: str | None = None,
        read_status: str | None = None,
    ):
        entry = self._repo.get_literature_entry(entry_id)
        if not entry:
            raise ValueError(f"Literature entry {entry_id} not found")
        if title is not None:
            entry.title = title
        if author is not None:
            entry.author = author
        if year is not None:
            entry.year = year
        if source is not None:
            entry.source = source
        if abstract is not None:
            entry.abstract = abstract
        if read_status is not None:
            entry.read_status = read_status
        self._repo.update_literature_entry(entry)
        return entry

    def delete_literature_entry(self, entry_id: str) -> None:
        self._repo.remove_literature_entry(entry_id)

    def add_note(
        self,
        entry_id: str,
        content: str,
        created_by: str = "anonymous",
    ) -> "ResearchNote":
        from ..domain.entities.research_workspace import ResearchNote
        note = ResearchNote(
            entry_id=entry_id,
            content=content,
            created_by=created_by,
        )
        self._repo.add_note(note)
        return note

    def get_notes_for_entry(self, entry_id: str) -> list:
        return self._repo.get_notes_for_entry(entry_id)

    def add_citation(
        self,
        source_id: str,
        target_id: str,
        citation_type: str,
        page: int = 0,
        note: str = "",
    ) -> "Citation":
        from ..domain.entities.research_workspace import Citation
        citation = Citation(
            source_id=source_id,
            target_id=target_id,
            citation_type=citation_type,
            page=page,
            note=note,
        )
        self._repo.add_citation(citation)
        return citation

    def get_citations_for_entry(self, entry_id: str) -> list:
        return self._repo.get_citations_for_entry(entry_id)

    def create_knowledge_map(
        self,
        project_id: str,
        name: str,
    ) -> "KnowledgeMap":
        from ..domain.entities.research_workspace import KnowledgeMap
        km = KnowledgeMap(project_id=project_id, name=name)
        self._repo.add_knowledge_map(km)
        return km

    def get_knowledge_map(self, map_id: str):
        return self._repo.get_knowledge_map(map_id)

    def add_concept_to_map(
        self,
        map_id: str,
        name: str,
        description: str,
        category: str,
    ):
        km = self._repo.get_knowledge_map(map_id)
        if not km:
            raise ValueError(f"Knowledge map {map_id} not found")
        from ..domain.entities.research_workspace import KnowledgeConcept
        concept = KnowledgeConcept(name=name, description=description, category=category)
        km.concepts.append(concept)
        self._repo.update_knowledge_map(km)
        return concept

    def add_link_to_map(
        self,
        map_id: str,
        source_id: str,
        target_id: str,
        relationship: str,
        weight: float = 1.0,
    ):
        km = self._repo.get_knowledge_map(map_id)
        if not km:
            raise ValueError(f"Knowledge map {map_id} not found")
        from ..domain.entities.research_workspace import KnowledgeLink
        link = KnowledgeLink(
            source_id=source_id,
            target_id=target_id,
            relationship=relationship,
            weight=weight,
        )
        km.links.append(link)
        self._repo.update_knowledge_map(km)
        return link

    def get_knowledge_maps(self, project_id: str) -> list:
        return self._repo.get_knowledge_maps_for_project(project_id)

    def create_reading_list(
        self,
        project_id: str,
        name: str,
        item_ids: list[str] | None = None,
    ) -> "ReadingList":
        from ..domain.entities.research_workspace import ReadingList
        rl = ReadingList(project_id=project_id, name=name, item_ids=item_ids)
        self._repo.add_reading_list(rl)
        return rl

    def get_reading_lists(self, project_id: str) -> list:
        return self._repo.get_reading_lists_for_project(project_id)

    def create_bibliography(
        self,
        project_id: str,
        name: str = "default",
        entries: list[str] | None = None,
        format: str = "apa",
    ) -> "Bibliography":
        from ..domain.entities.research_workspace import Bibliography
        bib = Bibliography(
            project_id=project_id,
            name=name,
            entries=entries,
            format=format,
        )
        self._repo.add_bibliography(bib)
        return bib

    def get_bibliographies(self, project_id: str) -> list:
        return self._repo.get_bibliographies_for_project(project_id)
