"""Sim 4: selective forgetting through decay and tier collapse."""

from __future__ import annotations

import json
from pathlib import Path

from crabpath import DecayConfig, Edge, Graph, LearningConfig, Node, TraversalConfig, apply_decay, apply_outcome, traverse


RESULT_PATH = Path(__file__).with_name("forgetting_results.json")


def _build_graph() -> tuple[Graph, list[tuple[str, str]]]:
    graph = Graph()
    for idx in range(50):
        graph.add_node(Node(f"n{idx:02d}", f"forgets at node {idx}"))

    tracked_paths = [
        ("n00", "n01"),
        ("n02", "n03"),
        ("n04", "n05"),
        ("n06", "n07"),
        ("n08", "n09"),
        ("n10", "n11"),
        ("n12", "n13"),
        ("n14", "n15"),
        ("n16", "n17"),
        ("n18", "n19"),
    ]
    tracked_set = set(tracked_paths)

    node_ids = [f"n{idx:02d}" for idx in range(50)]
    for source_idx in range(50):
        source = node_ids[source_idx]
        source_int = int(source[1:])

        forward = node_ids[(source_int + 1) % 50]
        skip_one = node_ids[(source_int + 6) % 50]
        skip_two = node_ids[(source_int + 12) % 50]

        for target in (forward, skip_one, skip_two):
            weight = 0.62 if (source, target) in tracked_set else 0.34
            graph.add_edge(Edge(source, target, weight))

    return graph, tracked_paths


def _tier_distribution(graph: Graph) -> dict[str, float]:
    total = max(graph.edge_count(), 1)
    dormant = habitual = reflex = 0
    for node in graph.nodes():
        for _, edge in graph.outgoing(node.id):
            if edge.weight >= 0.8:
                reflex += 1
            elif edge.weight >= 0.3:
                habitual += 1
            else:
                dormant += 1

    return {
        "total_edges": total,
        "dormant": dormant,
        "habitual": habitual,
        "reflex": reflex,
        "dormant_pct": dormant / total,
        "habitual_pct": habitual / total,
        "reflex_pct": reflex / total,
    }


def _run() -> dict:
    graph, paths = _build_graph()
    config = TraversalConfig(max_hops=1, beam_width=1)
    decay = DecayConfig(half_life=100, min_weight=0.01)
    learning_config = LearningConfig(learning_rate=1.0)

    history: list[dict] = []
    snapshots: list[dict] = []
    tracked_queries = {1, 25, 50, 100}

    for q in range(1, 101):
        source, _target = paths[(q - 1) % len(paths)]
        result = traverse(graph, [(source, 1.0)], config=config)
        apply_outcome(graph, result.fired, outcome=1.0, config=learning_config)
        apply_decay(graph, decay)
        dist = _tier_distribution(graph)
        dist["query"] = q
        history.append(dist.copy())

        if q in tracked_queries:
            snapshots.append({"query": q, **dist})

    final = _tier_distribution(graph)
    dormant_pct = final["dormant_pct"]
    return {
        "simulation": "selective_forgetting",
        "query_count": 100,
        "tier_history": history,
        "tracked_query_snapshots": snapshots,
        "tier_distribution_by_query": snapshots,
        "final_tier_distribution": final,
        "claim": {
            "dormant_after_training": {
                "dormant_pct": dormant_pct,
                "low": 0.85,
                "high": 0.95,
                "met": 0.85 <= dormant_pct <= 0.95,
            }
        },
    }


def main() -> None:
    RESULT_PATH.write_text(json.dumps(_run(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
