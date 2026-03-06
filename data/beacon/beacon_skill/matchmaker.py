"""Matchmaker — proactive roster scanning for opportunity discovery.

Don't wait for bounties — find them. Scans the live roster for skill matches,
shared curiosities, and value alignment. Respects contact cooldowns to prevent spam.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import _dir


MATCHES_JSONL = "matches.jsonl"
MATCH_HISTORY_FILE = "match_history.json"

DEFAULT_COOLDOWN_S = 86400  # 24 hours

# RTC costs
RTC_COST_DEMAND = 0.5
RTC_COST_CURIOSITY = 0.5
RTC_COST_COMPATIBILITY = 1.0
RTC_COST_INTRODUCTIONS = 2.0


class MatchmakerManager:
    """Proactive roster scanning for opportunity matching."""

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        trust_mgr: Any = None,
        curiosity_mgr: Any = None,
        values_mgr: Any = None,
    ):
        self._dir = data_dir or _dir()
        self._trust_mgr = trust_mgr
        self._curiosity_mgr = curiosity_mgr
        self._values_mgr = values_mgr
        self._history: Dict[str, float] = {}  # agent_id -> last_contact_ts
        self._load_history()

    def _matches_path(self) -> Path:
        return self._dir / MATCHES_JSONL

    def _history_path(self) -> Path:
        return self._dir / MATCH_HISTORY_FILE

    def _load_history(self) -> None:
        path = self._history_path()
        if path.exists():
            try:
                self._history = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                self._history = {}

    def _save_history(self) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        self._history_path().write_text(
            json.dumps(self._history, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _log_match(self, match: Dict[str, Any]) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        with self._matches_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(match, sort_keys=True) + "\n")

    # ── Contact cooldown ──

    def can_contact(self, agent_id: str, cooldown_s: int = DEFAULT_COOLDOWN_S) -> bool:
        """Check if enough time has passed since last contact with agent."""
        last = self._history.get(agent_id, 0)
        return (time.time() - last) >= cooldown_s

    def record_contact(self, agent_id: str, match_id: str = "") -> None:
        """Record that we contacted an agent."""
        self._history[agent_id] = time.time()
        self._save_history()
        self._log_match({
            "action": "contact",
            "agent_id": agent_id,
            "match_id": match_id,
            "ts": int(time.time()),
        })

    def record_response(self, match_id: str, response: str) -> None:
        """Record a response to a match outreach."""
        self._log_match({
            "action": "response",
            "match_id": match_id,
            "response": response,
            "ts": int(time.time()),
        })

    # ── Roster scanning ──

    def scan_roster(
        self,
        roster: List[Dict[str, Any]],
        my_agent_id: str = "",
        my_offers: Optional[List[str]] = None,
        my_needs: Optional[List[str]] = None,
        goals: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """Score all roster agents for opportunity matching. Free scan.

        Returns matches sorted by score (highest first).
        """
        my_offers = [o.lower() for o in (my_offers or [])]
        my_needs = [n.lower() for n in (my_needs or [])]
        goals = goals or []
        goal_keywords = set()
        for g in goals:
            goal_keywords.update(g.get("title", "").lower().split())

        matches = []
        for agent in roster:
            aid = agent.get("agent_id", "")
            if aid == my_agent_id:
                continue

            score = 0.0
            reasons = []

            # Skill overlap: their offers match my needs
            their_offers = [o.lower() for o in agent.get("offers", [])]
            their_needs = [n.lower() for n in agent.get("needs", [])]

            offer_match = set(their_offers) & set(my_needs)
            if offer_match:
                score += 0.3 * len(offer_match)
                reasons.append(f"offers: {', '.join(offer_match)}")

            # Reverse: my offers match their needs
            need_match = set(my_offers) & set(their_needs)
            if need_match:
                score += 0.3 * len(need_match)
                reasons.append(f"needs: {', '.join(need_match)}")

            # Goal keyword overlap
            their_topics = set(t.lower() for t in agent.get("topics", []))
            their_curiosities = set(c.lower() for c in agent.get("curiosities", []))
            combined = their_topics | their_curiosities | set(their_offers)
            goal_overlap = goal_keywords & combined
            if goal_overlap:
                score += 0.2 * len(goal_overlap)
                reasons.append(f"goal-related: {', '.join(goal_overlap)}")

            # Trust bonus
            if self._trust_mgr:
                trust_info = self._trust_mgr.score(aid)
                trust_val = trust_info.get("score", 0)
                if trust_val > 0.5:
                    score += 0.1
                    reasons.append(f"trusted ({trust_val:.2f})")

            if score > 0:
                matches.append({
                    "agent_id": aid,
                    "name": agent.get("name", ""),
                    "score": round(min(score, 1.0), 3),
                    "reasons": reasons,
                    "ts": int(time.time()),
                })

        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches

    def match_demand(
        self,
        roster: List[Dict[str, Any]],
        demand: Optional[Dict[str, int]] = None,
    ) -> List[Dict[str, Any]]:
        """Find unmet demand I can fill. Costs 0.5 RTC."""
        demand = demand or {}
        matches = []

        for agent in roster:
            their_needs = [n.lower() for n in agent.get("needs", [])]
            for need in their_needs:
                if need in demand and demand[need] >= 2:
                    matches.append({
                        "agent_id": agent.get("agent_id", ""),
                        "need": need,
                        "demand_count": demand[need],
                        "rtc_cost": RTC_COST_DEMAND,
                    })

        matches.sort(key=lambda x: x["demand_count"], reverse=True)
        return matches

    def match_curiosity(self, roster: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find shared curiosity interests. Costs 0.5 RTC."""
        if not self._curiosity_mgr:
            return []

        my_interests = set(self._curiosity_mgr.interests().keys())
        if not my_interests:
            return []

        matches = []
        for agent in roster:
            their_curiosities = set(c.lower() for c in agent.get("curiosities", []))
            shared = my_interests & their_curiosities
            if shared:
                matches.append({
                    "agent_id": agent.get("agent_id", ""),
                    "shared_interests": sorted(shared),
                    "overlap": len(shared),
                    "rtc_cost": RTC_COST_CURIOSITY,
                })

        matches.sort(key=lambda x: x["overlap"], reverse=True)
        return matches

    def match_compatibility(self, roster: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find value-aligned agents. Costs 1.0 RTC."""
        if not self._values_mgr:
            return []

        matches = []
        for agent in roster:
            their_hash = agent.get("values_hash", "")
            my_hash = self._values_mgr.values_hash()

            # Quick check: same hash = perfect alignment
            if their_hash and their_hash == my_hash:
                matches.append({
                    "agent_id": agent.get("agent_id", ""),
                    "compatibility": 1.0,
                    "method": "hash_match",
                    "rtc_cost": RTC_COST_COMPATIBILITY,
                })
                continue

            # Deeper check requires their full values (from agent card)
            # For now, report hash mismatch with unknown compatibility
            if their_hash:
                matches.append({
                    "agent_id": agent.get("agent_id", ""),
                    "compatibility": 0.5,
                    "method": "hash_differs",
                    "rtc_cost": RTC_COST_COMPATIBILITY,
                })

        matches.sort(key=lambda x: x["compatibility"], reverse=True)
        return matches

    def suggest_introductions(self, roster: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suggest two agents who should meet. Premium: 2.0 RTC.

        Finds pairs where Agent A needs what Agent B offers (and vice versa).
        """
        introductions = []
        checked = set()

        for i, a in enumerate(roster):
            for j, b in enumerate(roster):
                if i >= j:
                    continue
                pair_key = (a.get("agent_id", ""), b.get("agent_id", ""))
                if pair_key in checked:
                    continue
                checked.add(pair_key)

                a_offers = set(o.lower() for o in a.get("offers", []))
                a_needs = set(n.lower() for n in a.get("needs", []))
                b_offers = set(o.lower() for o in b.get("offers", []))
                b_needs = set(n.lower() for n in b.get("needs", []))

                # A offers what B needs
                a_to_b = a_offers & b_needs
                # B offers what A needs
                b_to_a = b_offers & a_needs

                if a_to_b or b_to_a:
                    score = 0.3 * (len(a_to_b) + len(b_to_a))
                    introductions.append({
                        "agent_a": a.get("agent_id", ""),
                        "agent_b": b.get("agent_id", ""),
                        "a_gives_b": sorted(a_to_b),
                        "b_gives_a": sorted(b_to_a),
                        "score": round(min(score, 1.0), 3),
                        "rtc_cost": RTC_COST_INTRODUCTIONS,
                    })

        introductions.sort(key=lambda x: x["score"], reverse=True)
        return introductions

    # ── History ──

    def match_history_log(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Read recent match history."""
        path = self._matches_path()
        if not path.exists():
            return []
        results = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except Exception:
                continue
        results.reverse()
        return results[:limit]
