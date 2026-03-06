"""War/Den Local Memory Store -- SQLite-backed persistent memory for community tier."""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone

from warden_governance.settings import Settings


class LocalMemoryStore:
    """Local SQLite memory store.

    Community tier: simple text search, namespace filtering, TTL expiry.
    Enterprise tier uses EngramPort with Eidetic synthesis.
    """

    def __init__(self, config: Settings):
        self.db_path = os.path.expanduser(config.warden_memory_db)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    bot_id TEXT NOT NULL,
                    namespace TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT,
                    ttl_days INTEGER,
                    expires_at TEXT
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_bot_ns "
                "ON memories(bot_id, namespace)"
            )
            conn.commit()

    def write(
        self,
        bot_id: str,
        content: str,
        namespace: str,
        metadata: dict,
        ttl_days: int = 30,
    ) -> str:
        memory_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        created_at = now.isoformat()
        expires_at = (now + timedelta(days=ttl_days)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO memories
                (memory_id, bot_id, namespace, content, metadata,
                 created_at, ttl_days, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    memory_id,
                    bot_id,
                    namespace,
                    content,
                    json.dumps(metadata, sort_keys=True),
                    created_at,
                    ttl_days,
                    expires_at,
                ),
            )
            conn.commit()

        return memory_id

    def read(
        self,
        bot_id: str,
        query: str,
        namespace: str,
        limit: int = 10,
    ) -> list[dict]:
        now = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT memory_id, content, metadata, created_at
                FROM memories
                WHERE bot_id = ?
                  AND namespace = ?
                  AND expires_at > ?
                  AND content LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (bot_id, namespace, now, f"%{query}%", limit),
            ).fetchall()

        return [
            {
                "memory_id": row["memory_id"],
                "content": row["content"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def delete(self, bot_id: str, memory_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM memories WHERE memory_id = ? AND bot_id = ?",
                (memory_id, bot_id),
            )
            conn.commit()
        return cursor.rowcount > 0

    def synthesize(
        self,
        bot_id: str,
        query: str,
        namespaces: list[str],
    ) -> str:
        """Basic synthesis: gather top memories across namespaces."""
        now = datetime.now(timezone.utc).isoformat()
        placeholders = ",".join("?" for _ in namespaces)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                f"""
                SELECT content, namespace, created_at
                FROM memories
                WHERE bot_id = ?
                  AND namespace IN ({placeholders})
                  AND expires_at > ?
                ORDER BY created_at DESC
                LIMIT 5
                """,
                (bot_id, *namespaces, now),
            ).fetchall()

        if not rows:
            return ""

        parts = []
        for row in rows:
            parts.append(f"[{row['namespace']}] {row['content']}")

        return "\n".join(parts)
