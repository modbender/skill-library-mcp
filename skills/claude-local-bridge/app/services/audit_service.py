"""Simple in-memory audit log for file access events."""

from __future__ import annotations

from collections import deque
from datetime import datetime

from app.models.schemas import AuditAction, AuditEntry


class AuditService:
    def __init__(self, max_entries: int = 5000) -> None:
        self._log: deque[AuditEntry] = deque(maxlen=max_entries)

    def log(
        self,
        action: AuditAction,
        path: str,
        detail: str = "",
        success: bool = True,
    ) -> AuditEntry:
        entry = AuditEntry(
            action=action, path=path, detail=detail, success=success
        )
        self._log.append(entry)
        return entry

    def recent(self, limit: int = 100) -> list[AuditEntry]:
        return list(self._log)[-limit:]

    def for_path(self, path: str, limit: int = 50) -> list[AuditEntry]:
        return [e for e in self._log if e.path == path][-limit:]
