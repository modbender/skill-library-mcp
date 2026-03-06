#!/usr/bin/env python3
"""
export_data.py — Data export and backup utility.

Export all SQLite data + redacted config as JSON or CSV.
Import from a previous backup. GDPR-friendly data portability.

Usage:
  python3 export_data.py --export --output ~/proactive-backup/ --format json
  python3 export_data.py --export --format csv
  python3 export_data.py --import ~/proactive-backup/
  python3 export_data.py --list-tables
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": "Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"
DB_FILE = SKILL_DIR / "memory.db"

SECRET_KEYS = {"bot_token", "chat_id", "clawhub_token", "password",
               "api_key_env", "token"}


def redact_config(config: dict) -> dict:
    """Remove secrets from config for safe export."""
    redacted = {}
    for key, val in config.items():
        if isinstance(val, dict):
            redacted[key] = redact_config(val)
        elif key in SECRET_KEYS and val:
            redacted[key] = "***REDACTED***"
        else:
            redacted[key] = val
    return redacted


def list_tables() -> list:
    """List all tables in memory.db."""
    if not DB_FILE.exists():
        return []
    conn = sqlite3.connect(str(DB_FILE))
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    result = []
    for t in tables:
        name = t[0]
        count = conn.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
        result.append({"table": name, "rows": count})
    conn.close()
    return result


def export_table_json(conn: sqlite3.Connection, table_name: str) -> list:
    """Export a single table as list of dicts."""
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f"SELECT * FROM [{table_name}]").fetchall()
    return [dict(r) for r in rows]


def export_table_csv(conn: sqlite3.Connection, table_name: str) -> str:
    """Export a single table as CSV string."""
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f"SELECT * FROM [{table_name}]").fetchall()
    if not rows:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    for r in rows:
        writer.writerow(dict(r))
    return output.getvalue()


def export_all(output_dir: str, fmt: str = "json") -> dict:
    """Export all tables + redacted config."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    manifest = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "format": fmt,
        "tables": {},
    }

    # Export config (redacted)
    if CONFIG_FILE.exists():
        config = json.loads(CONFIG_FILE.read_text())
        redacted = redact_config(config)
        (output_path / "config.json").write_text(json.dumps(redacted, indent=2))
        manifest["config_exported"] = True

    # Export DB tables
    if DB_FILE.exists():
        conn = sqlite3.connect(str(DB_FILE))
        conn.row_factory = sqlite3.Row
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()

        for t in tables:
            table_name = t[0]
            try:
                if fmt == "csv":
                    data = export_table_csv(conn, table_name)
                    (output_path / f"{table_name}.csv").write_text(data)
                else:
                    data = export_table_json(conn, table_name)
                    (output_path / f"{table_name}.json").write_text(
                        json.dumps(data, indent=2))
                count = len(data) if isinstance(data, list) else data.count("\n")
                manifest["tables"][table_name] = count
            except Exception as e:
                manifest["tables"][table_name] = f"error: {e}"

        conn.close()

    # Write manifest
    (output_path / "manifest.json").write_text(json.dumps(manifest, indent=2))

    return {
        "status": "ok",
        "output_dir": str(output_path),
        "tables_exported": len(manifest["tables"]),
        "manifest": manifest,
    }


def import_backup(backup_dir: str) -> dict:
    """Import from a previous export."""
    backup_path = Path(backup_dir)
    manifest_path = backup_path / "manifest.json"

    if not manifest_path.exists():
        return {"status": "error", "detail": "manifest.json not found in backup directory."}

    manifest = json.loads(manifest_path.read_text())
    fmt = manifest.get("format", "json")

    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    imported = {}

    for table_name in manifest.get("tables", {}):
        try:
            if fmt == "csv":
                file_path = backup_path / f"{table_name}.csv"
                if not file_path.exists():
                    continue
                reader = csv.DictReader(io.StringIO(file_path.read_text()))
                rows = list(reader)
            else:
                file_path = backup_path / f"{table_name}.json"
                if not file_path.exists():
                    continue
                rows = json.loads(file_path.read_text())

            if not rows:
                continue

            columns = list(rows[0].keys())
            placeholders = ",".join(["?"] * len(columns))
            col_names = ",".join(f"[{c}]" for c in columns)

            count = 0
            for row in rows:
                values = [row.get(c) for c in columns]
                try:
                    conn.execute(
                        f"INSERT OR REPLACE INTO [{table_name}] ({col_names}) VALUES ({placeholders})",
                        values
                    )
                    count += 1
                except Exception:
                    pass
            imported[table_name] = count

        except Exception as e:
            imported[table_name] = f"error: {e}"

    conn.commit()
    conn.close()

    return {
        "status": "ok",
        "backup_dir": str(backup_path),
        "tables_imported": imported,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", action="store_true", help="Export all data")
    parser.add_argument("--output", default=str(SKILL_DIR / "backup"),
                        help="Output directory for export")
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    parser.add_argument("--import", dest="import_dir", metavar="DIR",
                        help="Import from backup directory")
    parser.add_argument("--list-tables", action="store_true",
                        help="List all tables and row counts")
    args = parser.parse_args()

    if args.export:
        print(json.dumps(export_all(args.output, args.format), indent=2))
    elif args.import_dir:
        print(json.dumps(import_backup(args.import_dir), indent=2))
    elif args.list_tables:
        print(json.dumps({"tables": list_tables()}, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
