#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from collections.abc import Callable
from typing import Any
import time

from crabpath import HashEmbedder, apply_outcome, inject_correction, load_state, save_state


FIRE_LOG = "fired_log.jsonl"
INJECTED_CORRECTIONS_LOG = "injected_corrections.jsonl"
EMBED_MODEL = "text-embedding-3-small"


def _state_dir(state_path: Path) -> Path:
    return state_path.parent


def _fire_log_path(state_path: Path) -> Path:
    return _state_dir(state_path) / FIRE_LOG


def _injected_log_path(state_path: Path) -> Path:
    return _state_dir(state_path) / INJECTED_CORRECTIONS_LOG


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
    payload = "\n".join(json.dumps(row) for row in rows)
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(path)


def _require_api_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(
            "This script must run inside the agent framework exec environment where OPENAI_API_KEY is injected."
        )
    return api_key


def _resolve_embed_fn(meta: dict[str, object]) -> Callable[[str], list[float]]:
    embedder_name = meta.get("embedder_name")
    if embedder_name == "hash-v1":
        return HashEmbedder().embed

    if embedder_name in {"text-embedding-3-small", "openai-text-embedding-3-small"}:
        from openai import OpenAI

        api_key = _require_api_key()
        client = OpenAI(api_key=api_key)

        def _embed(content: str) -> list[float]:
            response = client.embeddings.create(model=EMBED_MODEL, input=[content])
            return list(response.data[0].embedding)

        return _embed

    return HashEmbedder().embed


def _unique_fired_nodes(entries: list[dict[str, object]]) -> list[str]:
    seen: set[str] = set()
    fired: list[str] = []
    for entry in entries:
        for node_id in entry.get("fired_nodes", []) if isinstance(entry.get("fired_nodes"), list) else []:
            if isinstance(node_id, str) and node_id not in seen:
                seen.add(node_id)
                fired.append(node_id)
    return fired


def _load_recent_fired_nodes(state_path: Path, chat_id: str, lookback: int) -> list[str]:
    entries = _read_jsonl(_fire_log_path(state_path))
    candidates = []
    for entry in entries:
        if entry.get("chat_id") != chat_id:
            continue
        ts = entry.get("ts")
        if not isinstance(ts, (int, float)):
            continue
        candidates.append((ts, entry))

    candidates.sort(key=lambda item: item[0], reverse=True)
    selected = [entry for _, entry in candidates[:lookback]]
    return _unique_fired_nodes(selected)


def _read_injected_correction_hashes(state_path: Path) -> dict[str, str]:
    by_hash: dict[str, str] = {}
    for entry in _read_jsonl(_injected_log_path(state_path)):
        content_hash = entry.get("content_hash")
        node_id = entry.get("node_id")
        if isinstance(content_hash, str) and isinstance(node_id, str):
            by_hash[content_hash] = node_id
    return by_hash


def _append_injected_correction(state_path: Path, content_hash: str, node_id: str, chat_id: str) -> None:
    rows = _read_jsonl(_injected_log_path(state_path))
    rows.append(
        {
            "content_hash": content_hash,
            "node_id": node_id,
            "chat_id": chat_id,
            "ts": time.time(),
        }
    )
    _write_jsonl(_injected_log_path(state_path), rows)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Learn from a correction linked to chat-id fired nodes")
    parser.add_argument("--state", required=True, help="Path to state.json")
    parser.add_argument("--chat-id", required=True, help="Conversation id used during query")
    parser.add_argument("--outcome", type=float, default=-1.0, help="Learn outcome value")
    parser.add_argument("--lookback", type=int, default=1, help="Number of recent queries to penalize")
    parser.add_argument("--content", help="Optional CORRECTION text to inject")
    return parser.parse_args(argv)


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _correction_node_id(content: str) -> str:
    return f"correction::{_content_hash(content)[:12]}"


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    if args.lookback <= 0:
        raise SystemExit("--lookback must be >= 1")

    state_path = Path(args.state).expanduser()
    if not state_path.exists():
        raise SystemExit(f"state file not found: {state_path}")

    fired_ids = _load_recent_fired_nodes(state_path, args.chat_id, args.lookback)
    edges_updated = 0
    graph = None
    index = None
    meta: dict[str, Any] = {}

    if fired_ids:
        graph, index, meta = load_state(str(state_path))
        updates = apply_outcome(graph=graph, fired_nodes=fired_ids, outcome=args.outcome)
        edges_updated = len(updates)
        save_state(graph=graph, index=index, path=str(state_path), meta=meta)

    correction_injected = False
    if args.content is not None:
        content = args.content.strip()
        if content:
            if graph is None or index is None:
                graph, index, meta = load_state(str(state_path))

            embed_fn = _resolve_embed_fn(meta)
            content_hash = _content_hash(content)
            existing = _read_injected_correction_hashes(state_path)
            if content_hash not in existing:
                node_id = _correction_node_id(content)
                inject_correction(
                    graph=graph,
                    index=index,
                    node_id=node_id,
                    content=content,
                    metadata={"source": "learn_correction", "chat_id": args.chat_id},
                    embed_fn=embed_fn,
                )
                _append_injected_correction(state_path, content_hash, node_id, args.chat_id)
                save_state(graph=graph, index=index, path=str(state_path), meta=meta)
                correction_injected = True

    summary = {
        "fired_ids_penalized": fired_ids,
        "edges_updated": edges_updated,
        "correction_injected": correction_injected,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
