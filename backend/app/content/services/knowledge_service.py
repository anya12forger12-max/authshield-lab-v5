"""Knowledge graph management service."""

from __future__ import annotations

from collections import deque
from typing import Any, Optional

from ..domain.entities.content import KnowledgeNode
from ..domain.interfaces.content_repository import KnowledgeNodeRepository


class KnowledgeService:
    """Service for managing the knowledge graph of concepts, topics, and principles.

    Parameters
    ----------
    repo:
        Repository for knowledge node persistence.
    """

    def __init__(self, repo: KnowledgeNodeRepository) -> None:
        self._repo = repo

    async def create_node(
        self,
        title: str,
        description: str = "",
        node_type: str = "concept",
        related_nodes: list[str] | None = None,
        prerequisites: list[str] | None = None,
        competencies: list[str] | None = None,
    ) -> KnowledgeNode:
        """Create a new knowledge node."""
        if not title or not title.strip():
            raise ValueError("Knowledge node title is required.")
        existing = await self._repo.find_all()
        for node in existing:
            if node.title.lower() == title.strip().lower():
                raise ValueError(f"Knowledge node with title '{title}' already exists.")
        node = KnowledgeNode(
            title=title.strip(),
            description=description,
            node_type=node_type,
            related_nodes=related_nodes or [],
            prerequisites=prerequisites or [],
            competencies=competencies or [],
        )
        for prereq_id in node.prerequisites:
            prereq = await self._repo.find_by_id(prereq_id)
            if prereq is None:
                raise ValueError(f"Prerequisite node {prereq_id} not found.")
        return await self._repo.save(node)

    async def link_nodes(self, source_id: str, target_id: str) -> dict[str, Any]:
        """Create a bidirectional relationship between two nodes."""
        source = await self._repo.find_by_id(source_id)
        if source is None:
            raise ValueError(f"Source node {source_id} not found.")
        target = await self._repo.find_by_id(target_id)
        if target is None:
            raise ValueError(f"Target node {target_id} not found.")
        if source_id == target_id:
            raise ValueError("A node cannot be related to itself.")
        if target_id not in source.related_nodes:
            source.related_nodes.append(target_id)
            await self._repo.save(source)
        if source_id not in target.related_nodes:
            target.related_nodes.append(source_id)
            await self._repo.save(target)
        return {
            "source_id": source_id,
            "target_id": target_id,
            "bidirectional": True,
        }

    async def get_node_graph(self) -> dict[str, Any]:
        """Return the full knowledge graph as nodes and edges."""
        all_nodes = await self._repo.find_all()
        nodes = [
            {
                "id": n.id,
                "title": n.title,
                "description": n.description,
                "node_type": n.node_type,
                "competencies": n.competencies,
                "related_count": len(n.related_nodes),
                "prerequisites_count": len(n.prerequisites),
            }
            for n in all_nodes
        ]
        edges: list[dict[str, str]] = []
        # The key carries the edge kind. Related edges are bidirectional, so
        # they dedupe on the sorted pair; prerequisites are *directed*, and
        # previously shared the same direction-independent key space -- a
        # prerequisite whose endpoints matched an already-seen related edge
        # was silently dropped (graph reported edge_count 1 for two edges).
        seen_edges: set[tuple[str, str, str]] = set()
        for n in all_nodes:
            for related_id in n.related_nodes:
                lo, hi = sorted((n.id, related_id))
                edge_key = ("related", lo, hi)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges.append({"source": n.id, "target": related_id})
            for prereq_id in n.prerequisites:
                edge_key = ("prereq", prereq_id, n.id)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges.append({"source": prereq_id, "target": n.id})
        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": nodes,
            "edges": edges,
        }

    async def find_paths(self, start_id: str, end_id: str) -> list[list[str]]:
        """Find all simple paths between two nodes using BFS (limited depth)."""
        start_node = await self._repo.find_by_id(start_id)
        if start_node is None:
            raise ValueError(f"Start node {start_id} not found.")
        end_node = await self._repo.find_by_id(end_id)
        if end_node is None:
            raise ValueError(f"End node {end_id} not found.")
        all_nodes = await self._repo.find_all()
        adjacency: dict[str, set[str]] = {}
        for n in all_nodes:
            adjacency.setdefault(n.id, set())
            for related_id in n.related_nodes:
                adjacency[n.id].add(related_id)
                adjacency.setdefault(related_id, set()).add(n.id)
            for prereq_id in n.prerequisites:
                adjacency[prereq_id].add(n.id)
                adjacency.setdefault(n.id, set()).add(prereq_id)
        paths: list[list[str]] = []
        max_depth = 10
        queue: deque[tuple[str, list[str]]] = deque()
        queue.append((start_id, [start_id]))
        while queue:
            current, path = queue.popleft()
            if current == end_id:
                paths.append(list(path))
                continue
            if len(path) > max_depth:
                continue
            for neighbor in adjacency.get(current, set()):
                if neighbor not in path:
                    queue.append((neighbor, path + [neighbor]))
        return paths

    async def search_by_tag(self, tag: str) -> list[KnowledgeNode]:
        """Search knowledge nodes whose competencies contain the given tag."""
        all_nodes = await self._repo.find_all()
        tag_lower = tag.lower()
        return [
            n
            for n in all_nodes
            if any(tag_lower in c.lower() for c in n.competencies)
            or tag_lower in n.title.lower()
            or tag_lower in n.description.lower()
        ]

    async def validate_prerequisites(self, node_id: str) -> dict[str, Any]:
        """Validate that all prerequisites for a node exist and are resolvable."""
        node = await self._repo.find_by_id(node_id)
        if node is None:
            raise ValueError(f"Node {node_id} not found.")
        missing: list[str] = []
        found: list[str] = []
        circular: list[str] = []
        for prereq_id in node.prerequisites:
            prereq = await self._repo.find_by_id(prereq_id)
            if prereq is None:
                missing.append(prereq_id)
            else:
                found.append(prereq_id)
                if prereq_id == node_id:
                    circular.append(prereq_id)
                elif node_id in prereq.prerequisites:
                    circular.append(prereq_id)
        return {
            "node_id": node_id,
            "valid": len(missing) == 0 and len(circular) == 0,
            "total_prerequisites": len(node.prerequisites),
            "resolved": found,
            "missing": missing,
            "circular": circular,
        }

    async def get_uncovered_topics(self) -> dict[str, Any]:
        """Find knowledge nodes that have no related nodes (disconnected)."""
        all_nodes = await self._repo.find_all()
        node_ids = {n.id for n in all_nodes}
        referenced: set[str] = set()
        for n in all_nodes:
            referenced.update(n.related_nodes)
            referenced.update(n.prerequisites)
        orphans = [n for n in all_nodes if n.id not in referenced and not n.related_nodes]
        return {
            "total_nodes": len(all_nodes),
            "orphan_count": len(orphans),
            "orphans": [
                {
                    "id": n.id,
                    "title": n.title,
                    "node_type": n.node_type,
                    "description": n.description,
                }
                for n in orphans
            ],
        }
