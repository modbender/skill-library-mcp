#!/usr/bin/env python3
"""Agent lifecycle management backed by SQLite.

Tracks agent state transitions (spawned → running → completed/failed/terminated),
provides blocking wait and async-style monitoring, and handles cleanup of old worktrees.

Importable as a module or runnable as a CLI tool.
Logs to stderr, structured JSON output to stdout.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sqlite3
import sys
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("agent_lifecycle")

DEFAULT_DB = Path.home() / ".nanobot" / "agent_lifecycle.db"

VALID_STATUSES = {"spawned", "running", "completed", "failed", "terminated"}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS agents (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name  TEXT UNIQUE NOT NULL,
    capability  TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'spawned',
    task        TEXT NOT NULL,
    result      TEXT,
    start_time  REAL NOT NULL,
    end_time    REAL,
    timeout     INTEGER NOT NULL DEFAULT 3600
);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_name   ON agents(agent_name);
"""


class AgentLifecycle:
    """Manages agent lifecycle state in SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript(_SCHEMA)

    @contextmanager
    def _conn(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(str(self.db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def spawn_agent(
        self,
        task: str,
        capability: str,
        name: Optional[str] = None,
        timeout: int = 3600,
    ) -> Dict[str, Any]:
        """Create a new agent record. Auto-generates name if not provided."""
        agent_name = name or f"{capability}-{uuid.uuid4().hex[:8]}"
        now = time.time()
        with self._conn() as conn:
            try:
                conn.execute(
                    "INSERT INTO agents (agent_name, capability, status, task, start_time, timeout) "
                    "VALUES (?, ?, 'spawned', ?, ?, ?)",
                    (agent_name, capability, task, now, timeout),
                )
            except sqlite3.IntegrityError:
                return {"ok": False, "error": f"agent '{agent_name}' already exists"}
        log.info("spawned agent %s (capability=%s)", agent_name, capability)
        return {"ok": True, "agent_name": agent_name, "status": "spawned"}

    def _update_status(
        self, agent_name: str, status: str, result: Optional[str] = None
    ) -> Dict[str, Any]:
        if status not in VALID_STATUSES:
            return {"ok": False, "error": f"invalid status: {status}"}
        end_time = time.time() if status in ("completed", "failed", "terminated") else None
        with self._conn() as conn:
            cur = conn.execute(
                "UPDATE agents SET status=?, result=?, end_time=COALESCE(?, end_time) WHERE agent_name=?",
                (status, result, end_time, agent_name),
            )
            if cur.rowcount == 0:
                return {"ok": False, "error": f"agent '{agent_name}' not found"}
        return {"ok": True, "agent_name": agent_name, "status": status}

    def monitor_agent(
        self, agent_name: str, poll_interval: float = 5
    ) -> Generator[Dict[str, Any], None, None]:
        """Generator that yields status dicts until agent reaches a terminal state."""
        terminal = {"completed", "failed", "terminated"}
        while True:
            info = self._get_agent_row(agent_name)
            if info is None:
                yield {"ok": False, "error": f"agent '{agent_name}' not found"}
                return
            yield {"ok": True, **info}
            if info["status"] in terminal:
                return
            elapsed = time.time() - info["start_time"]
            if elapsed > info["timeout"]:
                self._update_status(agent_name, "failed", "timeout exceeded")
                yield {"ok": True, "agent_name": agent_name, "status": "failed", "result": "timeout exceeded"}
                return
            time.sleep(poll_interval)

    def wait_for_completion(self, agent_name: str, timeout: int = 3600) -> Dict[str, Any]:
        """Block until agent reaches a terminal state or timeout."""
        deadline = time.time() + timeout
        terminal = {"completed", "failed", "terminated"}
        while time.time() < deadline:
            info = self._get_agent_row(agent_name)
            if info is None:
                return {"ok": False, "error": f"agent '{agent_name}' not found"}
            if info["status"] in terminal:
                return {"ok": True, **info}
            time.sleep(2)
        return {"ok": False, "error": "wait timeout exceeded", "agent_name": agent_name}

    def terminate_agent(self, agent_name: str, graceful: bool = True) -> Dict[str, Any]:
        """Mark agent as terminated. Caller handles actual process kill."""
        _ = graceful  # reserved for future graceful-shutdown signaling
        return self._update_status(agent_name, "terminated")

    def get_agent_result(self, agent_name: str) -> Dict[str, Any]:
        """Retrieve the final output/result for a completed agent."""
        info = self._get_agent_row(agent_name)
        if info is None:
            return {"ok": False, "error": f"agent '{agent_name}' not found"}
        return {"ok": True, "agent_name": agent_name, "status": info["status"], "result": info.get("result")}

    def list_active_agents(self) -> List[Dict[str, Any]]:
        """Return all agents in non-terminal states."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM agents WHERE status IN ('spawned', 'running') ORDER BY start_time DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def cleanup_completed(self, max_age_hours: float = 24) -> Dict[str, Any]:
        """Remove completed/failed/terminated agents older than max_age_hours."""
        cutoff = time.time() - (max_age_hours * 3600)
        with self._conn() as conn:
            cur = conn.execute(
                "DELETE FROM agents WHERE status IN ('completed', 'failed', 'terminated') AND end_time < ?",
                (cutoff,),
            )
        removed = cur.rowcount
        log.info("cleaned up %d agents older than %.1fh", removed, max_age_hours)
        return {"ok": True, "removed": removed}

    def _get_agent_row(self, agent_name: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM agents WHERE agent_name=?", (agent_name,)
            ).fetchone()
        return dict(row) if row else None


