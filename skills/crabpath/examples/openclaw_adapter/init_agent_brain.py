#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import hashlib
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI
from crabpath import Node, VectorIndex, load_state, save_state, split_workspace
from crabpath._batch import batch_or_single_embed
from crabpath.autotune import measure_health
from crabpath.replay import extract_queries, extract_queries_from_dir, replay_queries

from connect_learnings import apply_correction_inhibitions, connect_learning_nodes


EMBED_MODEL = "openai-text-embedding-3-small"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536
EMBED_BATCH_SIZE = 100


def require_api_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(
            "This script must run inside the agent framework exec environment where OPENAI_API_KEY is injected."
        )
    return api_key


def _infer_agent_id(output: Path, sessions: Path) -> str:
    candidates = [output.name, output.parent.name, sessions.name, sessions.parent.name]
    for candidate in candidates:
        if candidate and candidate not in {"", "state.json", "sessions", "state"}:
            return candidate
    return "main"


def _learning_row_to_content(row: sqlite3.Row) -> str:
    parts = []
    if row["tag"]:
        parts.append(f"[{row['tag']}]")
    if row["type"]:
        parts.append(f"Type: {row['type']}")
    if row["error_class"]:
        parts.append(f"Error: {row['error_class']}")
    if row["prevention_rule"]:
        parts.append(f"Rule: {row['prevention_rule']}")
    if row["source_text"]:
        parts.append(row["source_text"])
    if row["recurrence_count"] and row["recurrence_count"] > 1:
        parts.append(f"(occurred {row['recurrence_count']}x)")
    return "\n".join(parts)


def _correction_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _load_injected_correction_rows(state_path: Path) -> list[tuple[str, str]]:
    log_path = state_path.parent / "injected_corrections.jsonl"
    if not log_path.exists():
        return []

    rows: list[tuple[str, str]] = []
    for raw_line in log_path.read_text(encoding="utf-8").splitlines():
        try:
            payload = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        content_hash = payload.get("content_hash")
        node_id = payload.get("node_id")
        if isinstance(content_hash, str) and isinstance(node_id, str):
            rows.append((content_hash, node_id))
    return rows


def _load_injected_correction_hashes(state_path: Path) -> set[str]:
    return {content_hash for content_hash, _ in _load_injected_correction_rows(state_path)}


def _load_injected_node_ids(state_path: Path) -> set[str]:
    return {node_id for _, node_id in _load_injected_correction_rows(state_path)}


def _snapshot_injected_nodes(
    state_path: Path, injected_node_ids: set[str]
) -> tuple[dict[str, Node], dict[str, list[float]]]:
    if not injected_node_ids:
        return {}, {}

    graph, index, _ = load_state(str(state_path))
    nodes: dict[str, Node] = {}
    vectors: dict[str, list[float]] = {}

    for node_id in injected_node_ids:
        node = graph.get_node(node_id)
        vector = index._vectors.get(node_id)
        if node is not None:
            nodes[node_id] = Node(
                id=node.id,
                content=node.content,
                summary=node.summary,
                metadata=dict(node.metadata),
            )
        if isinstance(vector, list):
            vectors[node_id] = list(vector)

    return nodes, vectors


def _restore_injected_nodes(
    graph: Graph,
    index: VectorIndex,
    preserved_nodes: dict[str, Node],
    preserved_vectors: dict[str, list[float]],
) -> int:
    restored = 0
    for node_id, node in preserved_nodes.items():
        if graph.get_node(node_id) is None:
            graph.add_node(node)
            restored += 1

        vector = preserved_vectors.get(node_id)
        if vector is not None:
            index._vectors[node_id] = list(vector)

    return restored


def _load_active_learnings(
    learning_db: Path,
    agent_id: str,
    injected_correction_hashes: set[str] | None = None,
    skip_node_ids: set[str] | None = None,
) -> list[tuple[str, str]]:
    if not learning_db.exists():
        print(f"  [learnings] DB not found: {learning_db}")
        return []

    conn = sqlite3.connect(str(learning_db))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, type, tag, error_class, prevention_rule, source_text, recurrence_count "
        "FROM learnings WHERE status='active' AND (agent=? OR agent IS NULL) ORDER BY created_at",
        (agent_id,)
    ).fetchall()
    conn.close()

    learnings = []
    skip_hashes = injected_correction_hashes or set()
    for row in rows:
        content = _learning_row_to_content(row)
        if content.strip():
            if row["type"] == "CORRECTION" and _correction_content_hash(content) in skip_hashes:
                continue
            node_id = f"learning::{row['id']}"
            if skip_node_ids and node_id in skip_node_ids:
                continue
            learnings.append((node_id, content))

    return learnings


