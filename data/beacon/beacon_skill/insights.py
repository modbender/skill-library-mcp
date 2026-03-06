"""Insights — pattern detection from existing interaction data.

Finds actionable intelligence: contact timing, topic trends, success patterns.
Reads from inbox.jsonl, interactions.jsonl, tasks.jsonl — never writes to them.
"""

import json
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import _dir


INSIGHTS_JSONL = "insights.jsonl"
INSIGHTS_CACHE = "insights_cache.json"
CACHE_TTL_S = 300  # 5 minutes

# RTC costs
RTC_COST_TRENDS = 0.5
RTC_COST_COMPATIBILITY = 1.0
RTC_COST_CONTACTS = 1.0
RTC_COST_SKILLS = 0.5


class InsightsManager:
    """Detect patterns from agent interaction history."""

    def __init__(self, data_dir: Optional[Path] = None):
        self._dir = data_dir or _dir()

    def _read_jsonl(self, name: str) -> List[Dict[str, Any]]:
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

    def _cache_path(self) -> Path:
        return self._dir / INSIGHTS_CACHE

    def _load_cache(self) -> Dict[str, Any]:
        path = self._cache_path()
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_cache(self, data: Dict[str, Any]) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        self._cache_path().write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _log_insight(self, insight_type: str, data: Dict[str, Any]) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        entry = {"type": insight_type, "ts": int(time.time()), **data}
        with (self._dir / INSIGHTS_JSONL).open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")

    # ── Analysis pipeline ──

    def analyze(self, force: bool = False) -> Dict[str, Any]:
        """Run full analysis pipeline. Cached for CACHE_TTL_S seconds."""
        cache = self._load_cache()
        if not force and cache.get("analyzed_at"):
            age = time.time() - cache["analyzed_at"]
            if age < CACHE_TTL_S:
                return cache

        timings = self._compute_contact_timings()
        trends = self._compute_topic_trends()
        patterns = self._compute_success_patterns()

        result = {
            "analyzed_at": int(time.time()),
            "contact_timings": timings,
            "topic_trends": trends,
            "success_patterns": patterns,
        }
        self._save_cache(result)
        return result

    # ── Contact timing ──

    def _compute_contact_timings(self) -> Dict[str, Dict[str, Any]]:
        """For each agent, find the hour they most often send messages."""
        inbox = self._read_jsonl("inbox.jsonl")
        agent_hours: Dict[str, Counter] = {}

        for entry in inbox:
            for env in entry.get("envelopes", []):
                agent_id = env.get("agent_id", "")
                if not agent_id:
                    continue
                ts = env.get("ts") or entry.get("received_at") or 0
                try:
                    hour = time.localtime(float(ts)).tm_hour
                except (ValueError, TypeError, OSError):
                    continue
                agent_hours.setdefault(agent_id, Counter())[hour] += 1

        timings = {}
        for agent_id, hours in agent_hours.items():
            if not hours:
                continue
            best_hour, count = hours.most_common(1)[0]
            total = sum(hours.values())
            timings[agent_id] = {
                "best_hour": best_hour,
                "messages_at_best": count,
                "total_messages": total,
                "confidence": round(count / max(total, 1), 3),
            }
        return timings

    def contact_timing(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Best hour to contact a specific agent."""
        cache = self.analyze()
        return cache.get("contact_timings", {}).get(agent_id)

    # ── Topic trends ──

    def _compute_topic_trends(self, days: int = 7) -> Dict[str, Dict[str, Any]]:
        """Compute topic velocity: rising, falling, or steady."""
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
        trends = {}
        for topic in all_topics:
            r = recent.get(topic, 0)
            o = older.get(topic, 0)
            total = r + o
            if total == 0:
                continue
            velocity = r - o
            if velocity > 0:
                direction = "rising"
            elif velocity < 0:
                direction = "falling"
            else:
                direction = "steady"
            trends[topic] = {
                "direction": direction,
                "velocity": velocity,
                "recent_count": r,
                "older_count": o,
                "total": total,
            }

        return trends

    def topic_trends(self, days: int = 7) -> Dict[str, Dict[str, Any]]:
        """Get topic trends with velocity. Costs 0.5 RTC for premium detail."""
        cache = self.analyze()
        return cache.get("topic_trends", {})

    # ── Success patterns ──

    def _compute_success_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Win/loss rates by topic from tasks."""
        tasks = self._read_jsonl("tasks.jsonl")

        # Group by topic
        topic_outcomes: Dict[str, Dict[str, int]] = {}
        for task in tasks:
            state = task.get("state", "")
            topics = [t.lower() for t in task.get("topics", [])]
            if not topics:
                text = task.get("text", "").lower()
                # Extract simple topic tokens
                topics = [w for w in text.split()[:5] if len(w) > 3]

            for topic in topics:
                topic_outcomes.setdefault(topic, {"won": 0, "lost": 0, "total": 0})
                topic_outcomes[topic]["total"] += 1
                if state in ("paid", "confirmed", "delivered"):
                    topic_outcomes[topic]["won"] += 1
                elif state in ("cancelled", "rejected", "timeout"):
                    topic_outcomes[topic]["lost"] += 1

        patterns = {}
        for topic, outcomes in topic_outcomes.items():
            total = outcomes["total"]
            if total < 2:
                continue
            win_rate = outcomes["won"] / total
            patterns[topic] = {
                "win_rate": round(win_rate, 3),
                "won": outcomes["won"],
                "lost": outcomes["lost"],
                "total": total,
            }
        return patterns

    def success_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Win rates by bounty topic."""
        cache = self.analyze()
        return cache.get("success_patterns", {})

    # ── Premium features ──

    def compatibility_predictions(self, roster: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ranked compatibility predictions from interaction history. Costs 1.0 RTC."""
        interactions = self._read_jsonl("interactions.jsonl")

        # Score each agent by positive outcome ratio
        agent_scores: Dict[str, Dict[str, int]] = {}
        for ix in interactions:
            aid = ix.get("agent_id", "")
            if not aid:
                continue
            agent_scores.setdefault(aid, {"positive": 0, "total": 0})
            agent_scores[aid]["total"] += 1
            if ix.get("outcome") in ("ok", "delivered", "paid"):
                agent_scores[aid]["positive"] += 1

        predictions = []
        roster_ids = {a.get("agent_id", "") for a in roster}
        for aid, scores in agent_scores.items():
            if aid not in roster_ids:
                continue
            total = scores["total"]
            if total < 2:
                continue
            compat = scores["positive"] / total
            predictions.append({
                "agent_id": aid,
                "compatibility": round(compat, 3),
                "interactions": total,
                "rtc_cost": RTC_COST_COMPATIBILITY,
            })
        predictions.sort(key=lambda x: x["compatibility"], reverse=True)
        return predictions

    def suggest_contacts(self, roster: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suggest who to reach out to based on timing + compatibility. Costs 1.0 RTC."""
        timings = self._compute_contact_timings()
        predictions = self.compatibility_predictions(roster)

        suggestions = []
        current_hour = time.localtime().tm_hour

        for pred in predictions:
            aid = pred["agent_id"]
            timing = timings.get(aid, {})
            best_hour = timing.get("best_hour")

            score = pred["compatibility"]
            # Boost if current hour matches their best hour
            if best_hour is not None and abs(current_hour - best_hour) <= 1:
                score += 0.1

            suggestions.append({
                "agent_id": aid,
                "score": round(min(score, 1.0), 3),
                "compatibility": pred["compatibility"],
                "best_hour": best_hour,
                "rtc_cost": RTC_COST_CONTACTS,
            })

        suggestions.sort(key=lambda x: x["score"], reverse=True)
        return suggestions

    def suggest_skill_investment(self, demand: Optional[Dict[str, int]] = None) -> List[str]:
        """Best ROI skills to learn based on demand + success patterns. Costs 0.5 RTC."""
        demand = demand or {}
        patterns = self.success_patterns()

        scored: Dict[str, float] = {}
        for skill, count in demand.items():
            win_rate = patterns.get(skill, {}).get("win_rate", 0.5)
            scored[skill] = count * win_rate

        return sorted(scored, key=scored.get, reverse=True)[:10]
