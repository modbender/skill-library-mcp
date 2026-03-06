"""Sim: traversal performance over increasing graph sizes."""

from __future__ import annotations

import json
import random
from pathlib import Path
from time import perf_counter

from crabpath import Edge, Graph, Node, TraversalConfig, traverse


RESULT_PATH = Path(__file__).with_name("scaling_analysis_results.json")


def _build_graph(node_count: int) -> tuple[Graph, list[str]]:
    if node_count < 5:
        raise ValueError("node_count must be at least 5")

    rng = random.Random(42)
    nodes = [f"n{idx:04d}" for idx in range(node_count)]
    correct_path = nodes[:5]
    graph = Graph()

    for node_id in nodes:
        graph.add_node(Node(node_id, node_id))

    for source in nodes:
        targets: list[str] = []
        if source in correct_path[:-1]:
            next_index = correct_path.index(source) + 1
            targets.append(correct_path[next_index])
        elif source == correct_path[-1]:
            targets.append(correct_path[0])

        while len(targets) < 8:
            candidate = rng.choice(nodes)
            if candidate == source or candidate in targets:
                continue
            targets.append(candidate)

        for target in targets:
            graph.add_edge(Edge(source, target, 0.4))

    return graph, correct_path


def _run() -> dict:
    sizes = [50, 100, 250, 500, 1000, 2000]
    query_config = TraversalConfig(max_hops=4, beam_width=1, habitual_range=(0.2, 0.8))

    rows = []
    for size in sizes:
        random.seed(42)
        graph, correct_path = _build_graph(size)
        _ = correct_path

        elapsed_ms = 0.0
        nodes_fired: list[int] = []
        for _ in range(50):
            start = perf_counter()
            result = traverse(graph, [(nodes := graph.nodes()[0].id, 1.0)], config=query_config)
            elapsed_ms += (perf_counter() - start) * 1000.0
            nodes_fired.append(len(result.fired))

        avg_ms = elapsed_ms / 50.0
        avg_fired = sum(nodes_fired) / len(nodes_fired)
        rows.append(
            {
                "graph_size": size,
                "avg_traversal_ms": avg_ms,
                "avg_nodes_fired": avg_fired,
                "nodes_fired_min": min(nodes_fired),
                "nodes_fired_max": max(nodes_fired),
            }
        )

    ratios = []
    for idx in range(1, len(rows)):
        previous = rows[idx - 1]
        current = rows[idx]
        size_ratio = current["graph_size"] / previous["graph_size"]
        ms_ratio = current["avg_traversal_ms"] / previous["avg_traversal_ms"] if previous["avg_traversal_ms"] > 0 else 0.0
        ratios.append({"from": previous["graph_size"], "to": current["graph_size"], "size_ratio": size_ratio, "time_ratio": ms_ratio})

    return {
        "simulation": "scaling_analysis",
        "query_count": 50,
        "graph_sizes": sizes,
        "average_nodes_fired_by_size": rows,
        "query_config": {
            "max_hops": query_config.max_hops,
            "beam_width": query_config.beam_width,
        },
        "scale_vs_size": ratios,
        "summary": {
            "is_sublinear_time_growth": all(row["time_ratio"] <= row["size_ratio"] for row in ratios),
            "final_size": sizes[-1],
        },
    }


def main() -> None:
    RESULT_PATH.write_text(json.dumps(_run(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