def build_embed_batch_fn(client: OpenAI, batch_size: int = EMBED_BATCH_SIZE):
    def embed_batch(texts: list[tuple[str, str]]) -> dict[str, list[float]]:
        if not texts:
            return {}

        if batch_size <= 0:
            raise ValueError("embed batch_size must be >= 1")

        results = {}
        for start in range(0, len(texts), batch_size):
            chunk = texts[start : start + batch_size]
            _, contents = zip(*chunk)
            response = client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=list(contents))
            for index, embedding in enumerate(response.data):
                results[chunk[index][0]] = embedding.embedding

        return results

    return embed_batch


def build_llm_fn(client: OpenAI):
    def llm_fn(system: str, user: str) -> str:
        resp = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user[:4000]},
            ],
            max_completion_tokens=500,
        )
        return resp.choices[0].message.content
    return llm_fn


def load_session_queries(sessions_path: Path) -> list[str]:
    if not sessions_path.exists():
        raise SystemExit(f"sessions path not found: {sessions_path}")

    if sessions_path.is_dir():
        return extract_queries_from_dir(sessions_path)
    return extract_queries(sessions_path)


def resolve_output_paths(output_path: Path) -> tuple[Path, Path, Path, Path]:
    if output_path.exists() and output_path.is_file() and output_path.suffix.lower() == ".json":
        state_path = output_path
        output_dir = output_path.parent
    else:
        output_dir = output_path
        state_path = output_dir / "state.json"

    output_dir = output_dir.expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir, state_path, output_dir / "graph.json", output_dir / "index.json"


