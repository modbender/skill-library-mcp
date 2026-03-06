"""Sim: evaluate robustness when outcome feedback is noisy."""

from __future__ import annotations

import json
import random
from pathlib import Path

from crabpath import Edge, Graph, LearningConfig, Node, TraversalConfig, apply_outcome, traverse


RESULT_PATH = Path(__file__).with_name("noise_robustness_results.json")


def _build_graph() -> tuple[Graph, list[str]]:
    rng = random.Random(42)
    correct_path = ["query_node", "inspect", "validate", "approve", "ship"]
    distractors = [f"detour_{idx:02d}" for idx in range(10)]
    nodes = correct_path + distractors

    graph = Graph()
    for node_id in nodes:
        graph.add_node(Node(node_id, node_id.replace("_", " ").title()))

    for source in nodes:
        targets = []
        if source in correct_path[:-1]:
            idx = correct_path.index(source)
            targets.append(correct_path[idx + 1])
        elif source == correct_path[-1]:
            targets.append(correct_path[0])

        while len(targets) < 7:
            candidate = rng.choice(nodes)
            if candidate == source or candidate in targets:
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


def _run_with_noise(noise_rate: float) -> dict:
    graph, correct_path = _build_graph()
    correct_pairs = list(zip(correct_path[:-1], correct_path[1:]))
    rng = random.Random(42)

    query_config = TraversalConfig(max_hops=4, beam_width=1, habitual_range=(0.2, 0.8))
    nodes_fired: list[int] = []
    flipped = 0

    for query_index in range(1, 101):
        _ = query_index
        result = traverse(graph, [("query_node", 1.0)], config=query_config)
        nodes_fired.append(len(result.fired))

        if rng.random() < noise_rate:
            outcome = -1.0
            flipped += 1
        else:
            outcome = 1.0
        apply_outcome(
            graph,
            result.fired,
            outcome=outcome,
            config=LearningConfig(learning_rate=0.1),
        )

    correct_weights = {
        f"{source}->{target}": _edge_weight(graph, source, target)
        for source, target in correct_pairs
    }
    final_distractor_weights = []
    for source_id, edges in graph._edges.items():
        for target, edge in edges.items():
            if (source_id, target) not in correct_pairs:
                final_distractor_weights.append(edge.weight)

    inhibitory_correct = [
        edge_id for edge_id, weight in correct_weights.items() if weight < 0.0
    ]

    return {
        "noise_rate": noise_rate,
        "query_count": 100,
        "noise_flips": flipped,
        "correct_path": [f"{source}->{target}" for source, target in correct_pairs],
        "reaches_reflex_by_q100": all(weight >= 0.6 for weight in correct_weights.values()),
        "avg_nodes_fired_last_10": sum(nodes_fired[-10:]) / len(nodes_fired[-10:]),
        "final_correct_path_weights": correct_weights,
        "distractor_final_avg_weight": sum(final_distractor_weights) / len(final_distractor_weights),
        "inhibitory_edges_on_correct_path": inhibitory_correct,
        "nodes_fired_series": nodes_fired,
    }


def _run() -> dict:
    levels = [0.0, 0.1, 0.2, 0.3]
    level_results = [_run_with_noise(level) for level in levels]
    return {
        "simulation": "noise_robustness",
        "query_count": 100,
        "noise_levels": levels,
        "results": level_results,
        "comparison_table": [
            {
                "noise_rate": item["noise_rate"],
                "reaches_reflex_by_q100": item["reaches_reflex_by_q100"],
                "avg_nodes_fired_last_10": item["avg_nodes_fired_last_10"],
                "inhibitory_correct_edges": bool(item["inhibitory_edges_on_correct_path"]),
                "correct_vs_distractor_gap": (
                    sum(item["final_correct_path_weights"].values()) / len(item["final_correct_path_weights"])
                    - item["distractor_final_avg_weight"]
                ),
            }
            for item in level_results
        ],
    }


def main() -> None:
    RESULT_PATH.write_text(json.dumps(_run(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
