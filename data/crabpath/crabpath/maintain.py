"""Maintenance operations composed from existing fast-path primitives."""

from __future__ import annotations

import copy
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .decay import DecayConfig, apply_decay
from .graph import Graph, Node
from .index import VectorIndex
from .journal import log_event, log_health
from .merge import apply_merge, suggest_merges
from .autotune import measure_health
from .store import load_state, save_state


def _health_payload(graph: Graph) -> dict:
    """Build a dict health snapshot for logging and reports."""
    health = measure_health(graph)
    return health.__dict__ | {"nodes": graph.node_count(), "edges": graph.edge_count()}


def _node_authority(node: Node | None) -> str:
    """Get node authority with safe fallback."""
    if node is None or not isinstance(node.metadata, dict):
        return "overlay"
    authority = node.metadata.get("authority")
    if authority in {"constitutional", "canonical", "overlay"}:
        return authority
    return "overlay"


def _node_ids_with_authority(graph: Graph, authority: str) -> set[str]:
    """Return node IDs with a given authority."""
    return {node.id for node in graph.nodes() if _node_authority(node) == authority}


def prune_edges(graph: Graph, below: float = 0.01) -> int:
    """Delete edges with weight below threshold. Returns count deleted."""
    if below <= 0:
        return 0

    removed = 0
    for source_id, edges in list(graph._edges.items()):
        for target_id, edge in list(edges.items()):
            source_auth = _node_authority(graph.get_node(source_id))
            target_auth = _node_authority(graph.get_node(target_id))
            if source_auth == "constitutional" or target_auth == "constitutional":
                continue
            if (
                ("canonical" in {source_auth, target_auth})
                and abs(edge.weight) > 0.1
            ):
                continue
            if abs(edge.weight) < below:
                graph.remove_edge(source_id, target_id)
                removed += 1
    return removed


def prune_orphan_nodes(graph: Graph) -> int:
    """Delete nodes with no incoming or outgoing edges. Returns count deleted."""
    orphaned: list[str] = []
    for node in graph.nodes():
        if _node_authority(node) in {"constitutional", "canonical"}:
            continue
        if not graph.incoming(node.id) and not graph.outgoing(node.id):
            orphaned.append(node.id)

    for node_id in orphaned:
        graph.remove_node(node_id)
    return len(orphaned)


def _node_vector(graph: Graph, index: VectorIndex, node_id: str, embed_fn: Callable[[str], list[float]] | None) -> list[float] | None:
    """Resolve a node embedding from index or callback."""
    existing = index._vectors.get(node_id)
    if existing is not None:
        return list(existing)
    if embed_fn is None:
        return None
    node = graph.get_node(node_id)
    if node is None:
        return None
    return list(embed_fn(node.content))


def connect_learning_nodes(
    graph: Graph,
    index: VectorIndex,
    top_k: int = 3,
    min_sim: float = 0.3,
    embed_fn: Callable[[str], list[float]] | None = None,
) -> int:
    """Connect learning nodes (``learning::*``) to nearest workspace nodes."""
    if top_k <= 0:
        raise ValueError("top_k must be >= 1")
    if min_sim < 0:
        raise ValueError("min_sim must be >= 0")

    learning_nodes = [node for node in graph.nodes() if node.id.startswith("learning::")]
    workspace_nodes = [node for node in graph.nodes() if not node.id.startswith("learning::")]
    if not learning_nodes or not workspace_nodes:
        return 0

    suggestions: list[tuple[str, str, float, str]] = []

    workspace_vectors: dict[str, list[float]] = {}
    for node in workspace_nodes:
        vector = _node_vector(graph, index, node.id, embed_fn)
        if vector:
            workspace_vectors[node.id] = vector
    if not workspace_vectors:
        raise ValueError("no workspace vectors found for connect task")

    for learning_node in learning_nodes:
        learning_vector = _node_vector(graph, index, learning_node.id, embed_fn)
        if not learning_vector:
            continue

        scored: list[tuple[str, float]] = []
        for workspace_id, workspace_vector in workspace_vectors.items():
            sim = VectorIndex.cosine(learning_vector, workspace_vector)
            scored.append((workspace_id, sim))

        scored.sort(key=lambda item: item[1], reverse=True)
        for workspace_id, sim in scored[:top_k]:
            if sim < min_sim:
                continue

            score = min(0.7, max(0.35, sim))
            suggestions.append((learning_node.id, workspace_id, score, "embedding neighborhood"))
            suggestions.append((workspace_id, learning_node.id, score, "embedding neighborhood"))

    return apply_connections(graph, suggestions)


@dataclass
class MaintenanceReport:
    health_before: dict
    health_after: dict
    tasks_run: list[str]
    decay_applied: bool
    edges_before: int
    edges_after: int
    merges_proposed: int
    merges_applied: int
    pruned_edges: int
    pruned_nodes: int
    notes: list[str]