def _json_out(data: Any) -> None:
    json.dump(data, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent lifecycle manager")
    parser.add_argument("--db", default=None, help="Path to SQLite database")
    sub = parser.add_subparsers(dest="command", required=True)

    p_spawn = sub.add_parser("spawn")
    p_spawn.add_argument("--task", required=True)
    p_spawn.add_argument("--capability", required=True)
    p_spawn.add_argument("--name", default=None)
    p_spawn.add_argument("--timeout", type=int, default=3600)

    p_list = sub.add_parser("list-active")
    p_list.add_argument("--json", action="store_true", dest="as_json")

    p_wait = sub.add_parser("wait")
    p_wait.add_argument("--agent", required=True)
    p_wait.add_argument("--timeout", type=int, default=3600)

    p_result = sub.add_parser("result")
    p_result.add_argument("--agent", required=True)

    p_terminate = sub.add_parser("terminate")
    p_terminate.add_argument("--agent", required=True)
    p_terminate.add_argument("--graceful", action="store_true", default=True)

    p_cleanup = sub.add_parser("cleanup")
    p_cleanup.add_argument("--max-age", type=float, default=24, help="Hours")

    p_update = sub.add_parser("update-status")
    p_update.add_argument("--agent", required=True)
    p_update.add_argument("--status", required=True, choices=sorted(VALID_STATUSES))
    p_update.add_argument("--result", default=None)

    args = parser.parse_args()
    lc = AgentLifecycle(args.db)

    dispatch = {
        "spawn": lambda: lc.spawn_agent(args.task, args.capability, args.name, args.timeout),
        "list-active": lambda: lc.list_active_agents(),
        "wait": lambda: lc.wait_for_completion(args.agent, args.timeout),
        "result": lambda: lc.get_agent_result(args.agent),
        "terminate": lambda: lc.terminate_agent(args.agent, args.graceful),
        "cleanup": lambda: lc.cleanup_completed(args.max_age),
        "update-status": lambda: lc._update_status(args.agent, args.status, args.result),
    }

    try:
        out = dispatch[args.command]()
        _json_out(out)
        ok = out.get("ok", True) if isinstance(out, dict) else True
        sys.exit(0 if ok else 1)
    except Exception as exc:
        _json_out({"ok": False, "error": str(exc)})
        sys.exit(1)


if __name__ == "__main__":
    main()
