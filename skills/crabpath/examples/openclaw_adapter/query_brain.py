#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from openai import OpenAI
from crabpath import TraversalConfig, load_state, traverse


EMBED_MODEL = "text-embedding-3-small"
FIRED_LOG_TTL_SECONDS = 7 * 24 * 60 * 60


def _fired_log_path(state_path: Path) -> Path:
    return state_path.parent / "fired_log.jsonl"


def _read_fired_log(log_path: Path) -> list[dict[str, object]]:
    if not log_path.exists():
        return []

    entries = []
    for raw_line in log_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        entries.append(record)
    return entries


def _write_fired_log(log_path: Path, entries: list[dict[str, object]]) -> None:
    tmp = log_path.with_name(f"{log_path.name}.tmp")
    payload = "\n".join(json.dumps(entry) for entry in entries)
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(log_path)


def _prune_fired_log(entries: list[dict[str, object]], now: float) -> list[dict[str, object]]:
    cutoff = now - FIRED_LOG_TTL_SECONDS
    output = []
    for entry in entries:
        ts = entry.get("ts")
        if isinstance(ts, (int, float)) and ts >= cutoff:
            output.append(entry)
    return output


def _append_fired_log(log_path: Path, entry: dict[str, object], now: float | None = None) -> None:
    entries = _read_fired_log(log_path)
    entries.append(entry)
    entries = _prune_fired_log(entries, now if now is not None else time.time())
    _write_fired_log(log_path, entries)


def require_api_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(
            "This script must run inside the agent framework exec environment where OPENAI_API_KEY is injected."
        )
    return api_key


def embed_query(client: OpenAI, query: str) -> list[float]:
    response = client.embeddings.create(model=EMBED_MODEL, input=[query])
    return response.data[0].embedding


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Query a CrabPath state.json with OpenAI embeddings"
    )
    parser.add_argument("state_path", help="Path to state.json")
    parser.add_argument("query", nargs="+", help="Query text")
    parser.add_argument("--chat-id", help="Conversation id to persist fired nodes")
    parser.add_argument("--top", type=int, default=4, help="Top-k vector matches")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args(argv)

    query_text = " ".join(args.query).strip()
    state_path = Path(args.state_path)
    if not state_path.exists():
        raise SystemExit(f"state file not found: {state_path}")
    if args.top <= 0:
        raise SystemExit("--top must be >= 1")

    api_key = require_api_key()
    client = OpenAI(api_key=api_key)

    graph, index, meta = load_state(str(state_path))
    query_vector = embed_query(client, query_text)

    expected_dim = meta.get("embedder_dim")
    if isinstance(expected_dim, int) and len(query_vector) != expected_dim:
        raise SystemExit(
            "Embedding dimension mismatch: "
            f"query={len(query_vector)} index={expected_dim}. "
            "Rebuild state.json with text-embedding-3-small."
        )

    seeds = index.search(query_vector, top_k=args.top)
    result = traverse(graph=graph, seeds=seeds, query_text=query_text, config=TraversalConfig(max_context_chars=20000))

    if args.chat_id:
        log_entry = {
            "chat_id": args.chat_id,
            "query": query_text,
            "fired_nodes": result.fired,
            "ts": time.time(),
        }
        _append_fired_log(_fired_log_path(state_path), log_entry)

    output = {
        "state": str(state_path),
        "query": query_text,
        "seeds": seeds,
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
