from __future__ import annotations

from crabpath.graph import Edge, Graph, Node
from crabpath.traverse import TraversalConfig, traverse, _tier


def test_traverse_prefers_highest_reflex_edge() -> None:
    """test traverse prefers highest reflex edge."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.95))
    graph.add_edge(Edge("a", "c", 0.45))

    result = traverse(graph, [("a", 1.0)], config=TraversalConfig(max_hops=1, beam_width=1))
    assert result.fired == ["a", "b"]
    assert result.steps[0].to_node == "b"
    assert result.steps[0].tier == "reflex"


def test_reflex_tier_auto_follows_without_route_fn() -> None:
    """test reflex tier auto follows without route fn."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.9))
    graph.add_edge(Edge("a", "c", 0.9))

    result = traverse(graph, [("a", 1.0)], config=TraversalConfig(max_hops=1, beam_width=2))
    assert result.steps
    assert any(step.tier == "reflex" for step in result.steps)
    assert {step.to_node for step in result.steps} == {"b", "c"}


def test_habitual_tier_calls_route_fn() -> None:
    """test habitual tier calls route fn."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.4))
    graph.add_edge(Edge("a", "c", 0.4))

    result = traverse(
        graph,
        [("a", 1.0)],
        config=TraversalConfig(max_hops=1, beam_width=2, reflex_threshold=0.95),
        route_fn=lambda _query, cands, _context: ["c"] if any(edge.target == "c" for edge in cands) else [],
    )

    assert result.fired == ["a", "c"]
    assert "b" not in result.fired


def test_dormant_tier_is_skipped() -> None:
    """test dormant tier is skipped."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 0.19))

    result = traverse(graph, [("a", 1.0)], config=TraversalConfig(max_hops=2, beam_width=1))
    assert result.fired == ["a"]
    assert len(result.steps) == 0


def test_traverse_edge_damping_reduces_effective_weight() -> None:
    """test traverse edge damping reduces effective weight."""
    graph = Graph()
    graph.add_node(Node("x", "X"))
    graph.add_node(Node("y", "Y"))
    graph.add_edge(Edge("x", "y", 0.9))
    graph.add_edge(Edge("y", "x", 0.9))

    result = traverse(graph, [("x", 1.0)], config=TraversalConfig(max_hops=4, beam_width=1, edge_damping=0.3))
    assert len(result.steps) == 4
    assert result.steps[0].effective_weight == 0.9
    assert result.steps[1].effective_weight == 0.9
    assert result.steps[2].effective_weight == 0.27
    assert result.steps[3].effective_weight == 0.27


def test_edge_damping_prevents_unbounded_cycles() -> None:
    """test edge damping prevents unbounded cycles."""
    graph = Graph()
    for node_id in "abcd":
        graph.add_node(Node(node_id, node_id))
    graph.add_edge(Edge("a", "b", 0.9))
    graph.add_edge(Edge("b", "c", 0.9))
    graph.add_edge(Edge("c", "a", 0.9))
    graph.add_edge(Edge("c", "d", 0.01))

    result = traverse(
        graph,
        [("a", 1.0)],
        config=TraversalConfig(max_hops=20, beam_width=1, edge_damping=0.2, fire_threshold=0.0),
    )
    assert len(result.steps) == 20
    assert len(result.fired) >= 3


def test_traverse_beam_width_explores_multiple_paths() -> None:
    """test traverse beam width explores multiple paths."""
    graph = Graph()
    for node_id in ["a", "b", "c", "d", "e"]:
        graph.add_node(Node(node_id, node_id))

    graph.add_edge(Edge("a", "b", 0.9))
    graph.add_edge(Edge("a", "c", 0.8))
    graph.add_edge(Edge("b", "d", 0.8))
    graph.add_edge(Edge("c", "e", 0.8))

    result = traverse(graph, [("a", 1.0)], config=TraversalConfig(max_hops=2, beam_width=2))
    assert result.fired[0] == "a"
    assert {"b", "c"}.issubset(set(result.fired))
    assert {"d", "e"}.issubset(set(result.fired))


def test_max_hops_is_respected() -> None:
    """test max hops is respected."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 0.9))
    graph.add_edge(Edge("b", "a", 0.9))

    result = traverse(graph, [("a", 1.0)], config=TraversalConfig(max_hops=3, beam_width=1))
    assert len(result.steps) == 3
    assert len(result.fired) == 2


def test_route_fn_empty_culls_all_habitual_choices() -> None:
    """test route fn empty culls all habitual choices."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.4))
    graph.add_edge(Edge("a", "c", 0.4))

    result = traverse(
        graph,
        [("a", 1.0)],
        config=TraversalConfig(max_hops=3, beam_width=2, reflex_threshold=0.95),
        route_fn=lambda _query, cands, _context: [],
    )

    assert result.fired == ["a"]
    assert result.steps == []


