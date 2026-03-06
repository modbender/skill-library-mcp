#!/usr/bin/env python3
"""Guardian Layer 2 runtime behavioral monitor."""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

CREDENTIAL_PATTERNS: list[tuple[str, str]] = [
    ("aws_access_key", r"AKIA[0-9A-Z]{16}"),
    ("github_token", r"ghp_[A-Za-z0-9]{36,}"),
    ("generic_api_key", r"(?i)(api[_-]?key|token|secret|password)\s*[=:]\s*[^\s\"']{6,}"),
    ("bearer_token", r"(?i)bearer\s+[A-Za-z0-9._-]{12,}"),
    ("private_key", r"-----BEGIN (?:RSA|EC|OPENSSH|DSA|PGP) PRIVATE KEY-----"),
]

EXFIL_PATTERNS: list[tuple[str, str]] = [
    ("credit_card_like", r"\b(?:\d[ -]*?){13,16}\b"),
    ("ssn_like", r"\b\d{3}-\d{2}-\d{4}\b"),
    ("access_token", r"(?i)(access[_-]?token|refresh[_-]?token)\s*[=:]\s*[^\s\"']{8,}"),
    ("private_key", r"-----BEGIN (?:RSA|EC|OPENSSH|DSA|PGP) PRIVATE KEY-----"),
]

URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
TOOL_SEQUENCE = ["read_file", "web_fetch", "send_email"]
TOOL_TABLE_HINTS = ("tool", "call", "action", "event")
MESSAGE_TABLE_HINTS = ("message", "conversation", "chat", "session")
EXCLUDED_TABLES = {"runtime_events", "egress_events", "threats", "metrics", "scan_bookmarks", "sqlite_sequence"}


def resolve_db_path() -> Path:
    workspace = Path(os.environ.get("GUARDIAN_WORKSPACE", os.getcwd())).expanduser().resolve()
    return workspace / "guardian.db"