def write_graph(path: Path, graph, *, embedder_name: str, embedder_dim: int) -> None:
    payload = {
        "graph": {
            "nodes": [
                {
                    "id": node.id,
                    "content": node.content,
                    "summary": node.summary,
                    "metadata": node.metadata,
                }
                for node in graph.nodes()
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "weight": edge.weight,
                    "kind": edge.kind,
                    "metadata": edge.metadata,
                }
                for source_edges in graph._edges.values()
                for edge in source_edges.values()
            ],
        },
        "meta": {
            "embedder_name": embedder_name,
            "embedder_dim": embedder_dim,
            "schema_version": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "node_count": graph.node_count(),
        },
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run(
    workspace: Path,
    sessions: Path,
    output: Path,
    learning_db: Path | None = None,
    do_connect_learnings: bool = True,
    batch_size: int = EMBED_BATCH_SIZE,
    preserve_injected: bool = True,
) -> None:
    if not workspace.exists():
        raise SystemExit(f"workspace not found: {workspace}")

    api_key = require_api_key()
    client = OpenAI(api_key=api_key)
    embed_batch = build_embed_batch_fn(client, batch_size=batch_size)

    output_dir, state_path, graph_path, index_path = resolve_output_paths(output)
    preserved_nodes: dict[str, Node] = {}
    preserved_vectors: dict[str, list[float]] = {}
    injected_correction_node_ids: set[str] = set()

    if preserve_injected and state_path.exists():
        injected_correction_node_ids = _load_injected_node_ids(state_path)
        if injected_correction_node_ids:
            preserved_nodes, preserved_vectors = _snapshot_injected_nodes(state_path, injected_correction_node_ids)

    graph, texts = split_workspace(str(workspace), llm_fn=None, llm_batch_fn=None)

    agent_id = _infer_agent_id(output, sessions)
    injected_correction_hashes = set()
    if learning_db is not None:
        injected_correction_hashes = _load_injected_correction_hashes(state_path)
    learning_count = 0
    if learning_db is not None:
        learnings = _load_active_learnings(
            learning_db=learning_db,
            agent_id=agent_id,
            injected_correction_hashes=injected_correction_hashes,
            skip_node_ids=injected_correction_node_ids,
        )
        learning_count = len(learnings)
        print(f"  Learnings from DB ({agent_id}): {learning_count}")
        for node_id, content in learnings:
            graph.add_node(
                Node(
                    id=node_id,
                    content=content,
                    summary=content.split("\n")[0][:100],
                    metadata={"source": "learning_db", "agent": agent_id},
                )
            )
            texts[node_id] = content

    session_queries = load_session_queries(sessions)
    replay_stats = replay_queries(graph=graph, queries=session_queries, verbose=False)

    embeddings = batch_or_single_embed(list(texts.items()), embed_batch_fn=embed_batch)
    index = VectorIndex()
    for node_id, vector in embeddings.items():
        index.upsert(node_id, vector)

    restored_nodes = _restore_injected_nodes(
        graph=graph,
        index=index,
        preserved_nodes=preserved_nodes,
        preserved_vectors=preserved_vectors,
    )
    if restored_nodes:
        print(f"  Preserved injected nodes: {restored_nodes}")

    embedder_dim = EMBEDDING_DIM
    save_state(
        graph=graph,
        index=index,
        path=str(state_path),
        embedder_name=EMBED_MODEL,
        embedder_dim=embedder_dim,
    )

    learning_connections = 0
    correction_inhibitions = 0
    if learning_db is not None and do_connect_learnings:
        learning_connections = connect_learning_nodes(graph=graph, index=index, top_k=3, min_sim=0.3)
        correction_inhibitions = apply_correction_inhibitions(graph=graph, learning_db_path=learning_db, agent_id=agent_id)
        save_state(
            graph=graph,
            index=index,
            path=str(state_path),
            embedder_name=EMBED_MODEL,
            embedder_dim=embedder_dim,
        )

    write_graph(
        graph_path,
        graph,
        embedder_name=EMBED_MODEL,
        embedder_dim=embedder_dim,
    )
    index_path.write_text(json.dumps(index._vectors, indent=2), encoding="utf-8")

    health = measure_health(graph)
    health_payload = {
        "nodes": graph.node_count(),
        "edges": graph.edge_count(),
        "embedder_name": EMBED_MODEL,
        "embedder_dim": embedder_dim,
        "state_path": str(state_path),
        "graph_path": str(graph_path),
        "index_path": str(index_path),
        "embeddings": len(embeddings),
        "workspace_nodes": graph.node_count(),
        "replayed_sessions": len(session_queries),
        "replayed_queries": replay_stats["queries_replayed"],
        "reinforced_edges": replay_stats["edges_reinforced"],
        "cross_file_edges_created": replay_stats["cross_file_edges_created"],
    }
    if learning_db is not None:
        health_payload.update(
            {
                "learning_nodes": learning_count,
                "learning_connections": learning_connections,
                "correction_inhibitions": correction_inhibitions,
                "connect_learnings": do_connect_learnings,
            }
        )

    health_payload["health"] = {
        "dormant_pct": health.dormant_pct,
        "habitual_pct": health.habitual_pct,
        "reflex_pct": health.reflex_pct,
        "cross_file_edge_pct": health.cross_file_edge_pct,
        "orphan_nodes": health.orphan_nodes,
    }
    summary = {
        "status": "ok",
        "output_dir": str(output_dir),
        "state": str(state_path),
        "graph": str(graph_path),
        "index": str(index_path),
    }
    summary.update(health_payload)
    print(json.dumps(summary, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a CrabPath state.json for OpenClaw adapters")
    parser.add_argument("workspace_path", help="Path to agent workspace markdown directory")
    parser.add_argument("sessions_path", help="Path to OpenClaw sessions file or directory")
    parser.add_argument("output_path", help="Output directory (or state.json path)")
    parser.add_argument("--learning-db", type=Path, help="Path to SQLite DB containing active learnings")
    parser.add_argument("--batch-size", type=int, default=EMBED_BATCH_SIZE, help="Batch size for OpenAI embedding requests")

    connect_group = parser.add_mutually_exclusive_group()
    connect_group.add_argument(
        "--connect-learnings",
        dest="connect_learnings",
        action="store_true",
        help="Enable learning node to workspace connection and correction inhibition steps",
    )
    connect_group.add_argument(
        "--no-connect-learnings",
        dest="connect_learnings",
        action="store_false",
        help="Skip learning node to workspace connection and correction inhibition steps",
    )
    parser.add_argument(
        "--preserve-injected",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Preserve injected CORRECTION nodes across rebuilds",
    )
    parser.set_defaults(connect_learnings=None)
    args = parser.parse_args()

    if args.batch_size <= 0:
        raise SystemExit("--batch-size must be >= 1")

    if args.learning_db is None:
        do_connect_learnings = False
    else:
        do_connect_learnings = args.connect_learnings if args.connect_learnings is not None else True

    run(
        workspace=Path(args.workspace_path),
        sessions=Path(args.sessions_path),
        output=Path(args.output_path),
        learning_db=args.learning_db,
        do_connect_learnings=do_connect_learnings,
        batch_size=args.batch_size,
        preserve_injected=args.preserve_injected,
    )


if __name__ == "__main__":
    main()
