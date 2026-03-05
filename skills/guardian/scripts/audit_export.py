#!/usr/bin/env python3
"""Guardian Layer 4 audit trail export with hash chaining."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

EXPORT_PREFIX = "guardian-audit-"


def resolve_workspace() -> Path:
    return Path(os.environ.get("GUARDIAN_WORKSPACE", os.getcwd())).expanduser().resolve()


def resolve_db_path() -> Path:
    return resolve_workspace() / "guardian.db"


def connect_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def parse_iso(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (name,),
    ).fetchone()
    return row is not None


def fetch_rows_since(conn: sqlite3.Connection, table: str, ts_col: str, since: datetime) -> list[dict[str, Any]]:
    if not table_exists(conn, table):
        return []
    rows = conn.execute(
        f"SELECT * FROM {table} WHERE {ts_col} >= ? ORDER BY {ts_col} ASC",
        (since.isoformat(),),
    ).fetchall()
    return [dict(row) for row in rows]


def export_dir(workspace: Path) -> Path:
    target = workspace / "audit_exports"
    target.mkdir(parents=True, exist_ok=True)
    return target


def list_export_files(target: Path) -> list[Path]:
    return sorted(p for p in target.glob(f"{EXPORT_PREFIX}*.json") if p.is_file())


def read_export(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compute_file_hash(path: Path) -> str:
    return sha256_text(path.read_text(encoding="utf-8"))


def previous_export_hash(target: Path) -> Optional[str]:
    files = list_export_files(target)
    if not files:
        return None
    return compute_file_hash(files[-1])


def build_export_payload(conn: sqlite3.Connection, since_days: int, prev_hash: Optional[str]) -> dict[str, Any]:
    since = datetime.now(timezone.utc) - timedelta(days=since_days)
    payload: dict[str, Any] = {
        "version": "2.3.0",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "since_days": since_days,
        "since": since.isoformat(),
        "previous_export_sha256": prev_hash,
        "records": {
            "threats": fetch_rows_since(conn, "threats", "detected_at", since),
            "runtime_events": fetch_rows_since(conn, "runtime_events", "timestamp", since),
            "egress_events": fetch_rows_since(conn, "egress_events", "timestamp", since),
            "override_events": fetch_rows_since(conn, "override_events", "event_at", since),
            "approval_requests": fetch_rows_since(conn, "approval_requests", "created_at", since),
        },
    }
    content_hash = sha256_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    payload["export_sha256"] = content_hash
    return payload


def write_export(target: Path, payload: dict[str, Any]) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    file_path = target / f"{EXPORT_PREFIX}{ts}.json"
    file_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return file_path


def verify_exports(target: Path) -> dict[str, Any]:
    files = list_export_files(target)
    if not files:
        return {"ok": True, "checked": 0, "errors": []}

    errors: list[str] = []
    prev_file_hash: Optional[str] = None

    for idx, file_path in enumerate(files):
        data = read_export(file_path)

        expected_chain = data.get("previous_export_sha256")
        if idx == 0:
            if expected_chain not in (None, ""):
                errors.append(f"{file_path.name}: first export should not declare previous hash")
        else:
            if expected_chain != prev_file_hash:
                errors.append(
                    f"{file_path.name}: previous_export_sha256 mismatch (expected {prev_file_hash}, got {expected_chain})"
                )

        export_copy = dict(data)
        stored_hash = str(export_copy.pop("export_sha256", ""))
        computed_hash = sha256_text(json.dumps(export_copy, sort_keys=True, separators=(",", ":")))
        if stored_hash != computed_hash:
            errors.append(f"{file_path.name}: export_sha256 mismatch")

        prev_file_hash = compute_file_hash(file_path)

    return {"ok": len(errors) == 0, "checked": len(files), "errors": errors}


def run_export(since_days: int) -> dict[str, Any]:
    workspace = resolve_workspace()
    db_path = resolve_db_path()
    target = export_dir(workspace)

    conn = connect_db(db_path)
    try:
        prev_hash = previous_export_hash(target)
        payload = build_export_payload(conn, since_days=since_days, prev_hash=prev_hash)
        out = write_export(target, payload)
        return {
            "ok": True,
            "export_path": str(out),
            "previous_export_sha256": prev_hash,
            "export_sha256": payload.get("export_sha256"),
            "record_counts": {k: len(v) for k, v in payload["records"].items()},
        }
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Guardian audit export")
    parser.add_argument("--export", action="store_true", help="Write a new chained audit export")
    parser.add_argument("--since", type=int, default=1, help="Export trailing N days (default: 1)")
    parser.add_argument("--verify", action="store_true", help="Verify audit export chain integrity")
    args = parser.parse_args()

    workspace = resolve_workspace()
    target = export_dir(workspace)

    output: dict[str, Any] = {"ok": True}
    if args.export:
        output["export"] = run_export(since_days=max(1, int(args.since)))
    if args.verify:
        output["verify"] = verify_exports(target)
        output["ok"] = output["ok"] and bool(output["verify"]["ok"])

    if not args.export and not args.verify:
        parser.print_help()
        return 1

    print(json.dumps(output, indent=2))
    return 0 if output.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
