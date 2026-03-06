from __future__ import annotations

from math import isclose, isfinite

from crabpath.graph import Edge, Graph, Node
from crabpath.learn import LearningConfig, apply_outcome, apply_outcome_pg, hebbian_update


def test_apply_outcome_positive_strengthens_edges() -> None:
    """test apply outcome positive strengthens edges."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.5))
    graph.add_edge(Edge("b", "c", 0.2))

    apply_outcome(graph, ["a", "b", "c"], outcome=1.0, config=LearningConfig(learning_rate=0.1, discount=1.0))

    assert graph._edges["a"]["b"].weight > 0.5
    assert graph._edges["b"]["c"].weight > 0.2


def test_apply_outcome_negative_weakens_edges() -> None:
    """test apply outcome negative weakens edges."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 0.5))

    apply_outcome(graph, ["a", "b"], outcome=-1.0, config=LearningConfig(learning_rate=0.2, discount=1.0))
    assert graph._edges["a"]["b"].weight < 0.5
    assert graph._edges["a"]["b"].weight > 0.0
    assert graph._edges["a"]["b"].kind in {"sibling", "inhibitory"}


def test_negative_outcome_creates_inhibitory_edge_if_missing() -> None:
    """test negative outcome creates inhibitory edge if missing."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))

    updates = apply_outcome(graph, ["a", "b"], outcome=-1.0, config=LearningConfig(learning_rate=0.2, discount=1.0))
    assert "a->b" in updates
    assert graph._edges["a"]["b"].kind == "inhibitory"
    assert graph._edges["a"]["b"].weight < 0.0


def test_learning_clips_weights_to_bounds() -> None:
    """test learning clips weights to bounds."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 0.98))

    apply_outcome(graph, ["a", "b"], outcome=1.0, config=LearningConfig(learning_rate=1.0, discount=1.0))
    assert graph._edges["a"]["b"].weight <= 1.0
    assert graph._edges["a"]["b"].weight == 1.0


def test_hebbian_update_strengthens_shared_edges() -> None:
    """test hebbian update strengthens shared edges."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))

    graph.add_edge(Edge("a", "b", 0.2))
    hebbian_update(graph, ["a", "b", "c"])

    assert graph._edges["a"].get("c").weight == 0.06
    assert graph._edges["a"]["b"].weight == 0.26
    assert graph._edges["b"].get("c").weight == 0.06


def test_hebbian_disconnected_nodes_create_edges() -> None:
    """test hebbian disconnected nodes create edges."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    apply_outcome(graph, ["a", "b", "c"], outcome=1.0)

    assert graph._edges.get("a", {}).get("c") is not None
    assert graph._edges.get("c") is None


def test_learning_rate_controls_magnitude_of_change() -> None:
    """test learning rate controls magnitude of change."""
    graph_slow = Graph()
    graph_fast = Graph()
    for graph in (graph_slow, graph_fast):
        graph.add_node(Node("a", "A"))
        graph.add_node(Node("b", "B"))
        graph.add_edge(Edge("a", "b", 0.2))

    apply_outcome(graph_slow, ["a", "b"], outcome=1.0, config=LearningConfig(learning_rate=0.01, discount=1.0))
    apply_outcome(graph_fast, ["a", "b"], outcome=1.0, config=LearningConfig(learning_rate=0.2, discount=1.0))

    assert graph_fast._edges["a"]["b"].weight > graph_slow._edges["a"]["b"].weight


def test_apply_outcome_uses_per_node_scores() -> None:
    """test apply outcome uses per node scores."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.2))
    graph.add_edge(Edge("b", "c", 0.2))

    apply_outcome(
        graph=graph,
        fired_nodes=["a", "b", "c"],
        outcome=1.0,
        config=LearningConfig(learning_rate=0.4, discount=1.0),
        per_node_outcomes={"a": 1.0, "b": -0.5},
    )

    assert graph._edges["a"]["b"].weight > 0.2
    assert graph._edges["b"]["c"].weight < 0.2


def test_discount_factor_reduces_later_step_credit() -> None:
    """test discount factor reduces later step credit."""
    graph = Graph()
    for node_id in ["a", "b", "c"]:
        graph.add_node(Node(node_id, node_id))
    graph.add_edge(Edge("a", "b", 0.5))
    graph.add_edge(Edge("b", "c", 0.5))

    apply_outcome(graph, ["a", "b", "c"], outcome=1.0, config=LearningConfig(learning_rate=1.0, discount=0.5))
    assert graph._edges["a"]["b"].weight > graph._edges["b"]["c"].weight


def test_apply_outcome_empty_fired_nodes_is_noop() -> None:
    """test apply outcome empty fired nodes is noop."""
    graph = Graph()
    updates = apply_outcome(graph, [], outcome=1.0)
    assert updates == {}


def test_apply_outcome_single_node_does_not_update_edges() -> None:
    """test apply outcome single node does not update edges."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    updates = apply_outcome(graph, ["a"], outcome=1.0)

    assert updates == {}
    assert graph.edge_count() == 0


