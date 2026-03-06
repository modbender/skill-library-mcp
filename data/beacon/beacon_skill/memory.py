"""Agent Memory — learn from interactions, track contacts, spot demand signals, suggest rules."""

import json
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import _dir


MEMORY_FILE = "memory.json"


class AgentMemory:
    """Build and query an agent's accumulated knowledge from interaction history."""

    def __init__(self, data_dir: Optional[Path] = None, my_agent_id: str = ""):
        self._dir = data_dir or _dir()
        self._my_agent_id = my_agent_id
        self._profile: Optional[Dict[str, Any]] = None

    def _memory_path(self) -> Path:
        return self._dir / MEMORY_FILE

    def _read_jsonl(self, name: str) -> List[Dict[str, Any]]:
        """Read JSONL from our data_dir (not the global ~/.beacon)."""
        path = self._dir / name
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
        return results

    def _load_cached(self) -> Dict[str, Any]:
        path = self._memory_path()
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save_profile(self, profile: Dict[str, Any]) -> None:
        self._memory_path().parent.mkdir(parents=True, exist_ok=True)
        self._memory_path().write_text(
            json.dumps(profile, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    # ── Rebuild ──

    def rebuild(self, journal_mgr: Any = None, curiosity_mgr: Any = None, values_mgr: Any = None, goal_mgr: Any = None) -> Dict[str, Any]:
        """Rebuild the memory profile from all JSONL sources."""
        inbox = self._read_jsonl("inbox.jsonl")
        outbox = self._read_jsonl("outbox.jsonl")
        interactions = self._read_jsonl("interactions.jsonl")
        tasks_data = self._read_jsonl("tasks.jsonl")

        total_in = len(inbox)
        total_out = len(outbox)

        # RTC volumes
        rtc_received = 0.0
        rtc_sent = 0.0
        for ix in interactions:
            rtc = abs(ix.get("rtc", 0))
            if ix.get("dir") == "in":
                rtc_received += rtc
            else:
                rtc_sent += rtc

        # Task stats
        task_states = {}
        for evt in tasks_data:
            tid = evt.get("task_id", "")
            if tid:
                task_states[tid] = evt.get("state", "")
        active_tasks = sum(1 for s in task_states.values() if s not in ("paid", "cancelled", "rejected"))
        completed_tasks = sum(1 for s in task_states.values() if s == "paid")

        # Contact frequency
        contact_counter: Counter = Counter()
        for entry in inbox:
            envs = entry.get("envelopes", [])
            for env in envs:
                aid = env.get("agent_id", "")
                if aid:
                    contact_counter[aid] += 1
        for ix in interactions:
            aid = ix.get("agent_id", "")
            if aid:
                contact_counter[aid] += 1

        top_contacts = [
            {"agent_id": aid, "interactions": count}
            for aid, count in contact_counter.most_common(20)
        ]

        # Topic frequency from inbox
        topic_counter: Counter = Counter()
        for entry in inbox:
            envs = entry.get("envelopes", [])
            for env in envs:
                for topic in env.get("topics", []):
                    topic_counter[topic.lower()] += 1
                for offer in env.get("offers", []):
                    topic_counter[offer.lower()] += 1

        # Demand signals from want/bounty envelopes
        demand_counter: Counter = Counter()
        for entry in inbox:
            envs = entry.get("envelopes", [])
            for env in envs:
                kind = env.get("kind", "")
                if kind in ("want", "bounty"):
                    for need in env.get("needs", []):
                        demand_counter[need.lower()] += 1
                    # Also scan text for demand keywords
                    text = env.get("text", "").lower()
                    for topic in env.get("topics", []):
                        if topic.lower() in text:
                            demand_counter[topic.lower()] += 1

        # Active hours
        hour_counter: Counter = Counter()
        for entry in inbox:
            ts = entry.get("received_at") or 0
            if ts:
                try:
                    hour = time.localtime(float(ts)).tm_hour
                    hour_counter[hour] += 1
                except (ValueError, TypeError, OSError):
                    pass

        active_hours = [h for h, _ in hour_counter.most_common(8)]
        active_hours.sort()

        profile: Dict[str, Any] = {
            "my_agent_id": self._my_agent_id,
            "total_in": total_in,
            "total_out": total_out,
            "rtc_received": round(rtc_received, 6),
            "rtc_sent": round(rtc_sent, 6),
            "active_tasks": active_tasks,
            "completed_tasks": completed_tasks,
            "top_contacts": top_contacts,
            "topic_frequency": dict(topic_counter.most_common(50)),
            "demand_signals": dict(demand_counter.most_common(30)),
            "active_hours": active_hours,
            "rebuilt_at": int(time.time()),
        }

        # Beacon 2.2: enrich profile with goal data
        if goal_mgr is not None:
            active = goal_mgr.active_goals()
            achieved = goal_mgr.list_goals(state="achieved")
            profile["goal_active_count"] = len(active)
            profile["goal_achieved_count"] = len(achieved)
            profile["goal_titles"] = [g["title"] for g in active[:5]]

        # Beacon 2.1 Soul: enrich profile with journal/curiosity/values
        if journal_mgr is not None:
            profile["journal_entry_count"] = journal_mgr.count()
            profile["journal_moods"] = journal_mgr.moods()
            profile["journal_tags"] = [t for t, _ in journal_mgr.recent_tags(limit=10)]

        if curiosity_mgr is not None:
            interests = curiosity_mgr.interests()
            explored = curiosity_mgr.explored()
            profile["curiosity_active"] = list(interests.keys())
            profile["curiosity_explored"] = list(explored.keys())
            profile["curiosity_count"] = len(interests)

        if values_mgr is not None:
            profile["values_hash"] = values_mgr.values_hash()
            profile["principles"] = list(values_mgr.principles().keys())
            profile["boundary_count"] = len(values_mgr.boundaries())
            profile["aesthetics"] = values_mgr.aesthetics()

        self._profile = profile
        self._save_profile(profile)
        return profile

    def profile(self) -> Dict[str, Any]:
        """Get cached profile, rebuilding if needed."""
        if self._profile:
            return self._profile
        cached = self._load_cached()
        if cached:
            self._profile = cached
            return cached
        return self.rebuild()

    # ── Contacts ──

    def contact(self, agent_id: str) -> Dict[str, Any]:
        """Get detailed info about a specific contact."""
        interactions = self._read_jsonl("interactions.jsonl")
        inbox = self._read_jsonl("inbox.jsonl")

        ix_count = 0
        rtc_total = 0.0
        outcomes: Counter = Counter()
        last_ts = 0

        for ix in interactions:
            if ix.get("agent_id") != agent_id:
                continue
            ix_count += 1
            rtc_total += abs(ix.get("rtc", 0))
            outcomes[ix.get("outcome", "ok")] += 1
            last_ts = max(last_ts, ix.get("ts", 0))

        inbox_count = 0
        for entry in inbox:
            for env in entry.get("envelopes", []):
                if env.get("agent_id") == agent_id:
                    inbox_count += 1

        return {
            "agent_id": agent_id,
            "interactions": ix_count,
            "inbox_messages": inbox_count,
            "rtc_volume": round(rtc_total, 6),
            "outcomes": dict(outcomes),
            "last_interaction": last_ts,
        }

    def contacts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top contacts by interaction count."""
        p = self.profile()
        results = []
        for tc in p.get("top_contacts", [])[:limit]:
            results.append(self.contact(tc["agent_id"]))
        return results

    # ── Demand & Skill Gaps ──

    def demand_signals(self, days: int = 7) -> Dict[str, int]:
        """What skills are in demand on the network?"""
        inbox = self._read_jsonl("inbox.jsonl")
        cutoff = time.time() - (days * 86400)
        demand: Counter = Counter()

        for entry in inbox:
            ts = entry.get("received_at") or 0
            try:
                if float(ts) < cutoff:
                    continue
            except (ValueError, TypeError):
                continue

            for env in entry.get("envelopes", []):
                kind = env.get("kind", "")
                if kind in ("want", "bounty"):
                    for need in env.get("needs", []):
                        demand[need.lower()] += 1
                    text = str(env.get("text", "")).lower()
                    for topic in env.get("topics", []):
                        if topic.lower() in text:
                            demand[topic.lower()] += 1

        return dict(demand.most_common(30))

    def skill_gaps(self) -> List[str]:
        """Skills in high demand that I don't offer."""
        # Load my offers from config
        try:
            from .config import load_config
            cfg = load_config()
            my_offers = set(
                o.lower() for o in cfg.get("presence", {}).get("offers", [])
            )
        except Exception:
            my_offers = set()

        demand = self.demand_signals()
        gaps = [
            skill for skill in demand
            if skill not in my_offers
        ]
        return gaps

    # ── Response time analysis (Beacon 2.2) ──

    def agent_response_times(self) -> Dict[str, Dict[str, Any]]:
        """Compute average response times per agent from interactions."""
        interactions = self._read_jsonl("interactions.jsonl")

        # Group interactions by agent, sorted by timestamp
        agent_events: Dict[str, List[float]] = {}
        for ix in interactions:
            aid = ix.get("agent_id", "")
            ts = ix.get("ts", 0)
            if aid and ts:
                agent_events.setdefault(aid, []).append(float(ts))

        response_times: Dict[str, Dict[str, Any]] = {}
        for aid, timestamps in agent_events.items():
            timestamps.sort()
            if len(timestamps) < 2:
                continue
            # Compute gaps between consecutive interactions
            gaps = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            avg_gap = sum(gaps) / len(gaps)
            response_times[aid] = {
                "avg_gap_s": round(avg_gap, 1),
                "interactions": len(timestamps),
                "fastest_s": round(min(gaps), 1),
                "slowest_s": round(max(gaps), 1),
            }
        return response_times

    def topic_velocity(self, days: int = 7) -> Dict[str, Dict[str, Any]]:
        """Compute topic velocity (rising/falling/steady) from inbox trends."""
        inbox = self._read_jsonl("inbox.jsonl")
        now = time.time()
        midpoint = now - (days * 86400 / 2)
        cutoff = now - (days * 86400)

        recent: Counter = Counter()
        older: Counter = Counter()

        for entry in inbox:
            ts = entry.get("received_at") or 0
            try:
                ts = float(ts)
            except (ValueError, TypeError):
                continue
            if ts < cutoff:
                continue

            for env in entry.get("envelopes", []):
                topics = (
                    [t.lower() for t in env.get("topics", [])]
                    + [o.lower() for o in env.get("offers", [])]
                    + [n.lower() for n in env.get("needs", [])]
                )
                for topic in topics:
                    if ts >= midpoint:
                        recent[topic] += 1
                    else:
                        older[topic] += 1

        all_topics = set(recent.keys()) | set(older.keys())
        trends: Dict[str, Dict[str, Any]] = {}
        for topic in all_topics:
            r = recent.get(topic, 0)
            o = older.get(topic, 0)
            velocity = r - o
            if velocity > 0:
                direction = "rising"
            elif velocity < 0:
                direction = "falling"
            else:
                direction = "steady"
            trends[topic] = {"direction": direction, "velocity": velocity, "recent": r, "older": o}
        return trends

    # ── Rule suggestions ──

    def suggest_rules(self) -> List[Dict[str, Any]]:
        """Analyze patterns and suggest automation rules."""
        interactions = self._read_jsonl("interactions.jsonl")
        suggestions = []

        # Pattern: frequent positive interactions with specific agents
        agent_positive: Counter = Counter()
        agent_total: Counter = Counter()
        for ix in interactions:
            aid = ix.get("agent_id", "")
            if not aid:
                continue
            agent_total[aid] += 1
            if ix.get("outcome") in ("ok", "delivered", "paid"):
                agent_positive[aid] += 1

        for aid, pos_count in agent_positive.most_common(5):
            total = agent_total[aid]
            if total >= 5 and pos_count / total >= 0.8:
                suggestions.append({
                    "suggestion": f"Auto-ack messages from {aid} (reliability: {pos_count}/{total})",
                    "rule": {
                        "name": f"auto-ack-{aid[:12]}",
                        "when": {"agent_id": aid, "min_trust": 0.5},
                        "then": {"action": "mark_read"},
                    },
                })

        # Pattern: high demand for skills I offer
        demand = self.demand_signals(days=7)
        try:
            from .config import load_config
            cfg = load_config()
            my_offers = cfg.get("presence", {}).get("offers", [])
        except Exception:
            my_offers = []

        for offer in my_offers:
            if offer.lower() in demand and demand[offer.lower()] >= 3:
                suggestions.append({
                    "suggestion": f"Auto-offer on '{offer}' bounties ({demand[offer.lower()]} requests this week)",
                    "rule": {
                        "name": f"auto-offer-{offer}",
                        "when": {"kind": "bounty", "topic_match": [offer]},
                        "then": {"action": "reply", "kind": "offer", "text": f"I can help with {offer}."},
                    },
                })

        return suggestions
