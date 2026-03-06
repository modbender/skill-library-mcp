"""Sim: merge reduces context cost for co-firing neighbors."""

from __future__ import annotations

import json
from pathlib import Path

from crabpath import (
    Edge,
    Graph,
    LearningConfig,
    Node,
    TraversalConfig,
    apply_outcome,
    apply_merge,
    suggest_merges,
    traverse,
)


RESULT_PATH = Path(__file__).with_name("merge_compression_results.json")


def _build_graph() -> tuple[Graph, list[tuple[str, str]]]:
    graph = Graph()
    pair_nodes: list[tuple[str, str]] = []

    for pair_idx in range(8):
        node_a = f"pair_{pair_idx:02d}_a"
        node_b = f"pair_{pair_idx:02d}_b"
        base = f"src/{pair_idx:02d}/pipeline.py"
        graph.add_node(
            Node(
                node_a,
                content=(
                    f"{base}: prepare the shared payload for pair {pair_idx}. "
                    f"Step A normalizes incoming artifacts and writes chunk A."
                ),
                metadata={"file": base},
            )
        )
        graph.add_node(
            Node(
                node_b,
                content=(
                    f"{base}: prepare the shared payload for pair {pair_idx}. "
                    f"Step B normalizes incoming artifacts and writes chunk B."
                ),
                metadata={"file": base},
            )
        )
        graph.add_edge(Edge(node_a, node_b, 0.85))
        graph.add_edge(Edge(node_b, node_a, 0.85))
        pair_nodes.append((node_a, node_b))

    for index in range(24):
        node_id = f"noise_{index:02d}"
        graph.add_node(Node(node_id, f"unrelated noise context chunk {index:02d}"))

    return graph, pair_nodes


def _run_queries(
    graph: Graph,
    pair_nodes: list[tuple[str, str]],
    query_count: int,
    seeds_for_pair: callable,
) -> list[dict[str, float | int]]:
    config = TraversalConfig(max_hops=1, beam_width=8, max_fired_nodes=6)
    updates: list[dict[str, float | int]] = []

    for query_index in range(1, query_count + 1):
        source_pair = pair_nodes[(query_index - 1) % len(pair_nodes)]
        seeds = seeds_for_pair(source_pair)
        result = traverse(graph, seeds, config=config)
        apply_outcome(
            graph,
            result.fired,
            outcome=1.0,
            config=LearningConfig(learning_rate=0.08),
        )
        updates.append(
            {
                "query": query_index,
                "pair": list(source_pair),
                "nodes_fired": len(result.fired),
                "context_chars": len(result.context),
            }
        )

    return updates


def _sum_before(graph: Graph) -> int:
    return graph.node_count()


def _sum_edges(graph: Graph) -> int:
    return graph.edge_count()


def _avg(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _run() -> dict:
    graph, pair_nodes = _build_graph()

    before = _run_queries(
        graph,
        pair_nodes,
        query_count=50,
        seeds_for_pair=lambda pair: [(pair[0], 1.0), (pair[1], 1.0)],
    )
    nodes_before = _sum_before(graph)
    edges_before = _sum_edges(graph)
    avg_nodes_before = _avg([float(item["nodes_fired"]) for item in before])
    avg_context_before = _avg([float(item["context_chars"]) for item in before])

    suggested = suggest_merges(graph)
    paired_suggestions = [pair for pair in pair_nodes if pair in suggested]
    merged_map: dict[tuple[str, str], str] = {}
    for source_id, target_id in paired_suggestions:
        merged_map[(source_id, target_id)] = apply_merge(graph, source_id, target_id)

    def _merged_seeds(pair: tuple[str, str]) -> list[tuple[str, float]]:
        merged_id = merged_map.get(pair)
        if merged_id is not None and graph.get_node(merged_id) is not None:
            return [(merged_id, 1.0)]
        left, right = pair
        if graph.get_node(left) is not None and graph.get_node(right) is not None:
            return [(left, 1.0), (right, 1.0)]
        if graph.get_node(left) is not None:
            return [(left, 1.0)]
        if graph.get_node(right) is not None:
            return [(right, 1.0)]
        return []

    after = _run_queries(
        graph,
        pair_nodes,
        query_count=50,
        seeds_for_pair=_merged_seeds,
    )
    nodes_after = _sum_before(graph)
    edges_after = _sum_edges(graph)
    avg_nodes_after = _avg([float(item["nodes_fired"]) for item in after])
    avg_context_after = _avg([float(item["context_chars"]) for item in after])

    return {
        "simulation": "merge_compression",
        "query_count": 50,
        "pairs": [{"source": source, "target": target} for source, target in pair_nodes],
        "edges_before_merge": edges_before,
        "edges_after_merge": edges_after,
        "nodes_before_merge": nodes_before,
        "nodes_after_merge": nodes_after,
        "avg_nodes_fired_before": avg_nodes_before,
        "avg_nodes_fired_after": avg_nodes_after,
        "avg_context_chars_before": avg_context_before,
        "avg_context_chars_after": avg_context_after,
        "suggested_pairs": paired_suggestions,
        "merges_applied": len(paired_suggestions),
        "query_series": {
            "before_merge": before,
            "after_merge": after,
        },
        "claim": {
            "merge_reduces_nodes_fired": {
                "from": avg_nodes_before,
                "to": avg_nodes_after,
                "met": avg_nodes_after < avg_nodes_before,
            },
            "merge_reduces_context": {
                "from": avg_context_before,
                "to": avg_context_after,
                "met": avg_context_after < avg_context_before,
            },
        },
    }


def main() -> None:
    RESULT_PATH.write_text(json.dumps(_run(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
