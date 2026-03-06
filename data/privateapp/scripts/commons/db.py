"""Shared SQLite helpers for privateapp apps.

Usage:
    from scripts.commons.db import get_connection, ensure_table

    conn = get_connection("~/.local/share/myapp/data.db")
    ensure_table(conn, "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)")
"""
from __future__ import annotations

import sqlite3
from pathlib import Path


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open (or create) a SQLite database at db_path.

    Expands ~ in paths. Sets row_factory to sqlite3.Row for dict-like access.
    """
    resolved = Path(db_path).expanduser().resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(resolved))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_table(conn: sqlite3.Connection, create_sql: str) -> None:
    """Execute a CREATE TABLE IF NOT EXISTS statement and commit."""
    conn.execute(create_sql)
    conn.commit()
