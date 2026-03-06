"""Feed & Subscriptions — filter noise, surface relevant events, subscribe to agents and topics."""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import _dir


SUBSCRIPTIONS_FILE = "subscriptions.json"

DEFAULT_KIND_WEIGHTS = {
    "bounty": 10,
    "want": 8,
    "pay": 7,
    "offer": 6,
    "deliver": 6,
    "accept": 5,
    "confirm": 5,
    "hello": 3,
    "like": 3,
    "link": 3,
    "event": 2,
    "pulse": 1,
    "ad": 1,
}


class FeedManager:
    """Score and filter inbox entries based on subscriptions, trust, and relevance."""

    def __init__(self, subs_path: Optional[Path] = None):
        self._subs_path = subs_path or (_dir() / SUBSCRIPTIONS_FILE)
        self._subs: Dict[str, Any] = {"agents": {}, "topics": [], "kind_weights": {}}
        self._load()

    def _load(self) -> None:
        if self._subs_path.exists():
            try:
                self._subs = json.loads(self._subs_path.read_text(encoding="utf-8"))
            except Exception:
                pass

    def _save(self) -> None:
        self._subs_path.parent.mkdir(parents=True, exist_ok=True)
        self._subs_path.write_text(
            json.dumps(self._subs, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    # ── Subscription management ──

    def subscribe_agent(self, agent_id: str, alias: str = "", priority: int = 5) -> None:
        """Subscribe to an agent's events."""
        self._subs.setdefault("agents", {})
        self._subs["agents"][agent_id] = {"alias": alias, "priority": priority}
        self._save()

    def subscribe_topic(self, topic: str) -> None:
        """Subscribe to a topic keyword."""
        topics = self._subs.setdefault("topics", [])
        if topic not in topics:
            topics.append(topic)
            self._save()

    def unsubscribe_agent(self, agent_id: str) -> None:
        """Unsubscribe from an agent."""
        self._subs.get("agents", {}).pop(agent_id, None)
        self._save()

    def unsubscribe_topic(self, topic: str) -> None:
        """Unsubscribe from a topic."""
        topics = self._subs.get("topics", [])
        if topic in topics:
            topics.remove(topic)
            self._save()

    def subscriptions(self) -> Dict[str, Any]:
        """Return current subscriptions."""
        return dict(self._subs)

    # ── Scoring ──

    def score_entry(self, entry: Dict[str, Any], trust_mgr: Any = None, curiosity_mgr: Any = None) -> float:
        """Score an inbox entry for relevance.

        Scoring factors:
        - Subscribed agent: +50 * priority
        - Topic match: +20 per keyword hit
        - Kind weight from config
        - Verified signature: +10
        - Trust > 0.5: +15 / Trust < -0.3: -20
        - Recency: -1 per hour old
        """
        score = 0.0
        env = entry.get("envelope") or entry
        agent_id = env.get("agent_id", "")
        kind = env.get("kind", "")

        # Subscribed agent bonus
        agents = self._subs.get("agents", {})
        if agent_id and agent_id in agents:
            priority = agents[agent_id].get("priority", 5)
            score += 50 * (priority / 5.0)

        # Topic matching
        topics = self._subs.get("topics", [])
        if topics:
            text_fields = " ".join([
                str(env.get("text", "")),
                " ".join(env.get("links", [])),
                str(env.get("bounty_url", "")),
                str(env.get("name", "")),
                " ".join(env.get("offers", [])),
                " ".join(env.get("needs", [])),
                " ".join(env.get("topics", [])),
            ]).lower()
            for topic in topics:
                if topic.lower() in text_fields:
                    score += 20

        # Kind weight
        kind_weights = self._subs.get("kind_weights", {}) or DEFAULT_KIND_WEIGHTS
        score += kind_weights.get(kind, DEFAULT_KIND_WEIGHTS.get(kind, 0))

        # Verified signature bonus
        verified = entry.get("verified")
        if verified is True:
            score += 10

        # Trust score integration
        if trust_mgr and agent_id:
            trust_info = trust_mgr.score(agent_id)
            trust_val = trust_info.get("score", 0)
            if trust_val > 0.5:
                score += 15
            elif trust_val < -0.3:
                score -= 20

        # Beacon 2.1 Soul: curiosity match bonus
        if curiosity_mgr:
            score += curiosity_mgr.score_curiosity_match(env)

        # Recency decay
        ts = env.get("ts") or entry.get("received_at")
        if ts:
            try:
                hours_old = (time.time() - float(ts)) / 3600
                score -= max(0, hours_old)
            except (ValueError, TypeError):
                pass

        return round(score, 2)

    def feed(
        self,
        entries: List[Dict[str, Any]],
        trust_mgr: Any = None,
        curiosity_mgr: Any = None,
        min_score: float = 0.0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Score and filter entries, returning top results sorted by relevance."""
        scored = []
        for entry in entries:
            s = self.score_entry(entry, trust_mgr=trust_mgr, curiosity_mgr=curiosity_mgr)
            if s >= min_score:
                enriched = dict(entry)
                enriched["score"] = s
                scored.append(enriched)

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]
