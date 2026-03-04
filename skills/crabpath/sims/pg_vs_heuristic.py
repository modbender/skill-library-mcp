"""Sim: compare policy-gradient updates with the heuristic outcome updates."""

from __future__ import annotations

import json
import random
from pathlib import Path

from crabpath import (
    Edge,
    Graph,
    LearningConfig,
    Node,
    TraversalConfig,
    apply_outcome,
    apply_outcome_pg,
    traverse,
)


RESULT_PATH = Path(__file__).with_name("pg_vs_heuristic_results.json")


def _build_graph() -> tuple[Graph, list[str]]:
    random.seed(42)
    correct_path = ["start_task", "prepare", "compile", "deploy", "verify"]
    distractor_nodes = [f"aux_{idx:02d}" for idx in range(15)]
    node_ids = correct_path + distractor_nodes

    graph = Graph()
    for node_id in node_ids:
        graph.add_node(Node(node_id, node_id.replace("_", " ").title()))

    for source in node_ids:
        targets = []
        if source in correct_path[:-1]:
            targets.append(correct_path[correct_path.index(source) + 1])
        elif source == correct_path[-1]:
            targets.append(correct_path[0])

        while len(targets) < 8:
            candidate = random.choice(node_ids)
            if candidate == source:
                continue
            if candidate in targets:
                continue
            targets.append(candidate)

        for target in targets:
            graph.add_edge(Edge(source, target, 0.4))

    return graph, correct_path


def _edge_weight(graph: Graph, source: str, target: str) -> float:
    for _, edge in graph.outgoing(source):
        if edge.target == target:
            return edge.weight
    return 0.0


def _total_edge_weight(graph: Graph) -> float:
    return sum(edge.weight for source_edges in graph._edges.values() for edge in source_edges.values())


def _edge_pairs(graph: Graph) -> list[tuple[str, str, float]]:
    return [
        (source_id, edge.target, edge.weight)
        for source_id, edges in graph._edges.items()
        for edge in edges.values()
    ]


def _run_variant(
    graph: Graph,
    correct_path: list[str],
    apply_fn: callable,
) -> dict:
    query_config = TraversalConfig(max_hops=4, beam_width=1, habitual_range=(0.2, 0.8))
    nodes_fired: list[int] = []
    correct_path_weights: list[dict[str, float]] = []
    conservation_trace: list[float] = []
    convergence_query = None

    correct_pairs = list(zip(correct_path[:-1], correct_path[1:]))
    correct_set = set(correct_pairs)

    for query_index in range(1, 101):
        result = traverse(graph, [("start_task", 1.0)], config=query_config)
        updates = apply_fn(graph, result.fired)

        fired_count = len(result.fired)
        nodes_fired.append(fired_count)

        current_correct_weights = {
            f"{source}->{target}": _edge_weight(graph, source, target)
            for source, target in correct_pairs
        }
        correct_path_weights.append(current_correct_weights)

        conservation_trace.append(sum(updates.values()))
        if convergence_query is None and all(value >= 0.6 for value in current_correct_weights.values()):
            convergence_query = query_index

    final_correct_weights = correct_path_weights[-1]
    all_edges = _edge_pairs(graph)
    distractor_weights = [weight for source, target, weight in all_edges if (source, target) not in correct_set]

    return {
        "nodes_fired": nodes_fired,
        "nodes_fired_last_10_average": sum(nodes_fired[-10:]) / len(nodes_fired[-10:]),
        "convergence_query_reflex_threshold": convergence_query,
        "final_correct_path_weights": final_correct_weights,
        "final_total_edge_weight": _total_edge_weight(graph),
        "final_distractor_edge_avg_weight": sum(distractor_weights) / len(distractor_weights),
        "final_distractor_edge_count": len(distractor_weights),
        "final_node_count": len(graph.nodes()),
        "edge_weights_series_last_10": correct_path_weights[-10:],
        "conservation_check": {
            "per_query_delta_sum_min": min(conservation_trace),
            "per_query_delta_sum_max": max(conservation_trace),
            "per_query_delta_sum_mean": sum(conservation_trace) / len(conservation_trace),
            "total_delta_sum": sum(conservation_trace),
        },
    }


def _run() -> dict:
    graph_heuristic, correct_path = _build_graph()
    correct_pairs = list(zip(correct_path[:-1], correct_path[1:]))
    heuristic_result = _run_variant(
        graph_heuristic,
        correct_path,
        lambda g, fired: apply_outcome(g, fired, outcome=1.0, config=LearningConfig(learning_rate=0.1)),
    )

    graph_pg, _ = _build_graph()
    pg_result = _run_variant(
        graph_pg,
        correct_path,
        lambda g, fired: apply_outcome_pg(
            g,
            fired,
            outcome=1.0,
            config=LearningConfig(learning_rate=0.1),
            baseline=0.0,
            temperature=1.0,
        ),
    )

    return {
        "simulation": "pg_vs_heuristic",
        "query_count": 100,
        "correct_path": [f"{source}->{target}" for source, target in correct_pairs],
        "runs": {
            "heuristic": heuristic_result,
            "policy_gradient": pg_result,
        },
        "claim": {
            "heuristic_reaches_reflex": heuristic_result["convergence_query_reflex_threshold"] is not None,
            "pg_reaches_reflex": pg_result["convergence_query_reflex_threshold"] is not None,
            "pg_conservation_near_zero": abs(pg_result["conservation_check"]["total_delta_sum"]) <= 0.1,
            "heuristic_growth_overshoots": heuristic_result["final_total_edge_weight"]
            > pg_result["final_total_edge_weight"],
        },
    }


def main() -> None:
    RESULT_PATH.write_text(json.dumps(_run(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
