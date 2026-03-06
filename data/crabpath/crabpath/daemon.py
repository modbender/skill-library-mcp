"""Persistent long-running NDJSON worker for CrabPath."""

from __future__ import annotations

import argparse
import copy
import json
import os
import signal
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .autotune import measure_health
from .decay import DecayConfig, apply_decay
from .graph import Graph, Node
from .hasher import HashEmbedder
from .index import VectorIndex
from .journal import log_health, log_learn, log_query
from .learn import apply_outcome
from .maintain import connect_learning_nodes, prune_edges, prune_orphan_nodes
from .merge import apply_merge, suggest_merges
from .store import load_state, save_state
from .traverse import TraversalConfig, traverse


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="crabpathd")
    parser.add_argument("--state", required=True)
    parser.add_argument("--embed-model", default="text-embedding-3-small")
    parser.add_argument("--auto-save-interval", type=int, default=10)
    return parser


def _make_embed_fn(embed_model: str) -> Callable[[str], list[float]] | None:
    """Create embedding callback when OPENAI_API_KEY is present."""
    if not os.getenv("OPENAI_API_KEY"):
        return None

    from openai import OpenAI

    client = OpenAI()
    return lambda text: [float(v) for v in client.embeddings.create(model=embed_model, input=[text]).data[0].embedding]


def _journal_path(state_path: str) -> str:
    """Resolve journal.jsonl path for the loaded state directory."""
    return str(Path(state_path).expanduser().parent / "journal.jsonl")


def _ms(start: float, end: float) -> float:
    """Convert elapsed duration in seconds to milliseconds."""
    return round((end - start) * 1000.0, 3)


def _node_authority(node: Node | None) -> str:
    """Extract node authority with safe fallback."""
    if node is None or not isinstance(node.metadata, dict):
        return "overlay"
    authority = node.metadata.get("authority")
    if authority in {"constitutional", "canonical", "overlay"}:
        return authority
    return "overlay"


def _node_ids_with_authority(graph: Graph, authority: str) -> set[str]:
    """Collect node ids for a given authority label."""
    return {node.id for node in graph.nodes() if _node_authority(node) == authority}


def _health_payload(graph: Graph) -> dict[str, object]:
    """Build health payload with node/edge counts included."""
    health = measure_health(graph)
    return health.__dict__ | {"nodes": graph.node_count(), "edges": graph.edge_count()}


def _emit_response(req_id: object, payload: object, error: dict[str, object] | None = None) -> None:
    """Emit one NDJSON object."""
    if error is None:
        print(json.dumps({"id": req_id, "result": payload}), flush=True)
    else:
        print(json.dumps({"id": req_id, "error": error}), flush=True)


def _parse_int(value: object, label: str, default: int | None = None, min_value: int = 1) -> int:
    """Validate integer input."""
    if value is None:
        if default is None:
            raise ValueError(f"{label} is required")
        return default
    if not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    if value < min_value:
        raise ValueError(f"{label} must be >= {min_value}")
    return value


def _parse_float(value: object, label: str, required: bool = False, default: float | None = None) -> float:
    """Validate float input."""
    if value is None:
        if not required:
            if default is None:
                raise ValueError(f"{label} is required")
            return default
        raise ValueError(f"{label} is required")
    if not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a number")
    return float(value)


def _parse_str_list(value: object, label: str, required: bool = True) -> list[str]:
    """Parse a JSON list of non-empty strings."""
    if value is None:
        if required:
            raise ValueError(f"{label} is required")
        return []
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    entries: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{label} must only contain non-empty strings")
        entries.append(item)
    if not entries and required:
        raise ValueError(f"{label} must not be empty")
    return entries


