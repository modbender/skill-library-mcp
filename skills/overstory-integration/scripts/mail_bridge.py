#!/usr/bin/env python3
"""Thread-safe message bridge using overstory's native SQLite mail format.

Supports direct messages, broadcasts to named channels (@all, @builders, etc.),
and threaded conversations.

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
import threading
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
log = logging.getLogger("mail_bridge")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id   TEXT,
    from_agent  TEXT NOT NULL,
    to_agent    TEXT NOT NULL,
    subject     TEXT NOT NULL DEFAULT '',
    body        TEXT NOT NULL DEFAULT '',
    priority    TEXT NOT NULL DEFAULT 'normal',
    read        INTEGER NOT NULL DEFAULT 0,
    created_at  REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_msg_to      ON messages(to_agent);
CREATE INDEX IF NOT EXISTS idx_msg_thread  ON messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_msg_read    ON messages(to_agent, read);

CREATE TABLE IF NOT EXISTS threads (
    id          TEXT PRIMARY KEY,
    subject     TEXT NOT NULL DEFAULT '',
    agents      TEXT NOT NULL DEFAULT '',
    created_at  REAL NOT NULL
);
"""


class MailBridge:
    """Thread-safe inter-agent mail system backed by SQLite."""

    def __init__(self, workspace_path: Optional[str] = None):
        workspace = Path(workspace_path) if workspace_path else Path.cwd()
        self.db_path = workspace / ".overstory" / "mail.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript(_SCHEMA)

    @contextmanager
    def _conn(self) -> Generator[sqlite3.Connection, None, None]:
        with self._lock:
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

    def send(
        self,
        from_agent: str,
        to_agent: str,
        subject: str,
        body: str,
        priority: str = "normal",
    ) -> Dict[str, Any]:
        """Send a direct message."""
        if priority not in ("normal", "high", "urgent"):
            return {"ok": False, "error": f"invalid priority: {priority}"}
        now = time.time()
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO messages (from_agent, to_agent, subject, body, priority, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (from_agent, to_agent, subject, body, priority, now),
            )
        log.info("mail %s → %s: %s", from_agent, to_agent, subject)
        return {"ok": True, "message_id": cur.lastrowid}

    def read(
        self,
        agent_name: str,
        unread_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """Read messages for an agent."""
        with self._conn() as conn:
            if unread_only:
                rows = conn.execute(
                    "SELECT * FROM messages WHERE to_agent=? AND read=0 ORDER BY created_at ASC",
                    (agent_name,),
                ).fetchall()
                conn.execute(
                    "UPDATE messages SET read=1 WHERE to_agent=? AND read=0",
                    (agent_name,),
                )
            else:
                rows = conn.execute(
                    "SELECT * FROM messages WHERE to_agent=? ORDER BY created_at ASC",
                    (agent_name,),
                ).fetchall()
        return [dict(r) for r in rows]

    def broadcast(
        self,
        from_agent: str,
        channel: str,
        message: str,
    ) -> Dict[str, Any]:
        """Broadcast to a channel (@all, @builders, @researchers, etc.).

        Channel names are stored as the to_agent field so agents can subscribe
        by reading messages addressed to the channel name.
        """
        now = time.time()
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO messages (from_agent, to_agent, subject, body, priority, created_at) "
                "VALUES (?, ?, ?, ?, 'normal', ?)",
                (from_agent, channel, f"[broadcast] {channel}", message, now),
            )
        log.info("broadcast %s → %s", from_agent, channel)
        return {"ok": True, "message_id": cur.lastrowid, "channel": channel}

    def create_thread(
        self,
        agents: List[str],
        subject: str,
    ) -> Dict[str, Any]:
        """Create a conversation thread between agents."""
        thread_id = f"thread-{uuid.uuid4().hex[:12]}"
        now = time.time()
        agents_str = ",".join(agents)
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO threads (id, subject, agents, created_at) VALUES (?, ?, ?, ?)",
                (thread_id, subject, agents_str, now),
            )
        log.info("created thread %s: %s (%s)", thread_id, subject, agents_str)
        return {"ok": True, "thread_id": thread_id, "agents": agents}

    def reply_to_thread(
        self,
        thread_id: str,
        from_agent: str,
        body: str,
    ) -> Dict[str, Any]:
        """Post a reply in a thread. Delivers to all thread participants except sender."""
        with self._conn() as conn:
            thread_row = conn.execute(
                "SELECT * FROM threads WHERE id=?", (thread_id,)
            ).fetchone()
            if thread_row is None:
                return {"ok": False, "error": f"thread '{thread_id}' not found"}
            agents = [a.strip() for a in thread_row["agents"].split(",") if a.strip()]
            subject = thread_row["subject"]
            now = time.time()
            ids = []
            for agent in agents:
                if agent == from_agent:
                    continue
                cur = conn.execute(
                    "INSERT INTO messages (thread_id, from_agent, to_agent, subject, body, priority, created_at) "
                    "VALUES (?, ?, ?, ?, ?, 'normal', ?)",
                    (thread_id, from_agent, agent, f"Re: {subject}", body, now),
                )
                ids.append(cur.lastrowid)
        return {"ok": True, "thread_id": thread_id, "message_ids": ids}

    def get_thread(self, thread_id: str) -> Dict[str, Any]:
        """Get all messages in a thread, ordered chronologically."""
        with self._conn() as conn:
            thread_row = conn.execute(
                "SELECT * FROM threads WHERE id=?", (thread_id,)
            ).fetchone()
            if thread_row is None:
                return {"ok": False, "error": f"thread '{thread_id}' not found"}
            rows = conn.execute(
                "SELECT * FROM messages WHERE thread_id=? ORDER BY created_at ASC",
                (thread_id,),
            ).fetchall()
        return {
            "ok": True,
            "thread_id": thread_id,
            "subject": thread_row["subject"],
            "agents": [a.strip() for a in thread_row["agents"].split(",") if a.strip()],
            "messages": [dict(r) for r in rows],
        }


