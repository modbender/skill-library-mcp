"""Sim 7: brain-death recovery via health + autotune diagnostics."""

from __future__ import annotations

import json
from pathlib import Path

from crabpath import (
    Edge,
    Graph,
    Node,
    TraversalConfig,
    apply_decay,
    apply_outcome,
    autotune,
    measure_health,
    traverse,
)


RESULT_PATH = Path(__file__).with_name("brain_death_results.json")


def _build_graph() -> Graph:
    graph = Graph()
    for idx in range(16):
        graph.add_node(Node(f"n{idx:02d}", f"node {idx:02d}"))

    node_ids = [f"n{idx:02d}" for idx in range(16)]
    for source in node_ids:
        for target in node_ids:
            if source == target:
                continue
            graph.add_edge(Edge(source, target, 0.72))
    return graph


def _zero_weights(graph: Graph) -> None:
    for source in [node.id for node in graph.nodes()]:
        for _, edge in graph.outgoing(source):
            graph.add_edge(Edge(edge.source, edge.target, 0.01, kind=edge.kind))


def _run() -> dict:
    graph = _build_graph()
    _zero_weights(graph)

    rounds = []
    for round_idx in range(1, 31):
        pre_health = measure_health(graph)
        suggestions = autotune(graph, pre_health)

        config = TraversalConfig(
            max_hops=2,
            beam_width=3,
            reflex_threshold=0.001,
            habitual_range=(0.0, 1.0),
            edge_damping=0.6,
        )
        result = traverse(graph, [("n00", 1.0)], config=config)
        apply_outcome(graph, result.fired, outcome=1.0)
        apply_decay(graph, config=None)

        post_health = measure_health(graph)
        rounds.append(
            {
                "round": round_idx,
                "pre_health": pre_health.__dict__,
                "post_health": post_health.__dict__,
                "suggestions": suggestions,
                "fired_nodes": result.fired,
            }
        )

    final_health = rounds[-1]["post_health"]
    return {
        "simulation": "brain_death_recovery",
        "round_count": 30,
        "rounds": rounds,
        "recovery_signals": sorted(
            {suggestion["knob"] for item in rounds for suggestion in item["suggestions"]}
        ),
        "final_health": final_health,
        "claim": {
            "met": (
                rounds[0]["pre_health"]["dormant_pct"] > 0.9
                and any(item["suggestions"] for item in rounds)
                and final_health["reflex_pct"] > rounds[0]["post_health"]["reflex_pct"]
            ),
            "autotune_detected_failure": rounds[0]["pre_health"]["dormant_pct"] > 0.9,
            "suggests_recovery": any(item["suggestions"] for item in rounds),
            "health_moved_toward_reflexive": final_health["reflex_pct"] > rounds[0]["pre_health"]["reflex_pct"],
        },
    }


def main() -> None:
    RESULT_PATH.write_text(json.dumps(_run(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
