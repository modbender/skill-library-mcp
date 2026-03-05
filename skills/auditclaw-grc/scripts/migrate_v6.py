#!/usr/bin/env python3
"""V6 Migration: Add integration_credentials table + credential directories.

Idempotent — safe to run multiple times.

Usage:
    python3 migrate_v6.py [--db-path /path/to/compliance.sqlite]
"""

import argparse
import json
import os
import sqlite3
import sys

DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/grc/compliance.sqlite")
CREDENTIALS_DIR = os.path.expanduser("~/.openclaw/grc/credentials")

V6_SCHEMA = """
-- V6: Integration Credentials (secure auth storage)
CREATE TABLE IF NOT EXISTS integration_credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    auth_method TEXT NOT NULL,
    config TEXT NOT NULL,
    credential_path TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_used TEXT,
    expires_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_integration_credentials_provider ON integration_credentials(provider);
CREATE INDEX IF NOT EXISTS idx_integration_credentials_status ON integration_credentials(status);
"""


def migrate(db_path):
    """Run V6 migration."""
    if not os.path.exists(db_path):
        return {"status": "error", "message": f"Database not found: {db_path}"}

    conn = sqlite3.connect(db_path, timeout=10)
    try:
        # Check if table already exists
        existing = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='integration_credentials'"
        ).fetchone()

        if existing:
            # Ensure credential directories exist even if table is already there
            _create_credential_dirs()
            return {
                "status": "already_migrated",
                "table": "integration_credentials",
                "credentials_dir": CREDENTIALS_DIR,
            }

        # Create table
        conn.executescript(V6_SCHEMA)
        conn.commit()

        # Create credential directories
        _create_credential_dirs()

        # Update schema version (create metadata table if missing)
        conn.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)")
        conn.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('schema_version', '6.0.0')")
        conn.commit()

        return {
            "status": "migrated",
            "version": "6.0",
            "table_created": "integration_credentials",
            "credentials_dir": CREDENTIALS_DIR,
            "providers": ["aws", "github", "azure", "gcp", "idp"],
        }
    finally:
        conn.close()


def _create_credential_dirs():
    """Create secure credential directory structure."""
    os.makedirs(CREDENTIALS_DIR, mode=0o700, exist_ok=True)
    for provider in ["aws", "github", "azure", "gcp", "idp"]:
        provider_dir = os.path.join(CREDENTIALS_DIR, provider)
        os.makedirs(provider_dir, mode=0o700, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="V6 Migration: Integration Credentials")
    parser.add_argument("--db-path", help="Path to SQLite database")
    args = parser.parse_args()

    db_path = args.db_path or os.environ.get("GRC_DB_PATH", DEFAULT_DB_PATH)

    try:
        result = migrate(db_path)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["status"] != "error" else 1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
