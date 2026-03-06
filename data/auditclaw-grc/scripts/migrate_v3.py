#!/usr/bin/env python3
"""
GRC Compliance Database Migration: v2.0.0 -> v3.0.0

Upgrades the compliance.sqlite database from schema v2 to v3.0.0 by:
  - Adding new columns to existing tables (incidents, policies, controls)
  - Creating new tables (incident_actions, incident_reviews, policy_approvals,
    policy_acknowledgments, test_results)
  - Creating new indexes
  - Updating schema_version to 3.0.0

Usage:
    python migrate_v3.py [--db-path PATH] [--dry-run]
"""

import argparse
import json
import os
import sqlite3
import sys
import traceback
from datetime import datetime

TARGET_VERSION = "3.0.0"

DEFAULT_DB_PATH = os.path.join(
    os.path.expanduser("~"), ".openclaw", "grc", "compliance.sqlite"
)

# ---------------------------------------------------------------------------
# New columns to add to existing tables  (column_name, column_def)
# Uses ALTER TABLE ... ADD COLUMN; wrapped in try/except for idempotency.
# ---------------------------------------------------------------------------

ALTER_INCIDENTS_COLUMNS = [
    ("preventive_actions", "TEXT"),
    ("impact_assessment", "TEXT"),           # may already exist in V2 schema
    ("estimated_cost", "REAL"),
    ("actual_cost", "REAL"),
    ("regulatory_notification_required", "INTEGER DEFAULT 0"),
    ("regulatory_bodies_notified", "TEXT"),  # JSON array
    ("regulatory_notification_sent_at", "TEXT"),
]

ALTER_POLICIES_COLUMNS = [
    ("parent_version_id", "INTEGER REFERENCES policies(id)"),
    ("owner", "TEXT"),
    ("effective_date", "TEXT"),
    ("change_summary", "TEXT"),
]

ALTER_CONTROLS_COLUMNS = [
    ("maturity_level", "TEXT"),              # initial, developing, defined, managed, optimizing
    ("effectiveness_score", "INTEGER"),      # 0-100
    ("effectiveness_rating", "TEXT"),        # effective, partially_effective, ineffective
    ("last_tested_at", "TEXT"),
]

# ---------------------------------------------------------------------------
# New tables (CREATE TABLE IF NOT EXISTS for idempotency)
# ---------------------------------------------------------------------------