def _json_out(data: Any) -> None:
    json.dump(data, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="overstory mail bridge")
    parser.add_argument("--workspace", default=None, help="Workspace root")
    sub = parser.add_subparsers(dest="command", required=True)

    p_send = sub.add_parser("send")
    p_send.add_argument("--from", dest="from_agent", required=True)
    p_send.add_argument("--to", dest="to_agent", required=True)
    p_send.add_argument("--subject", required=True)
    p_send.add_argument("--body", required=True)
    p_send.add_argument("--priority", default="normal", choices=["normal", "high", "urgent"])

    p_read = sub.add_parser("read")
    p_read.add_argument("--agent", required=True)
    p_read.add_argument("--unread", action="store_true", default=True)
    p_read.add_argument("--all", action="store_false", dest="unread")

    p_bcast = sub.add_parser("broadcast")
    p_bcast.add_argument("--from", dest="from_agent", required=True)
    p_bcast.add_argument("--channel", required=True)
    p_bcast.add_argument("--message", required=True)

    p_thread = sub.add_parser("create-thread")
    p_thread.add_argument("--agents", required=True, help="Comma-separated agent names")
    p_thread.add_argument("--subject", required=True)

    p_reply = sub.add_parser("reply")
    p_reply.add_argument("--thread", required=True)
    p_reply.add_argument("--from", dest="from_agent", required=True)
    p_reply.add_argument("--body", required=True)

    p_get = sub.add_parser("get-thread")
    p_get.add_argument("--thread", required=True)

    args = parser.parse_args()
    bridge = MailBridge(args.workspace)

    dispatch = {
        "send": lambda: bridge.send(
            args.from_agent, args.to_agent, args.subject, args.body, args.priority,
        ),
        "read": lambda: bridge.read(args.agent, args.unread),
        "broadcast": lambda: bridge.broadcast(args.from_agent, args.channel, args.message),
        "create-thread": lambda: bridge.create_thread(
            [a.strip() for a in args.agents.split(",")], args.subject,
        ),
        "reply": lambda: bridge.reply_to_thread(args.thread, args.from_agent, args.body),
        "get-thread": lambda: bridge.get_thread(args.thread),
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
