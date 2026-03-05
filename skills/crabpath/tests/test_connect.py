from __future__ import annotations

import json

from crabpath.connect import apply_connections, suggest_connections
from crabpath.graph import Graph, Node


def test_suggest_connections_with_llm() -> None:
    """test suggest connections with llm."""
    graph = Graph()
    graph.add_node(Node("a", "deploy production checklist", metadata={"file": "deploy.md"}))
    graph.add_node(Node("b", "production rollout notes", metadata={"file": "release.md"}))
    graph.add_node(Node("c", "alpha team notes", metadata={"file": "deploy.md"}))

    def fake_llm(system_prompt: str, user_prompt: str) -> str:
        """fake llm."""
        return json.dumps(
            {
                "should_connect": True,
                "weight": 0.94,
                "reason": "same release planning topic",
            }
        )

    suggestions = suggest_connections(graph, llm_fn=fake_llm, max_candidates=5)
    assert any(item == ("a", "b", 0.94, "same release planning topic") for item in suggestions)
    assert all(source != target for source, target, *_ in suggestions)


def test_suggest_connections_without_llm() -> None:
    """test suggest connections without llm."""
    graph = Graph()
    graph.add_node(Node("a", "deploy to production from git", metadata={"file": "deploy.md"}))
    graph.add_node(Node("b", "production deployment checklist", metadata={"file": "release.md"}))
    graph.add_node(Node("c", "production status review", metadata={"file": "product.md"}))

    suggestions = suggest_connections(graph, llm_fn=None, max_candidates=2)
    assert len(suggestions) == 2
    assert suggestions[0][0] in {"a", "b", "c"}
    assert suggestions[0][3].startswith("word overlap score:")
    assert 0.0 <= suggestions[0][2] <= 1.0
    assert all(item[0] != item[1] for item in suggestions)


def test_apply_connections() -> None:
    """test apply connections."""
    graph = Graph()
    graph.add_node(Node("a", "deploy", metadata={"file": "deploy.md"}))
    graph.add_node(Node("b", "rollback", metadata={"file": "ops.md"}))
    graph.add_node(Node("c", "release notes", metadata={"file": "release.md"}))
    graph.add_node(Node("d", "metrics", metadata={"file": "metrics.md"}))

    connections = [
        ("a", "b", 0.9, "same incident path"),
        ("c", "d", 0.6, "release context"),
    ]

    added = apply_connections(graph, connections)
    assert added == 2
    assert graph._edges["a"]["b"].kind == "cross_file"
    assert graph._edges["c"]["d"].kind == "cross_file"