def _handle_query(
    graph: Graph,
    index: VectorIndex,
    meta: dict[str, object],
    embed_fn: Callable[[str], list[float]] | None,
    params: dict[str, object],
    state_path: str,
) -> dict[str, object]:
    """Handle query requests with embed + traversal timings."""
    query_text = params.get("query")
    if not isinstance(query_text, str) or not query_text.strip():
        raise ValueError("query must be a non-empty string")

    top_k = _parse_int(params.get("top_k"), "top_k", default=4)

    total_start = time.perf_counter()
    resolved_embed = embed_fn or HashEmbedder().embed

    embed_start = time.perf_counter()
    query_vector = resolved_embed(query_text)
    embed_stop = time.perf_counter()

    expected_dim = meta.get("embedder_dim")
    if isinstance(expected_dim, int) and len(query_vector) != expected_dim:
        raise ValueError(
            f"query embedding dimension mismatch: expected {expected_dim}, got {len(query_vector)}"
        )

    traverse_start = time.perf_counter()
    seeds = index.search(query_vector, top_k=top_k)
    result = traverse(
        graph=graph,
        seeds=seeds,
        config=TraversalConfig(max_hops=15, max_context_chars=20000),
        query_text=query_text,
    )
    traverse_stop = time.perf_counter()
    total_stop = time.perf_counter()

    log_query(
        query_text=query_text,
        fired_ids=result.fired,
        node_count=graph.node_count(),
        journal_path=_journal_path(state_path),
        metadata={"chat_id": params.get("chat_id")},
    )

    return {
        "fired_nodes": result.fired,
        "context": result.context,
        "seeds": [[node_id, score] for node_id, score in seeds],
        "embed_query_ms": _ms(embed_start, embed_stop),
        "traverse_ms": _ms(traverse_start, traverse_stop),
        "total_ms": _ms(total_start, total_stop),
    }


def _handle_learn(graph: Graph, params: dict[str, object], state_path: str) -> dict[str, int]:
    """Handle learning updates."""
    fired_nodes = _parse_str_list(params.get("fired_nodes"), "fired_nodes")
    outcome = _parse_float(params.get("outcome"), "outcome", required=True)

    updates = apply_outcome(graph=graph, fired_nodes=fired_nodes, outcome=outcome)
    log_learn(
        fired_ids=fired_nodes,
        outcome=outcome,
        journal_path=_journal_path(state_path),
    )

    return {"edges_updated": len(updates)}


