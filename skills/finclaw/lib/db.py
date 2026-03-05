"""SQLite connection helper for FinClaw."""

import sqlite3
import os
from lib.config import get_db_path


def get_connection() -> sqlite3.Connection:
    """Get a SQLite connection with WAL mode and foreign keys enabled."""
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def execute(sql: str, params=None):
    """Execute a single SQL statement and return results."""
    conn = get_connection()
    try:
        cur = conn.execute(sql, params or ())
        conn.commit()
        return cur.fetchall()
    finally:
        conn.close()
