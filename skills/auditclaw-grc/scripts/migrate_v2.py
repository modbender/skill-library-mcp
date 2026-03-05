#!/usr/bin/env python3
"""
GRC Compliance Database Migration: v1 -> v2.0.0

Upgrades the compliance.sqlite database from schema v1 to v2.0.0 by:
  - Adding new columns to existing tables (assets, training_modules, training_assignments)
  - Creating new tables (vulnerabilities, vulnerability_controls, access_review_campaigns,
    access_review_items, questionnaire_templates, questionnaire_responses,
    questionnaire_answers, asset_controls)
  - Creating new indexes
  - Updating schema_version to 2.0.0

Usage:
    python migrate_v2.py [--db-path PATH] [--dry-run]
"""

import argparse
import json
import os
import sqlite3
import sys
import traceback
from datetime import datetime
from pathlib import Path

TARGET_VERSION = "2.0.0"

DEFAULT_DB_PATH = os.path.join(
    os.path.expanduser("~"), ".openclaw", "grc", "compliance.sqlite"
)

# ---------------------------------------------------------------------------
# New columns to add to existing tables  (column_name, column_def)
# Uses ALTER TABLE ... ADD COLUMN; wrapped in try/except for idempotency.
# ---------------------------------------------------------------------------

ALTER_ASSETS_COLUMNS = [
    ("ip_address", "TEXT"),
    ("hostname", "TEXT"),
    ("os_type", "TEXT"),
    ("software_version", "TEXT"),
    ("lifecycle_stage", "TEXT DEFAULT 'in_use'"),
    ("deployment_date", "TEXT"),
    ("encryption_status", "TEXT"),
    ("backup_status", "TEXT"),
    ("patch_status", "TEXT"),
    ("last_patched_date", "TEXT"),
    ("discovery_source", "TEXT DEFAULT 'manual'"),
    ("data_classification", "TEXT DEFAULT 'internal'"),
    ("created_at", "TEXT"),
    ("updated_at", "TEXT"),
]

ALTER_TRAINING_MODULES_COLUMNS = [
    ("content_type", "TEXT"),
    ("content_url", "TEXT"),
    ("difficulty_level", "TEXT DEFAULT 'beginner'"),
    ("requires_recertification", "INTEGER DEFAULT 0"),
    ("recertification_days", "INTEGER"),
    ("duration", "INTEGER"),
    ("created_at", "TEXT"),
    ("updated_at", "TEXT"),
]

ALTER_TRAINING_ASSIGNMENTS_COLUMNS = [
    ("certificate_path", "TEXT"),
    ("assigned_at", "TEXT"),
    ("created_at", "TEXT"),
    ("updated_at", "TEXT"),
]

# ---------------------------------------------------------------------------
# New tables (CREATE TABLE IF NOT EXISTS for idempotency)
# ---------------------------------------------------------------------------

