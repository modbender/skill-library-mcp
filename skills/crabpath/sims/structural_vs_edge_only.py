"""Sim: compare edge-only updates with structural maintenance strategies."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from crabpath import (
    DecayConfig,
    Edge,
    Graph,
    LearningConfig,
    Node,
    TraversalConfig,
    apply_outcome,
    load_state,
    measure_health,
    prune_edges,
    run_maintenance,
    traverse,
)


RESULT_PATH = Path(__file__).with_name("structural_vs_edge_only_results.json")


def _build_graph() -> tuple[Graph, str]:
    graph = Graph()
    query_seed = "proc_00"
    correct_nodes = [f"proc_{idx:02d}" for idx in range(10)]
    stale_nodes = [f"stale_{idx:02d}" for idx in range(15)]
    duplicate_pairs = [
        (f"ref_dup_{pair_idx:02d}_a", f"ref_dup_{pair_idx:02d}_b")
        for pair_idx in range(5)
    ]
    reference_misc = [f"ref_misc_{idx:02d}" for idx in range(15)]

    for node_id in correct_nodes:
        graph.add_node(
            Node(
                node_id,
                f"procedural step {node_id} for the repeated task.",
                metadata={"file": "procedural.md"},
            )
        )
    for node_id in stale_nodes:
        graph.add_node(
            Node(
                node_id,
                f"stale note {node_id}: outdated guidance to be suppressed.",
                metadata={"file": "stale.md"},
            )
        )
    for pair_index, (left, right) in enumerate(duplicate_pairs):
        graph.add_node(
            Node(
                left,
                f"reference chunk {pair_index}: run prechecks, then compile, then deploy.",
                metadata={"file": "reference.md"},
            )
        )
        graph.add_node(
            Node(
                right,
                f"reference chunk {pair_index}: execute prechecks, then compile, then deploy.",
                metadata={"file": "reference.md"},
            )
        )
        graph.add_edge(Edge(left, right, 0.86))
        graph.add_edge(Edge(right, left, 0.86))
    for node_id in reference_misc:
        graph.add_node(
            Node(
                node_id,
                f"reference note {node_id} for optional lookups.",
                metadata={"file": "reference.md"},
            )
        )

    for idx, proc_node in enumerate(correct_nodes):
        next_node = correct_nodes[(idx + 1) % len(correct_nodes)]
        graph.add_edge(Edge(proc_node, next_node, 0.8))

        dup_left, dup_right = duplicate_pairs[idx % len(duplicate_pairs)]
        graph.add_edge(Edge(proc_node, dup_left, 0.34))
        graph.add_edge(Edge(proc_node, dup_right, 0.31))

        stale_target = stale_nodes[idx % len(stale_nodes)]
        graph.add_edge(Edge(proc_node, stale_target, 0.03))

    for stale_node in stale_nodes:
        graph.add_edge(Edge(stale_node, stale_node, 0.0))

    for left, right in duplicate_pairs:
        graph.add_edge(Edge(left, query_seed, 0.1))
        graph.add_edge(Edge(right, query_seed, 0.1))

    return graph, query_seed


def _run_queries(
    graph: Graph,
    query_seed: str,
    strategy: str,
    query_count: int,
    state_path: Path | None = None,
) -> dict:
    config = TraversalConfig(max_hops=4, beam_width=4, habitual_range=(0.2, 0.8))
    learning = LearningConfig(learning_rate=0.08)
    nodes_fired_series: list[int] = []
    context_chars_series: list[int] = []
    edge_count_series: list[int] = []
    dormant_pct_series: list[float] = []
    learning_curve: list[dict[str, float | int]] = []
    total_cost = 0

    for query_index in range(1, query_count + 1):
        result = traverse(graph, [(query_seed, 1.0)], config=config)
        apply_outcome(graph, result.fired, outcome=1.0, config=learning)

        nodes_fired = len(result.fired)
        context_chars = len(result.context)
        edge_count = graph.edge_count()
        dormant_pct = measure_health(graph).dormant_pct

        nodes_fired_series.append(nodes_fired)
        context_chars_series.append(context_chars)
        edge_count_series.append(edge_count)
        dormant_pct_series.append(dormant_pct)
        total_cost += context_chars

        if query_index in {50, 100, 150, 200}:
            learning_curve.append(
                {
                    "query": query_index,
                    "nodes_fired": nodes_fired,
                    "context_chars": context_chars,
                    "edge_count": edge_count,
                    "dormant_pct": dormant_pct,
                }
            )

        if query_index % 50 == 0 and strategy == "edge_only_plus_prune":
            prune_edges(graph, below=0.05)
        elif query_index % 50 == 0 and strategy == "full_maintain":
            if state_path is None:
                raise RuntimeError("state_path required for full_maintain strategy")
            graph.save(str(state_path))
            run_maintenance(
                state_path=str(state_path),
                tasks=["decay", "prune", "merge"],
                prune_below=0.5,
                decay_config=DecayConfig(half_life=12, min_weight=0.01),
            )
            graph, _index, _meta = load_state(str(state_path))

    return {
        "nodes_fired_series": nodes_fired_series,
        "context_chars_series": context_chars_series,
        "edge_count_series": edge_count_series,
        "dormant_pct_series": dormant_pct_series,
        "learning_curve": learning_curve,
        "total_cost": total_cost,
        "final_nodes_fired": nodes_fired_series[-1] if nodes_fired_series else 0,
        "final_context_chars": context_chars_series[-1] if context_chars_series else 0,
        "edge_count": edge_count_series[-1] if edge_count_series else 0,
        "dormant_pct": dormant_pct_series[-1] if dormant_pct_series else 0.0,
    }


def _run() -> dict:
    strategy_configs = ("edge_only", "edge_only_plus_prune", "full_maintain")
    base_graph, query_seed = _build_graph()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_state:
        state_path = Path(tmp_state.name)

    base_graph.save(str(state_path))

    try:
        results: dict[str, dict] = {}
        for strategy in strategy_configs:
            graph, _index, _meta = load_state(str(state_path))
            outcome = _run_queries(
                graph=graph,
                query_seed=query_seed,
                strategy=strategy,
                query_count=200,
                state_path=state_path,
            )
            results[strategy] = outcome

        comparison_table = [
            {
                "strategy": strategy,
                "final_nodes_fired": payload["final_nodes_fired"],
                "final_context_chars": payload["final_context_chars"],
                "total_cost": payload["total_cost"],
                "dormant_pct": payload["dormant_pct"],
                "edge_count": payload["edge_count"],
            }
            for strategy, payload in results.items()
        ]

        return {
            "simulation": "structural_vs_edge_only",
            "query_count": 200,
            "query_seed": query_seed,
            "strategies": results,
            "learning_curves": {
                strategy: payload["learning_curve"] for strategy, payload in results.items()
            },
            "comparison_table": comparison_table,
            "claim": {
                "full_maintenance_lowest_cost": (
                    results["full_maintain"]["total_cost"]
                    == min(payload["total_cost"] for payload in results.values())
                )
            },
        }
    finally:
        state_path.unlink(missing_ok=True)


def main() -> None:
    RESULT_PATH.write_text(json.dumps(_run(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