def test_route_fn_always_picks_same_node_and_damping_applies() -> None:
    """test route fn always picks same node and damping applies."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.7))
    graph.add_edge(Edge("b", "a", 0.7))

    result = traverse(
        graph,
        [("a", 1.0)],
        config=TraversalConfig(max_hops=4, beam_width=1, edge_damping=0.2, fire_threshold=0.0),
        route_fn=lambda _query, cands, _context: [cands[0].target] if cands else [],
    )

    assert len(result.steps) == 4
    assert result.steps[0].effective_weight == 0.7
    assert round(result.steps[2].effective_weight, 12) == 0.14


def test_traversal_without_outgoing_edges_terminates() -> None:
    """test traversal without outgoing edges terminates."""
    graph = Graph()
    graph.add_node(Node("x", "X"))
    result = traverse(graph, [("x", 1.0)], config=TraversalConfig(max_hops=10, beam_width=3))
    assert result.fired == ["x"]
    assert result.steps == []


def test_traversal_with_non_existent_seed() -> None:
    """test traversal with non existent seed."""
    graph = Graph()
    graph.add_node(Node("x", "X"))
    result = traverse(graph, [("missing", 1.0)], config=TraversalConfig(max_hops=3, beam_width=2))
    assert result.fired == []
    assert result.steps == []
    assert result.context == ""


def test_traversal_with_all_dormant_edges_returns_seed_only() -> None:
    """test traversal with all dormant edges returns seed only."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.01))
    graph.add_edge(Edge("b", "c", 0.02))

    result = traverse(graph, [("a", 1.0)], config=TraversalConfig(max_hops=3, beam_width=2, reflex_threshold=0.9))
    assert result.fired == ["a"]
    assert not result.steps


def test_traversal_skips_inhibitory_edges() -> None:
    """test traversal skips inhibitory edges."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", -0.4, kind="inhibitory"))
    graph.add_edge(Edge("a", "c", 0.4))

    result = traverse(graph, [("a", 1.0)], config=TraversalConfig(max_hops=2, beam_width=2, reflex_threshold=0.95))
    assert result.fired == ["a", "c"]
    assert result.steps[0].to_node == "c"


def test_incoming_inhibitory_edges_can_suppress_seed_node() -> None:
    """test incoming inhibitory edges can suppress seed node."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.8))
    graph.add_edge(Edge("a", "b", -0.9, kind="inhibitory"))
    graph.add_edge(Edge("c", "a", -0.9, kind="inhibitory"))

    result = traverse(graph, [("a", 1.0), ("b", 1.0)], config=TraversalConfig(max_hops=1))
    assert "b" not in result.fired


def test_traversal_context_respects_max_context_chars() -> None:
    """test traversal context respects max context chars."""
    graph = Graph()
    graph.add_node(Node("a", "A " * 80))
    graph.add_node(Node("b", "B " * 80))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.95))
    graph.add_edge(Edge("b", "c", 0.95))

    result = traverse(graph, [("a", 1.0)], config=TraversalConfig(max_hops=2, beam_width=1, max_context_chars=100))
    assert len(result.context) <= 100


def test_max_context_chars_budget_stops_traversal_early() -> None:
    """test max_context_chars budget halts traversal during expansion."""
    graph = Graph()
    for i in range(5):
        graph.add_node(Node(f"n{i}", content="x" * 1200, metadata={}))
    for i in range(4):
        graph.add_edge(Edge(f"n{i}", f"n{i+1}", 0.95))

    result = traverse(
        graph,
        [("n0", 1.0)],
        config=TraversalConfig(max_hops=10, beam_width=1, max_context_chars=2500),
    )

    assert result.fired == ["n0", "n1", "n2"]
    assert "n3" not in result.fired
    assert len(result.context) <= 2500


def test_max_fired_nodes_cap_stops_traversal() -> None:
    """test max_fired_nodes budget limits traversal expansion."""
    graph = Graph()
    for i in range(10):
        graph.add_node(Node(f"n{i}", content=f"node {i}", metadata={}))
    for i in range(9):
        graph.add_edge(Edge(f"n{i}", f"n{i+1}", 0.95))

    result = traverse(
        graph,
        [("n0", 1.0)],
        config=TraversalConfig(max_hops=10, beam_width=1, max_fired_nodes=3),
    )

    assert result.fired == ["n0", "n1", "n2"]


def test_beam_width_8_reaches_more_targets_than_width_3() -> None:
    """test wider beam reaches deeper nodes unavailable under narrow beam."""
    graph = Graph()
    graph.add_node(Node("a", "seed"))
    for i in range(8):
        graph.add_node(Node(f"b{i}", f"branch {i}"))
        graph.add_node(Node(f"c{i}", f"leaf {i}"))
        graph.add_edge(Edge("a", f"b{i}", 0.95 - 0.01 * i))
        graph.add_edge(Edge(f"b{i}", f"c{i}", 0.95))

    narrow = traverse(graph, [("a", 1.0)], config=TraversalConfig(max_hops=2, beam_width=3))
    wide = traverse(graph, [("a", 1.0)], config=TraversalConfig(max_hops=2, beam_width=8))

    assert "c7" in wide.fired
    assert "c7" not in narrow.fired


