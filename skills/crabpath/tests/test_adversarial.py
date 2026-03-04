from __future__ import annotations

from pathlib import Path

from crabpath.graph import Edge, Graph, Node
from crabpath.replay import replay_queries
from crabpath.split import split_workspace
from crabpath.traverse import TraversalConfig, traverse


def test_traverse_handles_empty_content_node() -> None:
    """test traverse handles empty content node."""
    graph = Graph()
    graph.add_node(Node("empty", "", metadata={"file": "a.md"}))
    graph.add_node(Node("other", "other chunk", metadata={"file": "a.md"}))
    graph.add_edge(Edge("empty", "other", 0.9))

    result = traverse(graph=graph, seeds=[("empty", 1.0)], config=TraversalConfig(max_hops=2))

    assert result.fired == ["empty", "other"]


def test_unicode_heavy_split_and_traverse(tmp_path: Path) -> None:
    """test unicode heavy split and traverse."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "unicode.txt").write_text(
        "中文内容与🌟 emoji 表情，另外再加上 العربية and日本語.",
        encoding="utf-8",
    )

    graph, texts = split_workspace(workspace)
    assert graph.node_count() == 1
    assert len(next(iter(texts.values()))) > 0


def test_split_workspace_large_single_chunk(tmp_path: Path) -> None:
    """test split workspace large single chunk."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    payload = "x" * (100 * 1024)
    (workspace / "large.md").write_text(payload, encoding="utf-8")

    graph, texts = split_workspace(workspace)

    assert graph.node_count() == 1
    assert list(texts.values())[0] == payload


def test_traverse_self_loop_edge_stable() -> None:
    """test traverse self loop edge stable."""
    graph = Graph()
    graph.add_node(Node("a", "loop", metadata={"file": "loop.md"}))
    graph.add_edge(Edge("a", "a", 1.0))

    result = traverse(graph=graph, seeds=[("a", 1.0)], config=TraversalConfig(max_hops=4, beam_width=2))
    assert result.fired[0] == "a"
    assert len(result.steps) <= 4


def test_traverse_cycles_through_three_nodes() -> None:
    """test traverse cycles through three nodes."""
    graph = Graph()
    graph.add_node(Node("a", "A", metadata={"file": "a.md"}))
    graph.add_node(Node("b", "B", metadata={"file": "a.md"}))
    graph.add_node(Node("c", "C", metadata={"file": "a.md"}))
    graph.add_edge(Edge("a", "b", 0.9))
    graph.add_edge(Edge("b", "c", 0.9))
    graph.add_edge(Edge("c", "a", 0.9))

    result = traverse(graph=graph, seeds=[("a", 1.0)], config=TraversalConfig(max_hops=3, beam_width=2))
    assert {"a", "b", "c"}.issubset(set(result.fired))


def test_traverse_with_special_character_node_ids() -> None:
    """test traverse with special character node ids."""
    graph = Graph()
    source_id = "node:1/2?x#y"
    graph.add_node(Node(source_id, "special id node", metadata={"file": "a.md"}))
    graph.add_node(Node("other", "other node", metadata={"file": "a.md"}))
    graph.add_edge(Edge(source_id, "other", 0.9))

    result = traverse(graph=graph, seeds=[(source_id, 1.0)], config=TraversalConfig(max_hops=2))

    assert source_id in result.fired
    assert "other" in result.fired


def test_empty_graph_has_no_nodes_or_edges() -> None:
    """test empty graph has no nodes or edges."""
    graph = Graph()
    assert graph.node_count() == 0
    assert graph.edge_count() == 0


def test_query_on_empty_graph_is_noop() -> None:
    """test query on empty graph is noop."""
    graph = Graph()
    stats = replay_queries(graph=graph, queries=["anything"], config=TraversalConfig(max_hops=2))
    assert stats["queries_replayed"] == 1
    assert stats["edges_reinforced"] == 0
