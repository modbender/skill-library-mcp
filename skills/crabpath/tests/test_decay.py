from __future__ import annotations

from crabpath.decay import DecayConfig, apply_decay
from crabpath.graph import Edge, Graph, Node


def test_decay_single_step_reduces_all_edges() -> None:
    """test decay single step reduces all edges."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.8))
    graph.add_edge(Edge("b", "c", 0.2))

    changed = apply_decay(graph, config=DecayConfig(half_life=10, min_weight=0.0))
    assert changed == 2
    assert graph._edges["a"]["b"].weight < 0.8
    assert graph._edges["b"]["c"].weight < 0.2


def test_decay_half_life_approx_halves_after_rounds() -> None:
    """test decay half life approx halves after rounds."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 1.0))

    config = DecayConfig(half_life=4, min_weight=0.0)
    for _ in range(4):
        apply_decay(graph, config)
    assert round(graph._edges["a"]["b"].weight, 2) == 0.5


def test_decay_clears_weights_below_min_weight() -> None:
    """test decay clears weights below min weight."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 0.02))

    changed = apply_decay(graph, config=DecayConfig(half_life=1, min_weight=0.03))
    assert changed == 1
    assert graph._edges["a"]["b"].weight == 0.0


def test_decay_empty_graph() -> None:
    """test decay empty graph."""
    graph = Graph()
    assert apply_decay(graph, config=DecayConfig(half_life=10, min_weight=0.01)) == 0


def test_decay_does_not_change_zero_weight_edges() -> None:
    """test decay does not change zero weight edges."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 0.0))

    changed = apply_decay(graph, config=DecayConfig(half_life=1, min_weight=0.0))
    assert changed == 0
    assert graph._edges["a"]["b"].weight == 0.0


def test_decay_moves_negative_weights_toward_zero() -> None:
    """test decay moves negative weights toward zero."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", -0.8))

    apply_decay(graph, config=DecayConfig(half_life=1, min_weight=0.0))
    assert graph._edges["a"]["b"].weight == -0.4


def test_decay_preserves_metadata_and_kind() -> None:
    """test decay preserves metadata and kind."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 0.8, kind="inhibitory", metadata={"k": "v"}))

    apply_decay(graph, config=DecayConfig(half_life=2, min_weight=0.0))
    edge = graph._edges["a"]["b"]
    assert edge.kind == "inhibitory"
    assert edge.metadata == {"k": "v"}


def test_decay_multiple_rounds_compound() -> None:
    """test decay multiple rounds compound."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 1.0))

    config = DecayConfig(half_life=2, min_weight=0.0)
    apply_decay(graph, config)
    first = graph._edges["a"]["b"].weight
    apply_decay(graph, config)
    second = graph._edges["a"]["b"].weight

    assert first > second
    assert round(second / first, 4) == round(0.5 ** 0.5, 4)
