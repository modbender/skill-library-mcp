"""
Persistent lightweight memory store for SociClaw.

This module stores generation events so the agent can learn from prior activity
across sessions, enabling cross-run continuity and better planning decisions.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_memory_db_path() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / ".sociclaw" / "memory.db"


@dataclass(frozen=True)
class MemoryRecord:
    id: int
    provider: str
    provider_user_id: str
    generated_at: str
    post_date: Optional[str]
    category: str
    topic: str
    with_logo: bool
    has_image: bool
    text_preview: str
    image_url: Optional[str]


class SociClawMemoryStore:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or default_memory_db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS generated_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    provider_user_id TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    post_date TEXT,
                    category TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    has_image INTEGER NOT NULL,
                    with_logo INTEGER NOT NULL DEFAULT 0,
                    text_preview TEXT,
                    image_url TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_generated_posts_identity_time
                ON generated_posts (provider, provider_user_id, generated_at DESC)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_generated_posts_category
                ON generated_posts (provider, provider_user_id, category)
                """
            )
            conn.commit()

    def upsert_generation(
        self,
        *,
        provider: str,
        provider_user_id: str,
        category: str,
        topic: str,
        text: str = "",
        post_date: Optional[str] = None,
        has_image: bool = False,
        with_logo: bool = False,
        image_url: Optional[str] = None,
    ) -> int:
        preview = (text or "").strip().replace("\n", " ")[:240]
        generated_at = _utc_now_iso()

        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO generated_posts (
                    provider,
                    provider_user_id,
                    generated_at,
                    post_date,
                    category,
                    topic,
                    has_image,
                    with_logo,
                    text_preview,
                    image_url
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    provider,
                    provider_user_id,
                    generated_at,
                    post_date,
                    category,
                    topic,
                    1 if bool(has_image) else 0,
                    1 if bool(with_logo) else 0,
                    preview,
                    image_url,
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def get_recent_posts(
        self,
        *,
        provider: str,
        provider_user_id: str,
        limit: int = 20,
    ) -> List[MemoryRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM generated_posts
                WHERE provider = ? AND provider_user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (provider, provider_user_id, max(1, int(limit))),
            ).fetchall()

        return [
            MemoryRecord(
                id=row["id"],
                provider=row["provider"],
                provider_user_id=row["provider_user_id"],
                generated_at=row["generated_at"],
                post_date=row["post_date"],
                category=row["category"] or "",
                topic=row["topic"] or "",
                has_image=bool(row["has_image"]),
                with_logo=bool(row["with_logo"]),
                text_preview=row["text_preview"] or "",
                image_url=row["image_url"],
            )
            for row in rows
        ]

    def get_recent_topics(self, *, provider: str, provider_user_id: str, limit: int = 30) -> List[str]:
        seen = set()
        topics: List[str] = []
        for record in self.get_recent_posts(provider=provider, provider_user_id=provider_user_id, limit=max(1, int(limit))):
            topic = (record.topic or "").strip()
            if not topic:
                continue
            key = topic.lower()
            if key in seen:
                continue
            seen.add(key)
            topics.append(topic)
        return topics

    def get_category_distribution(
        self,
        *,
        provider: str,
        provider_user_id: str,
        days: int = 30,
    ) -> Dict[str, int]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT category, COUNT(*) as count
                FROM generated_posts
                WHERE provider = ?
                  AND provider_user_id = ?
                  AND generated_at >= datetime('now', '-' || ? || ' days')
                GROUP BY category
                ORDER BY count DESC
                """,
                (provider, provider_user_id, max(1, int(days))),
            ).fetchall()

        return {row["category"] or "other": row["count"] for row in rows}

    def clear_user(self, *, provider: str, provider_user_id: str) -> int:
        with self._connect() as conn:
            removed = conn.execute(
                "DELETE FROM generated_posts WHERE provider = ? AND provider_user_id = ?",
                (provider, provider_user_id),
            ).rowcount
            conn.commit()
            return int(removed)

