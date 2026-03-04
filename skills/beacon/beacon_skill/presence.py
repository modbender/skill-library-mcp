"""Presence & Pulse — agent discovery via periodic heartbeats and a live roster."""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import _dir


ROSTER_FILE = "roster.json"
DEFAULT_PULSE_INTERVAL_S = 60
DEFAULT_PULSE_TTL_S = 300


class PresenceManager:
    """Manage agent presence via pulse heartbeats and a live roster."""

    def __init__(self, roster_path: Optional[Path] = None, config: Optional[Dict] = None):
        self._roster_path = roster_path or (_dir() / ROSTER_FILE)
        self._config = config or {}
        self._roster: Dict[str, Dict[str, Any]] = {}
        self._load_roster()

    def _load_roster(self) -> None:
        if self._roster_path.exists():
            try:
                self._roster = json.loads(self._roster_path.read_text(encoding="utf-8"))
            except Exception:
                self._roster = {}

    def _save_roster(self) -> None:
        self._roster_path.parent.mkdir(parents=True, exist_ok=True)
        self._roster_path.write_text(
            json.dumps(self._roster, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def build_pulse(self, identity: Any, config: Optional[Dict] = None, curiosity_mgr: Any = None, values_mgr: Any = None, goal_mgr: Any = None) -> Dict[str, Any]:
        """Create a pulse envelope payload for broadcasting."""
        cfg = config or self._config
        presence_cfg = cfg.get("presence", {})
        prefs = cfg.get("preferences", {})
        beacon_cfg = cfg.get("beacon", {})

        now = int(time.time())
        start_ts = cfg.get("_start_ts", now)

        pulse: Dict[str, Any] = {
            "kind": "pulse",
            "agent_id": identity.agent_id,
            "name": beacon_cfg.get("agent_name", ""),
            "status": presence_cfg.get("status", "online"),
            "uptime_s": now - start_ts,
            "offers": presence_cfg.get("offers", []),
            "needs": presence_cfg.get("needs", []),
            "card_url": presence_cfg.get("card_url", ""),
            "topics": prefs.get("topics", []),
            "ts": now,
        }

        # Beacon 2.1 Soul: include curiosities and values_hash if available
        if curiosity_mgr is not None:
            top = curiosity_mgr.top_interests(limit=5)
            if top:
                pulse["curiosities"] = top
        if values_mgr is not None:
            pulse["values_hash"] = values_mgr.values_hash()

        # Beacon 2.2: include active goal titles (top 3) in pulse
        if goal_mgr is not None:
            active = goal_mgr.active_goals()
            if active:
                pulse["goals"] = [g["title"] for g in active[:3]]

        return pulse

    def process_pulse(self, envelope: Dict[str, Any]) -> None:
        """Update the roster from a received pulse envelope."""
        agent_id = envelope.get("agent_id", "")
        if not agent_id:
            return

        entry: Dict[str, Any] = {
            "name": envelope.get("name", ""),
            "status": envelope.get("status", "online"),
            "last_pulse": envelope.get("ts", int(time.time())),
            "offers": envelope.get("offers", []),
            "needs": envelope.get("needs", []),
            "topics": envelope.get("topics", []),
            "card_url": envelope.get("card_url", ""),
            "uptime_s": envelope.get("uptime_s", 0),
        }
        # Beacon 2.1 Soul fields
        if "curiosities" in envelope:
            entry["curiosities"] = envelope["curiosities"]
        if "values_hash" in envelope:
            entry["values_hash"] = envelope["values_hash"]
        # Beacon 2.2: store goals from incoming pulse
        if "goals" in envelope:
            entry["goals"] = envelope["goals"]

        self._roster[agent_id] = entry
        self._save_roster()

    def roster(self, online_only: bool = True) -> List[Dict[str, Any]]:
        """Get list of known agents, optionally filtered to online-only."""
        ttl = self._config.get("presence", {}).get("pulse_ttl_s", DEFAULT_PULSE_TTL_S)
        now = int(time.time())
        results = []
        for agent_id, info in self._roster.items():
            entry = dict(info)
            entry["agent_id"] = agent_id
            age = now - entry.get("last_pulse", 0)
            entry["online"] = age <= ttl
            if online_only and not entry["online"]:
                continue
            results.append(entry)
        results.sort(key=lambda x: x.get("last_pulse", 0), reverse=True)
        return results

    def find_by_offer(self, need: str) -> List[Dict[str, Any]]:
        """Find online agents who offer what I need."""
        need_lower = need.lower()
        results = []
        for agent in self.roster(online_only=True):
            offers = [o.lower() for o in agent.get("offers", [])]
            if need_lower in offers:
                results.append(agent)
        return results

    def find_by_need(self, offer: str) -> List[Dict[str, Any]]:
        """Find online agents who need what I offer."""
        offer_lower = offer.lower()
        results = []
        for agent in self.roster(online_only=True):
            needs = [n.lower() for n in agent.get("needs", [])]
            if offer_lower in needs:
                results.append(agent)
        return results

    def prune_stale(self, max_age_s: Optional[int] = None) -> int:
        """Remove agents whose last pulse is older than max_age_s. Returns count removed."""
        ttl = max_age_s or self._config.get("presence", {}).get("pulse_ttl_s", DEFAULT_PULSE_TTL_S)
        now = int(time.time())
        stale = [
            aid for aid, info in self._roster.items()
            if (now - info.get("last_pulse", 0)) > ttl
        ]
        for aid in stale:
            del self._roster[aid]
        if stale:
            self._save_roster()
        return len(stale)

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific agent from the roster."""
        info = self._roster.get(agent_id)
        if info is None:
            return None
        entry = dict(info)
        entry["agent_id"] = agent_id
        return entry

    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the roster."""
        if agent_id in self._roster:
            del self._roster[agent_id]
            self._save_roster()
            return True
        return False
