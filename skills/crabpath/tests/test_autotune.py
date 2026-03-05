from __future__ import annotations

from dataclasses import fields

from crabpath.autotune import GraphHealth, apply_autotune, autotune, measure_health
from crabpath.decay import DecayConfig
from crabpath.graph import Edge, Graph, Node
from crabpath.learn import LearningConfig
from crabpath.traverse import TraversalConfig


def test_measure_health_on_empty_graph() -> None:
    """test measure health on empty graph."""
    graph = Graph()
    health = measure_health(graph)

    assert health.dormant_pct == 0.0
    assert health.habitual_pct == 0.0
    assert health.reflex_pct == 0.0
    assert health.orphan_nodes == 0
    assert health.cross_file_edge_pct == 0.0


def test_measure_health_matches_manual_counts() -> None:
    """test measure health matches manual counts."""
    graph = Graph()
    for node_id in ["a", "b", "c", "d"]:
        graph.add_node(Node(node_id, node_id, metadata={"file": "f1"}))

    graph.add_node(Node("e", "e", metadata={"file": "f2"}))
    graph.add_edge(Edge("a", "b", 0.95))
    graph.add_edge(Edge("b", "c", 0.6))
    graph.add_edge(Edge("c", "d", 0.2))
    graph.add_edge(Edge("d", "e", 0.9))
    graph.add_edge(Edge("e", "a", 0.1))

    health = measure_health(graph)
    assert health.reflex_pct == 3 / 5
    assert health.habitual_pct == 1 / 5
    assert health.dormant_pct == 1 / 5
    assert health.cross_file_edge_pct == 2 / 5
    assert health.orphan_nodes == 0


def test_health_metrics_match_manual_count_with_orphans() -> None:
    """test health metrics match manual count with orphans."""
    graph = Graph()
    graph.add_node(Node("a", "a", metadata={"file": "a.md"}))
    graph.add_node(Node("b", "b", metadata={"file": "a.md"}))
    graph.add_node(Node("c", "c", metadata={"file": "b.md"}))
    graph.add_node(Node("d", "d", metadata={"file": "b.md"}))

    graph.add_edge(Edge("a", "b", 0.4))
    graph.add_edge(Edge("c", "d", 0.1))

    assert measure_health(graph).orphan_nodes == 0


def test_autotune_healthy_graph_returns_no_recommendations() -> None:
    """test autotune healthy graph returns no recommendations."""
    graph = Graph()
    graph.add_node(Node("a", "A", metadata={"file": "a.md"}))
    graph.add_node(Node("b", "B", metadata={"file": "a.md"}))
    graph.add_node(Node("c", "C", metadata={"file": "b.md"}))
    graph.add_node(Node("d", "D", metadata={"file": "b.md"}))
    graph.add_node(Node("e", "E", metadata={"file": "a.md"}))

    # Balanced distribution around thresholds
    graph.add_edge(Edge("a", "b", 0.85))
    graph.add_edge(Edge("b", "c", 0.5))
    graph.add_edge(Edge("c", "d", 0.5))
    graph.add_edge(Edge("d", "e", 0.85))
    graph.add_edge(Edge("e", "a", 0.5))

    health = measure_health(graph)
    deltas = autotune(graph, health)
    assert deltas == []


def test_autotune_dormant_graph_recommends_decay() -> None:
    """test autotune dormant graph recommends decay."""
    graph = Graph()
    graph.add_node(Node("a", "A", metadata={"file": "a.md"}))
    graph.add_node(Node("b", "B", metadata={"file": "a.md"}))

    graph.add_edge(Edge("a", "b", 0.1))

    health = measure_health(graph)
    deltas = autotune(graph, health)
    knobs = {change["knob"] for change in deltas}

    assert "half_life" in knobs
    assert deltas[0]["suggested_adjustment"] in {"decrease", "increase"}