def test_apply_outcome_uses_full_trajectory_not_last_edge_only() -> None:
    """test apply outcome uses full trajectory not last edge only."""
    graph = Graph()
    for node_id in ["a", "b", "c", "d"]:
        graph.add_node(Node(node_id, node_id))

    graph.add_edge(Edge("a", "b", 0.0))
    graph.add_edge(Edge("b", "c", 0.0))
    graph.add_edge(Edge("c", "d", 0.0))

    updates = apply_outcome(graph, ["a", "b", "c", "d"], outcome=1.0, config=LearningConfig(learning_rate=1.0, discount=0.5))
    assert updates["a->b"] > updates["b->c"] > updates["c->d"]


def test_apply_outcome_multiple_rounds_accumulate() -> None:
    """test apply outcome multiple rounds accumulate."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 0.1))

    for _ in range(3):
        apply_outcome(graph, ["a", "b"], outcome=1.0, config=LearningConfig(learning_rate=0.1, discount=1.0))

    assert graph._edges["a"]["b"].weight > 0.4
    assert graph._edges["a"]["b"].weight < 1.0


def test_apply_outcome_handles_missing_nodes_gracefully() -> None:
    """test apply outcome handles missing nodes gracefully."""
    graph = Graph()
    apply_outcome(graph, ["ghost", "ghost2"], outcome=1.0)
    graph.add_node(Node("ghost2", "G"))

    assert graph._edges.get("ghost", {}).get("ghost2") is not None


def test_hebbian_update_no_change_for_single_node() -> None:
    """test hebbian update no change for single node."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    hebbian_update(graph, ["a"])
    assert graph.edge_count() == 0


def test_zero_or_negative_outcome_can_flip_kind_to_inhibitory() -> None:
    """test zero or negative outcome can flip kind to inhibitory."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 0.02))

    apply_outcome(graph, ["a", "b"], outcome=-1.0, config=LearningConfig(learning_rate=0.2, discount=1.0))
    assert graph._edges["a"]["b"].kind == "inhibitory"
    assert graph._edges["a"]["b"].weight < 0.0


def test_apply_outcome_pg_updates_conserve_mass_including_stop() -> None:
    """test apply outcome pg updates conserve mass across all actions including stop."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.4))
    graph.add_edge(Edge("a", "c", -0.1))

    updates = apply_outcome_pg(graph, ["a", "b"], outcome=1.0, config=LearningConfig(learning_rate=0.6, discount=1.0))

    assert "a->__STOP__" in updates
    assert isclose(updates["a->b"] + updates["a->c"] + updates["a->__STOP__"], 0.0, rel_tol=1e-12, abs_tol=1e-12)


def test_apply_outcome_pg_chosen_edge_positive_and_non_chosen_negative_on_positive_outcome() -> None:
    """test apply outcome pg chosen edge positive while non chosen negative on positive outcome."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.2))
    graph.add_edge(Edge("a", "c", -0.2))

    updates = apply_outcome_pg(graph, ["a", "b"], outcome=1.0)

    assert updates["a->b"] > 0.0
    assert updates["a->c"] < 0.0


def test_apply_outcome_pg_signs_flip_on_negative_outcome() -> None:
    """test apply outcome pg signs flip when outcome is negative."""
    graph_positive = Graph()
    graph_negative = Graph()
    for node_id in ["a", "b", "c"]:
        graph_positive.add_node(Node(node_id, node_id))
        graph_negative.add_node(Node(node_id, node_id))
    graph_positive.add_edge(Edge("a", "b", 0.0))
    graph_negative.add_edge(Edge("a", "b", 0.0))

    updates_positive = apply_outcome_pg(graph_positive, ["a", "b"], outcome=1.0, config=LearningConfig(learning_rate=0.5))
    updates_negative = apply_outcome_pg(graph_negative, ["a", "b"], outcome=-1.0, config=LearningConfig(learning_rate=0.5))

    assert updates_positive["a->b"] > 0.0
    assert updates_negative["a->b"] < 0.0


def test_apply_outcome_pg_scales_with_temperature() -> None:
    """test apply outcome pg updates shrink as temperature increases."""
    graph_low_temp = Graph()
    graph_high_temp = Graph()
    for node_id in ["a", "b", "c"]:
        graph_low_temp.add_node(Node(node_id, node_id))
        graph_high_temp.add_node(Node(node_id, node_id))
    graph_low_temp.add_edge(Edge("a", "b", 0.0))
    graph_low_temp.add_edge(Edge("a", "c", 0.2))
    graph_high_temp.add_edge(Edge("a", "b", 0.0))
    graph_high_temp.add_edge(Edge("a", "c", 0.2))

    low = apply_outcome_pg(graph_low_temp, ["a", "b"], outcome=1.0, temperature=0.5, config=LearningConfig(learning_rate=1.0))
    high = apply_outcome_pg(graph_high_temp, ["a", "b"], outcome=1.0, temperature=2.0, config=LearningConfig(learning_rate=1.0))

    assert abs(low["a->b"]) > abs(high["a->b"])


def test_apply_outcome_pg_discounts_later_steps() -> None:
    """test apply outcome pg applies discount across trajectory steps."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_node(Node("d", "D"))
    graph.add_edge(Edge("a", "b", 0.0))
    graph.add_edge(Edge("a", "c", 0.0))
    graph.add_edge(Edge("b", "c", 0.0))
    graph.add_edge(Edge("b", "d", 0.0))

    updates = apply_outcome_pg(
        graph,
        ["a", "b", "c"],
        outcome=1.0,
        config=LearningConfig(learning_rate=1.0, discount=0.5),
    )

    assert isclose(updates["b->c"], 0.5 * updates["a->b"], rel_tol=1e-12)


