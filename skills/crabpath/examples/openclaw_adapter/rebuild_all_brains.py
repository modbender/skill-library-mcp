#!/usr/bin/env python3
"""Rebuild adapter brains from workspace + learning DB + sessions.

This script rebuilds each agent's graph from workspace markdown, merges active
learning records from the configured learning DB, replays historical sessions,
and then persists state before connecting learning nodes to workspace nodes.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

from crabpath import split_workspace, VectorIndex
from crabpath.replay import extract_queries_from_dir, replay_queries
from crabpath.store import save_state, load_state
from crabpath.autotune import measure_health
from crabpath.graph import Node
from connect_learnings import connect_learnings


LEARNING_DB = Path(os.environ.get("CRABPATH_LEARNING_DB", "~/.openclaw/workspace/learning/db/learning.db")).expanduser()

AGENTS = {
    "main": {
        "workspace": Path.home() / ".openclaw" / "workspace",
        "sessions": Path.home() / ".openclaw" / "agents" / "main" / "sessions",
        "output": Path.home() / ".crabpath" / "main",
        "cache": Path("/tmp/crabpath_main_embeddings.json"),
    },
    "pelican": {
        "workspace": Path.home() / ".openclaw" / "workspace-pelican",
        "sessions": Path.home() / ".openclaw" / "agents" / "pelican" / "sessions",
        "output": Path.home() / ".crabpath" / "pelican",
        "cache": Path("/tmp/crabpath_pelican_embeddings.json"),
    },
    "bountiful": {
        "workspace": Path.home() / ".openclaw" / "workspace-bountiful",
        "sessions": Path.home() / ".openclaw" / "agents" / "bountiful" / "sessions",
        "output": Path.home() / ".crabpath" / "bountiful",
        "cache": Path("/tmp/crabpath_bountiful_embeddings.json"),
    },
}


def _ts():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _backup(output_dir: Path):
    if output_dir.exists():
        bak = output_dir.parent / "_bak" / f"{output_dir.name}-{_ts()}"
        bak.parent.mkdir(parents=True, exist_ok=True)
        print(f"  [backup] {output_dir} -> {bak}")
        shutil.move(str(output_dir), str(bak))
    output_dir.mkdir(parents=True, exist_ok=True)


def _load_cache(cache_path: Path) -> dict[str, list[float]]:
    if not cache_path.exists():
        return {}
    data = json.loads(cache_path.read_text())
    return {k: v for k, v in data.items() if isinstance(v, list) and len(v) == 1536}


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


def _load_learnings(
    agent_id: str, skip_node_ids: set[str] | None = None
) -> list[tuple[str, str]]:
    """Load learning nodes from SQLite for this agent. Returns (node_id, content) pairs."""
    if not LEARNING_DB.exists():
        print(f"  [learnings] DB not found: {LEARNING_DB}")
        return []
    
    conn = sqlite3.connect(str(LEARNING_DB))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, type, tag, error_class, prevention_rule, source_text, recurrence_count, created_at "
        "FROM learnings WHERE status='active' AND (agent=? OR agent IS NULL) ORDER BY created_at",
        (agent_id,)
    ).fetchall()
    conn.close()
    
    results = []
    for row in rows:
        node_id = f"learning::{row['id']}"
        parts = []
        if row['tag']:
            parts.append(f"[{row['tag']}]")
        if row['type']:
            parts.append(f"Type: {row['type']}")
        if row['error_class']:
            parts.append(f"Error: {row['error_class']}")
        if row['prevention_rule']:
            parts.append(f"Rule: {row['prevention_rule']}")
        if row['source_text']:
            parts.append(row['source_text'])
        if row['recurrence_count'] and row['recurrence_count'] > 1:
            parts.append(f"(occurred {row['recurrence_count']}x)")
        content = "\n".join(parts)
        if content.strip():
            if skip_node_ids and node_id in skip_node_ids:
                continue
            results.append((node_id, content))
    
    return results


def _embed_new_nodes(new_texts: dict[str, str], batch_size: int = 50) -> dict[str, list[float]]:
    """Embed new nodes using OpenAI. Returns {node_id: vector}."""
    if not new_texts:
        return {}
    
    from openai import OpenAI
    client = OpenAI()
    
    results = {}
    items = list(new_texts.items())
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        texts = [content[:8000] for _, content in batch]
        ids = [nid for nid, _ in batch]
        
        resp = client.embeddings.create(model="text-embedding-3-small", input=texts)
        for j, emb in enumerate(resp.data):
            results[ids[j]] = emb.embedding
        
        done = min(i + batch_size, len(items))
        print(f"    Embedded {done}/{len(items)} new nodes")
    
    return results


def rebuild_agent(
    agent_id: str, config: dict, preserve_injected: bool = True
) -> dict[str, object]:
    workspace = config["workspace"]
    sessions = config["sessions"]
    output = config["output"]
    cache_path = config["cache"]
    state_path = output / "state.json"
    injected_node_ids: set[str] = set()
    preserved_nodes: dict[str, Node] = {}
    preserved_vectors: dict[str, list[float]] = {}
    if preserve_injected and state_path.exists():
        injected_node_ids = _load_injected_node_ids(state_path)
        if injected_node_ids:
            preserved_nodes, preserved_vectors = _snapshot_injected_nodes(state_path, injected_node_ids)
    
    print(f"\n{'='*60}")
    print(f"  {agent_id.upper()}")
    print(f"{'='*60}")
    
    t0 = time.time()
    _backup(output)
    
    # Load cached embeddings
    cached = _load_cache(cache_path)
    print(f"  Cached embeddings: {len(cached)}")
    
    # 1. Split workspace (.md files, depth 4 to capture docs/memory subdirs)
    print(f"  Splitting workspace: {workspace}")
    graph, texts = split_workspace(str(workspace), max_depth=4, file_extensions=[".md"])
    print(f"  Split: {graph.node_count()} nodes, {graph.edge_count()} edges, {len(texts)} texts")
    
    # 2. Add learning DB nodes
    learnings = _load_learnings(agent_id, skip_node_ids=injected_node_ids)
    print(f"  Learnings from DB: {len(learnings)} nodes")
    for node_id, content in learnings:
        node = Node(
            id=node_id,
            content=content,
            summary=content.split('\n')[0][:100],
            metadata={"source": "learning_db", "agent": agent_id}
        )
        graph.add_node(node)
        texts[node_id] = content
    
    # 3. Connect learnings to related workspace nodes (by keyword overlap)
    # Simple heuristic: link each learning to nodes whose file matches error_class keywords
    print(f"  Total graph: {graph.node_count()} nodes, {len(texts)} texts")
    
    # 4. Full replay
    if sessions.exists():
        queries = extract_queries_from_dir(sessions)
        print(f"  Replaying {len(queries)} queries...")
        replay_queries(graph=graph, queries=queries)
    else:
        print(f"  [skip] No sessions dir: {sessions}")
    
    # 5. Build index: reuse cached, embed new
    new_texts = {nid: content for nid, content in texts.items() if nid not in cached}
    reused = {nid: cached[nid] for nid in texts if nid in cached}
    print(f"  Index: {len(reused)} reused, {len(new_texts)} new nodes to embed")
    
    new_vecs = {}
    if new_texts:
        print(f"  Embedding {len(new_texts)} new nodes via OpenAI...")
        new_vecs = _embed_new_nodes(new_texts)
    
    # Build combined index
    index = VectorIndex()
    all_vecs = {**reused, **new_vecs}
    for nid, vec in all_vecs.items():
        index.upsert(nid, vec)

    restored = _restore_injected_nodes(
        graph=graph,
        index=index,
        preserved_nodes=preserved_nodes,
        preserved_vectors=preserved_vectors,
    )
    if restored:
        print(f"  Preserved injected nodes: {restored}")
    
    missing = len(texts) - len(all_vecs)
    print(f"  Index: {len(all_vecs)} vectors ({len(reused)} reused + {len(new_vecs)} new), {missing} missing")
    
    # 6. Save state
    meta = {
        "embedding_reused_count": len(reused),
        "embedding_new_count": len(new_vecs),
        "embedding_missing_count": missing,
        "learning_nodes_added": len(learnings),
        "total_nodes": graph.node_count(),
        "rebuilt_at": datetime.now(timezone.utc).isoformat(),
    }
    save_state(graph, index, str(state_path),
               embedder_name="openai-text-embedding-3-small", embedder_dim=1536, meta=meta)
    
    # 7. Save updated embedding cache (old + new) for future reuse
    updated_cache = {**cached, **new_vecs}
    cache_path.write_text(json.dumps(updated_cache))
    print(f"  Updated embedding cache: {len(updated_cache)} vectors (was {len(cached)})")
    
    # 8. Connect learning nodes to workspace nodes
    connected_edges = connect_learnings(str(state_path))
    print(f"  Connected learning nodes: {connected_edges} edges")
    graph, index, meta = load_state(str(state_path))

    # 9. Health
    h = measure_health(graph)
    elapsed = time.time() - t0
    print(f"  Health: dormant={h.dormant_pct:.0%}, reflex={h.reflex_pct:.0%}, cross-file={h.cross_file_edge_pct:.0%}")
    print(f"  Done in {elapsed:.1f}s")
    
    # 10. Doctor
    import subprocess
    result = subprocess.run(["crabpath", "doctor", "--state", str(state_path)],
                          capture_output=True, text=True)
    print(f"  Doctor:\n" + "\n".join(f"    {l}" for l in (result.stdout or "").strip().splitlines()))
    
    return {
        "nodes": graph.node_count(), "edges": graph.edge_count(),
        "reused": len(reused), "new": len(new_vecs), "missing": missing,
        "learnings": len(learnings), "learning_edges": connected_edges, "time": elapsed,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Rebuild one or all OpenClaw adapter brains from workspace + learning DB + sessions"
    )
    parser.add_argument(
        "--agent",
        choices=list(AGENTS.keys()),
        help="Rebuild only this agent (default: all)",
    )
    parser.add_argument(
        "--preserve-injected",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Preserve injected CORRECTION nodes across rebuilds",
    )
    args = parser.parse_args()

    agent_ids = [args.agent] if args.agent else list(AGENTS.keys())
    results = {}
    for agent_id in agent_ids:
        results[agent_id] = rebuild_agent(
            agent_id,
            AGENTS[agent_id],
            preserve_injected=args.preserve_injected,
        )
    
    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")
    for agent, r in results.items():
        print(f"  {agent}: {r['nodes']} nodes, {r['edges']} edges | "
              f"{r['reused']} reused + {r['new']} new + {r['missing']} missing | "
              f"{r['learning_edges']} learning-edges | {r['learnings']} learnings | {r['time']:.1f}s")


if __name__ == "__main__":
    main()
