"""Sim: compare traversal-only with heuristic and policy-gradient learning."""

from __future__ import annotations

import json
import random
from pathlib import Path

from crabpath import Edge, Graph, LearningConfig, Node, TraversalConfig, apply_outcome, apply_outcome_pg, traverse


RESULT_PATH = Path(__file__).with_name("static_vs_learning_results.json")


def _build_graph() -> tuple[Graph, list[str]]:
    rng = random.Random(42)
    correct_path = ["task_entry", "ingest", "transform", "verify", "publish"]
    distractor_nodes = [f"peer_{idx:02d}" for idx in range(20)]
    nodes = correct_path + distractor_nodes

    graph = Graph()
    for node_id in nodes:
        graph.add_node(Node(node_id, node_id.replace("_", " ").title()))

    for source in nodes:
        targets = []
        if source in correct_path[:-1]:
            targets.append(correct_path[correct_path.index(source) + 1])
        elif source == correct_path[-1]:
            targets.append(correct_path[0])

        while len(targets) < 6:
            candidate = rng.choice(nodes)
            if candidate == source or candidate in targets:
                continue
            targets.append(candidate)

        for target in targets:
            graph.add_edge(Edge(source, target, 0.4))

    return graph, correct_path


def _stable_path_index(signatures: list[tuple[str, ...]], window: int = 10) -> int | None:
    if len(signatures) < window:
        return None

    for start in range(len(signatures) - window + 1):
        window_set = set(signatures[start : start + window])
        if len(window_set) == 1:
            return start + 1
    return None

_STABLE_WINDOW = 10


def _run_mode(mode: str, learning_fn: callable | None = None) -> dict:
    graph, correct_path = _build_graph()
    query_config = TraversalConfig(max_hops=4, beam_width=1, habitual_range=(0.2, 0.8))
    learning_config = LearningConfig(learning_rate=0.1)

    nodes_fired_series: list[int] = []
    signatures: list[tuple[str, ...]] = []

    for query_index in range(1, 101):
        _ = query_index
        result = traverse(graph, [("task_entry", 1.0)], config=query_config)
        nodes_fired_series.append(len(result.fired))
        signatures.append(tuple(step.to_node for step in result.steps))

        if learning_fn is not None:
            learning_fn(graph, result.fired)

    stable_index = _stable_path_index(signatures, window=_STABLE_WINDOW)
    lt5_index = next((idx + 1 for idx, value in enumerate(nodes_fired_series) if value < 5), None)

    correct_pairs = list(zip(correct_path[:-1], correct_path[1:]))
    correct_weights = {}
    for source, target in correct_pairs:
        weight = 0.0
        for _, edge in graph.outgoing(source):
            if edge.target == target:
                weight = edge.weight
                break
        correct_weights[f"{source}->{target}"] = weight

    return {
        "mode": mode,
        "query_count": 100,
        "nodes_fired_series": nodes_fired_series,
        "average_nodes_fired": sum(nodes_fired_series) / len(nodes_fired_series),
        "converges_to_stable_path": stable_index is not None,
        "queries_until_stable_path": stable_index,
        "queries_until_nodes_fired_lt_5": lt5_index,
        "final_correct_path_weights": correct_weights,
        "correct_path": [f"{source}->{target}" for source, target in correct_pairs],
    }


def _run() -> dict:
    static = _run_mode("static")

    heuristic = _run_mode(
        "heuristic_learning",
        lambda graph, fired: apply_outcome(
            graph,
            fired,
            outcome=1.0,
            config=LearningConfig(learning_rate=0.1),
        ),
    )

    pg = _run_mode(
        "policy_gradient_learning",
        lambda graph, fired: apply_outcome_pg(
            graph,
            fired,
            outcome=1.0,
            config=LearningConfig(learning_rate=0.1),
            baseline=0.0,
            temperature=1.0,
        ),
    )

    return {
        "simulation": "static_vs_learning",
        "query_count": 100,
        "runs": {
            "static": static,
            "heuristic": heuristic,
            "policy_gradient": pg,
        },
        "claim": {
            "static_has_lowest_fired": static["average_nodes_fired"] <= min(
                heuristic["average_nodes_fired"],
                pg["average_nodes_fired"],
            ),
            "any_run_converges_stable": any(run["converges_to_stable_path"] for run in [static, heuristic, pg]),
        },
    }


def main() -> None:
    RESULT_PATH.write_text(json.dumps(_run(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
