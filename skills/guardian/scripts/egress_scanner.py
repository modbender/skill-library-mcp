#!/usr/bin/env python3
"""Guardian Layer 3 egress scanner."""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

SENSITIVE_PATTERNS: list[tuple[str, str]] = [
    ("aws_access_key", r"AKIA[0-9A-Z]{16}"),
    ("github_token", r"ghp_[A-Za-z0-9]{36,}"),
    ("private_key", r"-----BEGIN (?:RSA|EC|OPENSSH|DSA|PGP) PRIVATE KEY-----"),
    ("ssn_like", r"\b\d{3}-\d{2}-\d{4}\b"),
    ("email_address", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    ("password_assignment", r"(?i)password\s*[=:]\s*[^\s\"']{6,}"),
    ("bearer_token", r"(?i)bearer\s+[A-Za-z0-9._-]{12,}"),
]

TOOL_TABLE_HINTS = ("tool", "call", "action", "event")
EXCLUDED_TABLES = {"runtime_events", "egress_events", "threats", "metrics", "scan_bookmarks", "sqlite_sequence"}


def resolve_workspace() -> Path:
    return Path(os.environ.get("GUARDIAN_WORKSPACE", os.getcwd())).expanduser().resolve()


def resolve_db_path() -> Path:
    return resolve_workspace() / "guardian.db"


def connect_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_egress_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS egress_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            tool TEXT NOT NULL,
            destination TEXT,
            severity TEXT NOT NULL,
            flagged_pattern TEXT NOT NULL,
            content_preview TEXT
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_egress_events_time ON egress_events(timestamp DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_egress_events_tool ON egress_events(tool)")
    conn.commit()


def list_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    return [str(r[0]) for r in rows]


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [str(row[1]) for row in rows]


def pick(columns: Iterable[str], candidates: Iterable[str]) -> Optional[str]:
    lowered = {c.lower(): c for c in columns}
    for name in candidates:
        if name.lower() in lowered:
            return lowered[name.lower()]
    return None


def parse_iso(value: str) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return datetime.now(timezone.utc)


def pattern_hits(text: str) -> list[str]:
    hits: list[str] = []
    for key, pat in SENSITIVE_PATTERNS:
        try:
            if re.search(pat, text):
                hits.append(key)
        except re.error:
            continue
    return hits


def load_tool_records(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
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
        ts_col = pick(cols, ("timestamp", "created_at", "event_at", "detected_at", "time"))
        args_col = pick(cols, ("args", "arguments", "input", "request", "payload", "command", "body"))
        result_col = pick(cols, ("result", "output", "response", "content", "stdout", "return_value"))
        url_col = pick(cols, ("url", "target_url", "destination", "endpoint"))
        method_col = pick(cols, ("method", "http_method", "verb"))
        path_col = pick(cols, ("path", "file_path", "filepath", "target_path"))

        select_parts = [
            f"{tool_col} AS tool",
            f"{ts_col} AS timestamp" if ts_col else "'' AS timestamp",
            f"{args_col} AS args_text" if args_col else "'' AS args_text",
            f"{result_col} AS result_text" if result_col else "'' AS result_text",
            f"{url_col} AS url" if url_col else "'' AS url",
            f"{method_col} AS method" if method_col else "'' AS method",
            f"{path_col} AS path" if path_col else "'' AS path",
        ]
        sql = f"SELECT {', '.join(select_parts)} FROM {table}"
        for row in conn.execute(sql).fetchall():
            tool = str(row["tool"] or "").strip()
            if not tool:
                continue
            rows.append(
                {
                    "tool": tool,
                    "timestamp": str(row["timestamp"] or ""),
                    "args_text": str(row["args_text"] or ""),
                    "result_text": str(row["result_text"] or ""),
                    "url": str(row["url"] or ""),
                    "method": str(row["method"] or ""),
                    "path": str(row["path"] or ""),
                    "table": table,
                }
            )
    return rows


def event_exists(conn: sqlite3.Connection, tool: str, destination: str, pattern: str, preview: str) -> bool:
    row = conn.execute(
        "SELECT id FROM egress_events WHERE tool=? AND destination=? AND flagged_pattern=? AND content_preview=? LIMIT 1",
        (tool, destination, pattern, preview),
    ).fetchone()
    return row is not None


def insert_event(
    conn: sqlite3.Connection,
    tool: str,
    destination: str,
    severity: str,
    flagged_pattern: str,
    content_preview: str,
) -> bool:
    if event_exists(conn, tool, destination, flagged_pattern, content_preview):
        return False
    conn.execute(
        """
        INSERT INTO egress_events (timestamp, tool, destination, severity, flagged_pattern, content_preview)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            tool,
            destination,
            severity,
            flagged_pattern,
            content_preview[:400],
        ),
    )
    return True


def _is_inside_workspace(path_text: str, workspace: Path) -> bool:
    if not path_text:
        return True
    p = Path(path_text).expanduser()
    try:
        resolved = p.resolve()
    except OSError:
        return False
    try:
        return resolved.is_relative_to(workspace)
    except AttributeError:
        # Python <3.9 compatibility fallback
        return str(resolved).startswith(str(workspace))


def scan_egress(conn: sqlite3.Connection, since_hours: Optional[int] = None) -> dict[str, Any]:
    ensure_egress_table(conn)
    workspace = resolve_workspace()
    records = load_tool_records(conn)

    cutoff = None
    if since_hours is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)

    inserted = 0
    findings: list[dict[str, Any]] = []

    for rec in records:
        ts = parse_iso(rec.get("timestamp", ""))
        if cutoff and ts < cutoff:
            continue

        tool = str(rec.get("tool", "")).lower()
        args_text = str(rec.get("args_text", ""))
        result_text = str(rec.get("result_text", ""))
        method = str(rec.get("method", "")).upper()
        url = str(rec.get("url", ""))
        path = str(rec.get("path", ""))
        blob = f"{args_text}\n{result_text}".strip()
        destination = url or path or "unknown"

        # Email sends with sensitive payload
        if "email" in tool and ("send" in tool or tool == "email"):
            hits = pattern_hits(blob)
            if hits:
                pattern_name = ",".join(hits[:3])
                preview = blob[:300]
                if insert_event(conn, rec["tool"], destination, "high", pattern_name, preview):
                    inserted += 1
                    findings.append({"tool": rec["tool"], "severity": "high", "flagged_pattern": pattern_name, "destination": destination})

        # Exec commands with common exfil binaries
        if "exec" in tool:
            cmd = args_text.lower()
            if any(x in cmd for x in ("curl ", "wget ", " nc ", "netcat", "ssh ")):
                hits = pattern_hits(blob)
                severity = "critical" if hits else "high"
                pattern_name = ",".join(hits[:2]) if hits else "suspicious_egress_command"
                preview = args_text[:300]
                if insert_event(conn, rec["tool"], destination, severity, pattern_name, preview):
                    inserted += 1
                    findings.append({"tool": rec["tool"], "severity": severity, "flagged_pattern": pattern_name, "destination": destination})

        # web_fetch POST body inspection
        if ("web_fetch" in tool or "http" in tool or "fetch" in tool) and method == "POST":
            hits = pattern_hits(blob)
            if hits:
                pattern_name = ",".join(hits[:3])
                preview = blob[:300]
                if insert_event(conn, rec["tool"], destination, "high", pattern_name, preview):
                    inserted += 1
                    findings.append({"tool": rec["tool"], "severity": "high", "flagged_pattern": pattern_name, "destination": destination})

        # File writes outside workspace
        if any(x in tool for x in ("write", "save", "append")) and "file" in tool:
            candidate_path = path
            if not candidate_path:
                m = re.search(r"(?:path|file|target)\s*[=:]\s*([^\s,;]+)", args_text)
                if m:
                    candidate_path = m.group(1).strip("'\"")
            if candidate_path and not _is_inside_workspace(candidate_path, workspace):
                preview = f"write target={candidate_path} args={args_text[:180]}"
                if insert_event(conn, rec["tool"], candidate_path, "medium", "write_outside_workspace", preview):
                    inserted += 1
                    findings.append({"tool": rec["tool"], "severity": "medium", "flagged_pattern": "write_outside_workspace", "destination": candidate_path})

    conn.commit()
    return {
        "ok": True,
        "records_scanned": len(records),
        "events_inserted": inserted,
        "events": findings,
    }


def fetch_egress_events(conn: sqlite3.Connection, limit: int = 200) -> list[dict[str, Any]]:
    ensure_egress_table(conn)
    rows = conn.execute("SELECT * FROM egress_events ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
    return [dict(row) for row in rows]


def main() -> int:
    parser = argparse.ArgumentParser(description="Guardian egress scanner")
    parser.add_argument("--scan", action="store_true", help="Run egress scan")
    parser.add_argument("--since", type=int, help="Only inspect records from the last N hours")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if not args.scan:
        parser.print_help()
        return 1

    conn = connect_db(resolve_db_path())
    try:
        result = scan_egress(conn, since_hours=args.since)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            since = f" since={args.since}h" if args.since is not None else ""
            print(
                f"Egress scan complete:{since} records={result['records_scanned']} "
                f"events={result['events_inserted']}"
            )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
