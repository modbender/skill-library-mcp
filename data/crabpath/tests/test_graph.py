from __future__ import annotations

from pathlib import Path

from crabpath.graph import Edge, Graph, Node, remove_from_state
from crabpath.index import VectorIndex


def _simple_graph() -> Graph:
    """ simple graph."""
    graph = Graph()
    graph.add_node(Node("a", "A", metadata={"file": "a.md"}))
    graph.add_node(Node("b", "B", metadata={"file": "a.md"}))
    graph.add_node(Node("c", "C", metadata={"file": "b.md"}))
    return graph


def test_graph_add_nodes_and_edges() -> None:
    """test graph add nodes and edges."""
    graph = _simple_graph()
    graph.add_edge(Edge("a", "b", 0.7, kind="sibling"))
    graph.add_edge(Edge("b", "c", 0.6, kind="sibling"))

    assert graph.node_count() == 3
    assert graph.edge_count() == 2
    assert graph.get_node("a") is not None
    assert graph.get_node("c").content == "C"


def test_graph_duplicate_node_replaces_previous() -> None:
    """test graph duplicate node replaces previous."""
    graph = Graph()
    graph.add_node(Node("x", "first", summary="old"))
    graph.add_node(Node("x", "second", summary="new", metadata={"k": "v"}))

    node = graph.get_node("x")
    assert node is not None
    assert node.content == "second"
    assert node.summary == "new"
    assert node.metadata["k"] == "v"
    assert graph.node_count() == 1


def test_graph_remove_node_removes_incident_edges() -> None:
    """test graph remove node removes incident edges."""
    graph = _simple_graph()
    graph.add_edge(Edge("a", "b", 0.4))
    graph.add_edge(Edge("b", "a", 0.4))
    graph.add_edge(Edge("c", "a", 0.4))

    graph.remove_node("a")

    assert graph.node_count() == 2
    assert graph.get_node("a") is None
    assert graph.edge_count() == 0
    assert graph.outgoing("b") == []
    assert graph.incoming("b") == []


def test_graph_remove_nonexistent_node_is_noop() -> None:
    """test graph remove nonexistent node is noop."""
    graph = _simple_graph()
    graph.remove_node("missing")
    assert graph.node_count() == 3
    assert graph.edge_count() == 0


def test_remove_from_state_removes_graph_node_and_index_entry() -> None:
    """test remove from state removes graph node and index entry."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 0.5))

    index = VectorIndex()
    index.upsert("a", [1.0, 0.0])
    index.upsert("b", [0.0, 1.0])

    remove_from_state(graph, index, "a")

    assert graph.get_node("a") is None
    assert "a" not in index._vectors
    assert graph.edge_count() == 0


def test_graph_add_edge_replaces_existing_edge() -> None:
    """test graph add edge replaces existing edge."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 0.5, kind="sibling", metadata={"a": 1}))
    graph.add_edge(Edge("a", "b", 0.9, kind="inhibitory", metadata={"a": 2}))

    outgoing = graph.outgoing("a")
    assert len(outgoing) == 1
    assert outgoing[0][1].weight == 0.9
    assert outgoing[0][1].kind == "inhibitory"
    assert outgoing[0][1].metadata == {"a": 2}


def test_graph_remove_edge() -> None:
    """test graph remove edge."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 0.8))
    graph.remove_edge("a", "b")

    assert graph.edge_count() == 0
    assert graph.outgoing("a") == []


def test_graph_remove_edge_nonexistent_is_noop() -> None:
    """test graph remove edge nonexistent is noop."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.remove_edge("a", "b")

    assert graph.edge_count() == 0


def test_graph_outgoing_and_incoming_queries() -> None:
    """test graph outgoing and incoming queries."""
    graph = _simple_graph()
    graph.add_edge(Edge("a", "b", 0.5))
    graph.add_edge(Edge("a", "c", 0.6))
    graph.add_edge(Edge("b", "c", 0.4))

    outgoing_a = [n.id for n, _ in graph.outgoing("a")]
    incoming_c = {n.id for n, _ in graph.incoming("c")}

    assert outgoing_a == ["b", "c"]
    assert incoming_c == {"a", "b"}


