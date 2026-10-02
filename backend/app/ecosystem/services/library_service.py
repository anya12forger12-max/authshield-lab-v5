"""Library service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..domain.entities.library import LibraryItem, Bookmark, Annotation, Citation

if TYPE_CHECKING:
    from ..domain.interfaces import LibraryRepository


class LibraryService:
    def __init__(self, repo: LibraryRepository) -> None:
        self._repo = repo

    def add_item(self, item: LibraryItem) -> LibraryItem:
        self._repo.add_item(item)
        return item

    def search_items(self, query: str = "", item_type: str = "", tag: str = "") -> list[LibraryItem]:
        return self._repo.search_items(query, item_type, tag)

    def get_item(self, item_id: str) -> LibraryItem | None:
        return self._repo.get_item(item_id)

    def remove_item(self, item_id: str) -> None:
        self._repo.remove_item(item_id)

    def add_bookmark(self, item_id: str, user_id: str, note: str = "", page: int = 0) -> Bookmark:
        bm = Bookmark(item_id=item_id, user_id=user_id, note=note, page=page)
        self._repo.add_bookmark(bm)
        return bm

    def add_annotation(self, item_id: str, user_id: str, text: str, highlight: str = "", page: int = 0) -> Annotation:
        ann = Annotation(item_id=item_id, user_id=user_id, text=text, highlight=highlight, page=page)
        self._repo.add_annotation(ann)
        return ann

    def add_citation(self, source_item_id: str, target_item_id: str, citation_type: str, page: int = 0, note: str = "") -> Citation:
        cit = Citation(source_item_id=source_item_id, target_item_id=target_item_id, citation_type=citation_type, page=page, note=note)
        self._repo.add_citation(cit)
        return cit

    def get_bookmarks_for_item(self, item_id: str) -> list[Bookmark]:
        return self._repo.get_bookmarks_for_item(item_id)

    def get_annotations_for_item(self, item_id: str) -> list[Annotation]:
        return self._repo.get_annotations_for_item(item_id)

    def get_citations_for_item(self, item_id: str) -> list[Citation]:
        return self._repo.get_citations_for_item(item_id)

    def generate_bibliography(self, item_ids: list[str], format: str = "apa") -> str:
        lines: list[str] = []
        for item_id in item_ids:
            item = self._repo.get_item(item_id)
            if not item:
                continue
            if format == "apa":
                lines.append(f"{item.author} ({item.created_at.year}). {item.title}. [{item.item_type.value}].")
            elif format == "mla":
                lines.append(f"{item.author}. {item.title}. {item.created_at.year}.")
            elif format == "chicago":
                lines.append(f"{item.author}, {item.title}, {item.created_at.year}.")
            else:
                lines.append(f"{item.author}. {item.title}. {item.created_at.year}.")
        return "\n".join(lines)