NEW_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS vulnerabilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        cve_id TEXT,
        description TEXT,
        source TEXT,
        cvss_score REAL,
        cvss_vector TEXT,
        severity TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'open',
        assignee TEXT,
        affected_assets TEXT,
        affected_packages TEXT,
        remediation_steps TEXT,
        fix_version TEXT,
        due_date TEXT,
        resolved_at TEXT,
        resolved_by TEXT,
        risk_accepted INTEGER DEFAULT 0,
        risk_acceptance_reason TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        last_updated TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS vulnerability_controls (
        vulnerability_id INTEGER REFERENCES vulnerabilities(id) ON DELETE CASCADE,
        control_id INTEGER REFERENCES controls(id) ON DELETE CASCADE,
        created_at TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (vulnerability_id, control_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS access_review_campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        scope_type TEXT,
        scope_config TEXT,
        reviewer TEXT,
        status TEXT DEFAULT 'draft',
        start_date TEXT,
        due_date TEXT,
        completed_at TEXT,
        total_items INTEGER DEFAULT 0,
        reviewed_items INTEGER DEFAULT 0,
        approved_items INTEGER DEFAULT 0,
        revoked_items INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS access_review_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER REFERENCES access_review_campaigns(id) ON DELETE CASCADE,
        user_name TEXT NOT NULL,
        resource TEXT NOT NULL,
        current_access TEXT,
        decision TEXT DEFAULT 'pending',
        reviewer TEXT,
        reviewed_at TEXT,
        notes TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS questionnaire_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        questions TEXT,
        status TEXT DEFAULT 'active',
        total_questions INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS questionnaire_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_id INTEGER REFERENCES questionnaire_templates(id),
        respondent TEXT NOT NULL,
        vendor_id INTEGER REFERENCES vendors(id),
        status TEXT DEFAULT 'draft',
        total_questions INTEGER DEFAULT 0,
        answered_questions INTEGER DEFAULT 0,
        submitted_at TEXT,
        reviewed_at TEXT,
        reviewed_by TEXT,
        score REAL,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS questionnaire_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        response_id INTEGER REFERENCES questionnaire_responses(id) ON DELETE CASCADE,
        question_index INTEGER NOT NULL,
        answer_text TEXT,
        status TEXT DEFAULT 'pending',
        notes TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS asset_controls (
        asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
        control_id INTEGER REFERENCES controls(id) ON DELETE CASCADE,
        created_at TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (asset_id, control_id)
    );
    """,
]

# ---------------------------------------------------------------------------
# Indexes
# ---------------------------------------------------------------------------

NEW_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_vulnerabilities_status ON vulnerabilities(status);",
    "CREATE INDEX IF NOT EXISTS idx_vulnerabilities_severity ON vulnerabilities(severity);",
    "CREATE INDEX IF NOT EXISTS idx_vulnerabilities_cve ON vulnerabilities(cve_id);",
    "CREATE INDEX IF NOT EXISTS idx_access_reviews_status ON access_review_campaigns(status);",
    "CREATE INDEX IF NOT EXISTS idx_questionnaire_responses_status ON questionnaire_responses(status);",
    "CREATE INDEX IF NOT EXISTS idx_assets_lifecycle ON assets(lifecycle_stage);",
    "CREATE INDEX IF NOT EXISTS idx_assets_classification ON assets(data_classification);",
    "CREATE INDEX IF NOT EXISTS idx_training_assignments_status ON training_assignments(status);",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_schema_version(conn):
    """Read the current schema_version from the database metadata table."""
    cursor = conn.cursor()
    # Try common table names for schema metadata
    for table in ("schema_version", "metadata", "schema_info", "_meta"):
        try:
            cursor.execute(
                "SELECT value FROM {} WHERE key = 'schema_version'".format(table)
            )
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.OperationalError:
            continue

    # Fallback: check if schema_version is a single-column table
    try:
        cursor.execute("SELECT version FROM schema_version LIMIT 1")
        row = cursor.fetchone()
        if row:
            return row[0]
    except sqlite3.OperationalError:
        pass

    # If no schema_version table exists at all, assume v1 (pre-versioning)
    return "1.0.0"


def set_schema_version(conn, version):
    """Write the schema_version into the metadata table, creating it if needed."""
    cursor = conn.cursor()

    # Try updating in known metadata tables first
    for table in ("schema_version", "metadata", "schema_info", "_meta"):
        try:
            cursor.execute(
                "UPDATE {} SET value = ? WHERE key = 'schema_version'".format(table),
                (version,),
            )
            if cursor.rowcount > 0:
                return
        except sqlite3.OperationalError:
            continue

    # Try single-column schema_version table
    try:
        cursor.execute("UPDATE schema_version SET version = ?", (version,))
        if cursor.rowcount > 0:
            return
    except sqlite3.OperationalError:
        pass

    # Create a metadata table if nothing exists
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    cursor.execute(
        "INSERT OR REPLACE INTO metadata (key, value) VALUES ('schema_version', ?)",
        (version,),
    )


def add_column(conn, table, col_name, col_def):
    """
    Attempt to add a column to a table. Returns True if the column was added,
    False if it already exists. Raises on unexpected errors.
    """
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
    Execute the v1 -> v2.0.0 migration.

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
        "timestamp": datetime.utcnow().isoformat() + "Z",
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

        # -- assets --
        if table_exists(conn, "assets"):
            for col_name, col_def in ALTER_ASSETS_COLUMNS:
                added = add_column(conn, "assets", col_name, col_def)
                if added:
                    result["columns_added"].append("assets.{}".format(col_name))
                else:
                    result["warnings"].append(
                        "Column assets.{} already exists, skipped.".format(col_name)
                    )
        else:
            result["warnings"].append(
                "Table 'assets' does not exist; column additions skipped."
            )

        # -- training_modules --
        if table_exists(conn, "training_modules"):
            for col_name, col_def in ALTER_TRAINING_MODULES_COLUMNS:
                added = add_column(conn, "training_modules", col_name, col_def)
                if added:
                    result["columns_added"].append(
                        "training_modules.{}".format(col_name)
                    )
                else:
                    result["warnings"].append(
                        "Column training_modules.{} already exists, skipped.".format(
                            col_name
                        )
                    )
        else:
            result["warnings"].append(
                "Table 'training_modules' does not exist; column additions skipped."
            )

        # -- training_assignments --
        if table_exists(conn, "training_assignments"):
            for col_name, col_def in ALTER_TRAINING_ASSIGNMENTS_COLUMNS:
                added = add_column(conn, "training_assignments", col_name, col_def)
                if added:
                    result["columns_added"].append(
                        "training_assignments.{}".format(col_name)
                    )
                else:
                    result["warnings"].append(
                        "Column training_assignments.{} already exists, skipped.".format(
                            col_name
                        )
                    )
        else:
            result["warnings"].append(
                "Table 'training_assignments' does not exist; column additions skipped."
            )

        # ------------------------------------------------------------------
        # 3. Create new tables
        # ------------------------------------------------------------------
        new_table_names = [
            "vulnerabilities",
            "vulnerability_controls",
            "access_review_campaigns",
            "access_review_items",
            "questionnaire_templates",
            "questionnaire_responses",
            "questionnaire_answers",
            "asset_controls",
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
            # Extract index name for reporting
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
        description="Migrate GRC compliance database from v1 to v2.0.0"
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
    elif result["status"] == "already_migrated":
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
