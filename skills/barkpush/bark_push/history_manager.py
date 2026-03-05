from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .utils import now_iso, now_ts


class HistoryError(Exception):
    pass


@dataclass
class HistoryRecord:
    id: str
    timestamp: int
    datetime: str
    device_keys: list[str]
    user_aliases: list[str]
    title: str
    subtitle: str
    body: str
    content_type: str
    parameters: dict[str, Any]
    status: str
    success_count: int
    failed_count: int
    failed_users: list[str]
    error_messages: dict[str, str]
    bark_response: dict[str, Any] | None
    updated_at: int
    update_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "datetime": self.datetime,
            "device_keys": self.device_keys,
            "user_aliases": self.user_aliases,
            "title": self.title,
            "subtitle": self.subtitle,
            "body": self.body,
            "content_type": self.content_type,
            "parameters": self.parameters,
            "status": self.status,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "failed_users": self.failed_users,
            "error_messages": self.error_messages,
            "bark_response": self.bark_response or {},
            "updated_at": self.updated_at,
            "update_count": self.update_count,
        }

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "HistoryRecord":
        return HistoryRecord(
            id=str(d.get("id", "")),
            timestamp=int(d.get("timestamp", 0)),
            datetime=str(d.get("datetime", "")),
            device_keys=[str(x) for x in (d.get("device_keys") or [])],
            user_aliases=[str(x) for x in (d.get("user_aliases") or [])],
            title=str(d.get("title", "")),
            subtitle=str(d.get("subtitle", "")),
            body=str(d.get("body", "")),
            content_type=str(d.get("content_type", "")),
            parameters=dict(d.get("parameters") or {}),
            status=str(d.get("status", "success")),
            success_count=int(d.get("success_count", 0)),
            failed_count=int(d.get("failed_count", 0)),
            failed_users=[str(x) for x in (d.get("failed_users") or [])],
            error_messages={str(k): str(v) for k, v in (d.get("error_messages") or {}).items()},
            bark_response=dict(d.get("bark_response") or {}),
            updated_at=int(d.get("updated_at", 0)),
            update_count=int(d.get("update_count", 0)),
        )


class HistoryManager:
    def __init__(self, history_path: Path, limit: int) -> None:
        self._path = history_path
        self._limit = max(1, int(limit))
        self._records = self._load()

    @property
    def path(self) -> Path:
        return self._path

    def get(self, push_id: str) -> HistoryRecord | None:
        for r in self._records:
            if r.id == push_id:
                return r
        return None

    def has_user(self, push_id: str, user_alias: str) -> bool:
        record = self.get(push_id)
        if not record:
            return False
        return user_alias in set(record.user_aliases)

    def upsert(self, record: HistoryRecord) -> None:
        existing_idx = None
        for i, r in enumerate(self._records):
            if r.id == record.id:
                existing_idx = i
                break
        if existing_idx is None:
            self._records.append(record)
        else:
            self._records[existing_idx] = record
        self._trim()
        self._save()

    def mark_updated(self, push_id: str) -> None:
        record = self.get(push_id)
        if not record:
            return
        record.updated_at = now_ts()
        record.update_count += 1
        self.upsert(record)

    def list_recent(self, limit: int = 20) -> list[HistoryRecord]:
        n = max(0, int(limit))
        return list(sorted(self._records, key=lambda r: r.timestamp, reverse=True))[:n]

    def _trim(self) -> None:
        if len(self._records) <= self._limit:
            return
        self._records.sort(key=lambda r: r.timestamp)
        overflow = len(self._records) - self._limit
        if overflow > 0:
            self._records = self._records[overflow:]

    def _load(self) -> list[HistoryRecord]:
        if not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            return []
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                return []
            out: list[HistoryRecord] = []
            for item in raw:
                if isinstance(item, dict):
                    out.append(HistoryRecord.from_dict(item))
            return out
        except Exception:
            return []

    def _save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            payload = [r.to_dict() for r in self._records]
            self._path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            raise HistoryError(str(e)) from e


def new_history_record(
    *,
    push_id: str,
    device_keys: list[str],
    user_aliases: list[str],
    title: str,
    subtitle: str,
    body: str,
    content_type: str,
    parameters: dict[str, Any],
    status: str,
    success_count: int,
    failed_count: int,
    failed_users: list[str],
    error_messages: dict[str, str],
    bark_response: dict[str, Any] | None,
) -> HistoryRecord:
    ts = now_ts()
    return HistoryRecord(
        id=push_id,
        timestamp=ts,
        datetime=now_iso(),
        device_keys=device_keys,
        user_aliases=user_aliases,
        title=title,
        subtitle=subtitle,
        body=body,
        content_type=content_type,
        parameters=parameters,
        status=status,
        success_count=success_count,
        failed_count=failed_count,
        failed_users=failed_users,
        error_messages=error_messages,
        bark_response=bark_response,
        updated_at=ts,
        update_count=0,
    )
