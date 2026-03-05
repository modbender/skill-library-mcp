#!/usr/bin/env python3
"""
GRC Compliance Database Migration: v3.0.0 -> v4.0.0

Upgrades the compliance.sqlite database from schema v3 to v4.0.0 by:
  - Creating new tables (integrations, browser_checks)
  - Adding drift_details column to alerts table
  - Creating new indexes
  - Updating schema_version to 4.0.0

Usage:
    python migrate_v4.py [--db-path PATH] [--dry-run]
"""

import argparse
import json
import os
import sqlite3
import sys
import traceback
from datetime import datetime

TARGET_VERSION = "4.0.0"

DEFAULT_DB_PATH = os.path.join(
    os.path.expanduser("~"), ".openclaw", "grc", "compliance.sqlite"
)

# ---------------------------------------------------------------------------
# New columns to add to existing tables  (column_name, column_def)
# Uses ALTER TABLE ... ADD COLUMN; wrapped in try/except for idempotency.
# ---------------------------------------------------------------------------

ALTER_ALERTS_COLUMNS = [
    ("drift_details", "TEXT"),       # JSON: drift metadata for drift_detected alerts
    ("resource_type", "TEXT"),       # e.g. 's3_bucket', 'iam_user', 'github_repo'
    ("resource_id", "TEXT"),         # external resource identifier
    ("acknowledged_at", "TEXT"),     # when alert was acknowledged
    ("acknowledged_by", "TEXT"),     # who acknowledged
]

# ---------------------------------------------------------------------------
# New tables (CREATE TABLE IF NOT EXISTS for idempotency)
# ---------------------------------------------------------------------------

NEW_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS integrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider TEXT NOT NULL,
        name TEXT NOT NULL,
        status TEXT DEFAULT 'configured',
        schedule TEXT,
        last_sync TEXT,
        next_sync TEXT,
        last_error TEXT,
        error_count INTEGER DEFAULT 0,
        config TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS browser_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        check_type TEXT NOT NULL,
        schedule TEXT,
        status TEXT DEFAULT 'active',
        last_run TEXT,
        last_result TEXT,
        last_status TEXT,
        run_count INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    """,
]

# ---------------------------------------------------------------------------
# Indexes
# ---------------------------------------------------------------------------

NEW_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_integrations_provider ON integrations(provider);",
    "CREATE INDEX IF NOT EXISTS idx_integrations_status ON integrations(status);",
    "CREATE INDEX IF NOT EXISTS idx_browser_checks_type ON browser_checks(check_type);",
    "CREATE INDEX IF NOT EXISTS idx_browser_checks_status ON browser_checks(status);",
    "CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(type);",
    "CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);",
    "CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);",
    "CREATE INDEX IF NOT EXISTS idx_alerts_resource ON alerts(resource_type, resource_id);",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_schema_version(conn):
    """Read the current schema_version from the database."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT version FROM schema_version ORDER BY rowid DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return row[0]
    except sqlite3.OperationalError:
        pass
    return "1.0.0"


def set_schema_version(conn, version):
    """Write the schema_version into the schema_version table."""
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE schema_version SET version = ?", (version,))
        if cursor.rowcount > 0:
            return
    except sqlite3.OperationalError:
        pass
    cursor.execute(
        "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
        (version, datetime.utcnow().isoformat(timespec="seconds")),
    )


# ---------------------------------------------------------------------------
# Migration
# ---------------------------------------------------------------------------


def migrate(db_path, dry_run=False):
    """Run the v3 -> v4 migration."""

    result = {
        "status": "ok",
        "from_version": None,
        "to_version": TARGET_VERSION,
        "tables_created": [],
        "columns_added": [],
        "indexes_created": [],
        "message": "",
    }

    if not os.path.exists(db_path):
        result["status"] = "error"
        result["error"] = "Database file not found: {}".format(db_path)
        return result

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    try:
        current_version = get_schema_version(conn)
        result["from_version"] = current_version

        if current_version == TARGET_VERSION:
            result["message"] = "Database is already at version {}. No migration needed.".format(
                TARGET_VERSION
            )
            return result

        if current_version not in ("3.0.0",):
            result["status"] = "error"
            result["error"] = (
                "Expected schema version 3.0.0, found {}. "
                "Please run earlier migrations first.".format(current_version)
            )
            return result

        if dry_run:
            result["message"] = (
                "DRY RUN: Would migrate from {} to {}. "
                "No changes made.".format(current_version, TARGET_VERSION)
            )
            return result

        # ------------------------------------------------------------------
        # 1. Alter existing tables – add new columns
        # ------------------------------------------------------------------
        for col_name, col_def in ALTER_ALERTS_COLUMNS:
            try:
                conn.execute(
                    "ALTER TABLE alerts ADD COLUMN {} {}".format(col_name, col_def)
                )
                result["columns_added"].append("alerts.{}".format(col_name))
            except sqlite3.OperationalError:
                pass  # column already exists – idempotent

        # ------------------------------------------------------------------
        # 2. Create new tables
        # ------------------------------------------------------------------
        for table_sql in NEW_TABLES_SQL:
            table_name = table_sql.split("EXISTS")[1].split("(")[0].strip()
            conn.execute(table_sql)
            result["tables_created"].append(table_name)

        # ------------------------------------------------------------------
        # 3. Create new indexes
        # ------------------------------------------------------------------
        for idx_sql in NEW_INDEXES_SQL:
            idx_name = idx_sql.split("IF NOT EXISTS")[1].split("ON")[0].strip()
            conn.execute(idx_sql)
            result["indexes_created"].append(idx_name)

        # ------------------------------------------------------------------
        # 4. Update schema version
        # ------------------------------------------------------------------
        set_schema_version(conn, TARGET_VERSION)

        conn.commit()
        result["message"] = (
            "Migration from {} to {} completed successfully.".format(
                current_version, TARGET_VERSION
            )
        )

    except Exception as exc:
        conn.rollback()
        result["status"] = "error"
        result["error"] = str(exc)
        result["traceback"] = traceback.format_exc()
    finally:
        conn.close()

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Migrate GRC compliance database from v3.0.0 to v4.0.0"
    )
    parser.add_argument(
        "--db-path",
        default=DEFAULT_DB_PATH,
        help="Path to compliance.sqlite (default: {})".format(DEFAULT_DB_PATH),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check current version and report what would be done without making changes.",
    )
    args = parser.parse_args()

    result = migrate(args.db_path, dry_run=args.dry_run)

    print(json.dumps(result, indent=2))

    if result["status"] == "error":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
