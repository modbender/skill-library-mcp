#!/usr/bin/env python3
"""Connect learning nodes to workspace nodes via embedding similarity."""
from __future__ import annotations

import argparse
import re
import sqlite3
import time
from pathlib import Path

from crabpath.graph import Edge
from crabpath.store import load_state, save_state
from crabpath.autotune import measure_health


AGENT_STATES = {
    "main": Path.home() / ".crabpath" / "main" / "state.json",
    "pelican": Path.home() / ".crabpath" / "pelican" / "state.json",
    "bountiful": Path.home() / ".crabpath" / "bountiful" / "state.json",
}


def cosine_sim(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def connect_learning_nodes(graph, index, top_k: int = 3, min_sim: float = 0.3) -> int:
    if top_k <= 0 or min_sim < 0:
        raise ValueError("top_k must be >= 1 and min_sim >= 0")

    learning_nodes = [n for n in graph.nodes() if n.id.startswith("learning::")]
    workspace_nodes = [n for n in graph.nodes() if not n.id.startswith("learning::")]

    if not learning_nodes:
        return 0

    learning_vecs = {
        n.id: index._vectors.get(n.id)
        for n in learning_nodes
        if n.id in index._vectors
    }
    workspace_vecs = {
        n.id: index._vectors.get(n.id)
        for n in workspace_nodes
        if n.id in index._vectors
    }

    edges_added = 0
    for lid, lvec in learning_vecs.items():
        if lvec is None:
            continue

        sims = []
        for wid, wvec in workspace_vecs.items():
            if wvec is None:
                continue
            sims.append((wid, cosine_sim(lvec, wvec)))

        sims.sort(key=lambda item: item[1], reverse=True)
        for wid, sim in sims[:top_k]:
            if sim < min_sim:
                continue

            weight = min(0.7, max(0.35, sim))
            if graph._edges.get(lid, {}).get(wid) is None:
                graph.add_edge(Edge(source=lid, target=wid, weight=weight, kind="cross_file"))
                edges_added += 1
            if graph._edges.get(wid, {}).get(lid) is None:
                graph.add_edge(Edge(source=wid, target=lid, weight=weight, kind="cross_file"))
                edges_added += 1

    return edges_added


def _load_learning_rows(
    learning_db_path: Path, agent_id: str, learning_type: str | None = None
) -> list[sqlite3.Row]:
    if not learning_db_path.exists():
        return []

    conn = sqlite3.connect(str(learning_db_path))
    conn.row_factory = sqlite3.Row
    try:
        if agent_id:
            if learning_type:
                query = (
                    "SELECT id, type, tag, error_class, prevention_rule, source_text, recurrence_count "
                    "FROM learnings WHERE status='active' "
                    "AND type=? AND (agent=? OR agent IS NULL) ORDER BY created_at"
                )
                rows = conn.execute(query, (learning_type, agent_id)).fetchall()
            else:
                query = (
                    "SELECT id, type, tag, error_class, prevention_rule, source_text, recurrence_count "
                    "FROM learnings WHERE status='active' "
                    "AND (agent=? OR agent IS NULL) ORDER BY created_at"
                )
                rows = conn.execute(query, (agent_id,)).fetchall()
        else:
            if learning_type:
                query = (
                    "SELECT id, type, tag, error_class, prevention_rule, source_text, recurrence_count "
                    "FROM learnings WHERE status='active' AND type=? ORDER BY created_at"
                )
                rows = conn.execute(query, (learning_type,)).fetchall()
            else:
                query = (
                    "SELECT id, type, tag, error_class, prevention_rule, source_text, recurrence_count "
                    "FROM learnings WHERE status='active' ORDER BY created_at"
                )
                rows = conn.execute(query).fetchall()
        return list(rows)
    finally:
        conn.close()


def _row_to_tokens(row: sqlite3.Row) -> set[str]:
    text = " ".join(
        value
        for value in (
            str(row["error_class"] or ""),
            str(row["prevention_rule"] or ""),
            str(row["tag"] or ""),
            str(row["source_text"] or ""),
        )
    )
    return {word for word in re.findall(r"[a-z0-9]{3,}", text.lower())}


def apply_correction_inhibitions(graph, learning_db_path: str | Path, agent_id: str) -> int:
    db_path = Path(learning_db_path)
    correction_rows = _load_learning_rows(db_path, agent_id, learning_type="CORRECTION")
    if not correction_rows:
        return 0

    workspace_nodes = [n for n in graph.nodes() if not n.id.startswith("learning::")]
    if not workspace_nodes:
        return 0

    edges_added = 0
    for row in correction_rows:
        learning_id = f"learning::{row['id']}"
        if graph.get_node(learning_id) is None:
            continue

        tokens = _row_to_tokens(row)
        if not tokens:
            continue

        scored_nodes = []
        for node in workspace_nodes:
            node_tokens = {word for word in re.findall(r"[a-z0-9]{3,}", node.content.lower())}
            overlap = len(tokens & node_tokens)
            if overlap <= 0:
                continue
            scored_nodes.append((overlap, node.id))

        scored_nodes.sort(reverse=True)
        recurrence = int(row["recurrence_count"] or 1)
        base_weight = -0.35 - min(0.4, recurrence * 0.03)
        for overlap, target_id in scored_nodes[:3]:
            weight = max(-1.0, base_weight - 0.03 * overlap)

            existing = graph._edges.get(learning_id, {}).get(target_id)
            if existing is None:
                graph.add_edge(
                    Edge(
                        source=learning_id,
                        target=target_id,
                        weight=weight,
                        kind="inhibitory",
                        metadata={
                            "source": "correction_learning",
                            "learning_id": row["id"],
                            "agent": agent_id,
                            "recurrence_count": recurrence,
                        },
                    )
                )
                edges_added += 1
            else:
                existing.weight = min(existing.weight, weight)
                existing.kind = "inhibitory"

    return edges_added


def connect_learnings(state_path: str, top_k: int = 3, min_sim: float = 0.3):
    graph, index, meta = load_state(state_path)
    edges_added = connect_learning_nodes(graph=graph, index=index, top_k=top_k, min_sim=min_sim)

    save_state(
        graph=graph,
        index=index,
        path=state_path,
        embedder_name=meta.get("embedder_name", "openai-text-embedding-3-small"),
        embedder_dim=meta.get("embedder_dim", 1536),
        meta=meta,
    )
    return edges_added


def main():
    parser = argparse.ArgumentParser(
        description="Connect learning nodes into workspace neighborhoods for one or more adapter states"
    )
    parser.add_argument("--agent", choices=sorted(AGENT_STATES.keys()), help="Connect learning nodes for one agent state")
    parser.add_argument("--state", help="Connect learning nodes for this explicit state.json path")
    parser.add_argument("--top-k", type=int, default=3, help="Number of workspace matches per learning node")
    parser.add_argument("--min-sim", type=float, default=0.3, help="Minimum cosine similarity threshold")
    args = parser.parse_args()

    if args.agent and args.state:
        raise SystemExit("--agent and --state are mutually exclusive")

    if args.top_k <= 0:
        raise SystemExit("--top-k must be >= 1")
    if args.min_sim < 0:
        raise SystemExit("--min-sim must be >= 0")

    if args.state:
        state_paths = [Path(args.state)]
    elif args.agent:
        state_paths = [AGENT_STATES[args.agent]]
    else:
        state_paths = list(AGENT_STATES.values())

    for state_path in state_paths:
        label = str(state_path)
        if state_path.is_absolute():
            label = state_path.name
            for agent, path in AGENT_STATES.items():
                if path == state_path:
                    label = agent.upper()
                    break
        print(f"\n=== {label} ===")

        graph, _, meta = load_state(str(state_path))
        learning_count = sum(1 for n in graph.nodes() if n.id.startswith("learning::"))
        orphans_before = sum(
            1
            for n in graph.nodes()
            if not any(n.id in edges for edges in graph._edges.values()) and n.id not in graph._edges
        )
        print(f"  Before: {graph.node_count()} nodes, {graph.edge_count()} edges, {learning_count} learning nodes, {orphans_before} orphans")

        t0 = time.time()
        edges_added = connect_learnings(str(state_path), top_k=args.top_k, min_sim=args.min_sim)
        elapsed = time.time() - t0

        graph2, _, _ = load_state(str(state_path))
        orphans_after = sum(
            1
            for n in graph2.nodes()
            if not any(n.id in edges for edges in graph2._edges.values()) and n.id not in graph2._edges
        )
        h = measure_health(graph2)
        print(f"  After: {graph2.node_count()} nodes, {graph2.edge_count()} edges, {orphans_after} orphans")
        print(f"  Added: {edges_added} edges in {elapsed:.1f}s")
        print(
            f"  Health: dormant={h.dormant_pct:.0%} habitual={h.habitual_pct:.0%} reflex={h.reflex_pct:.0%} cross-file={h.cross_file_edge_pct:.0%}"
        )


if __name__ == "__main__":
    main()
