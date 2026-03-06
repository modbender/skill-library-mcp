"""Pure graph-operations CLI for CrabPath."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import shutil
from collections.abc import Callable, Iterable
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

from .connect import apply_connections, suggest_connections
from .autotune import measure_health
from .graph import Edge, Graph, Node
from .index import VectorIndex
from .inject import inject_correction, inject_node
from .compact import compact_daily_notes
from .journal import (
    log_health,
    log_learn,
    log_query,
    log_replay,
    journal_stats,
    read_journal,
)
from .learn import apply_outcome
from .merge import apply_merge, suggest_merges
from .replay import (
    extract_interactions,
    extract_query_records,
    extract_query_records_from_dir,
    extract_queries,
    extract_queries_from_dir,
    replay_queries,
)
from .split import split_workspace
from .hasher import HashEmbedder
from .traverse import TraversalConfig, TraversalResult, traverse
from .sync import DEFAULT_AUTHORITY_MAP, sync_workspace
from ._util import _tokenize
from .maintain import run_maintenance
from .store import load_state, save_state
from . import __version__


def _build_parser() -> argparse.ArgumentParser:
    """ build parser."""
    parser = argparse.ArgumentParser(prog="crabpath")
    sub = parser.add_subparsers(dest="command", required=True)

    i = sub.add_parser("init")
    i.add_argument("--workspace", required=True)
    i.add_argument("--output", required=True)
    i.add_argument("--sessions")
    i.add_argument("--embedder", choices=["hash", "openai"], default=None)
    i.add_argument("--llm", choices=["none", "openai"], default="none")
    i.add_argument("--json", action="store_true")

    q = sub.add_parser("query")
    q.add_argument("text")
    q.add_argument("--state")
    q.add_argument("--graph")
    q.add_argument("--index")
    q.add_argument("--top", type=int, default=10)
    q.add_argument("--query-vector-stdin", action="store_true")
    q.add_argument("--embedder", choices=["hash", "openai"], default=None)
    q.add_argument("--max-context-chars", type=int, default=None)
    q.add_argument("--json", action="store_true")

    l = sub.add_parser("learn")
    l.add_argument("--state")
    l.add_argument("--graph")
    l.add_argument("--outcome", type=float, required=True)
    l.add_argument("--fired-ids", required=True)
    l.add_argument("--json", action="store_true")

    m = sub.add_parser("merge")
    m.add_argument("--state")
    m.add_argument("--graph")
    m.add_argument("--llm", choices=["none", "openai"], default="none")
    m.add_argument("--json", action="store_true")

    a = sub.add_parser("anchor")
    a.add_argument("--state", required=True)
    a.add_argument("--node-id")
    a.add_argument("--authority", choices=["constitutional", "canonical"])
    a.add_argument("--remove", action="store_true")
    a.add_argument("--list", action="store_true")
    a.add_argument("--json", action="store_true")

    c = sub.add_parser("connect")
    c.add_argument("--state")
    c.add_argument("--graph")
    c.add_argument("--llm", choices=["none", "openai"], default="none")
    c.add_argument("--json", action="store_true")

    p = sub.add_parser("maintain")
    p.add_argument("--state", required=True)
    p.add_argument("--tasks", default="health,decay,merge,prune")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--max-merges", type=int, default=5)
    p.add_argument("--prune-below", type=float, default=0.01)
    p.add_argument("--llm", choices=["none", "openai"], default="none")
    p.add_argument("--json", action="store_true")

    z = sub.add_parser("compact")
    z.add_argument("--state", required=True)
    z.add_argument("--memory-dir", required=True)
    z.add_argument("--max-age-days", type=int, default=7)
    z.add_argument("--target-lines", type=int, default=15)
    z.add_argument("--llm", choices=["none", "openai"], default="none")
    z.add_argument("--dry-run", action="store_true")
    z.add_argument("--json", action="store_true")

    d = sub.add_parser("daemon")
    d.add_argument("--state", required=True)
    d.add_argument("--embed-model", default="text-embedding-3-small")
    d.add_argument("--auto-save-interval", type=int, default=10)

    x = sub.add_parser("inject")
    x.add_argument("--state", required=True)
    x.add_argument("--id", required=True)
    x.add_argument("--content", required=True)
    x.add_argument(
        "--type",
        choices=["CORRECTION", "TEACHING", "DIRECTIVE"],
        default="TEACHING",
    )
    x.add_argument("--summary")
    x.add_argument("--connect-top-k", type=int, default=3)
    x.add_argument("--connect-min-sim", type=float, default=None)
    x.add_argument("--embedder", choices=["hash", "openai"], default=None)
    x.add_argument("--vector-stdin", action="store_true")
    x.add_argument("--json", action="store_true")

    r = sub.add_parser("replay")
    r.add_argument("--state")
    r.add_argument("--graph")
    r.add_argument("--sessions", nargs="+", required=True)
    r.add_argument("--json", action="store_true")

    h = sub.add_parser("health")
    h.add_argument("--state")
    h.add_argument("--graph")
    h.add_argument("--json", action="store_true")

    j = sub.add_parser("journal")
    j.add_argument("--state")
    j.add_argument("--last", type=int, default=10)
    j.add_argument("--stats", action="store_true")
    j.add_argument("--json", action="store_true")

    doctor = sub.add_parser("doctor")
    doctor.add_argument("--state", required=True)

    info = sub.add_parser("info")
    info_group = info.add_mutually_exclusive_group(required=True)
    info_group.add_argument("--state")
    info_group.add_argument("--graph")
    info.add_argument("--json", action="store_true")

    sync = sub.add_parser("sync")
    sync.add_argument("--state", required=True)
    sync.add_argument("--workspace", required=True)
    sync.add_argument("--embedder", choices=["openai", "hash"], default=None)
    sync.add_argument(
        "--authority-map",
        help="JSON object mapping file name -> authority level",
    )
    sync.add_argument("--dry-run", action="store_true")
    sync.add_argument("--json", action="store_true")
    return parser


def _load_payload(path: str) -> dict:
    """ load payload."""
    payload_path = Path(os.path.expanduser(path))
    if payload_path.is_dir():
        payload_path = payload_path / "graph.json"
    if not payload_path.exists():
        raise SystemExit(f"missing graph file: {path}")
    return json.loads(payload_path.read_text(encoding="utf-8"))


def _load_graph(path: str) -> Graph:
    """ load graph."""
    payload = _load_payload(path)
    payload = payload["graph"] if "graph" in payload else payload
    graph = Graph()
    for node_data in payload.get("nodes", []):
        graph.add_node(
            Node(node_data["id"], node_data["content"], node_data.get("summary", ""), node_data.get("metadata", {}))
        )
    for edge_data in payload.get("edges", []):
        graph.add_edge(
            Edge(
                edge_data["source"],
                edge_data["target"],
                edge_data.get("weight", 0.5),
                edge_data.get("kind", "sibling"),
                edge_data.get("metadata", {}),
            )
        )
    return graph


def _resolve_graph_index(args: argparse.Namespace) -> tuple[Graph, VectorIndex | None, dict[str, object]]:
    """ resolve graph index."""
    if args.state is not None:
        graph, index, meta = load_state(args.state)
        return graph, index, meta
    if args.graph is None:
        raise SystemExit("--state or --graph is required")

    graph = _load_graph(args.graph)
    index_arg = getattr(args, "index", None)
    index = _load_index(index_arg) if index_arg is not None else None
    return graph, index, {}


def _graph_payload(graph: Graph) -> dict:
    """ graph payload."""
    return {
        "nodes": [
            {
                "id": n.id,
                "content": n.content,
                "summary": n.summary,
                "metadata": n.metadata,
            }
            for n in graph.nodes()
        ],
        "edges": [
            {"source": e.source, "target": e.target, "weight": e.weight, "kind": e.kind, "metadata": e.metadata}
            for source in graph._edges.values()
            for e in source.values()
        ],
    }


def _write_graph(
    path: str | Path,
    graph: Graph,
    *,
    include_meta: bool = False,
    meta: dict[str, object] | None = None,
) -> None:
    """Write graph payload to a JSON file."""
    destination = Path(path).expanduser()
    if destination.is_dir():
        destination = destination / "graph.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = _graph_payload(graph)
    if include_meta:
        payload = {"graph": payload, "meta": meta or {}}
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _load_query_vector_from_stdin() -> list[float]:
    """ load query vector from stdin."""
    data = sys.stdin.read().strip()
    if not data:
        raise SystemExit("query vector JSON required on stdin")
    payload = json.loads(data)
    if not isinstance(payload, list):
        raise SystemExit("query vector stdin payload must be a JSON array")
    return [float(v) for v in payload]


def _load_session_queries(session_paths: str | Iterable[str]) -> list[str]:
    """ load session queries."""
    if isinstance(session_paths, str):
        session_paths = [session_paths]
    queries: list[str] = []
    for session_path in session_paths:
        path = Path(session_path).expanduser()
        if path.is_dir():
            queries.extend(extract_queries_from_dir(path))
        elif path.is_file():
            queries.extend(extract_queries(path))
        else:
            raise SystemExit(f"invalid sessions path: {path}")
    return queries


def _resolve_journal_path(args: argparse.Namespace) -> str | None:
    """ resolve journal path."""
    if args.state is not None:
        path = Path(args.state).expanduser()
        return str(path.parent / "journal.jsonl")
    if getattr(args, "graph", None) is not None:
        graph_path = Path(args.graph).expanduser()
        if graph_path.is_dir():
            return str(graph_path / "journal.jsonl")
        return str(graph_path.parent / "journal.jsonl")
    return None


def _load_session_query_records(session_paths: str | Iterable[str], since_ts: float | None = None) -> list[tuple[str, float | None]]:
    """ load session query records."""
    if isinstance(session_paths, str):
        session_paths = [session_paths]
    records: list[tuple[str, float | None]] = []
    for session_path in session_paths:
        path = Path(session_path).expanduser()
        if path.is_dir():
            records.extend(extract_query_records_from_dir(path, since_ts=since_ts))
        elif path.is_file():
            records.extend(extract_query_records(path, since_ts=since_ts))
        else:
            raise SystemExit(f"invalid sessions path: {path}")
    return records


def _load_session_interactions(session_paths: str | Iterable[str], since_ts: float | None = None) -> list[dict[str, object]]:
    """ load session interactions."""
    if isinstance(session_paths, str):
        session_paths = [session_paths]
    interactions: list[dict[str, object]] = []
    for session_path in session_paths:
        path = Path(session_path).expanduser()
        if path.is_dir():
            for session_file in sorted(path.glob("*.jsonl")):
                interactions.extend(extract_interactions(session_file, since_ts=since_ts))
        elif path.is_file():
            interactions.extend(extract_interactions(path, since_ts=since_ts))
        else:
            raise SystemExit(f"invalid sessions path: {path}")
    return interactions


def _state_meta(meta: dict[str, object] | None, fallback_name: str | None = None, fallback_dim: int | None = None) -> dict[str, object]:
    """ state meta."""
    base = dict(meta or {})
    embedder_name, embedder_dim = _state_embedder_meta(base)
    if fallback_name is not None:
        base["embedder_name"] = embedder_name or fallback_name
    if fallback_dim is not None:
        base["embedder_dim"] = embedder_dim if embedder_dim is not None else fallback_dim
    return base


def _keyword_seeds(graph: Graph, text: str, top_k: int) -> list[tuple[str, float]]:
    """ keyword seeds."""
    query_tokens = _tokenize(text)
    if not query_tokens:
        return []
    scores = [
        (node.id, len(query_tokens & _tokenize(node.content)) / len(query_tokens))
        for node in graph.nodes()
    ]
    scores.sort(key=lambda item: (item[1], item[0]), reverse=True)
    return scores[:top_k]


def _load_index(path: str) -> VectorIndex:
    """ load index."""
    payload = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("index payload must be a JSON object")
    index = VectorIndex()
    for node_id, vector in payload.items():
        if not isinstance(vector, list):
            raise SystemExit("index payload vectors must be arrays")
        index.upsert(str(node_id), [float(v) for v in vector])
    return index


def _state_embedder_meta(meta: dict[str, object]) -> tuple[str | None, int | None]:
    """ state embedder meta."""
    embedder_name = meta.get("embedder_name")
    if not isinstance(embedder_name, str):
        embedder_name = meta.get("embedder")
        if not isinstance(embedder_name, str):
            embedder_name = None

    embedder_dim = meta.get("embedder_dim")
    if not isinstance(embedder_dim, int):
        embedder_dim = None

    return embedder_name, embedder_dim


def _resolve_embedder(
    args: argparse.Namespace, meta: dict[str, object]
) -> tuple[callable[[str], list[float]], callable[[list[tuple[str, str]]], dict[str, list[float]]], str, int]:
    """ resolve embedder."""
    openai_name = "openai-text-embedding-3-small"
    embedder_name, _ = _state_embedder_meta(meta)
    use_openai = args.embedder == "openai" or (args.embedder is None and embedder_name == openai_name)
    if use_openai:
        from .openai_embeddings import OpenAIEmbedder

        embedder = OpenAIEmbedder()
    else:
        embedder = HashEmbedder()

    return embedder.embed, embedder.embed_batch, embedder.name, embedder.dim


def _resolve_llm(args: argparse.Namespace) -> tuple[Callable[[str, str], str] | None, Callable[[list[dict]], list[dict]] | None]:
    """Resolve optional LLM callbacks."""
    if getattr(args, "llm", None) == "openai":
        from .openai_llm import openai_llm_batch_fn, openai_llm_fn

        return openai_llm_fn, openai_llm_batch_fn
    return None, None


def _load_json(path: str) -> dict:
    """ load json."""
    try:
        payload = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in state file: {path}") from exc
    except OSError as exc:
        raise SystemExit(f"missing state file: {path}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"state file payload must be an object: {path}")
    return payload


def _state_payload(meta_path: str) -> tuple[dict, dict[str, object], dict[str, list[float]], Graph]:
    """ state payload."""
    payload = _load_json(meta_path)
    graph_payload = payload.get("graph", payload)
    if not isinstance(graph_payload, dict):
        raise SystemExit("state file graph payload must be an object")

    index_payload = payload.get("index", {})
    if not isinstance(index_payload, dict):
        raise SystemExit("state index payload must be an object")

    graph = _load_graph(meta_path)
    return payload, graph_payload, index_payload, graph


def _check_result(ok: bool, label: str, details: str = "") -> bool:
    """ check result."""
    print(f"{label}: {'PASS' if ok else 'FAIL'}" + (f" ({details})" if details else ""))
    return ok


def _journal_entry_count(journal_path: str | None) -> int | None:
    """ journal entry count."""
    if journal_path is None:
        return None
    path = Path(journal_path)
    if not path.exists():
        return None
    return len(read_journal(journal_path=str(path)))


def _ensure_hash_embedder_compat(meta: dict[str, object]) -> None:
    """ ensure hash embedder compat."""
    embedder_name, embedder_dim = _state_embedder_meta(meta)
    if embedder_dim is None:
        return

    hash_dim = HashEmbedder().dim
    if embedder_dim != hash_dim:
        raise SystemExit(
            f"Index was built with {embedder_name} (dim={embedder_dim}). "
            "CLI hash embedder uses dim=1024. Dimension mismatch. "
            "Use --query-vector-stdin with matching embedder."
        )


def _result_payload(result: TraversalResult) -> dict:
    """ result payload."""
    return {
        "fired": result.fired,
        "steps": [step.__dict__ for step in result.steps],
        "context": result.context,
        "tier_thresholds": result.tier_summary,
    }


def _query_text_output(result: TraversalResult, graph: Graph, max_context_chars: int | None = None) -> str:
    """format query output with node IDs."""
    if not result.fired:
        return "(No matches.)"

    rendered: list[str] = []
    used_chars = 0
    for idx, node_id in enumerate(dict.fromkeys(result.fired)):
        node = graph.get_node(node_id)
        if node is None:
            continue
        block = f"{node_id}\n{'~' * len(node_id)}\n{node.content}"
        if max_context_chars is None:
            rendered.append(block)
            continue

        if max_context_chars <= 0:
            break
        separator = "\n\n"
        if not rendered:
            if len(block) > max_context_chars:
                if max_context_chars > 3:
                    rendered.append(block[: max_context_chars - 3] + "...")
                else:
                    rendered.append(block[:max_context_chars])
                break
            rendered.append(block)
            used_chars = len(block)
            continue

        if used_chars + len(separator) >= max_context_chars:
            break
        available = max_context_chars - used_chars - len(separator)
        if available <= 0:
            break
        if len(block) <= available:
            rendered.append(block)
            used_chars += len(separator) + len(block)
        else:
            if available > 3:
                rendered.append(block[:available - 3] + "...")
            else:
                rendered.append(block[:available])
            break

    return "\n\n".join(rendered)


def cmd_init(args: argparse.Namespace) -> int:
    """cmd init."""
    output_dir = Path(args.output).expanduser()
    if output_dir.suffix == ".json" and not output_dir.is_dir():
        output_dir = output_dir.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    llm_fn, llm_batch_fn = _resolve_llm(args)
    graph, texts = split_workspace(args.workspace, llm_fn=llm_fn, llm_batch_fn=llm_batch_fn)
    if args.sessions is not None:
        replay_queries(graph=graph, queries=_load_session_queries(args.sessions))

    embedder_fn, embed_batch_fn, embedder_name, embedder_dim = _resolve_embedder(args, {})
    print(
        f"Embedding {len(texts)} texts ({embedder_name}, dim={embedder_dim})",
        file=sys.stderr,
    )
    index_vectors = embed_batch_fn(list(texts.items()))
    index = VectorIndex()
    for node_id, vector in index_vectors.items():
        index.upsert(node_id, vector)

    graph_path = output_dir / "graph.json"
    text_path = output_dir / "texts.json"
    state_meta = _state_meta({}, fallback_name=embedder_name, fallback_dim=embedder_dim)
    _write_graph(graph_path, graph, include_meta=True, meta=state_meta)
    save_state(
        graph=graph,
        index=index,
        path=output_dir / "state.json",
        meta=state_meta,
    )
    index_path = output_dir / "index.json"
    index_path.write_text(json.dumps(index_vectors, indent=2), encoding="utf-8")
    text_path.write_text(json.dumps(texts, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps({"graph": str(graph_path), "texts": str(text_path)}))
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    """cmd query."""
    graph, index, meta = _resolve_graph_index(args)
    embed_fn, _, embedder_name, _ = _resolve_embedder(args, meta)
    if args.top <= 0:
        raise SystemExit("--top must be >= 1")

    if args.query_vector_stdin:
        if index is None:
            raise SystemExit("query-vector-stdin requires --index")
        query_vec = _load_query_vector_from_stdin()
        seeds = index.search(query_vec, top_k=args.top)
    elif index is not None:
        if embedder_name == HashEmbedder().name:
            _ensure_hash_embedder_compat(meta)
        query_vec = embed_fn(args.text)
        seeds = index.search(query_vec, top_k=args.top)
    else:
        seeds = _keyword_seeds(graph, args.text, args.top)

    result = traverse(
        graph=graph,
        seeds=seeds,
        config=TraversalConfig(max_hops=15, max_context_chars=args.max_context_chars),
        query_text=args.text,
    )
    log_query(
        query_text=args.text,
        fired_ids=result.fired,
        node_count=graph.node_count(),
        journal_path=_resolve_journal_path(args),
    )
    if args.json:
        print(json.dumps(_result_payload(result)))
    else:
        print(_query_text_output(result=result, graph=graph, max_context_chars=args.max_context_chars))
    return 0


def cmd_learn(args: argparse.Namespace) -> int:
    """cmd learn."""
    graph, index, meta = _resolve_graph_index(args)
    fired_ids = [value.strip() for value in args.fired_ids.split(",") if value.strip()]
    if not fired_ids:
        raise SystemExit("provide at least one fired id")

    updates = apply_outcome(graph, fired_nodes=fired_ids, outcome=args.outcome)
    if args.state is not None:
        state_meta = _state_meta(meta)
        save_state(graph=graph, index=index or VectorIndex(), path=args.state, meta=state_meta)
    updates_abs = [abs(delta) for delta in updates.values()]
    summary = {
        "edges_updated": len(updates),
        "max_weight_delta": max(updates_abs) if updates_abs else 0.0,
    }
    if args.state is None:
        payload = {"graph": _graph_payload(graph)}
        Path(args.graph).expanduser().write_text(json.dumps(payload, indent=2), encoding="utf-8")
    log_learn(fired_ids=fired_ids, outcome=args.outcome, journal_path=_resolve_journal_path(args))
    print(json.dumps(summary, indent=2) if args.json else f"updated {args.state or args.graph}")
    return 0


def cmd_merge(args: argparse.Namespace) -> int:
    """cmd merge."""
    graph, index, meta = _resolve_graph_index(args)
    llm_fn, llm_batch_fn = _resolve_llm(args)
    suggestions = suggest_merges(graph, llm_fn=llm_fn, llm_batch_fn=llm_batch_fn)
    applied = []
    for source_id, target_id in suggestions:
        if graph.get_node(source_id) and graph.get_node(target_id):
            merged = apply_merge(graph, source_id, target_id)
            applied.append({"from": [source_id, target_id], "to": [merged]})
    if args.state is not None:
        state_meta = _state_meta(meta)
        save_state(graph=graph, index=index or VectorIndex(), path=args.state, meta=state_meta)
    else:
        _write_graph(args.graph, graph)
    payload = {"suggestions": [{"from": [s, t]} for s, t in suggestions], "applied": applied}
    print(json.dumps(payload) if args.json else f"Applied merges: {len(applied)}")
    return 0


def cmd_connect(args: argparse.Namespace) -> int:
    """cmd connect."""
    graph, index, meta = _resolve_graph_index(args)
    llm_fn, llm_batch_fn = _resolve_llm(args)
    suggestions = suggest_connections(graph, llm_fn=llm_fn, llm_batch_fn=llm_batch_fn)
    added = apply_connections(graph=graph, connections=suggestions)
    if args.state is not None:
        state_meta = _state_meta(meta)
        save_state(graph=graph, index=index or VectorIndex(), path=args.state, meta=state_meta)
    else:
        _write_graph(args.graph, graph)
    payload = {
        "suggestions": [
            {"source_id": s, "target_id": t, "weight": w, "reason": r} for s, t, w, r in suggestions
        ],
        "added": added,
    }
    print(json.dumps(payload) if args.json else f"Added edges: {added}")
    return 0


def cmd_anchor(args: argparse.Namespace) -> int:
    """cmd anchor."""
    graph, index, meta = _resolve_graph_index(args)
    if args.list:
        nodes = [
            {"node_id": node.id, "authority": node.metadata.get("authority", "overlay")}
            for node in graph.nodes()
            if node.metadata.get("authority") in {"constitutional", "canonical"}
        ]
        payload = {"nodes": nodes, "count": len(nodes)}
        print(json.dumps(payload, indent=2) if args.json else "\n".join(f"{node['node_id']}: {node['authority']}" for node in nodes) or "No anchored nodes.")
        return 0

    if not args.node_id:
        raise SystemExit("--node-id required unless --list is set")
    node = graph.get_node(args.node_id)
    if node is None:
        raise SystemExit(f"node not found: {args.node_id}")

    current_authority = node.metadata.get("authority", "overlay")
    if args.remove:
        if "authority" in node.metadata:
            node.metadata.pop("authority", None)
            current_authority = "overlay"
            save_state(graph=graph, index=index or VectorIndex(), path=args.state, meta=_state_meta(meta))
        payload = {"node_id": args.node_id, "authority": current_authority}
        print(json.dumps(payload) if args.json else f"{args.node_id} authority: {current_authority}")
        return 0

    if args.authority:
        node.metadata["authority"] = args.authority
        current_authority = args.authority
        save_state(graph=graph, index=index or VectorIndex(), path=args.state, meta=_state_meta(meta))

    payload = {"node_id": args.node_id, "authority": current_authority}
    print(json.dumps(payload) if args.json else f"{args.node_id} authority: {current_authority}")
def cmd_compact(args: argparse.Namespace) -> int:
    """cmd compact."""
    if args.state is None:
        raise SystemExit("--state is required for compact")

    _, _, meta = _resolve_graph_index(args)

    embed_args = SimpleNamespace(embedder=None)
    embed_fn, _, _, _ = _resolve_embedder(embed_args, meta)
    if args.llm == "openai":
        from .openai_llm import openai_llm_fn

        llm_fn = openai_llm_fn
    else:
        llm_fn = None

    if embed_fn is None:
        raise SystemExit("embedding callback missing")

    report = compact_daily_notes(
        state_path=args.state,
        memory_dir=args.memory_dir,
        max_age_days=args.max_age_days,
        target_lines=args.target_lines,
        embed_fn=embed_fn,
        llm_fn=llm_fn,
        journal_path=_resolve_journal_path(args),
        dry_run=args.dry_run,
    )
    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"Compaction report for {args.state}")
        print(f"  scanned: {report.files_scanned}")
        print(f"  compacted: {report.files_compacted}")
        print(f"  skipped: {report.files_skipped}")
        print(f"  nodes_injected: {report.nodes_injected}")
        print(f"  lines: {report.lines_before} -> {report.lines_after}")
    return 0


def cmd_inject(args: argparse.Namespace) -> int:
    """cmd inject."""
    graph, index, meta = _resolve_graph_index(args)
    if args.state is None:
        raise SystemExit("--state is required for inject")
    if index is None:
        index = VectorIndex()
    embed_fn, _, embedder_name, _ = _resolve_embedder(args, meta)

    if args.vector_stdin:
        vector = _load_query_vector_from_stdin()
    else:
        if embedder_name == HashEmbedder().name:
            _ensure_hash_embedder_compat(meta)
        vector = None

    if args.summary is None:
        from ._util import _first_line

        summary = _first_line(args.content)
    else:
        summary = args.summary

    if args.connect_min_sim is not None:
        connect_min_sim = args.connect_min_sim
    else:
        connect_min_sim = 0.0 if embedder_name == "hash-v1" else 0.3

    node_type = args.type
    metadata = {"source": "cli_inject", "type": node_type}
    if node_type == "CORRECTION":
        payload = inject_correction(
            graph=graph,
            index=index,
            node_id=args.id,
            content=args.content,
            summary=summary,
            metadata=metadata,
            vector=vector,
            embed_fn=None if args.vector_stdin else embed_fn,
            connect_top_k=args.connect_top_k,
            connect_min_sim=connect_min_sim,
        )
    else:
        payload = inject_node(
            graph=graph,
            index=index,
            node_id=args.id,
            content=args.content,
            summary=summary,
            metadata=metadata,
            vector=vector,
            embed_fn=None if args.vector_stdin else embed_fn,
            connect_top_k=args.connect_top_k,
            connect_min_sim=connect_min_sim,
        )

    state_meta = _state_meta(
        meta,
    )
    save_state(graph=graph, index=index, path=args.state, meta=state_meta)

    print(json.dumps(payload, indent=2) if args.json else f"Injected {payload['node_id']}")
    return 0


def cmd_replay(args: argparse.Namespace) -> int:
    """cmd replay."""
    graph, index, meta = _resolve_graph_index(args)
    last_replayed_ts = meta.get("last_replayed_ts")
    if not isinstance(last_replayed_ts, (int, float)):
        last_replayed_ts = None

    query_records = _load_session_interactions(args.sessions, since_ts=last_replayed_ts)
    stats = replay_queries(
        graph=graph,
        queries=query_records,
        verbose=not args.json,
        since_ts=last_replayed_ts,
    )
    log_replay(
        queries_replayed=stats["queries_replayed"],
        edges_reinforced=stats["edges_reinforced"],
        cross_file_created=stats["cross_file_edges_created"],
        journal_path=_resolve_journal_path(args),
    )
    if args.state is not None:
        state_meta = _state_meta(meta)
        if stats.get("last_replayed_ts") is not None:
            state_meta["last_replayed_ts"] = stats["last_replayed_ts"]
        save_state(graph=graph, index=index or VectorIndex(), path=args.state, meta=state_meta)
    else:
        _write_graph(args.graph, graph)
    print(
        json.dumps(stats, indent=2)
        if args.json
        else f"Replayed {stats['queries_replayed']}/{len(query_records)} queries, {stats['cross_file_edges_created']} cross-file edges created"
    )
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    """cmd doctor."""
    checks_passed = 0
    checks_total = 0
    failed = False

    checks_total += 1
    python_ok = sys.version_info >= (3, 10)
    checks_passed += _check_result(python_ok, "python_version", f"{sys.version.split()[0]}")
    failed = failed or (not python_ok)

    state_path = Path(args.state).expanduser()
    checks_total += 1
    state_exists = state_path.exists()
    checks_passed += _check_result(state_exists, "state_file_exists", str(state_path))
    failed = failed or (not state_exists)
    if not state_exists:
        print(f"Summary: {checks_passed}/{checks_total} checks passed")
        return 1

    checks_total += 1
    try:
        payload = _load_json(args.state)
        checks_passed += _check_result(True, "state_json_valid", str(args.state))
    except SystemExit as exc:
        checks_passed += _check_result(False, "state_json_valid", str(exc))
        print(f"Summary: {checks_passed}/{checks_total} checks passed")
        return 1
    graph_payload = payload.get("graph", {})
    checks_total += 1
    if not isinstance(graph_payload, dict):
        checks_passed += _check_result(False, "state_json_valid", "graph payload must be object")
        print(f"Summary: {checks_passed}/{checks_total} checks passed")
        return 1

    graph = _load_graph(args.state)
    index_payload = payload.get("index", {})
    checks_total += 1
    checks_passed += _check_result(
        bool(graph_payload.get("nodes")),
        "graph_has_nodes",
        f"nodes={graph.node_count()}",
    )
    failed = failed or (not graph_payload.get("nodes"))

    checks_total += 1
    checks_passed += _check_result(
        graph.edge_count() > 0,
        "graph_has_edges",
        f"edges={graph.edge_count()}",
    )
    failed = failed or (graph.edge_count() == 0)

    checks_total += 1
    embedder_name = payload.get("meta", {}).get("embedder_name")
    embedder_dim = payload.get("meta", {}).get("embedder_dim")
    checks_passed += _check_result(
        isinstance(embedder_name, str) and isinstance(embedder_dim, int),
        "embedder_metadata_present",
        f"name={embedder_name}, dim={embedder_dim}",
    )
    failed = failed or (not isinstance(embedder_name, str) or not isinstance(embedder_dim, int))

    checks_total += 1
    if not isinstance(embedder_dim, int):
        checks_passed += _check_result(False, "index_dimension_matches_embedder", "missing embedder_dim")
        failed = True
    else:
        if not isinstance(index_payload, dict):
            checks_passed += _check_result(False, "index_dimension_matches_embedder", "index payload must be an object")
            failed = True
        elif not index_payload:
            checks_passed += _check_result(False, "index_dimension_matches_embedder", "missing index payload")
            failed = True
        else:
            index_dims: set[int] = set()
            for node_id, vector in index_payload.items():
                if not isinstance(vector, list):
                    checks_passed += _check_result(False, "index_dimension_matches_embedder", f"{node_id}: not a list")
                    failed = True
                    break
                index_dims.add(len(vector))
            else:
                dim_ok = len(index_dims) == 1 and next(iter(index_dims)) == embedder_dim
                dim_value = next(iter(index_dims), None)
                checks_passed += _check_result(dim_ok, "index_dimension_matches_embedder", f"index_dim={dim_value}")
                failed = failed or (not dim_ok)

    checks_total += 1
    journal_path = _resolve_journal_path(args)
    if journal_path is not None and Path(journal_path).exists():
        try:
            Path(journal_path).open("a", encoding="utf-8").close()
            journal_ok = True
        except OSError:
            journal_ok = False
        checks_passed += _check_result(journal_ok, "journal_writable", str(journal_path))
        failed = failed or (not journal_ok)
    else:
        checks_passed += _check_result(True, "journal_writable", "not present")

    print(f"Summary: {checks_passed}/{checks_total} checks passed")
    return 1 if failed else 0


def cmd_info(args: argparse.Namespace) -> int:
    """cmd info."""
    if getattr(args, "state", None) is not None:
        payload, _, _, graph = _state_payload(args.state)
        meta = payload.get("meta", {})
        state_bytes = Path(args.state).expanduser().stat().st_size
        embedder_name = meta.get("embedder_name", "n/a")
        embedder_dim = meta.get("embedder_dim", "n/a")
    else:
        graph = _load_graph(args.graph)
        state_bytes = Path(args.graph).expanduser().stat().st_size
        embedder_name = "n/a"
        embedder_dim = "n/a"

    health = measure_health(graph)
    payload = {
        "version": __version__,
        "node_count": graph.node_count(),
        "edge_count": graph.edge_count(),
        "embedder_name": embedder_name,
        "embedder_dim": embedder_dim,
        "dormant_pct": health.dormant_pct * 100,
        "habitual_pct": health.habitual_pct * 100,
        "reflex_pct": health.reflex_pct * 100,
        "journal_entry_count": _journal_entry_count(_resolve_journal_path(args)),
        "state_file_size": state_bytes,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
        return 0

    print("\n".join(
        [
            f"version: {payload['version']}",
            f"node_count: {payload['node_count']}",
            f"edge_count: {payload['edge_count']}",
            f"embedder_name: {payload['embedder_name']}",
            f"embedder_dim: {payload['embedder_dim']}",
            f"dormant_pct: {payload['dormant_pct']:.2f}",
            f"habitual_pct: {payload['habitual_pct']:.2f}",
            f"reflex_pct: {payload['reflex_pct']:.2f}",
            f"journal_entry_count: {payload['journal_entry_count'] if payload['journal_entry_count'] is not None else 'n/a'}",
            f"state_file_size: {payload['state_file_size']}",
        ]
    ))
    return 0


def _parse_authority_map(raw: str | None) -> dict[str, str]:
    """Parse authority map json string."""
    if raw is None:
        return dict(DEFAULT_AUTHORITY_MAP)
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise SystemExit("--authority-map must be a JSON object")

    parsed: dict[str, str] = {}
    for key, value in payload.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise SystemExit("--authority-map must map string keys to string values")
        parsed[key] = value
    return parsed


def cmd_sync(args: argparse.Namespace) -> int:
    """cmd sync."""
    authority_map = _parse_authority_map(getattr(args, "authority_map", None))
    graph, index, meta = _resolve_graph_index(args)

    embed_fn, embed_batch_fn, _, _ = _resolve_embedder(args, meta)

    if args.dry_run:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_state = Path(tmp_dir) / "state.json"
            shutil.copy2(args.state, tmp_state)
            report = sync_workspace(
                state_path=str(tmp_state),
                workspace_dir=args.workspace,
                embed_fn=embed_fn,
                embed_batch_fn=embed_batch_fn,
                journal_path=None,
                authority_map=authority_map,
            )
            if args.json:
                print(json.dumps(asdict(report), indent=2))
            else:
                print(
                    f"sync report: +{report.nodes_added}/~{report.nodes_updated} "
                    f"-{report.nodes_removed} ={report.nodes_unchanged} unchanged | "
                    f"{report.embeddings_computed} embeddings"
                )
            return 0

    report = sync_workspace(
        state_path=args.state,
        workspace_dir=args.workspace,
        embed_fn=embed_fn,
        embed_batch_fn=embed_batch_fn,
        journal_path=_resolve_journal_path(args),
        authority_map=authority_map,
    )

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(
            f"sync report: +{report.nodes_added}/~{report.nodes_updated} "
            f"-{report.nodes_removed} ={report.nodes_unchanged} unchanged | "
            f"{report.embeddings_computed} embeddings"
        )
    return 0


def cmd_health(args: argparse.Namespace) -> int:
    """cmd health."""
    graph, _, _ = _resolve_graph_index(args)
    payload = measure_health(graph).__dict__
    payload["nodes"] = graph.node_count()
    payload["edges"] = graph.edge_count()
    log_health(payload, journal_path=_resolve_journal_path(args))
    if args.json:
        print(json.dumps(payload, indent=2))
        return 0
    print(
        "\n".join(
            [
                "Brain health:",
                f"  Nodes: {payload['nodes']}",
                f"  Edges: {payload['edges']}",
                f"  Reflex: {payload['reflex_pct']:.1%}  Habitual: {payload['habitual_pct']:.1%}  Dormant: {payload['dormant_pct']:.1%}",
                f"  Orphans: {payload['orphan_nodes']}",
                f"  Cross-file edges: {payload['cross_file_edge_pct']:.1%}",
            ]
        )
    )
    return 0


def cmd_maintain(args: argparse.Namespace) -> int:
    """cmd maintain."""
    requested_tasks = [task.strip() for task in args.tasks.split(",") if task.strip()]
    llm_fn, _ = _resolve_llm(args)
    report = run_maintenance(
        state_path=args.state,
        tasks=requested_tasks,
        llm_fn=llm_fn,
        journal_path=_resolve_journal_path(args),
        dry_run=args.dry_run,
        max_merges=args.max_merges,
        prune_below=args.prune_below,
    )
    if args.json:
        print(json.dumps(asdict(report), indent=2))
        return 0

    print("\n".join([
        "Maintenance report:",
        f"  tasks: {', '.join(report.tasks_run) if report.tasks_run else '(none)'}",
        f"  nodes: {report.health_before['nodes']} -> {report.health_after['nodes']}",
        f"  edges: {report.edges_before} -> {report.edges_after}",
        f"  merges: {report.merges_applied}/{report.merges_proposed}",
        f"  pruned: edges={report.pruned_edges} nodes={report.pruned_nodes}",
        f"  decay_applied: {report.decay_applied}",
        f"  dry_run: {args.dry_run}",
    ]))
    if report.notes:
        print(f"  notes: {', '.join(report.notes)}")
    return 0


def cmd_daemon(args: argparse.Namespace) -> int:
    """cmd daemon."""
    from .daemon import main as daemon_main

    return daemon_main(
        [
            "--state",
            str(args.state),
            "--embed-model",
            args.embed_model,
            "--auto-save-interval",
            str(args.auto_save_interval),
        ]
    )


def cmd_journal(args: argparse.Namespace) -> int:
    """cmd journal."""
    journal_path = _resolve_journal_path(args)
    if args.stats:
        print(
            json.dumps(journal_stats(journal_path=journal_path), indent=2)
            if args.json
            else "\n".join(
                f"{k}: {v}"
                for k, v in journal_stats(journal_path=journal_path).items()
                if k != "avg_fired_per_query"
            )
        )
        return 0
    entries = read_journal(last_n=args.last, journal_path=journal_path)
    print(
        json.dumps(entries, indent=2)
        if args.json
        else "\n".join(f"{idx+1:>2}. {entry.get('type')} @ {entry.get('iso', entry.get('ts', ''))}: {entry}" for idx, entry in enumerate(entries))
        or "No entries."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    """main."""
    args = _build_parser().parse_args(argv)
    return {
        "init": cmd_init,
        "query": cmd_query,
        "learn": cmd_learn,
        "merge": cmd_merge,
        "maintain": cmd_maintain,
        "anchor": cmd_anchor,
        "connect": cmd_connect,
        "compact": cmd_compact,
        "daemon": cmd_daemon,
        "inject": cmd_inject,
        "replay": cmd_replay,
        "health": cmd_health,
        "journal": cmd_journal,
        "doctor": cmd_doctor,
        "info": cmd_info,
        "sync": cmd_sync,
    }[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