def test_graph_empty_operations_are_safe() -> None:
    """test graph empty operations are safe."""
    graph = Graph()
    assert graph.node_count() == 0
    assert graph.edge_count() == 0
    assert graph.outgoing("missing") == []
    assert graph.incoming("missing") == []


def test_graph_missing_target_node_is_ignored_by_queries() -> None:
    """test graph missing target node is ignored by queries."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_edge(Edge("a", "ghost", 0.7))

    assert graph.outgoing("a") == []
    assert len(graph.incoming("ghost")) == 1
    assert graph.incoming("ghost")[0][0].id == "a"


def test_graph_edge_with_inhibitory_weight_is_allowed() -> None:
    """test graph edge with inhibitory weight is allowed."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", -0.25, kind="inhibitory"))

    _, edge = graph.outgoing("a")[0]
    assert edge.kind == "inhibitory"
    assert edge.weight == -0.25


def test_graph_edge_weight_is_clamped_to_bounds() -> None:
    """test graph edge weight is clamped to bounds."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))

    graph.add_edge(Edge("a", "b", 3.14))
    assert graph.outgoing("a")[0][1].weight == 1.0

    graph.add_edge(Edge("a", "b", -3.14))
    assert graph.outgoing("a")[0][1].weight == -1.0


def test_graph_save_load_round_trip_with_kinds_and_metadata() -> None:
    """test graph save load round trip with kinds and metadata."""
    graph = Graph()
    graph.add_node(Node("a", "A", metadata={"file": "a.md"}))
    graph.add_node(Node("b", "B", metadata={"file": "b.md"}))
    graph.add_node(Node("c", "C", metadata={"file": "c.md"}))
    graph.add_edge(Edge("a", "b", 0.9, kind="sibling", metadata={"e": 1}))
    graph.add_edge(Edge("b", "c", -0.25, kind="inhibitory", metadata={"e": 2}))
    graph.add_edge(Edge("a", "c", 0.4, kind="habitual", metadata={"e": 3}))

    path = Path("/tmp/graph_roundtrip.json")
    graph.save(path.as_posix())
    loaded = Graph.load(path.as_posix())

    assert loaded.node_count() == 3
    assert loaded.edge_count() == 3
    assert loaded.get_node("a").metadata == {"file": "a.md"}

    _, sib = loaded.outgoing("a")[0]
    _, inh = loaded.outgoing("b")[0]
    _, hab = loaded.outgoing("a")[1]
    assert sib.kind == "sibling"
    assert sib.metadata == {"e": 1}
    assert inh.kind == "inhibitory"
    assert hab.kind == "habitual"


def test_graph_large_graph_has_expected_counts() -> None:
    """test graph large graph has expected counts."""
    graph = Graph()
    for idx in range(1000):
        graph.add_node(Node(str(idx), f"node {idx}"))

    for idx in range(999):
        graph.add_edge(Edge(str(idx), str(idx + 1), (idx % 10) / 10.0))

    assert graph.node_count() == 1000
    assert graph.edge_count() == 999
    assert graph.incoming("0") == []
    assert graph.outgoing("999") == []
    assert graph.outgoing("500")[0][1].weight == 0.0


def test_graph_with_self_loop_is_represented() -> None:
    """test graph with self loop is represented."""
    graph = Graph()
    graph.add_node(Node("loop", "Loop"))
    graph.add_edge(Edge("loop", "loop", 0.42))

    outgoing = graph.outgoing("loop")
    assert len(outgoing) == 1
    assert outgoing[0][1].weight == 0.42
    assert graph.incoming("loop") == outgoing
    assert graph.edge_count() == 1


def test_graph_negative_and_positive_weight_bounds_after_save_load() -> None:
    """test graph negative and positive weight bounds after save load."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", -1.2))
    path = Path("/tmp/graph_bounds.json")
    graph.save(path.as_posix())
    loaded = Graph.load(path.as_posix())

    assert loaded.outgoing("a")[0][1].weight == -1.0
