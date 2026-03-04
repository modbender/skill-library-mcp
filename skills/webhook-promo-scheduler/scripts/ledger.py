#!/usr/bin/env python3
"""Simple JSONL ledger to enforce max 1 post/day/channel.

Each JSON line contains:
  - date: YYYY-MM-DD (local time)
  - channel: arbitrary string
  - status: "reserved" | "posted" | "error"
  - hash: sha256 hex of message content

Stdlib only.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
from dataclasses import dataclass
from typing import Iterable, List, Optional

try:
    import fcntl  # type: ignore
except Exception:
    fcntl = None  # type: ignore

DEFAULT_LEDGER_PATH = os.path.expanduser("~/.openclaw/webhook-promo-ledger.jsonl")


@dataclass(frozen=True)
class LedgerEntry:
    date: str
    channel: str
    status: str
    hash: str


def today_local_yyyy_mm_dd() -> str:
    return _dt.date.today().isoformat()


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)


class Ledger:
    def __init__(self, path: str = DEFAULT_LEDGER_PATH):
        self.path = os.path.expanduser(path)

    def _open_locked(self, mode: str):
        ensure_parent_dir(self.path)
        f = open(self.path, mode, encoding="utf-8")
        if fcntl is not None:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            except Exception:
                pass
        return f

    def iter_entries(self) -> Iterable[LedgerEntry]:
        if not os.path.exists(self.path):
            return []

        entries: List[LedgerEntry] = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if not isinstance(obj, dict):
                    continue
                date = obj.get("date")
                channel = obj.get("channel")
                status = obj.get("status")
                h = obj.get("hash")
                if (
                    isinstance(date, str)
                    and isinstance(channel, str)
                    and isinstance(status, str)
                    and isinstance(h, str)
                ):
                    entries.append(LedgerEntry(date=date, channel=channel, status=status, hash=h))
        return entries

    def append(self, entry: LedgerEntry) -> None:
        payload = {
            "date": entry.date,
            "channel": entry.channel,
            "status": entry.status,
            "hash": entry.hash,
        }
        line = json.dumps(payload, ensure_ascii=True, separators=(",", ":"))
        with self._open_locked("a") as f:
            f.write(line + "\n")
            f.flush()
            os.fsync(f.fileno())

    def already_posted_today(self, channel: str, today: Optional[str] = None) -> bool:
        today_s = today or today_local_yyyy_mm_dd()
        with self._open_locked("a+") as f:
            f.seek(0)
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if not isinstance(obj, dict):
                    continue
                if obj.get("date") != today_s:
                    continue
                if obj.get("channel") != channel:
                    continue
                if obj.get("status") == "posted":
                    return True
        return False

    def last_posted_hash(self, channel: str) -> Optional[str]:
        last: Optional[str] = None
        with self._open_locked("a+") as f:
            f.seek(0)
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if not isinstance(obj, dict):
                    continue
                if obj.get("channel") != channel:
                    continue
                if obj.get("status") != "posted":
                    continue
                h = obj.get("hash")
                if isinstance(h, str):
                    last = h
        return last