NEW_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS incident_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id INTEGER NOT NULL REFERENCES incidents(id),
        action_type TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        action_taken_at TEXT DEFAULT (datetime('now')),
        outcome TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS incident_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id INTEGER NOT NULL REFERENCES incidents(id),
        conducted_by TEXT NOT NULL,
        review_date TEXT DEFAULT (date('now')),
        what_happened TEXT,
        what_went_well TEXT,
        what_went_wrong TEXT,
        lessons_learned TEXT,
        action_items TEXT,
        recommendations TEXT,
        is_completed INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS policy_approvals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        policy_id INTEGER NOT NULL REFERENCES policies(id),
        requested_by TEXT NOT NULL,
        requested_at TEXT DEFAULT (datetime('now')),
        request_notes TEXT,
        reviewed_by TEXT,
        reviewed_at TEXT,
        decision TEXT DEFAULT 'pending',
        decision_notes TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS policy_acknowledgments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        policy_id INTEGER NOT NULL REFERENCES policies(id),
        user_name TEXT NOT NULL,
        acknowledged_at TEXT,
        due_date TEXT,
        reminder_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT (datetime('now')),
        UNIQUE(policy_id, user_name)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS test_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_name TEXT NOT NULL,
        control_id INTEGER REFERENCES controls(id),
        status TEXT NOT NULL,
        items_checked INTEGER DEFAULT 0,
        items_passed INTEGER DEFAULT 0,
        items_failed INTEGER DEFAULT 0,
        findings TEXT,
        duration_ms INTEGER,
        tested_at TEXT DEFAULT (datetime('now')),
        created_at TEXT DEFAULT (datetime('now'))
    );
    """,
]

# ---------------------------------------------------------------------------
# Indexes
# ---------------------------------------------------------------------------

NEW_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_incident_actions_incident ON incident_actions(incident_id);",
    "CREATE INDEX IF NOT EXISTS idx_incident_reviews_incident ON incident_reviews(incident_id);",
    "CREATE INDEX IF NOT EXISTS idx_policy_approvals_policy ON policy_approvals(policy_id);",
    "CREATE INDEX IF NOT EXISTS idx_policy_approvals_decision ON policy_approvals(decision);",
    "CREATE INDEX IF NOT EXISTS idx_policy_acks_policy ON policy_acknowledgments(policy_id);",
    "CREATE INDEX IF NOT EXISTS idx_policy_acks_status ON policy_acknowledgments(status);",
    "CREATE INDEX IF NOT EXISTS idx_test_results_control ON test_results(control_id);",
    "CREATE INDEX IF NOT EXISTS idx_test_results_status ON test_results(status);",
    "CREATE INDEX IF NOT EXISTS idx_test_results_tested ON test_results(tested_at);",
    "CREATE INDEX IF NOT EXISTS idx_controls_maturity ON controls(maturity_level);",
    "CREATE INDEX IF NOT EXISTS idx_controls_effectiveness ON controls(effectiveness_score);",
    "CREATE INDEX IF NOT EXISTS idx_incidents_regulatory ON incidents(regulatory_notification_required);",
    "CREATE INDEX IF NOT EXISTS idx_policies_parent ON policies(parent_version_id);",
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

    # Fallback: insert new row
    try:
        cursor.execute(
            "INSERT INTO schema_version (version) VALUES (?)", (version,)
        )
    except sqlite3.OperationalError:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS schema_version (version TEXT NOT NULL, applied_at TEXT DEFAULT (datetime('now')))"
        )
        cursor.execute(
            "INSERT INTO schema_version (version) VALUES (?)", (version,)
        )


def add_column(conn, table, col_name, col_def):
    """Attempt to add a column. Returns True if added, False if already exists."""
    try:
        conn.execute(
            "ALTER TABLE {} ADD COLUMN {} {}".format(table, col_name, col_def)
        )
        return True
    except sqlite3.OperationalError as exc:
        msg = str(exc).lower()
        if "duplicate column" in msg or "already exists" in msg:
            return False
        raise


def table_exists(conn, table):
    cursor = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    )
    return cursor.fetchone()[0] > 0


# ---------------------------------------------------------------------------
# Main migration logic
# ---------------------------------------------------------------------------


def migrate(db_path, dry_run=False):
    """
    Execute the v2.0.0 -> v3.0.0 migration.

    Returns a result dict suitable for JSON serialization.
    """
    result = {
        "status": "success",
        "db_path": db_path,
        "target_version": TARGET_VERSION,
        "previous_version": None,
        "dry_run": dry_run,
        "columns_added": [],
        "tables_created": [],
        "indexes_created": [],
        "warnings": [],
        "timestamp": datetime.now().isoformat(),
    }

    if not os.path.exists(db_path):
        result["status"] = "error"
        result["error"] = "Database file not found: {}".format(db_path)
        return result

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        # ------------------------------------------------------------------
        # 1. Check current schema version
        # ------------------------------------------------------------------
        current_version = get_schema_version(conn)
        result["previous_version"] = current_version

        if current_version == TARGET_VERSION:
            result["status"] = "already_migrated"
            result["message"] = (
                "Database is already at schema version {}. "
                "No migration needed.".format(TARGET_VERSION)
            )
            return result

        if current_version not in ("2.0.0", "1.0.0"):
            result["warnings"].append(
                "Unexpected source version: {}. Proceeding anyway.".format(current_version)
            )

        if dry_run:
            result["message"] = (
                "Dry run: would migrate from {} to {}.".format(
                    current_version, TARGET_VERSION
                )
            )
            return result

        # ------------------------------------------------------------------
        # 2. Add new columns to existing tables
        # ------------------------------------------------------------------

        # -- incidents --
        if table_exists(conn, "incidents"):
            for col_name, col_def in ALTER_INCIDENTS_COLUMNS:
                added = add_column(conn, "incidents", col_name, col_def)
                if added:
                    result["columns_added"].append("incidents.{}".format(col_name))
                else:
                    result["warnings"].append(
                        "Column incidents.{} already exists, skipped.".format(col_name)
                    )
        else:
            result["warnings"].append(
                "Table 'incidents' does not exist; column additions skipped."
            )

        # -- policies --
        if table_exists(conn, "policies"):
            for col_name, col_def in ALTER_POLICIES_COLUMNS:
                added = add_column(conn, "policies", col_name, col_def)
                if added:
                    result["columns_added"].append("policies.{}".format(col_name))
                else:
                    result["warnings"].append(
                        "Column policies.{} already exists, skipped.".format(col_name)
                    )
        else:
            result["warnings"].append(
                "Table 'policies' does not exist; column additions skipped."
            )

        # -- controls --
        if table_exists(conn, "controls"):
            for col_name, col_def in ALTER_CONTROLS_COLUMNS:
                added = add_column(conn, "controls", col_name, col_def)
                if added:
                    result["columns_added"].append("controls.{}".format(col_name))
                else:
                    result["warnings"].append(
                        "Column controls.{} already exists, skipped.".format(col_name)
                    )
        else:
            result["warnings"].append(
                "Table 'controls' does not exist; column additions skipped."
            )

        # ------------------------------------------------------------------
        # 3. Create new tables
        # ------------------------------------------------------------------
        new_table_names = [
            "incident_actions",
            "incident_reviews",
            "policy_approvals",
            "policy_acknowledgments",
            "test_results",
        ]

        for sql, tname in zip(NEW_TABLES_SQL, new_table_names):
            existed_before = table_exists(conn, tname)
            conn.execute(sql)
            if not existed_before:
                result["tables_created"].append(tname)
            else:
                result["warnings"].append(
                    "Table '{}' already existed, CREATE IF NOT EXISTS was no-op.".format(
                        tname
                    )
                )

        # ------------------------------------------------------------------
        # 4. Create indexes
        # ------------------------------------------------------------------
        for idx_sql in NEW_INDEXES_SQL:
            idx_name = idx_sql.split("IF NOT EXISTS")[1].split("ON")[0].strip()
            conn.execute(idx_sql)
            result["indexes_created"].append(idx_name)

        # ------------------------------------------------------------------
        # 5. Update schema version
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
        description="Migrate GRC compliance database from v2.0.0 to v3.0.0"
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
