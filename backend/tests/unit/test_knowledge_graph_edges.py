"""Regression tests for a silent edge-dropping bug in the knowledge graph.

``get_node_graph`` de-duplicates edges with a single ``seen_edges`` set shared
by two loops, keyed on ``tuple(sorted((a, b)))`` -- a *direction-independent*
pair. That is correct for ``related_nodes`` (the sibling accessor marks those
edges ``bidirectional: True``), but prerequisites are **directed**: "B requires
A" is not the same edge as "A relates to B".

Because both loops wrote the same key space, a prerequisite whose endpoints
matched an already-seen related edge was silently discarded. Given node A
with ``related_nodes=["B"]`` and node B with ``prerequisites=["A"]``, the graph
reported ``edge_count: 1`` where two edges exist, and the prerequisite was gone
-- no error, no warning, just a wrong graph that a renderer would draw
correctly-looking but semantically wrong output from.

The key now carries the edge kind, so the two spaces cannot collide while
within-kind de-duplication is unchanged.
"""

from __future__ import annotations

import pytest

from app.content.services.knowledge_service import KnowledgeService


class _Node:
    def __init__(self, node_id, related=(), prerequisites=()):
        self.id = node_id
        self.title = node_id
        self.description = ""
        self.node_type = "concept"
        self.competencies: list[str] = []
        self.related_nodes = list(related)
        self.prerequisites = list(prerequisites)


class _Repo:
    def __init__(self, nodes):
        self._nodes = nodes

    async def find_all(self):
        return self._nodes


def _graph(nodes):
    import asyncio

    return asyncio.run(KnowledgeService(_Repo(nodes)).get_node_graph())  # type: ignore[arg-type]


class TestNodeGraphEdges:
    def test_prerequisite_is_not_dropped_by_a_related_edge(self):
        # Regression: edge_count came back 1 for these two declared edges.
        graph = _graph([_Node("A", related=["B"]), _Node("B", prerequisites=["A"])])
        assert graph["edge_count"] == 2
        assert ("A", "B") in [(e["source"], e["target"]) for e in graph["edges"]]

    def test_related_edges_are_still_deduplicated(self):
        # A<->B declared from both sides must still collapse to one edge.
        graph = _graph([_Node("A", related=["B"]), _Node("B", related=["A"])])
        assert graph["edge_count"] == 1

    def test_opposite_prerequisites_are_distinct(self):
        # Directed edges: A requires B and B requires A are two different edges.
        graph = _graph([_Node("A", prerequisites=["B"]), _Node("B", prerequisites=["A"])])
        assert graph["edge_count"] == 2

    def test_duplicate_prerequisite_is_still_deduplicated(self):
        # The same node listing the same prerequisite twice is one edge.
        graph = _graph([_Node("A", prerequisites=["B", "B"])])
        assert graph["edge_count"] == 1

    def test_empty_graph(self):
        graph = _graph([])
        assert graph["node_count"] == 0
        assert graph["edge_count"] == 0
        assert graph["edges"] == []

    @pytest.mark.parametrize("node_count", [1, 2, 3])
    def test_node_count_matches(self, node_count):
        nodes = [_Node(f"n{i}") for i in range(node_count)]
        graph = _graph(nodes)
        assert graph["node_count"] == node_count
