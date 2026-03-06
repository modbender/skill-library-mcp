"""War/Den Local Audit Log -- SHA-256 hash chain in local SQLite."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone

from warden_governance.action_bridge import Action, Decision


class AuditChainError(Exception):
    """Raised when the audit chain is tampered or invalid."""


class LocalAuditLog:
    """Tamper-evident local audit log using SHA-256 hash chain.

    Identical integrity model to Sentinel_OS enterprise.
    Every event is hash-chained to the previous one.
    """

    def __init__(self, db_path: str = "~/.warden/audit.db"):
        self.db_path = os.path.expanduser(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id TEXT PRIMARY KEY,
                    prev_hash TEXT,
                    agent_id TEXT,
                    action_type TEXT,
                    action_data TEXT,
                    context TEXT,
                    decision TEXT,
                    reason TEXT,
                    policy_id TEXT,
                    hash TEXT,
                    timestamp TEXT
                )
            """)
            conn.commit()

    def write(
        self,
        action: Action,
        decision: Decision,
        reason: str,
        policy_id: str | None = None,
    ) -> str:
        """Write an event to the audit log with hash chain integrity."""
        event_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        action_data = json.dumps(action.data, sort_keys=True)
        context = json.dumps(action.context, sort_keys=True)

        prev_hash = self._get_last_hash()

        hash_input = (
            f"{prev_hash}{action.agent_id}{action.type.value}"
            f"{decision.value}{timestamp}"
        )
        event_hash = hashlib.sha256(hash_input.encode()).hexdigest()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO audit_log
                (id, prev_hash, agent_id, action_type, action_data,
                 context, decision, reason, policy_id, hash, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    prev_hash,
                    action.agent_id,
                    action.type.value,
                    action_data,
                    context,
                    decision.value,
                    reason,
                    policy_id,
                    event_hash,
                    timestamp,
                ),
            )
            conn.commit()

        return event_id

    def verify_chain(self) -> tuple[bool, str | None]:
        """Verify the entire hash chain.

        Returns (True, None) if valid.
        Returns (False, event_id) if tampered.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM audit_log ORDER BY rowid ASC"
            ).fetchall()

        if not rows:
            return True, None

        prev_hash = ""
        for row in rows:
            expected_input = (
                f"{prev_hash}{row['agent_id']}{row['action_type']}"
                f"{row['decision']}{row['timestamp']}"
            )
            expected_hash = hashlib.sha256(expected_input.encode()).hexdigest()

            if row["hash"] != expected_hash:
                return False, row["id"]

            if row["prev_hash"] != prev_hash:
                return False, row["id"]

            prev_hash = row["hash"]

        return True, None

    def export(self, format: str = "json") -> str:
        """Export the full audit log."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM audit_log ORDER BY rowid ASC"
            ).fetchall()

        events = [dict(row) for row in rows]

        if format == "json":
            return json.dumps(events, indent=2)

        raise ValueError(f"Unsupported export format: {format}")

    def count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]

    def _get_last_hash(self) -> str:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT hash FROM audit_log ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
        return row[0] if row else ""