def _handle_maintain(
    graph: Graph,
    index: VectorIndex,
    params: dict[str, object],
    embed_fn: Callable[[str], list[float]] | None,
    state_path: str,
) -> tuple[dict[str, object], bool]:
    """Handle maintenance request directly against in-memory graph/index."""
    task_order = ["health", "decay", "prune", "merge", "connect"]
    default_tasks = ["health", "decay", "merge", "prune"]
    raw_tasks = params.get("tasks")

    if raw_tasks is None:
        requested = default_tasks
    elif isinstance(raw_tasks, str):
        requested = [task.strip() for task in raw_tasks.split(",") if task.strip()]
    elif isinstance(raw_tasks, list):
        requested = [task for task in raw_tasks if isinstance(task, str)]
    else:
        raise ValueError("tasks must be a list or comma-separated string")

    requested_clean = [task.strip() for task in requested if task.strip()]
    selected = [task for task in task_order if task in requested_clean]
    unknown = [task for task in requested_clean if task not in task_order]

    dry_run = params.get("dry_run", False)
    if not isinstance(dry_run, bool):
        raise ValueError("dry_run must be a boolean")

    max_merges = _parse_int(params.get("max_merges"), "max_merges", default=5)
    prune_below = _parse_float(params.get("prune_below"), "prune_below", required=False, default=0.01)

    work_graph = copy.deepcopy(graph) if dry_run else graph
    work_index = copy.deepcopy(index) if dry_run else index

    health_before = _health_payload(graph)
    edges_before = graph.edge_count()
    notes: list[str] = []
    merges_proposed = 0
    merges_applied = 0
    pruned_edges = 0
    pruned_nodes = 0
    decay_applied = False

    if unknown:
        notes.append(f"Unknown tasks skipped: {', '.join(unknown)}")

    if "health" in selected:
        log_health(health_before, journal_path=_journal_path(state_path))

    if "decay" in selected:
        canonical_nodes = _node_ids_with_authority(work_graph, "canonical")
        constitutional_nodes = _node_ids_with_authority(work_graph, "constitutional")

        def source_half_life(source_id: str) -> float:
            if source_id in canonical_nodes:
                return 2.0
            return 1.0

        apply_decay(
            work_graph,
            config=DecayConfig(),
            skip_source_ids=constitutional_nodes,
            source_half_life_scale=source_half_life,
        )
        decay_applied = not dry_run

    if "prune" in selected:
        pruned_edges = prune_edges(work_graph, below=prune_below)
        pruned_nodes = prune_orphan_nodes(work_graph)

    if "merge" in selected:
        suggestions = suggest_merges(work_graph)
        filtered: list[tuple[str, str]] = []
        for source_id, target_id in suggestions:
            source_node = work_graph.get_node(source_id)
            target_node = work_graph.get_node(target_id)
            if _node_authority(source_node) == "constitutional" or _node_authority(target_node) == "constitutional":
                continue
            filtered.append((source_id, target_id))

        merges_proposed = len(filtered)
        for source_id, target_id in filtered[:max_merges]:
            if work_graph.get_node(source_id) is None or work_graph.get_node(target_id) is None:
                continue
            if dry_run:
                merges_applied += 1
                continue
            apply_merge(work_graph, source_id, target_id)
            merges_applied += 1

    if "connect" in selected:
        learning_nodes = [node for node in work_graph.nodes() if node.id.startswith("learning::")]
        if not learning_nodes:
            notes.append("connect skipped: no learning nodes found")
        else:
            try:
                connect_learning_nodes(work_graph, work_index, embed_fn=embed_fn)
            except ValueError as exc:
                notes.append(f"connect skipped: {exc}")

    if dry_run:
        health_after = _health_payload(work_graph)
        return (
            {
                "health_before": health_before,
                "health_after": health_after,
                "merges_applied": merges_applied,
                "merges_proposed": merges_proposed,
                "decay_applied": decay_applied,
                "pruned_edges": pruned_edges,
                "pruned_nodes": pruned_nodes,
                "tasks_run": selected,
                "notes": notes + ["dry_run=True; no state write performed"],
                "edges_before": edges_before,
                "edges_after": work_graph.edge_count(),
            },
            False,
        )

    health_after = _health_payload(work_graph)
    log_health(health_after, journal_path=_journal_path(state_path))

    return (
        {
            "health_before": health_before,
            "health_after": health_after,
            "merges_applied": merges_applied,
            "merges_proposed": merges_proposed,
            "decay_applied": decay_applied,
            "pruned_edges": pruned_edges,
            "pruned_nodes": pruned_nodes,
            "tasks_run": selected,
            "notes": notes,
            "edges_before": edges_before,
            "edges_after": work_graph.edge_count(),
        },
        bool(selected) and not dry_run and any(task in selected for task in ("decay", "prune", "merge", "connect")),
    )


def _handle_health(graph: Graph) -> dict[str, object]:
    """Handle health request."""
    return _health_payload(graph)


def _handle_info(graph: Graph, meta: dict[str, object]) -> dict[str, object]:
    """Handle info request."""
    return {
        "nodes": graph.node_count(),
        "edges": graph.edge_count(),
        "embedder": str(meta.get("embedder_name", "hash-v1")),
    }


def _load_new_state(state_path: str) -> tuple[Graph, VectorIndex, dict[str, object]]:
    """Reload state.json from disk."""
    graph, index, meta = load_state(state_path)
    return graph, index, dict(meta)


@dataclass
class _DaemonState:
    graph: Graph
    index: VectorIndex
    meta: dict[str, object]
    write_count: int = 0


