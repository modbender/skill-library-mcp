"""Sim 6: cross-file separation and sparse bridge emergence."""

from __future__ import annotations

import json
from pathlib import Path

from crabpath import Edge, Graph, Node, TraversalConfig, apply_outcome, traverse


RESULT_PATH = Path(__file__).with_name("domain_separation_results.json")


def _build_graph() -> Graph:
    graph = Graph()
    files = ["alpha", "beta", "gamma"]
    for file_idx, file_name in enumerate(files):
        for chunk in range(5):
            node_id = f"{file_name}::{chunk}"
            graph.add_node(
                Node(
                    node_id,
                    f"{file_name} chunk {chunk}",
                    metadata={"file": file_name, "chunk": chunk},
                )
            )

    for file_name in files:
        nodes = [node.id for node in graph.nodes() if node.metadata["file"] == file_name]
        for source in nodes:
            for target in nodes:
                if source == target:
                    continue
                graph.add_edge(Edge(source, target, 0.5))
    return graph


def _graph_files(graph: Graph) -> dict[str, str]:
    return {node.id: node.metadata.get("file", "unknown") for node in graph.nodes()}


def _cross_file_edges(graph: Graph) -> list[tuple[str, str, float]]:
    file_map = _graph_files(graph)
    out: list[tuple[str, str, float]] = []
    for source in file_map:
        for _, edge in graph.outgoing(source):
            target_file = file_map.get(edge.target)
            if target_file is None or target_file == file_map[source]:
                continue
            out.append((source, edge.target, edge.weight))
    out.sort(key=lambda item: (item[0], item[1]))
    return out


def _connected_components(graph: Graph) -> list[list[str]]:
    file_map = _graph_files(graph)
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in file_map}
    for source in file_map:
        for _, edge in graph.outgoing(source):
            adjacency[source].add(edge.target)
            adjacency[edge.target].add(source)

    seen = set()
    components: list[list[str]] = []
    for node_id in file_map:
        if node_id in seen:
            continue
        stack = [node_id]
        seen.add(node_id)
        component: list[str] = []
        while stack:
            current = stack.pop()
            component.append(current)
            for nxt in adjacency[current]:
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        components.append(sorted(component))
    return sorted((sorted(c) for c in components), key=len, reverse=True)


def _run() -> dict:
    graph = _build_graph()

    mixed_steps = {8, 18, 28, 38, 48}
    records: list[dict] = []
    config = TraversalConfig(max_hops=1, beam_width=2)

    for step in range(1, 51):
        if step in mixed_steps:
            seeds = [("alpha::0", 1.0), ("beta::1", 0.95), ("gamma::2", 0.9)]
        else:
            bucket = step % 3
            if bucket == 1:
                seeds = [("alpha::0", 1.0), ("alpha::1", 0.96), ("alpha::2", 0.93)]
            elif bucket == 2:
                seeds = [("beta::0", 1.0), ("beta::1", 0.96), ("beta::2", 0.93)]
            else:
                seeds = [("gamma::0", 1.0), ("gamma::1", 0.96), ("gamma::2", 0.93)]

        result = traverse(graph, seeds, config=config)
        apply_outcome(graph, result.fired, outcome=1.0)

        records.append(
            {
                "query": step,
                "mixed": step in mixed_steps,
                "cross_file_edges": len(_cross_file_edges(graph)),
                "seeds": [seed for seed, _ in seeds],
            }
        )

    final_cross = _cross_file_edges(graph)
    components = _connected_components(graph)
    file_map = _graph_files(graph)
    nodes = [{"id": node_id, "file": file_name} for node_id, file_name in file_map.items()]

    return {
        "simulation": "domain_separation",
        "query_count": 50,
        "mixed_queries": sorted(mixed_steps),
        "progress": records,
        "final_cross_file_edge_count": len(final_cross),
        "final_cross_file_edges": final_cross,
        "cluster_count": len(components),
        "cluster_sizes": [len(component) for component in components],
        "nodes": nodes,
        "claim": {
            "cross_file_edges_formed": len(final_cross),
            "cross_file_edges_in_range": 2 <= len(final_cross) <= 8,
            "cross_density_low": len(final_cross) <= len(graph.outgoing("alpha::0")) * 2,
            "met": 2 <= len(final_cross) <= 8 and len(final_cross) <= len(graph.outgoing("alpha::0")) * 2,
        },
    }


def main() -> None:
    RESULT_PATH.write_text(json.dumps(_run(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
