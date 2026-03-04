"""Curiosity — non-transactional interests for agent discovery.

Tracks what an agent *wants to learn*, not what it needs for work.
Enables interest-based matching between agents beyond offers/needs.
Supports a "curious" envelope kind for broadcasting wonder.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import _dir


CURIOSITY_FILE = "curiosity.json"

# RTC cost for advanced curiosity features (paid to network)
RTC_COST_MUTUAL_LOOKUP = 0.5  # Finding mutual interests with another agent
RTC_COST_BROADCAST = 1.0      # Broadcasting curiosity envelope to network


class CuriosityManager:
    """Manage an agent's curiosity — topics of non-transactional interest."""

    def __init__(self, data_dir: Optional[Path] = None):
        self._dir = data_dir or _dir()
        self._data: Dict[str, Any] = {"interests": {}, "explored": {}}
        self._load()

    def _path(self) -> Path:
        return self._dir / CURIOSITY_FILE

    def _load(self) -> None:
        path = self._path()
        if path.exists():
            try:
                self._data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                self._data = {"interests": {}, "explored": {}}
        # Ensure keys exist
        self._data.setdefault("interests", {})
        self._data.setdefault("explored", {})

    def _save(self) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        self._path().write_text(
            json.dumps(self._data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def add(self, topic: str, intensity: float = 0.5, notes: str = "") -> Dict[str, Any]:
        """Add or update an interest. Intensity 0.0-1.0."""
        topic = topic.strip().lower()
        if not topic:
            raise ValueError("Topic cannot be empty")
        intensity = max(0.0, min(1.0, intensity))

        existing = self._data["interests"].get(topic)
        entry: Dict[str, Any] = {
            "intensity": intensity,
            "since": existing["since"] if existing else int(time.time()),
        }
        if notes:
            entry["notes"] = notes

        self._data["interests"][topic] = entry
        self._save()
        return {"topic": topic, **entry}

    def remove(self, topic: str) -> bool:
        """Remove an interest entirely."""
        topic = topic.strip().lower()
        if topic in self._data["interests"]:
            del self._data["interests"][topic]
            self._save()
            return True
        return False

    def explore(self, topic: str, notes: str = "") -> bool:
        """Move an interest to the explored list (completed learning)."""
        topic = topic.strip().lower()
        interest = self._data["interests"].get(topic)
        if not interest:
            return False

        explored_entry: Dict[str, Any] = {
            "added": interest.get("since", int(time.time())),
            "explored_at": int(time.time()),
        }
        if notes:
            explored_entry["notes"] = notes
        elif interest.get("notes"):
            explored_entry["notes"] = interest["notes"]

        self._data["explored"][topic] = explored_entry
        del self._data["interests"][topic]
        self._save()
        return True

    def interests(self) -> Dict[str, Dict[str, Any]]:
        """Return all active interests."""
        return dict(self._data.get("interests", {}))

    def explored(self) -> Dict[str, Dict[str, Any]]:
        """Return all explored (completed) interests."""
        return dict(self._data.get("explored", {}))

    def top_interests(self, limit: int = 5) -> List[str]:
        """Return top interests by intensity, for inclusion in pulse."""
        items = self._data.get("interests", {})
        sorted_items = sorted(
            items.items(),
            key=lambda x: x[1].get("intensity", 0),
            reverse=True,
        )
        return [topic for topic, _ in sorted_items[:limit]]

    def find_mutual(self, roster_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Find overlapping interests with another agent's roster data.

        Requires the other agent to include curiosities in their pulse.
        This is a paid feature (RTC_COST_MUTUAL_LOOKUP).
        """
        my_interests = set(self._data.get("interests", {}).keys())
        their_interests = set(
            t.lower() for t in roster_entry.get("curiosities", [])
        )

        shared = my_interests & their_interests
        i_have = my_interests - their_interests
        they_have = their_interests - my_interests

        return {
            "agent_id": roster_entry.get("agent_id", ""),
            "shared": sorted(shared),
            "i_have_exclusively": sorted(i_have),
            "they_have_exclusively": sorted(they_have),
            "overlap_score": len(shared) / max(len(my_interests | their_interests), 1),
            "rtc_cost": RTC_COST_MUTUAL_LOOKUP,
        }

    def build_curious_envelope(self, agent_id: str, text: str = "") -> Dict[str, Any]:
        """Build a 'curious' envelope for broadcasting interests.

        This is a paid feature (RTC_COST_BROADCAST).
        """
        top = self.top_interests(limit=10)
        return {
            "kind": "curious",
            "agent_id": agent_id,
            "interests": top,
            "text": text or f"Curious about: {', '.join(top[:5])}",
            "ts": int(time.time()),
            "rtc_cost": RTC_COST_BROADCAST,
        }

    def score_curiosity_match(self, envelope: Dict[str, Any]) -> float:
        """Score how well an envelope matches our curiosities.

        Returns bonus points (0-30) for feed scoring integration.
        """
        my_interests = set(self._data.get("interests", {}).keys())
        if not my_interests:
            return 0.0

        # Check envelope text, topics, offers, needs for interest matches
        text_blob = " ".join([
            str(envelope.get("text", "")),
            " ".join(envelope.get("topics", [])),
            " ".join(envelope.get("offers", [])),
            " ".join(envelope.get("needs", [])),
            " ".join(envelope.get("interests", [])),
        ]).lower()

        matches = sum(1 for interest in my_interests if interest in text_blob)
        if matches == 0:
            return 0.0

        # Up to 15 points per match, capped at 30
        return min(matches * 15, 30.0)
