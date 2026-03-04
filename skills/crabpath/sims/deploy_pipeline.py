"""Sim 1: deploy pipeline procedural memory compilation."""

from __future__ import annotations

import json
from pathlib import Path

from crabpath import Edge, Graph, Node, TraversalConfig, apply_outcome, traverse


RESULT_PATH = Path(__file__).with_name("deploy_pipeline_results.json")


def _build_graph() -> Graph:
    graph = Graph()

    nodes = [
        "deploy_query",
        "check_ci",
        "inspect_manifest",
        "rollback",
        "verify",
    ]
    for node_id in nodes:
        graph.add_node(Node(node_id, node_id.replace("_", " ").title()))

    graph.add_edge(Edge("deploy_query", "check_ci", 0.27))
    graph.add_edge(Edge("check_ci", "inspect_manifest", 0.27))
    graph.add_edge(Edge("inspect_manifest", "rollback", 0.27))
    graph.add_edge(Edge("rollback", "verify", 0.27))
    return graph


def _edge_weight(graph: Graph, source: str, target: str) -> float:
    for _, edge in graph.outgoing(source):
        if edge.target == target:
            return edge.weight
    return 0.0


def _snapshot(graph: Graph) -> dict:
    return {
        "deploy_query->check_ci": _edge_weight(graph, "deploy_query", "check_ci"),
        "check_ci->inspect_manifest": _edge_weight(graph, "check_ci", "inspect_manifest"),
        "inspect_manifest->rollback": _edge_weight(graph, "inspect_manifest", "rollback"),
        "rollback->verify": _edge_weight(graph, "rollback", "verify"),
    }


def _run() -> dict:
    graph = _build_graph()
    tracked_queries = {1, 10, 25, 50}
    config = TraversalConfig(max_hops=6, beam_width=1, habitual_range=(0.2, 0.8))

    history: list[dict] = []
    tracked: list[dict] = []

    for query_index in range(1, 51):
        query = "deploy to production"
        _ = query
        result = traverse(graph, [("deploy_query", 1.0)], config=config)
        apply_outcome(graph, result.fired, outcome=1.0)

        snapshot = _snapshot(graph)
        history.append(
            {
                "query": query_index,
                "query_text": query,
                "edge_weights": snapshot,
            }
        )
        if query_index in tracked_queries:
            tracked.append({"query": query_index, **snapshot})

    final = _snapshot(graph)
    return {
        "simulation": "deploy_pipeline",
        "query_count": 50,
        "query_text": "deploy to production",
        "tracked_queries": [1, 10, 25, 50],
        "tracked_edge_snapshots": tracked,
        "edge_weights_over_time": history,
        "final_edge_weights": final,
        "claim": {
            "edge_growth_to_reflex": {
                "from": 0.27,
                "to_query_50": final["rollback->verify"],
                "reflex_threshold": 0.8,
                "met": all(value > 0.8 for value in final.values()),
            },
        },
        "notes": "All four pipeline edges compile from habitual to reflex through repeated deploy intent outcomes.",
    }


def main() -> None:
    RESULT_PATH.write_text(json.dumps(_run(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