def connect_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_runtime_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS runtime_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            detail TEXT NOT NULL,
            raw_context TEXT
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_runtime_events_time ON runtime_events(timestamp DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_runtime_events_session ON runtime_events(session_id)")
    conn.commit()


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [str(row[1]) for row in rows]


def list_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    return [str(row[0]) for row in rows]


def pick(columns: Iterable[str], candidates: Iterable[str]) -> Optional[str]:
    lowered = {c.lower(): c for c in columns}
    for name in candidates:
        if name.lower() in lowered:
            return lowered[name.lower()]
    return None


def load_message_urls(conn: sqlite3.Connection, session_filter: Optional[str] = None) -> dict[str, set[str]]:
    by_session: dict[str, set[str]] = defaultdict(set)
    for table in list_tables(conn):
        t = table.lower()
        if table in EXCLUDED_TABLES:
            continue
        if not any(h in t for h in MESSAGE_TABLE_HINTS):
            continue
        cols = table_columns(conn, table)
        session_col = pick(cols, ("session_id", "session", "conversation_id", "thread_id", "chat_id"))
        role_col = pick(cols, ("role", "sender_role", "author_role", "actor"))
        content_col = pick(cols, ("content", "message", "text", "body", "payload"))
        if not session_col or not content_col:
            continue

        sql = f"SELECT {session_col} AS session_id, {content_col} AS content"
        params: list[Any] = []
        if role_col:
            sql += f", {role_col} AS role"
        else:
            sql += ", '' AS role"
        sql += f" FROM {table}"

        where = []
        if role_col:
            where.append(f"lower({role_col})='user'")
        if session_filter:
            where.append(f"{session_col}=?")
            params.append(session_filter)
        if where:
            sql += " WHERE " + " AND ".join(where)

        for row in conn.execute(sql, tuple(params)).fetchall():
            session_id = str(row["session_id"] or "unknown")
            content = str(row["content"] or "")
            for url in URL_RE.findall(content):
                by_session[session_id].add(url.lower())
    return by_session


def load_tool_records(conn: sqlite3.Connection, session_filter: Optional[str] = None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for table in list_tables(conn):
        t = table.lower()
        if table in EXCLUDED_TABLES:
            continue
        if not any(h in t for h in TOOL_TABLE_HINTS):
            continue

        cols = table_columns(conn, table)
        tool_col = pick(cols, ("tool", "tool_name", "name", "action", "operation"))
        if not tool_col:
            continue
        session_col = pick(cols, ("session_id", "session", "conversation_id", "thread_id", "chat_id"))
        ts_col = pick(cols, ("timestamp", "created_at", "event_at", "detected_at", "time"))
        args_col = pick(cols, ("args", "arguments", "input", "request", "payload", "command", "body"))
        result_col = pick(cols, ("result", "output", "response", "content", "stdout", "return_value"))
        url_col = pick(cols, ("url", "target_url", "destination", "endpoint"))

        select_parts = [
            f"{session_col} AS session_id" if session_col else "'unknown' AS session_id",
            f"{ts_col} AS timestamp" if ts_col else "'' AS timestamp",
            f"{tool_col} AS tool",
            f"{args_col} AS args_text" if args_col else "'' AS args_text",
            f"{result_col} AS result_text" if result_col else "'' AS result_text",
            f"{url_col} AS url" if url_col else "'' AS url",
        ]

        sql = f"SELECT {', '.join(select_parts)} FROM {table}"
        params: list[Any] = []
        if session_filter and session_col:
            sql += f" WHERE {session_col}=?"
            params.append(session_filter)

        for row in conn.execute(sql, tuple(params)).fetchall():
            tool = str(row["tool"] or "").strip()
            if not tool:
                continue
            record = {
                "session_id": str(row["session_id"] or "unknown"),
                "timestamp": str(row["timestamp"] or ""),
                "tool": tool,
                "args_text": str(row["args_text"] or ""),
                "result_text": str(row["result_text"] or ""),
                "url": str(row["url"] or ""),
                "table": table,
            }
            records.append(record)
    return records


def parse_ts(value: str) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return datetime.now(timezone.utc)


def _find_pattern_hits(text: str, patterns: list[tuple[str, str]]) -> list[str]:
    hits: list[str] = []
    for key, pattern in patterns:
        try:
            if re.search(pattern, text):
                hits.append(key)
        except re.error:
            continue
    return hits


def has_sequence(tools: list[str], sequence: list[str]) -> bool:
    pos = 0
    lowered = [t.lower() for t in tools]
    for tool in lowered:
        if sequence[pos] in tool:
            pos += 1
            if pos == len(sequence):
                return True
    return False


def event_exists(conn: sqlite3.Connection, session_id: str, event_type: str, detail: str) -> bool:
    row = conn.execute(
        "SELECT id FROM runtime_events WHERE session_id=? AND event_type=? AND detail=? LIMIT 1",
        (session_id, event_type, detail),
    ).fetchone()
    return row is not None


def insert_event(
    conn: sqlite3.Connection,
    session_id: str,
    event_type: str,
    severity: str,
    detail: str,
    raw_context: dict[str, Any],
) -> bool:
    if event_exists(conn, session_id, event_type, detail):
        return False
    conn.execute(
        """
        INSERT INTO runtime_events (session_id, timestamp, event_type, severity, detail, raw_context)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            datetime.now(timezone.utc).isoformat(),
            event_type,
            severity,
            detail,
            json.dumps(raw_context, ensure_ascii=True),
        ),
    )
    return True


def scan_runtime(conn: sqlite3.Connection, session_filter: Optional[str] = None) -> dict[str, Any]:
    ensure_runtime_table(conn)
    records = load_tool_records(conn, session_filter=session_filter)
    user_urls = load_message_urls(conn, session_filter=session_filter)

    by_session: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rec in records:
        by_session[rec["session_id"]].append(rec)

    inserted = 0
    findings: list[dict[str, Any]] = []

    for session_id, session_rows in by_session.items():
        ordered = sorted(session_rows, key=lambda r: parse_ts(r.get("timestamp", "")).timestamp())
        tools = [str(r["tool"]) for r in ordered]

        if has_sequence(tools, TOOL_SEQUENCE):
            detail = "Unusual sequence detected: read_file -> web_fetch -> send_email"
            ctx = {"tools": tools[-20:]}
            if insert_event(conn, session_id, "unusual_tool_sequence", "high", detail, ctx):
                inserted += 1
                findings.append({"session_id": session_id, "event_type": "unusual_tool_sequence", "severity": "high", "detail": detail})

        counts: dict[str, int] = defaultdict(int)
        for t in tools:
            counts[t.lower()] += 1
        for tool, count in counts.items():
            if count > 10:
                detail = f"High-frequency tool usage: {tool} called {count} times in one session"
                ctx = {"tool": tool, "count": count}
                if insert_event(conn, session_id, "high_frequency_tool_calls", "medium", detail, ctx):
                    inserted += 1
                    findings.append({"session_id": session_id, "event_type": "high_frequency_tool_calls", "severity": "medium", "detail": detail})

        allowed_urls = user_urls.get(session_id, set())
        for rec in ordered:
            tool = str(rec["tool"]).lower()
            args_text = str(rec.get("args_text", ""))
            result_text = str(rec.get("result_text", ""))
            text_blob = f"{args_text}\n{result_text}".strip()

            if "exec" in tool:
                hits = _find_pattern_hits(text_blob, CREDENTIAL_PATTERNS)
                if hits:
                    detail = f"Credential-like values passed to exec command ({', '.join(hits[:3])})"
                    ctx = {"tool": rec["tool"], "args_preview": args_text[:260], "patterns": hits}
                    if insert_event(conn, session_id, "exec_credential_pattern", "critical", detail, ctx):
                        inserted += 1
                        findings.append({"session_id": session_id, "event_type": "exec_credential_pattern", "severity": "critical", "detail": detail})

            outbound_urls = set(URL_RE.findall(rec.get("url", "") or ""))
            outbound_urls.update(URL_RE.findall(args_text))
            if outbound_urls and allowed_urls:
                unknown = sorted({u.lower() for u in outbound_urls if u.lower() not in allowed_urls})
            else:
                unknown = sorted({u.lower() for u in outbound_urls}) if outbound_urls and not allowed_urls else []

            if unknown:
                detail = f"Outbound URL(s) not found in original user message: {', '.join(unknown[:2])}"
                ctx = {"tool": rec["tool"], "unknown_urls": unknown[:5], "known_user_urls": sorted(list(allowed_urls))[:5]}
                if insert_event(conn, session_id, "outbound_url_mismatch", "medium", detail, ctx):
                    inserted += 1
                    findings.append({"session_id": session_id, "event_type": "outbound_url_mismatch", "severity": "medium", "detail": detail})

            exfil_hits = _find_pattern_hits(result_text, EXFIL_PATTERNS)
            if exfil_hits:
                detail = f"Tool result matched exfiltration signatures ({', '.join(exfil_hits[:3])})"
                ctx = {"tool": rec["tool"], "result_preview": result_text[:260], "patterns": exfil_hits}
                if insert_event(conn, session_id, "tool_result_exfil_signature", "high", detail, ctx):
                    inserted += 1
                    findings.append({"session_id": session_id, "event_type": "tool_result_exfil_signature", "severity": "high", "detail": detail})

    conn.commit()
    return {
        "ok": True,
        "scanned_sessions": len(by_session),
        "records_scanned": len(records),
        "events_inserted": inserted,
        "events": findings,
    }


def fetch_runtime_events(conn: sqlite3.Connection, limit: int = 200, session_id: Optional[str] = None) -> list[dict[str, Any]]:
    ensure_runtime_table(conn)
    if session_id:
        rows = conn.execute(
            "SELECT * FROM runtime_events WHERE session_id=? ORDER BY timestamp DESC LIMIT ?",
            (session_id, limit),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM runtime_events ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
    return [dict(row) for row in rows]


def main() -> int:
    parser = argparse.ArgumentParser(description="Guardian runtime behavior monitor")
    parser.add_argument("--scan", action="store_true", help="Run a runtime scan")
    parser.add_argument("--session", dest="session_id", help="Scan only one session")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    db_path = resolve_db_path()
    conn = connect_db(db_path)
    try:
        if not args.scan:
            parser.print_help()
            return 1

        result = scan_runtime(conn, session_filter=args.session_id)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(
                f"Runtime scan complete: sessions={result['scanned_sessions']} "
                f"records={result['records_scanned']} events={result['events_inserted']}"
            )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