def test_autotune_reflex_graph_recommends_longer_half_life() -> None:
    """test autotune reflex graph recommends longer half life."""
    graph = Graph()
    graph.add_node(Node("a", "A", metadata={"file": "a.md"}))
    graph.add_node(Node("b", "B", metadata={"file": "b.md"}))

    graph.add_edge(Edge("a", "b", 0.95))
    graph.add_edge(Edge("b", "a", 0.95))

    health = measure_health(graph)
    deltas = autotune(graph, health)
    assert any(item["knob"] == "half_life" for item in deltas)
    assert any(item["suggested_adjustment"] == "increase" for item in deltas)


def test_autotune_without_cross_file_edges_reduces_promotion_threshold() -> None:
    """test autotune without cross file edges reduces promotion threshold."""
    graph = Graph()
    graph.add_node(Node("a", "A", metadata={"file": "same.md"}))
    graph.add_node(Node("b", "B", metadata={"file": "same.md"}))
    graph.add_node(Node("c", "C", metadata={"file": "same.md"}))

    graph.add_edge(Edge("a", "b", 0.4))
    graph.add_edge(Edge("b", "c", 0.4))

    deltas = autotune(graph, measure_health(graph))
    assert any(
        change["knob"] == "promotion_threshold" and change["suggested_adjustment"] == "decrease"
        for change in deltas
    )


def test_autotune_detects_orphan_nodes() -> None:
    """test autotune detects orphan nodes."""
    graph = Graph()
    graph.add_node(Node("root", "root", metadata={"file": "a.md"}))
    graph.add_node(Node("orphan", "orphan", metadata={"file": "b.md"}))
    graph.add_edge(Edge("root", "root", 0.5))

    health = measure_health(graph)
    assert health.orphan_nodes == 1


def test_autotune_recommendations_are_actionable() -> None:
    """test autotune recommendations are actionable."""
    graph = Graph()
    graph.add_node(Node("a", "A", metadata={"file": "a.md"}))
    graph.add_node(Node("b", "B", metadata={"file": "b.md"}))
    graph.add_edge(Edge("a", "b", 0.01))

    deltas = autotune(graph, measure_health(graph))
    knobs = {change["knob"] for change in deltas}
    assert knobs.issubset(
        {"half_life", "promotion_threshold", "hebbian_increment", "reflex_threshold"}
    )
    assert all("suggested_adjustment" in change for change in deltas)


def test_autotune_suggestions_match_config_fields() -> None:
    """test autotune suggestions match config fields."""
    graph = Graph()
    graph.add_node(Node("a", "A", metadata={"file": "a.md"}))
    graph.add_node(Node("b", "B", metadata={"file": "b.md"}))
    graph.add_node(Node("c", "C", metadata={"file": "c.md"}))

    graph.add_edge(Edge("a", "b", 0.1))
    graph.add_edge(Edge("b", "c", 0.1))
    graph.add_edge(Edge("c", "a", 0.95))

    deltas = autotune(graph, measure_health(graph))
    assert deltas

    suggestion_keys = {change["knob"] for change in deltas}
    valid_fields = set(fields(DecayConfig))
    valid_fields.update(fields(LearningConfig))
    valid_fields.update(fields(TraversalConfig))
    valid_field_names = {item.name for item in valid_fields}

    assert suggestion_keys.issubset(valid_field_names)


def test_apply_autotune_updates_configs() -> None:
    """test apply autotune updates configs."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_edge(Edge("a", "a", 0.1))
    suggestions = [
        {"knob": "half_life", "suggested_adjustment": "decrease", "value": 1000},
        {"knob": "promotion_threshold", "suggested_adjustment": "increase", "value": 1},
        {"knob": "hebbian_increment", "suggested_adjustment": "increase", "value": 0.04},
    ]

    decay_cfg, learn_cfg = apply_autotune(
        graph=graph,
        suggestions=suggestions,
        decay_config=DecayConfig(half_life=20),
        learning_config=LearningConfig(hebbian_increment=0.06, promotion_threshold=2),
    )

    assert decay_cfg.half_life == 10
    assert learn_cfg.promotion_threshold == 3
    assert learn_cfg.hebbian_increment == 0.1
