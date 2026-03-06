#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from crabpath import HashEmbedder, apply_outcome, inject_correction, load_state, save_state


CORRECTION_LOG = "injected_corrections.jsonl"


def _state_dir(state_path: Path) -> Path:
    return state_path.parent


def _fire_log_path(state_path: Path) -> Path:
    return _state_dir(state_path) / "fired_log.jsonl"


def _correction_log_path(state_path: Path) -> Path:
    return _state_dir(state_path) / CORRECTION_LOG


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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply delayed correction against last chat-fired nodes")
    parser.add_argument("--state", required=True, help="Path to state.json")
    parser.add_argument("--chat-id", required=True, help="Conversation id used by the query")
    parser.add_argument("--outcome", type=float, default=-1.0, help="Learn outcome")
    parser.add_argument("--lookback", type=int, default=1, help="How many recent queries to penalize")
    parser.add_argument("--content", help="Optional CORRECTION text to inject")
    return parser.parse_args()


def _read_recent_fired_ids(path: Path, chat_id: str, lookback: int) -> list[str]:
    rows = []
    for entry in _read_jsonl(path):
        if entry.get("chat_id") != chat_id:
            continue
        ts = entry.get("ts")
        if isinstance(ts, (int, float)):
            rows.append((ts, entry))

    rows.sort(key=lambda item: item[0], reverse=True)
    seen: set[str] = set()
    fired: list[str] = []
    for _, entry in rows[:lookback]:
        for node_id in entry.get("fired_nodes", []) if isinstance(entry.get("fired_nodes"), list) else []:
            if isinstance(node_id, str) and node_id not in seen:
                seen.add(node_id)
                fired.append(node_id)
    return fired


def _read_injected_hashes(path: Path) -> dict[str, str]:
    emitted: dict[str, str] = {}
    for row in _read_jsonl(path):
        content_hash = row.get("content_hash")
        node_id = row.get("node_id")
        if isinstance(content_hash, str) and isinstance(node_id, str):
            emitted[content_hash] = node_id
    return emitted


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _correction_node_id(content: str) -> str:
    return f"correction::{_content_hash(content)[:12]}"


def main() -> None:
    args = _parse_args()
    if args.lookback <= 0:
        raise SystemExit("--lookback must be >= 1")

    state_path = Path(args.state).expanduser()
    if not state_path.exists():
        raise SystemExit(f"state file not found: {state_path}")

    fired_ids = _read_recent_fired_ids(_fire_log_path(state_path), args.chat_id, args.lookback)

    graph, index, meta = load_state(str(state_path))
    edges_updated = 0
    if fired_ids:
        updates = apply_outcome(graph=graph, fired_nodes=fired_ids, outcome=args.outcome)
        edges_updated = len(updates)

    correction_injected = False
    if args.content is not None:
        content = args.content.strip()
        if content:
            correction_node_id = _correction_node_id(content)
            content_hash = _content_hash(content)
            injected = _read_injected_hashes(_correction_log_path(state_path))

            if content_hash not in injected:
                inject_correction(
                    graph=graph,
                    index=index,
                    node_id=correction_node_id,
                    content=content,
                    metadata={"source": "generic_correct"},
                    embed_fn=HashEmbedder().embed,
                )
                rows = _read_jsonl(_correction_log_path(state_path))
                rows.append(
                    {
                        "content_hash": content_hash,
                        "node_id": correction_node_id,
                        "ts": float(time.time()),
                        "chat_id": args.chat_id,
                    }
                )
                _write_jsonl(_correction_log_path(state_path), rows)
                correction_injected = True

    save_state(graph=graph, index=index, path=str(state_path), meta=meta)

    print(
        json.dumps(
            {
                "fired_ids_penalized": fired_ids,
                "edges_updated": edges_updated,
                "correction_injected": correction_injected,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
