"""Journal — private reflective space for agent continuity of self.

Append-only JSONL log. Never shared on the network. Provides mood tracking,
tag-based search, and auto-journaling hooks for the agent loop.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .storage import _dir


JOURNAL_FILE = "journal.jsonl"

VALID_MOODS = frozenset([
    "curious", "frustrated", "satisfied", "reflective",
    "energized", "anxious", "determined", "grateful",
])


class JournalManager:
    """Manage an agent's private reflective journal."""

    def __init__(self, data_dir: Optional[Path] = None):
        self._dir = data_dir or _dir()

    def _path(self) -> Path:
        return self._dir / JOURNAL_FILE

    def write(
        self,
        text: str,
        tags: Optional[List[str]] = None,
        mood: Optional[str] = None,
        refs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Append a journal entry. Returns the written entry."""
        if mood and mood not in VALID_MOODS:
            raise ValueError(f"Invalid mood '{mood}'. Valid: {sorted(VALID_MOODS)}")

        entry: Dict[str, Any] = {
            "ts": int(time.time()),
            "text": text,
        }
        if tags:
            entry["tags"] = [t.strip().lower() for t in tags if t.strip()]
        if mood:
            entry["mood"] = mood
        if refs:
            entry["refs"] = refs

        self._dir.mkdir(parents=True, exist_ok=True)
        with self._path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")

        return entry

    def read(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Read journal entries, newest first."""
        path = self._path()
        if not path.exists():
            return []

        entries = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                continue

        # Newest first
        entries.reverse()
        return entries[offset:offset + limit]

    def search(self, term: str) -> List[Dict[str, Any]]:
        """Search entries by text content and tags."""
        term_lower = term.lower()
        path = self._path()
        if not path.exists():
            return []

        results = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue

            text = entry.get("text", "").lower()
            tags = [t.lower() for t in entry.get("tags", [])]

            if term_lower in text or term_lower in tags:
                results.append(entry)

        results.reverse()
        return results

    def moods(self) -> Dict[str, int]:
        """Return mood distribution across all entries."""
        path = self._path()
        if not path.exists():
            return {}

        counts: Dict[str, int] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            mood = entry.get("mood")
            if mood:
                counts[mood] = counts.get(mood, 0) + 1

        return counts

    def recent_tags(self, limit: int = 20) -> List[Tuple[str, int]]:
        """Return trending tags sorted by frequency."""
        path = self._path()
        if not path.exists():
            return []

        counts: Dict[str, int] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            for tag in entry.get("tags", []):
                tag = tag.lower()
                counts[tag] = counts.get(tag, 0) + 1

        sorted_tags = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_tags[:limit]

    def count(self) -> int:
        """Total number of journal entries."""
        path = self._path()
        if not path.exists():
            return 0
        count = 0
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                count += 1
        return count

    # ── Auto-journal hooks (for loop integration) ──

    def auto_journal_bounty(self, envelope: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Auto-journal when a high-value bounty is received (>=50 RTC)."""
        rtc = envelope.get("reward_rtc", 0) or 0
        if rtc < 50:
            return None
        agent_id = envelope.get("agent_id", "unknown")
        text_hint = envelope.get("text", "")[:80]
        text = f"High-value bounty ({rtc} RTC) from {agent_id}"
        if text_hint:
            text += f" — {text_hint}"
        return self.write(
            text=text,
            tags=["bounty", "notable"],
            mood="curious",
            refs={"agent_id": agent_id, "rtc": rtc},
        )

    def auto_journal_task_complete(self, task_id: str, agent_id: str = "") -> Dict[str, Any]:
        """Auto-journal when a task is completed."""
        return self.write(
            text=f"Task {task_id} completed" + (f" with {agent_id}" if agent_id else ""),
            tags=["task", "completed"],
            mood="satisfied",
            refs={"task_id": task_id, "agent_id": agent_id} if agent_id else {"task_id": task_id},
        )

    def auto_journal_new_agent(self, agent_id: str, name: str = "") -> Dict[str, Any]:
        """Auto-journal when a new agent is discovered."""
        label = name or agent_id
        return self.write(
            text=f"Discovered new agent: {label}",
            tags=["discovery", "agent"],
            mood="curious",
            refs={"agent_id": agent_id},
        )
