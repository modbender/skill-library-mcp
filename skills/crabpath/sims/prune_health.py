"""Sim: pruning low-weight edges improves graph health without breaking traversal."""

from __future__ import annotations

import json
from pathlib import Path

from crabpath import (
    DecayConfig,
    Edge,
    Graph,
    LearningConfig,
    Node,
    TraversalConfig,
    apply_decay,
    apply_outcome,
    measure_health,
    prune_edges,
    traverse,
)


RESULT_PATH = Path(__file__).with_name("prune_health_results.json")


def _build_graph() -> tuple[Graph, list[str]]:
    graph = Graph()
    node_count = 30
    node_ids = [f"k{idx:02d}" for idx in range(node_count)]

    for node_id in node_ids:
        graph.add_node(Node(node_id, f"fully connected node {node_id}"))

    for source in node_ids:
        for target in node_ids:
            if source == target:
                continue
            graph.add_edge(Edge(source, target, 0.35))

    return graph, node_ids[:5]


def _run_query_batch(
    graph: Graph,
    keys: list[str],
    query_count: int,
    config: TraversalConfig,
    learning_rate: float = 0.08,
) -> list[dict[str, int | list[str]]]:
    decay = DecayConfig(half_life=10, min_weight=0.01)
    records: list[dict[str, int | list[str]]] = []
    for query_index in range(1, query_count + 1):
        source = keys[(query_index - 1) % len(keys)]
        result = traverse(graph, [(source, 1.0)], config=config)
        apply_outcome(
            graph,
            result.fired,
            outcome=1.0,
            config=LearningConfig(learning_rate=learning_rate),
        )
        apply_decay(graph, decay)
        result_fired = result.fired
        records.append(
            {
                "query": query_index,
                "seed": source,
                "nodes_fired": len(result_fired),
                "fired": result_fired,
            }
        )

    return records


def _avg(values: list[int]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _run() -> dict:
    graph, keys = _build_graph()
    config = TraversalConfig(max_hops=2, beam_width=5, habitual_range=(0.2, 0.8))

    training_records = _run_query_batch(graph, keys, 100, config=config)
    health_before = measure_health(graph).__dict__
    edges_before = graph.edge_count()
    nodes_before_termination = _avg([record["nodes_fired"] for record in training_records if isinstance(record["nodes_fired"], int)])

    edges_removed = prune_edges(graph, below=0.05)
    edges_after = graph.edge_count()
    health_after = measure_health(graph).__dict__

    post_records = []
    verification_ok = True
    post_run_records = _run_query_batch(graph, keys, 20, config=config)
    for record in post_run_records:
        source = record["seed"]
        fired_nodes = record["fired"]
        post_records.append(
            {
                "query": record["query"],
                "seed": source,
                "nodes_fired": record["nodes_fired"],
                "reached_non_seed_key": any(item for item in fired_nodes if item != source and item in keys),
            }
        )
        if not post_records[-1]["reached_non_seed_key"]:
            verification_ok = False

    return {
        "simulation": "prune_health",
        "query_count": 120,
        "keys": keys,
        "edges_before_prune": edges_before,
        "edges_after_prune": edges_after,
        "edges_removed": edges_removed,
        "dormant_pct_before": health_before["dormant_pct"],
        "dormant_pct_after": health_after["dormant_pct"],
        "avg_nodes_fired_after_prune": _avg([record["nodes_fired"] for record in post_run_records]),
        "first_100_avg_nodes_fired": nodes_before_termination,
        "training_records": training_records,
        "post_prune_records": post_records,
        "claim": {
            "prune_improves_health": {
                "before": health_before["dormant_pct"],
                "after": health_after["dormant_pct"],
                "met": health_after["dormant_pct"] < health_before["dormant_pct"],
            },
            "prune_removed_edges": {
                "before": edges_before,
                "after": edges_after,
                "met": edges_removed > 0,
            },
            "traversal_not_broken": {
                "met": verification_ok,
                "queries_ok": sum(1 for item in post_records if item["reached_non_seed_key"]),
            },
        },
    }


def main() -> None:
    RESULT_PATH.write_text(json.dumps(_run(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