def main(argv: list[str] | None = None) -> int:
    """Run NDJSON worker loop."""
    args = _build_parser().parse_args(argv)
    state_path = str(Path(args.state).expanduser())

    graph, index, meta = load_state(state_path)
    daemon_state = _DaemonState(graph=graph, index=index, meta=meta)
    embed_fn = _make_embed_fn(args.embed_model)
    auto_save_interval = max(1, args.auto_save_interval) if args.auto_save_interval > 0 else 0

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    stop_requested = False

    def _on_signal(_sig: int, _frame: object | None) -> None:
        nonlocal stop_requested
        stop_requested = True

    prev_handlers = {
        signal.SIGINT: signal.getsignal(signal.SIGINT),
        signal.SIGTERM: signal.getsignal(signal.SIGTERM),
    }
    signal.signal(signal.SIGINT, _on_signal)
    signal.signal(signal.SIGTERM, _on_signal)

    try:
        for raw_line in sys.stdin:
            if stop_requested:
                break

            line = raw_line.strip()
            if not line:
                continue

            req_id: object = None
            should_write = False
            try:
                request = json.loads(line)
                if not isinstance(request, dict):
                    raise ValueError("request must be a JSON object")
                req_id = request.get("id")
                method = request.get("method")
                params = request.get("params", {})
                if not isinstance(params, dict):
                    raise ValueError("params must be a JSON object")
                if not isinstance(method, str):
                    raise ValueError("method must be a string")

                if method == "query":
                    payload = _handle_query(
                        graph=daemon_state.graph,
                        index=daemon_state.index,
                        meta=daemon_state.meta,
                        embed_fn=embed_fn,
                        params=params,
                        state_path=state_path,
                    )
                elif method == "learn":
                    payload = _handle_learn(daemon_state.graph, params, state_path)
                    should_write = True
                elif method == "maintain":
                    payload, should_write = _handle_maintain(
                        daemon_state.graph,
                        daemon_state.index,
                        params,
                        embed_fn,
                        state_path,
                    )
                elif method == "health":
                    payload = _handle_health(daemon_state.graph)
                elif method == "info":
                    payload = _handle_info(daemon_state.graph, daemon_state.meta)
                elif method == "save":
                    save_state(
                        graph=daemon_state.graph,
                        index=daemon_state.index,
                        path=state_path,
                        meta=daemon_state.meta,
                    )
                    daemon_state.write_count = 0
                    payload = {"saved": True}
                elif method == "reload":
                    daemon_state.graph, daemon_state.index, daemon_state.meta = _load_new_state(state_path)
                    daemon_state.write_count = 0
                    payload = {"reloaded": True}
                elif method == "shutdown":
                    if daemon_state.write_count > 0:
                        save_state(
                            graph=daemon_state.graph,
                            index=daemon_state.index,
                            path=state_path,
                            meta=daemon_state.meta,
                        )
                    _emit_response(req_id, {"shutdown": True})
                    break
                else:
                    _emit_response(req_id, None, {"code": -32601, "message": f"unknown method: {method}"})
                    continue

                if should_write:
                    daemon_state.write_count += 1
                    if auto_save_interval and daemon_state.write_count % auto_save_interval == 0:
                        save_state(
                            graph=daemon_state.graph,
                            index=daemon_state.index,
                            path=state_path,
                            meta=daemon_state.meta,
                        )

                _emit_response(req_id, payload)
            except Exception as exc:  # noqa: BLE001
                _emit_response(req_id, None, {"code": -1, "message": str(exc)})

    except KeyboardInterrupt:
        pass
    finally:
        if stop_requested and daemon_state.write_count > 0:
            save_state(
                graph=daemon_state.graph,
                index=daemon_state.index,
                path=state_path,
                meta=daemon_state.meta,
            )
        signal.signal(signal.SIGINT, prev_handlers[signal.SIGINT])
        signal.signal(signal.SIGTERM, prev_handlers[signal.SIGTERM])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
