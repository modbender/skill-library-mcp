"""Sim 8: same start point, different workloads produce different graphs."""

from __future__ import annotations

import json
from pathlib import Path

from crabpath import (
    DecayConfig,
    Edge,
    Graph,
    Node,
    TraversalConfig,
    apply_decay,
    apply_outcome,
    traverse,
)


RESULT_PATH = Path(__file__).with_name("individuation_results.json")


def _build_graph() -> Graph:
    graph = Graph()
    for idx in range(18):
        graph.add_node(Node(f"n{idx:02d}", f"shared node {idx}"))

    node_ids = [f"n{idx:02d}" for idx in range(18)]
    for source in node_ids:
        for target in node_ids:
            if source == target:
                continue
            graph.add_edge(Edge(source, target, 0.36))
    return graph


def _edge_map(graph: Graph) -> dict[tuple[str, str], float]:
    out: dict[tuple[str, str], float] = {}
    for source in [node.id for node in graph.nodes()]:
        for _, edge in graph.outgoing(source):
            out[(source, edge.target)] = edge.weight
    return out


def _run_workload(graph: Graph, seeds_pattern: list[str]) -> dict[tuple[str, str], float]:
    config = TraversalConfig(max_hops=2, beam_width=2)
    decay = DecayConfig(half_life=20, min_weight=0.01)

    for query_idx in range(50):
        source = seeds_pattern[query_idx % len(seeds_pattern)]
        result = traverse(graph, [(source, 1.0)], config=config)
        apply_outcome(graph, result.fired, outcome=1.0)
        apply_decay(graph, decay)
    return _edge_map(graph)


def _run() -> dict:
    base_a = _build_graph()
    base_b = _build_graph()

    coding_seeds = ["n00", "n01", "n02", "n03", "n04", "n05"]
    safety_seeds = ["n10", "n11", "n12", "n13", "n14"]

    edges_a = _run_workload(base_a, coding_seeds)
    edges_b = _run_workload(base_b, safety_seeds)

    all_keys = sorted(set(edges_a) | set(edges_b))
    diffs = [abs(edges_a[key] - edges_b[key]) for key in all_keys]
    diff_count = len([value for value in diffs if value > 0.05])
    mean_abs_diff = sum(diffs) / len(diffs)

    reflex_a = [value >= 0.8 for value in edges_a.values()]
    reflex_b = [value >= 0.8 for value in edges_b.values()]
    reflex_overlap = (
        sum(1 for ra, rb in zip(reflex_a, reflex_b) if ra and rb),
        reflex_a.count(True),
        reflex_b.count(True),
    )

    top_differences = sorted(
        [
            {"source": source, "target": target, "diff": abs(edges_a[(source, target)] - edges_b[(source, target)])}
            for source, target in all_keys
            if abs(edges_a[(source, target)] - edges_b[(source, target)]) > 0.05
        ],
        key=lambda item: item["diff"],
        reverse=True,
    )[:20]

    return {
        "simulation": "individuation",
        "query_count": 50,
        "workloads": {
            "agent_a": "coding",
            "agent_b": "safety",
        },
        "nodes": [node.id for node in sorted(base_a.nodes(), key=lambda node: node.id)],
        "graph_a_size": {"nodes": base_a.node_count(), "edges": base_a.edge_count()},
        "graph_b_size": {"nodes": base_b.node_count(), "edges": base_b.edge_count()},
        "graph_a_edges": [
            {"source": source, "target": target, "weight": weight}
            for (source, target), weight in sorted(edges_a.items())
        ],
        "graph_b_edges": [
            {"source": source, "target": target, "weight": weight}
            for (source, target), weight in sorted(edges_b.items())
        ],
        "structural_distinctness": {
            "edge_count": len(all_keys),
            "mean_abs_weight_diff": mean_abs_diff,
            "edges_differ_by_gt_0_05": diff_count,
            "reflex_overlap_count": reflex_overlap[0],
            "reflex_counts": {
                "graph_a": reflex_overlap[1],
                "graph_b": reflex_overlap[2],
            },
            "top_differences": top_differences,
        },
        "claim": {
            "met": diff_count > 10,
            "distinct_graphs": diff_count > 10,
        },
    }


def main() -> None:
    RESULT_PATH.write_text(json.dumps(_run(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
