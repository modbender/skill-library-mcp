"""
Local session store for SociClaw topups (SQLite).

Why SQLite:
- Atomic writes (safer than JSON if the process crashes mid-write)
- No external dependencies
- Suitable for single-instance bots on VPS/Mac mini

Data stored:
- telegram_user_id -> session_id (provider topup session)
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_db_path() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / ".tmp" / "sociclaw_sessions.db"


@dataclass(frozen=True)
class SessionRecord:
    telegram_user_id: str
    session_id: str
    created_at: str
    updated_at: str


class LocalSessionStore:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or default_db_path()
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
                CREATE TABLE IF NOT EXISTS topup_sessions (
                    telegram_user_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def upsert_session(self, telegram_user_id: str, session_id: str) -> SessionRecord:
        now = _utc_now_iso()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT telegram_user_id, session_id, created_at, updated_at FROM topup_sessions WHERE telegram_user_id = ?",
                (str(telegram_user_id),),
            ).fetchone()

            if row:
                created_at = row["created_at"]
                conn.execute(
                    """
                    UPDATE topup_sessions
                    SET session_id = ?, updated_at = ?
                    WHERE telegram_user_id = ?
                    """,
                    (session_id, now, str(telegram_user_id)),
                )
            else:
                created_at = now
                conn.execute(
                    """
                    INSERT INTO topup_sessions (telegram_user_id, session_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (str(telegram_user_id), session_id, now, now),
                )

            conn.commit()

        return SessionRecord(
            telegram_user_id=str(telegram_user_id),
            session_id=session_id,
            created_at=created_at,
            updated_at=now,
        )

    def get_session(self, telegram_user_id: str) -> Optional[SessionRecord]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT telegram_user_id, session_id, created_at, updated_at FROM topup_sessions WHERE telegram_user_id = ?",
                (str(telegram_user_id),),
            ).fetchone()

        if not row:
            return None

        return SessionRecord(
            telegram_user_id=row["telegram_user_id"],
            session_id=row["session_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def delete_session(self, telegram_user_id: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM topup_sessions WHERE telegram_user_id = ?",
                (str(telegram_user_id),),
            )
            conn.commit()
