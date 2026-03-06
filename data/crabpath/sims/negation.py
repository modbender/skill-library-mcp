"""Sim 2: inhibitory edges suppress wrong paths."""

from __future__ import annotations

import json
from pathlib import Path

from crabpath import Edge, Graph, LearningConfig, Node, TraversalConfig, apply_outcome, traverse


RESULT_PATH = Path(__file__).with_name("negation_results.json")


def _build_graph() -> Graph:
    graph = Graph()

    run_source = "run_tests_query"
    skip_source = "skip_tests_query"
    run_target = "run_tests_before_deploy"
    skip_target = "skip_tests_for_hotfix"

    for node_id in [run_source, skip_source, run_target, skip_target]:
        graph.add_node(Node(node_id, node_id.replace("_", " ").title()))

    graph.add_edge(Edge(run_source, run_target, 0.45))
    graph.add_edge(Edge(skip_source, skip_target, 0.45))
    return graph


def _edge_weight(graph: Graph, source: str, target: str) -> float:
    for _, edge in graph.outgoing(source):
        if edge.target == target:
            return edge.weight
    return 0.0


def _run() -> dict:
    graph = _build_graph()
    config = TraversalConfig(
        max_hops=3,
        beam_width=1,
        habitual_range=(-1.0, 0.8),
    )
    learning_config = LearningConfig(learning_rate=1.0)
    history: list[dict] = []

    for query_index in range(1, 21):
        if query_index <= 10:
            source = "run_tests_query"
            target = "run_tests_before_deploy"
            outcome = 1.0
            query = "run tests before deploy"
        else:
            source = "skip_tests_query"
            target = "skip_tests_for_hotfix"
            outcome = -1.0
            query = "skip tests for hotfix"

        result = traverse(graph, [(source, 1.0)], config=config)
        if len(result.fired) >= 2:
            apply_outcome(
                graph,
                result.fired,
                outcome=outcome,
                config=learning_config,
            )
        else:
            # Keep pressure on the intended inhibitory edge even after it becomes dormant.
            apply_outcome(
                graph,
                [source, target],
                outcome=outcome,
                config=learning_config,
            )

        history.append(
            {
                "query": query_index,
                "query_text": query,
                "good_weight": _edge_weight(graph, "run_tests_query", "run_tests_before_deploy"),
                "bad_weight": _edge_weight(graph, "skip_tests_query", "skip_tests_for_hotfix"),
            }
        )

    final_good = history[-1]["good_weight"]
    final_bad = history[-1]["bad_weight"]

    return {
        "simulation": "negation",
        "query_count": 20,
        "query_plan": {
            "first_10": "run tests (+1 outcome)",
            "last_10": "skip tests (-1 outcome)",
        },
        "weight_history": history,
        "final_weights": {
            "run_tests_before_deploy": final_good,
            "skip_tests_for_hotfix": final_bad,
        },
        "claim": {
            "bad_edge_inhibitory": {
                "threshold": 0.0,
                "value": final_bad,
                "met": final_bad < 0.0,
            },
            "good_edge_strengthened": final_good > 0.75,
        },
    }


def main() -> None:
    RESULT_PATH.write_text(json.dumps(_run(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