def run_maintenance(
    state_path: str,
    *,
    tasks: list[str] | None = None,
    embed_fn: Callable[[str], list[float]] | None = None,
    llm_fn: Callable[[str, str], str] | None = None,
    journal_path: str | None = None,
    dry_run: bool = False,
    max_merges: int = 5,
    prune_below: float = 0.01,
    decay_config: DecayConfig | None = None,
) -> MaintenanceReport:
    """Run an optional maintenance sweep over persisted graph state."""
    task_order = ["health", "decay", "prune", "merge", "connect"]
    default_tasks = ["health", "decay", "merge", "prune"]
    requested = (
        list(dict.fromkeys([task.strip() for task in tasks if task.strip()]))
        if tasks is not None
        else default_tasks
    )
    selected = [task for task in task_order if task in requested]
    unknown = [task for task in requested if task not in task_order]
    graph, index, meta = load_state(state_path)

    target_graph = copy.deepcopy(graph)
    target_index = copy.deepcopy(index)

    health_before = _health_payload(graph)
    edges_before = graph.edge_count()
    notes: list[str] = []
    if unknown:
        notes.append(f"Unknown tasks skipped: {', '.join(unknown)}")

    merges_proposed = 0
    merges_applied = 0
    pruned_edges = 0
    pruned_nodes = 0
    decay_applied = False
    tasks_run: list[str] = []

    if "health" in selected:
        tasks_run.append("health")
        log_health(health_before, journal_path=journal_path)

    if "decay" in selected:
        tasks_run.append("decay")
        canonical_nodes = _node_ids_with_authority(target_graph, "canonical")
        constitutional_nodes = _node_ids_with_authority(target_graph, "constitutional")

        def _source_half_life(source_id: str) -> float:
            if source_id in canonical_nodes:
                return 2.0
            return 1.0

        changed = apply_decay(
            target_graph,
            config=decay_config,
            skip_source_ids=constitutional_nodes,
            source_half_life_scale=_source_half_life,
        )
        decay_applied = not dry_run
        log_event(
            {
                "type": "maintenance",
                "task": "decay",
                "edges_decayed": changed,
                "dry_run": dry_run,
            },
            journal_path=journal_path,
        )

    if "prune" in selected:
        tasks_run.append("prune")
        removed_edges = prune_edges(target_graph, below=prune_below)
        removed_nodes = prune_orphan_nodes(target_graph)
        pruned_edges += removed_edges
        pruned_nodes += removed_nodes
        log_event(
            {
                "type": "maintenance",
                "task": "prune",
                "edges_removed": removed_edges,
                "nodes_removed": removed_nodes,
                "dry_run": dry_run,
            },
            journal_path=journal_path,
        )

    if "merge" in selected:
        tasks_run.append("merge")
        suggestions = suggest_merges(target_graph, llm_fn=llm_fn)
        filtered_suggestions: list[tuple[str, str]] = []
        for source_id, target_id in suggestions:
            source_node = target_graph.get_node(source_id)
            target_node = target_graph.get_node(target_id)
            if _node_authority(source_node) == "constitutional" or _node_authority(target_node) == "constitutional":
                continue
            if "canonical" in {_node_authority(source_node), _node_authority(target_node)} and llm_fn is None:
                continue
            filtered_suggestions.append((source_id, target_id))

        merges_proposed = len(filtered_suggestions)
        for source_id, target_id in filtered_suggestions[:max_merges]:
            if target_graph.get_node(source_id) is None or target_graph.get_node(target_id) is None:
                continue
            apply_merge(target_graph, source_id, target_id)
            merges_applied += 1
        log_event(
            {
                "type": "maintenance",
                "task": "merge",
                "suggested": merges_proposed,
                "applied": merges_applied,
                "max_merges": max_merges,
                "dry_run": dry_run,
            },
            journal_path=journal_path,
        )

    if "connect" in selected:
        tasks_run.append("connect")
        learning_nodes = [node for node in target_graph.nodes() if node.id.startswith("learning::")]
        if not learning_nodes:
            notes.append("connect skipped: no learning nodes found")
            log_event(
                {
                    "type": "maintenance",
                    "task": "connect",
                    "connected": 0,
                    "reason": "no learning nodes",
                    "dry_run": dry_run,
                },
                journal_path=journal_path,
            )
        else:
            try:
                added = connect_learning_nodes(target_graph, target_index, embed_fn=embed_fn)
                log_event(
                    {
                        "type": "maintenance",
                        "task": "connect",
                        "connected": added,
                        "dry_run": dry_run,
                    },
                    journal_path=journal_path,
                )
            except ValueError as exc:
                notes.append(f"connect skipped: {exc}")
                added = 0

    if dry_run:
        notes.append("dry_run=True; no state write performed")
    elif any(task in selected for task in ("decay", "prune", "merge", "connect")):
        save_state(graph=target_graph, index=target_index, path=str(Path(state_path)), meta=meta)

    health_after = _health_payload(target_graph)
    log_health(health_after, journal_path=journal_path)

    return MaintenanceReport(
        health_before=health_before,
        health_after=health_after,
        tasks_run=tasks_run,
        decay_applied=decay_applied,
        edges_before=edges_before,
        edges_after=target_graph.edge_count(),
        merges_proposed=merges_proposed,
        merges_applied=merges_applied,
        pruned_edges=pruned_edges,
        pruned_nodes=pruned_nodes,
        notes=notes,
    )
