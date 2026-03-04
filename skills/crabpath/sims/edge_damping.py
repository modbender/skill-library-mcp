"""Sim 5: edge damping prevents loop lock-in."""

from __future__ import annotations

import json
from pathlib import Path

from crabpath import Edge, Graph, Node, TraversalConfig, traverse


RESULT_PATH = Path(__file__).with_name("edge_damping_results.json")


def _build_graph() -> Graph:
    graph = Graph()
    for node_id in ["A", "B", "C", "D"]:
        graph.add_node(Node(node_id, node_id))

    graph.add_edge(Edge("A", "B", 0.9))
    graph.add_edge(Edge("B", "C", 0.9))
    graph.add_edge(Edge("C", "A", 0.9))
    graph.add_edge(Edge("A", "D", 0.5))
    return graph


def _simulate(damping: float) -> dict:
    graph = _build_graph()
    config = TraversalConfig(max_hops=12, beam_width=1, edge_damping=damping)
    result = traverse(graph, [("A", 1.0)], config=config)
    return {
        "damping": damping,
        "nodes_fired": result.fired,
        "steps": [
            {
                "from_node": step.from_node,
                "to_node": step.to_node,
                "tier": step.tier,
                "edge_weight": step.edge_weight,
                "effective_weight": step.effective_weight,
            }
            for step in result.steps
        ],
        "reached_D": "D" in result.fired,
        "d_discovered_at_step": next(
            (
                idx + 1
                for idx, step in enumerate(result.steps)
                if step.to_node == "D"
            ),
            None,
        ),
    }


def _run() -> dict:
    damped = _simulate(0.3)
    undamped = _simulate(1.0)

    return {
        "simulation": "edge_damping",
        "damped": damped,
        "undamped": undamped,
        "claim": {
            "damped_discovers_D": damped["reached_D"],
            "undamped_loops_without_D": not undamped["reached_D"],
            "met": damped["reached_D"] and not undamped["reached_D"],
        },
    }


def main() -> None:
    RESULT_PATH.write_text(json.dumps(_run(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