def test_apply_outcome_pg_supports_baseline_subtraction() -> None:
    """test apply outcome pg subtracts baseline from outcome."""
    graph_without_baseline = Graph()
    graph_with_baseline = Graph()
    for node_id in ["a", "b", "c"]:
        graph_without_baseline.add_node(Node(node_id, node_id))
        graph_with_baseline.add_node(Node(node_id, node_id))
    graph_without_baseline.add_edge(Edge("a", "b", 0.0))
    graph_with_baseline.add_edge(Edge("a", "b", 0.0))
    graph_without_baseline.add_edge(Edge("a", "c", 0.0))
    graph_with_baseline.add_edge(Edge("a", "c", 0.0))

    updates_without_baseline = apply_outcome_pg(graph_without_baseline, ["a", "b"], outcome=1.0, baseline=0.0, config=LearningConfig(learning_rate=1.0))
    updates_with_baseline = apply_outcome_pg(graph_with_baseline, ["a", "b"], outcome=1.0, baseline=0.5, config=LearningConfig(learning_rate=1.0))

    assert isclose(updates_with_baseline["a->b"], 0.5 * updates_without_baseline["a->b"], rel_tol=1e-12)


def test_apply_outcome_pg_includes_stop_in_softmax_denominator() -> None:
    """test apply outcome pg includes stop action in softmax denominator."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.0))
    graph.add_edge(Edge("a", "c", 0.0))

    updates = apply_outcome_pg(graph, ["a", "b"], outcome=1.0, config=LearningConfig(learning_rate=0.6))

    assert "a->__STOP__" in updates
    assert isclose(updates["a->__STOP__"], -0.2, rel_tol=1e-12, abs_tol=1e-12)


def test_apply_outcome_pg_single_node_trajectory_returns_empty() -> None:
    """test apply outcome pg single-node trajectory does not update edges."""
    graph = Graph()
    graph.add_node(Node("a", "A"))

    updates = apply_outcome_pg(graph, ["a"], outcome=1.0)

    assert updates == {}


def test_apply_outcome_pg_differs_from_heuristic() -> None:
    """test apply outcome pg produces different updates from apply_outcome heuristic."""
    graph_heuristic = Graph()
    graph_pg = Graph()
    for node_id in ["a", "b", "c"]:
        graph_heuristic.add_node(Node(node_id, node_id))
        graph_pg.add_node(Node(node_id, node_id))
    graph_heuristic.add_edge(Edge("a", "b", 0.0))
    graph_heuristic.add_edge(Edge("a", "c", 0.0))
    graph_pg.add_edge(Edge("a", "b", 0.0))
    graph_pg.add_edge(Edge("a", "c", 0.0))

    heuristic_updates = apply_outcome(graph_heuristic, ["a", "b"], outcome=1.0, config=LearningConfig(learning_rate=1.0))
    pg_updates = apply_outcome_pg(graph_pg, ["a", "b"], outcome=1.0, config=LearningConfig(learning_rate=1.0))

    assert heuristic_updates["a->b"] != pg_updates["a->b"]
    assert "a->c" in pg_updates


def test_apply_outcome_pg_handles_extreme_logits_stably() -> None:
    """test apply outcome pg handles extreme edge weights without producing NaN."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_node(Node("d", "D"))
    graph.add_edge(Edge("a", "b", 1_000.0))
    graph.add_edge(Edge("a", "c", -1_000.0))
    graph.add_edge(Edge("a", "d", 500.0))

    updates = apply_outcome_pg(graph, ["a", "b"], outcome=1.0, config=LearningConfig(learning_rate=1.0))

    assert all(isfinite(delta) for delta in updates.values())
