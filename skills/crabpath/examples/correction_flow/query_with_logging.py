#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from crabpath import HashEmbedder, load_state, traverse


FIRE_LOG_TTL_SECONDS = 7 * 24 * 60 * 60


def _fired_log_path(state_path: Path) -> Path:
    return state_path.parent / "fired_log.jsonl"


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []

    rows: list[dict[str, object]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    tmp.replace(path)


def _prune(rows: list[dict[str, object]], now: float) -> list[dict[str, object]]:
    cutoff = now - FIRE_LOG_TTL_SECONDS
    return [row for row in rows if isinstance(row.get("ts"), (int, float)) and row["ts"] >= cutoff]


def _append_fired_log(state_path: Path, entry: dict[str, object]) -> None:
    path = _fired_log_path(state_path)
    rows = _read_jsonl(path)
    rows.append(entry)
    rows = _prune(rows, float(time.time()))
    _write_jsonl(path, rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Query CrabPath state.json with hash embeddings and log fired nodes")
    parser.add_argument("state_path", help="Path to state.json")
    parser.add_argument("query", nargs="+", help="Query text")
    parser.add_argument("--chat-id", help="Conversation id to persist fired nodes")
    parser.add_argument("--top", type=int, default=4, help="Top-k vector matches")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    state_path = Path(args.state_path)
    if not state_path.exists():
        raise SystemExit(f"state file not found: {state_path}")
    if args.top <= 0:
        raise SystemExit("--top must be >= 1")

    graph, index, meta = load_state(str(state_path))
    embedder = HashEmbedder()
    query_text = " ".join(args.query).strip()
    query_vector = embedder.embed(query_text)
    expected_dim = meta.get("embedder_dim")
    if isinstance(expected_dim, int) and len(query_vector) != expected_dim:
        raise SystemExit("Embedding dimension mismatch: rebuild state with hash embeddings")

    seeds = index.search(query_vector, top_k=args.top)
    result = traverse(graph=graph, seeds=seeds, query_text=query_text)

    if args.chat_id:
        _append_fired_log(
            state_path,
            {
                "chat_id": args.chat_id,
                "query": query_text,
                "fired_nodes": result.fired,
                "ts": float(time.time()),
            },
        )

    output = {
        "state": str(state_path),
        "query": query_text,
        "fired_nodes": result.fired,
        "context": result.context,
    }

    if args.json:
        print(json.dumps(output, indent=2))
        return

    print("Fired nodes:")
    for node_id in result.fired:
        print(f"- {node_id}")
    print("Context:")
    print(result.context or "(no context)")


if __name__ == "__main__":
    main()
