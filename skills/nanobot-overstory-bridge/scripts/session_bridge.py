#!/usr/bin/env python3
"""
Session/agent ID mapping between nanobot and overstory.
Uses SQLite for thread-safe persistent storage.
"""

import json
import logging
import os
import sqlite3
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=os.environ.get("BRIDGE_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("session_bridge")

DEFAULT_DB = Path(
    os.environ.get("SESSION_BRIDGE_DB", Path.home() / ".nanobot" / "session_bridge.db")
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS session_mappings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nanobot_session TEXT    NOT NULL,
    overstory_agent TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'active',
    created_at      REAL    NOT NULL,
    updated_at      REAL    NOT NULL,
    metadata        TEXT    DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_nanobot_session
    ON session_mappings(nanobot_session);
CREATE INDEX IF NOT EXISTS idx_overstory_agent
    ON session_mappings(overstory_agent);
CREATE INDEX IF NOT EXISTS idx_status
    ON session_mappings(status);
"""


class SessionBridge:
    """Thread-safe mapping between nanobot sessions and overstory agents."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._init_schema()

    @contextmanager
    def _conn(self):
        """Thread-local connection with WAL mode for concurrency."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                str(self.db_path), timeout=10
            )
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield self._local.conn
            self._local.conn.commit()
        except Exception:
            self._local.conn.rollback()
            raise

    def _init_schema(self):
        with self._conn() as conn:
            conn.executescript(SCHEMA)

    def create_mapping(
        self,
        nanobot_session_id: str,
        overstory_agent_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Store a new nanobot ↔ overstory mapping."""
        now = time.time()
        meta_json = json.dumps(metadata or {})
        with self._conn() as conn:
            cursor = conn.execute(
                """INSERT INTO session_mappings
                   (nanobot_session, overstory_agent, status, created_at, updated_at, metadata)
                   VALUES (?, ?, 'active', ?, ?, ?)""",
                (nanobot_session_id, overstory_agent_name, now, now, meta_json),
            )
            row_id = cursor.lastrowid

        log.info("Mapped nanobot:%s ↔ overstory:%s (id=%d)",
                 nanobot_session_id, overstory_agent_name, row_id)
        return {
            "id": row_id,
            "nanobot_session": nanobot_session_id,
            "overstory_agent": overstory_agent_name,
            "status": "active",
        }

    def get_overstory_agent(self, nanobot_session_id: str) -> Optional[Dict[str, Any]]:
        """Get the overstory agent name for a nanobot session."""
        with self._conn() as conn:
            row = conn.execute(
                """SELECT * FROM session_mappings
                   WHERE nanobot_session = ? AND status = 'active'
                   ORDER BY created_at DESC LIMIT 1""",
                (nanobot_session_id,),
            ).fetchone()
        return dict(row) if row else None

    def get_nanobot_session(self, overstory_agent_name: str) -> Optional[Dict[str, Any]]:
        """Get the nanobot session for an overstory agent."""
        with self._conn() as conn:
            row = conn.execute(
                """SELECT * FROM session_mappings
                   WHERE overstory_agent = ? AND status = 'active'
                   ORDER BY created_at DESC LIMIT 1""",
                (overstory_agent_name,),
            ).fetchone()
        return dict(row) if row else None

    def list_active_mappings(self) -> List[Dict[str, Any]]:
        """List all active session mappings."""
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT * FROM session_mappings
                   WHERE status = 'active'
                   ORDER BY created_at DESC"""
            ).fetchall()
        return [dict(r) for r in rows]

    def update_status(self, nanobot_session_id: str, status: str) -> bool:
        """Update mapping status (active, completed, failed, stale)."""
        now = time.time()
        with self._conn() as conn:
            cursor = conn.execute(
                """UPDATE session_mappings
                   SET status = ?, updated_at = ?
                   WHERE nanobot_session = ? AND status = 'active'""",
                (status, now, nanobot_session_id),
            )
        updated = cursor.rowcount > 0
        if updated:
            log.info("Updated nanobot:%s → status=%s", nanobot_session_id, status)
        return updated

    def cleanup_stale(self, max_age_hours: float = 24) -> Dict[str, Any]:
        """Remove mappings older than max_age_hours."""
        cutoff = time.time() - (max_age_hours * 3600)
        with self._conn() as conn:
            cursor = conn.execute(
                """UPDATE session_mappings
                   SET status = 'stale', updated_at = ?
                   WHERE status = 'active' AND created_at < ?""",
                (time.time(), cutoff),
            )
        count = cursor.rowcount
        log.info("Marked %d stale mappings (older than %.1fh)", count, max_age_hours)
        return {"stale_count": count, "max_age_hours": max_age_hours}


# ── CLI interface ───────────────────────────────────────────────

def _cli():
    import argparse

    parser = argparse.ArgumentParser(description="Session bridge: nanobot ↔ overstory mapping")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="Create a new mapping")
    p_create.add_argument("--nanobot-session", required=True)
    p_create.add_argument("--overstory-agent", required=True)
    p_create.add_argument("--json", action="store_true")

    p_get_agent = sub.add_parser("get-agent", help="Get overstory agent for nanobot session")
    p_get_agent.add_argument("--nanobot-session", required=True)
    p_get_agent.add_argument("--json", action="store_true")

    p_get_session = sub.add_parser("get-session", help="Get nanobot session for overstory agent")
    p_get_session.add_argument("--overstory-agent", required=True)
    p_get_session.add_argument("--json", action="store_true")

    p_list = sub.add_parser("list", help="List active mappings")
    p_list.add_argument("--json", action="store_true")

    p_cleanup = sub.add_parser("cleanup", help="Mark stale mappings")
    p_cleanup.add_argument("--max-age", type=float, default=24, help="Max age in hours")
    p_cleanup.add_argument("--json", action="store_true")

    args = parser.parse_args()
    bridge = SessionBridge()

    if args.command == "create":
        result = bridge.create_mapping(args.nanobot_session, args.overstory_agent)
    elif args.command == "get-agent":
        result = bridge.get_overstory_agent(args.nanobot_session)
        if result is None:
            result = {"error": "No active mapping found", "nanobot_session": args.nanobot_session}
    elif args.command == "get-session":
        result = bridge.get_nanobot_session(args.overstory_agent)
        if result is None:
            result = {"error": "No active mapping found", "overstory_agent": args.overstory_agent}
    elif args.command == "list":
        result = {"mappings": bridge.list_active_mappings()}
    elif args.command == "cleanup":
        result = bridge.cleanup_stale(args.max_age)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    _cli()