def test_edge_damping_factor_one_steps_until_hops() -> None:
    """test edge damping factor one steps until hops."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 0.9))
    graph.add_edge(Edge("b", "a", 0.9))

    result = traverse(graph, [("a", 1.0)], config=TraversalConfig(max_hops=6, beam_width=1, edge_damping=1.0))
    assert len(result.steps) == 6
    assert len(result.fired) == 2


def test_edge_damping_factor_zero_never_reuses_directed_edges() -> None:
    """test edge damping factor zero never reuses directed edges."""
    graph = Graph()
    for node_id in ["x", "y", "z"]:
        graph.add_node(Node(node_id, node_id))
    graph.add_edge(Edge("x", "y", 1.0))
    graph.add_edge(Edge("x", "z", 1.0))
    graph.add_edge(Edge("y", "x", 1.0))
    graph.add_edge(Edge("z", "x", 1.0))

    result = traverse(graph, [("x", 1.0)], config=TraversalConfig(max_hops=4, beam_width=1, edge_damping=0.0))
    assert len(result.steps) == 4
    assert len(result.steps) == len(set((step.from_node, step.to_node) for step in result.steps))


def test_traversal_context_includes_all_fired_content() -> None:
    """test traversal context includes all fired content."""
    graph = Graph()
    graph.add_node(Node("a", "alpha content"))
    graph.add_node(Node("b", "beta content"))
    graph.add_node(Node("c", "gamma content"))
    graph.add_edge(Edge("a", "b", 0.95))
    graph.add_edge(Edge("b", "c", 0.95))

    result = traverse(graph, [("a", 1.0)], config=TraversalConfig(max_hops=2, beam_width=1))
    assert "alpha content" in result.context
    assert "beta content" in result.context
    assert "gamma content" in result.context


def test_large_graph_traversal_is_responsive() -> None:
    """test large graph traversal is responsive."""
    graph = Graph()
    for i in range(50):
        graph.add_node(Node(f"n{i}", f"node {i}"))
        if i > 0:
            graph.add_edge(Edge(f"n{i-1}", f"n{i}", 0.8))

    result = traverse(
        graph,
        [("n0", 1.0)],
        config=TraversalConfig(max_hops=25, beam_width=2, fire_threshold=0.0),
    )
    assert len(result.steps) == 25
    assert len(result.fired) == 26


def test_seeds_with_higher_weights_are_explored_first() -> None:
    """test seeds with higher weights are explored first."""
    graph = Graph()
    graph.add_node(Node("high", "H"))
    graph.add_node(Node("low", "L"))
    graph.add_node(Node("common", "C"))
    graph.add_edge(Edge("high", "common", 0.6))
    graph.add_edge(Edge("low", "common", 0.6))

    result = traverse(
        graph,
        [("low", 0.1), ("high", 1.0)],
        config=TraversalConfig(max_hops=1, beam_width=2),
    )
    assert result.fired[:2] == ["high", "low"]


def test_visit_penalty_discourages_revisiting_nodes() -> None:
    """test visit penalty discourages revisiting nodes."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_node(Node("d", "D"))

    graph.add_edge(Edge("a", "b", 0.8))
    graph.add_edge(Edge("a", "c", 0.8))
    graph.add_edge(Edge("b", "d", 0.8))
    graph.add_edge(Edge("b", "a", 0.8))
    graph.add_edge(Edge("c", "d", 0.8))

    result = traverse(
        graph,
        [("a", 1.0)],
        config=TraversalConfig(max_hops=2, beam_width=2, visit_penalty=1.5),
    )

    assert result.fired == ["a", "b", "c", "d"]


def test_traversal_with_all_edges_inhibitory_or_low_returns_seed_only() -> None:
    """test traversal with all edges inhibitory or low returns seed only."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", -0.4))
    graph.add_edge(Edge("a", "c", -0.1))

    result = traverse(graph, [("a", 1.0)], config=TraversalConfig(max_hops=2, beam_width=1, reflex_threshold=0.0))
    assert result.steps == []
    assert result.fired == ["a"]


def test_traversal_tier_classification_is_stable() -> None:
    """test traversal tier classification is stable."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.9))
    graph.add_edge(Edge("a", "c", 0.5))

    result = traverse(graph, [("a", 1.0)], config=TraversalConfig(max_hops=1, beam_width=2, reflex_threshold=0.8))
    tiers = [step.tier for step in result.steps]
    assert tiers == ["reflex", "habitual"]


def test_tier_summary_in_result() -> None:
    """test tier summary in result."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_edge(Edge("a", "b", 0.2))

    result = traverse(graph, [("a", 1.0)], config=TraversalConfig())
    assert result.tier_summary == {
        "reflex": ">= 0.6",
        "habitual": "0.2 - 0.6",
        "dormant": "< 0.2",
        "inhibitory": "< -0.01",
    }


def test_tier_thresholds_use_new_boundaries() -> None:
    """test tier thresholds use new default boundaries."""
    assert _tier(0.7, TraversalConfig()) == "reflex"
    assert _tier(0.25, TraversalConfig()) == "habitual"
    assert _tier(-0.02, TraversalConfig()) == "inhibitory"
