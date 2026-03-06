"""Append-only JSONL journal for query/learn/health/replay telemetry."""

from __future__ import annotations

import json
import time
from pathlib import Path

DEFAULT_JOURNAL_PATH = "~/.crabpath/journal.jsonl"


def log_event(event: dict, journal_path: str | None = None) -> None:
    """log event."""
    path = Path(journal_path or DEFAULT_JOURNAL_PATH).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    event["ts"] = time.time()
    event["iso"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, default=str) + "\n")


def log_query(
    query_text: str,
    fired_ids: list[str],
    node_count: int | None = None,
    journal_path: str | None = None,
    metadata: dict[str, object] | None = None,
) -> None:
    """Log a query event to the journal."""
    resolved_node_count = node_count if node_count is not None else len(fired_ids)
    log_event(
        {
            "type": "query",
            "query": query_text,
            "fired": fired_ids,
            "fired_count": len(fired_ids),
            "node_count": resolved_node_count,
            "metadata": metadata,
        },
        journal_path,
    )


def log_learn(
    fired_ids: list[str],
    outcome: float,
    journal_path: str | None = None,
    metadata: dict[str, object] | None = None,
) -> None:
    """Log a learn event to the journal."""
    log_event(
        {
            "type": "learn",
            "fired": fired_ids,
            "outcome": outcome,
            "metadata": metadata,
        },
        journal_path,
    )


def log_replay(queries_replayed: int, edges_reinforced: int, cross_file_created: int, journal_path: str | None = None) -> None:
    """Log replay statistics to the journal."""
    log_event(
        {
            "type": "replay",
            "queries_replayed": queries_replayed,
            "edges_reinforced": edges_reinforced,
            "cross_file_created": cross_file_created,
        },
        journal_path,
    )


def log_health(health_data: dict, journal_path: str | None = None) -> None:
    """Log graph health metrics to the journal."""
    log_event({"type": "health", **health_data}, journal_path)


def read_journal(journal_path: str | None = None, last_n: int | None = None) -> list[dict]:
    """read journal."""
    path = Path(journal_path or DEFAULT_JOURNAL_PATH).expanduser()
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    entries = [json.loads(line) for line in lines if line.strip()]
    if last_n is not None:
        entries = entries[-last_n:]
    return entries


def journal_stats(journal_path: str | None = None) -> dict:
    """journal stats."""
    entries = read_journal(journal_path)
    queries = [e for e in entries if e.get("type") == "query"]
    learns = [e for e in entries if e.get("type") == "learn"]
    positive = [e for e in learns if e.get("outcome", 0) > 0]
    negative = [e for e in learns if e.get("outcome", 0) < 0]
    return {
        "total_entries": len(entries),
        "queries": len(queries),
        "learns": len(learns),
        "positive_outcomes": len(positive),
        "negative_outcomes": len(negative),
        "avg_fired_per_query": sum(e.get("fired_count", 0) for e in queries) / max(len(queries), 1),
    }
