from __future__ import annotations

import json
from pathlib import Path

from crabpath.graph import Edge, Graph, Node
from crabpath.learn import maybe_create_node
from crabpath.merge import apply_merge, suggest_merges
from crabpath.score import score_retrieval
from crabpath.split import generate_summaries, split_workspace


def test_score_retrieval_with_llm_scores() -> None:
    """test score retrieval with llm scores."""
    fired = [("a", "alpha content"), ("b", "beta content")]

    def fake_llm(system_prompt: str, user_prompt: str) -> str:
        """fake llm."""
        assert "Score how useful" in system_prompt
        return json.dumps({"scores": {"a": 0.95, "b": 0.2}})

    scores = score_retrieval("find docs", fired, llm_fn=fake_llm)
    assert scores == {"a": 0.95, "b": 0.2}


def test_score_retrieval_defaults_without_llm() -> None:
    """test score retrieval defaults without llm."""
    fired = [("a", "alpha content"), ("b", "beta content")]
    scores = score_retrieval("find docs", fired, llm_fn=None)
    assert scores == {"a": 1.0, "b": 1.0}


def test_score_retrieval_accepts_node_ids_with_graph_lookup() -> None:
    """test score retrieval accepts node ids and resolves content from graph."""
    graph = Graph()
    graph.add_node(Node("a", "alpha content"))
    graph.add_node(Node("b", "beta content"))

    def fake_llm(system_prompt: str, user_prompt: str) -> str:
        """fake llm."""
        return json.dumps({"scores": {"a": 0.95, "b": 0.2}})

    scores = score_retrieval("find docs", ["a", "b"], graph=graph, llm_fn=fake_llm)
    assert scores == {"a": 0.95, "b": 0.2}


def test_suggest_merges_with_llm_confirmation() -> None:
    """test suggest merges with llm confirmation."""
    graph = Graph()
    graph.add_node(Node("a", "alpha"))
    graph.add_node(Node("b", "beta"))
    graph.add_node(Node("c", "gamma"))
    graph.add_edge(Edge("a", "b", 0.9))
    graph.add_edge(Edge("b", "a", 0.9))
    graph.add_edge(Edge("a", "c", 0.95))
    graph.add_edge(Edge("c", "a", 0.95))

    def fake_llm(system_prompt: str, user_prompt: str) -> str:
        """fake llm."""
        return json.dumps({"should_merge": True, "reason": "always co-fire"})

    suggestions = suggest_merges(graph, llm_fn=fake_llm)
    assert ("a", "b") in suggestions
    assert ("a", "c") in suggestions


def test_suggest_merges_without_llm_uses_weight_pairs() -> None:
    """test suggest merges without llm uses weight pairs."""
    graph = Graph()
    graph.add_node(Node("a", "alpha"))
    graph.add_node(Node("b", "beta"))
    graph.add_node(Node("c", "gamma"))
    graph.add_edge(Edge("a", "b", 0.9))
    graph.add_edge(Edge("b", "a", 0.9))
    graph.add_edge(Edge("a", "c", 0.2))
    graph.add_edge(Edge("c", "a", 0.95))

    suggestions = suggest_merges(graph)
    assert suggestions == [("a", "b")]
    merged = apply_merge(graph, "a", "b")
    assert merged.startswith("merged:")
    assert graph.get_node(merged) is not None


def test_maybe_create_node_with_llm() -> None:
    """test maybe create node with llm."""
    graph = Graph()
    graph.add_node(Node("a", "alpha"))
    graph.add_node(Node("b", "beta"))

    def fake_llm(system_prompt: str, user_prompt: str) -> str:
        """fake llm."""
        return json.dumps(
            {
                "should_create": True,
                "content": "How to index graphs",
                "summary": "Indexing note",
                "reason": "new query path",
            }
        )

    node_id = maybe_create_node(graph, "new query about indexing", ["a", "b"], llm_fn=fake_llm)
    assert node_id is not None
    node = graph.get_node(node_id)
    assert node is not None
    assert node.content == "How to index graphs"


def test_generate_summaries_with_llm() -> None:
    """test generate summaries with llm."""
    graph = Graph()
    graph.add_node(Node("a", "alpha topic\nMore context"))
    graph.add_node(Node("b", "beta topic\nMore context"))

    def fake_llm(system_prompt: str, user_prompt: str) -> str:
        """fake llm."""
        return json.dumps({"summary": f"summary:{user_prompt[:8]}"})

    summaries = generate_summaries(graph, llm_fn=fake_llm)
    assert summaries["a"].startswith("summary:")
    assert summaries["b"].startswith("summary:")


def test_split_workspace_with_llm_fn_signature_matches_contract(tmp_path: Path) -> None:
    """test split workspace with llm fn signature matches contract."""
    workspace = tmp_path / "split_workspace"
    workspace.mkdir()
    (workspace / "note.md").write_text("## One\nA\n\n## Two\nB")

    graph, texts = split_workspace(
        str(workspace),
        llm_fn=lambda _system, user: json.dumps({"sections": ["One section", "Two section"]}),
    )

    assert graph.node_count() == 2
    assert texts["note.md::0"] == "One section"
    assert texts["note.md::1"] == "Two section"
