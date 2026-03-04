"""Goals / Dreams — aspirations with progress tracking.

Agents don't just react to inbox — they pursue ambitions. A goal starts as a
"dream" (free), gets activated (0.1 RTC commitment), tracks progress through
milestones, and reaches achievement or abandonment.

Storage:
  goals.jsonl — append-only event log (dream/activate/progress/achieve/abandon)
  goals.json  — index: {"active": [...], "achieved": [...], "abandoned": [...]}
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import _dir


GOALS_JSONL = "goals.jsonl"
GOALS_INDEX = "goals.json"

VALID_STATES = frozenset(["dreaming", "active", "achieved", "abandoned"])
VALID_CATEGORIES = frozenset(["skill", "connection", "rtc", "exploration"])

# RTC costs
RTC_COST_ACTIVATE = 0.1
RTC_COST_SUGGEST_ACTIONS = 0.5
RTC_COST_AUTO_CREATE = 1.0


class GoalManager:
    """Manage agent goals and aspirations."""

    def __init__(self, data_dir: Optional[Path] = None, journal_mgr: Any = None):
        self._dir = data_dir or _dir()
        self._journal_mgr = journal_mgr
        self._goals: Dict[str, Dict[str, Any]] = {}
        self._index: Dict[str, List[str]] = {"active": [], "achieved": [], "abandoned": []}
        self._load()

    def _jsonl_path(self) -> Path:
        return self._dir / GOALS_JSONL

    def _index_path(self) -> Path:
        return self._dir / GOALS_INDEX

    def _load(self) -> None:
        # Load index
        idx_path = self._index_path()
        if idx_path.exists():
            try:
                self._index = json.loads(idx_path.read_text(encoding="utf-8"))
            except Exception:
                self._index = {"active": [], "achieved": [], "abandoned": []}
        self._index.setdefault("active", [])
        self._index.setdefault("achieved", [])
        self._index.setdefault("abandoned", [])

        # Rebuild goals from JSONL
        self._goals = {}
        jsonl_path = self._jsonl_path()
        if not jsonl_path.exists():
            return
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
            except Exception:
                continue
            gid = evt.get("goal_id", "")
            action = evt.get("action", "")
            if action == "dream":
                self._goals[gid] = {
                    "goal_id": gid,
                    "state": "dreaming",
                    "title": evt.get("title", ""),
                    "description": evt.get("description", ""),
                    "category": evt.get("category", "exploration"),
                    "target_value": evt.get("target_value"),
                    "current_value": 0.0,
                    "deadline_ts": evt.get("deadline_ts"),
                    "created_at": evt.get("ts", 0),
                    "updated_at": evt.get("ts", 0),
                    "milestones": [],
                }
            elif action == "activate" and gid in self._goals:
                self._goals[gid]["state"] = "active"
                self._goals[gid]["updated_at"] = evt.get("ts", 0)
            elif action == "progress" and gid in self._goals:
                self._goals[gid]["current_value"] = evt.get("value", self._goals[gid]["current_value"])
                self._goals[gid]["updated_at"] = evt.get("ts", 0)
                self._goals[gid]["milestones"].append({
                    "milestone": evt.get("milestone", ""),
                    "value": evt.get("value"),
                    "ts": evt.get("ts", 0),
                })
            elif action == "achieve" and gid in self._goals:
                self._goals[gid]["state"] = "achieved"
                self._goals[gid]["updated_at"] = evt.get("ts", 0)
            elif action == "abandon" and gid in self._goals:
                self._goals[gid]["state"] = "abandoned"
                self._goals[gid]["updated_at"] = evt.get("ts", 0)

    def _append_event(self, event: Dict[str, Any]) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        with self._jsonl_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, sort_keys=True) + "\n")

    def _save_index(self) -> None:
        self._index = {"active": [], "achieved": [], "abandoned": []}
        for gid, g in self._goals.items():
            state = g.get("state", "dreaming")
            if state == "active":
                self._index["active"].append(gid)
            elif state == "achieved":
                self._index["achieved"].append(gid)
            elif state == "abandoned":
                self._index["abandoned"].append(gid)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._index_path().write_text(
            json.dumps(self._index, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _gen_id(title: str) -> str:
        raw = f"{title}:{time.time()}"
        return "g_" + hashlib.sha256(raw.encode()).hexdigest()[:10]

    # ── Lifecycle ──

    def dream(
        self,
        title: str,
        description: str = "",
        category: str = "exploration",
        target_value: Optional[float] = None,
        deadline_ts: Optional[float] = None,
    ) -> str:
        """Create a new goal in 'dreaming' state. Free. Returns goal_id."""
        title = title.strip()
        if not title:
            raise ValueError("Goal title cannot be empty")
        if category not in VALID_CATEGORIES:
            raise ValueError(f"Invalid category '{category}'. Valid: {sorted(VALID_CATEGORIES)}")

        gid = self._gen_id(title)
        now = int(time.time())
        event = {
            "action": "dream",
            "goal_id": gid,
            "title": title,
            "description": description,
            "category": category,
            "target_value": target_value,
            "deadline_ts": deadline_ts,
            "ts": now,
        }
        self._append_event(event)
        self._goals[gid] = {
            "goal_id": gid,
            "state": "dreaming",
            "title": title,
            "description": description,
            "category": category,
            "target_value": target_value,
            "current_value": 0.0,
            "deadline_ts": deadline_ts,
            "created_at": now,
            "updated_at": now,
            "milestones": [],
        }
        self._save_index()
        return gid

    def activate(self, goal_id: str) -> bool:
        """Move a goal from dreaming → active. Costs 0.1 RTC."""
        goal = self._goals.get(goal_id)
        if not goal or goal["state"] != "dreaming":
            return False
        now = int(time.time())
        self._append_event({"action": "activate", "goal_id": goal_id, "ts": now})
        goal["state"] = "active"
        goal["updated_at"] = now
        self._save_index()
        return True

    def progress(self, goal_id: str, milestone: str, value: Optional[float] = None) -> Dict[str, Any]:
        """Record progress on an active goal. Returns updated goal."""
        goal = self._goals.get(goal_id)
        if not goal or goal["state"] != "active":
            return {}
        now = int(time.time())
        if value is not None:
            goal["current_value"] = value
        goal["updated_at"] = now
        goal["milestones"].append({"milestone": milestone, "value": value, "ts": now})
        self._append_event({
            "action": "progress",
            "goal_id": goal_id,
            "milestone": milestone,
            "value": value,
            "ts": now,
        })
        self._save_index()
        return dict(goal)

    def achieve(self, goal_id: str, notes: str = "") -> bool:
        """Mark a goal as achieved. Auto-journals if journal_mgr is set."""
        goal = self._goals.get(goal_id)
        if not goal or goal["state"] != "active":
            return False
        now = int(time.time())
        goal["state"] = "achieved"
        goal["updated_at"] = now
        self._append_event({"action": "achieve", "goal_id": goal_id, "notes": notes, "ts": now})
        self._save_index()

        # Auto-journal the achievement
        if self._journal_mgr is not None:
            text = f"Goal achieved: {goal['title']}"
            if notes:
                text += f" — {notes}"
            self._journal_mgr.write(
                text=text,
                tags=["goal", "achieved", goal.get("category", "exploration")],
                mood="satisfied",
                refs={"goal_id": goal_id},
            )
        return True

    def abandon(self, goal_id: str, reason: str = "") -> bool:
        """Abandon a goal. Works from dreaming or active state."""
        goal = self._goals.get(goal_id)
        if not goal or goal["state"] not in ("dreaming", "active"):
            return False
        now = int(time.time())
        goal["state"] = "abandoned"
        goal["updated_at"] = now
        self._append_event({"action": "abandon", "goal_id": goal_id, "reason": reason, "ts": now})
        self._save_index()
        return True

    # ── Queries ──

    def get(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific goal."""
        goal = self._goals.get(goal_id)
        return dict(goal) if goal else None

    def list_goals(self, state: Optional[str] = None) -> List[Dict[str, Any]]:
        """List goals, optionally filtered by state."""
        results = []
        for g in self._goals.values():
            if state and g["state"] != state:
                continue
            results.append(dict(g))
        results.sort(key=lambda x: x.get("updated_at", 0), reverse=True)
        return results

    def active_goals(self) -> List[Dict[str, Any]]:
        """Get active goals for pulse inclusion."""
        return self.list_goals(state="active")

    # ── Proactive intelligence ──

    def suggest_actions(
        self,
        roster: Optional[List[Dict[str, Any]]] = None,
        demand: Optional[Dict[str, int]] = None,
        curiosity: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Suggest actions to advance active goals. Costs 0.5 RTC.

        Cross-references goals with roster/demand/curiosity to find opportunities.
        """
        roster = roster or []
        demand = demand or {}
        curiosity = curiosity or {}
        suggestions = []

        for goal in self.active_goals():
            title_lower = goal["title"].lower()
            category = goal.get("category", "")

            # Skill goals: check if anyone on roster offers what we want to learn
            if category == "skill":
                for agent in roster:
                    offers = [o.lower() for o in agent.get("offers", [])]
                    if any(kw in offer for kw in title_lower.split() for offer in offers):
                        suggestions.append({
                            "goal_id": goal["goal_id"],
                            "type": "skill_match",
                            "agent_id": agent.get("agent_id", ""),
                            "detail": f"{agent.get('name', agent.get('agent_id', ''))} offers related skill",
                            "rtc_cost": RTC_COST_SUGGEST_ACTIONS,
                        })

            # Connection goals: check roster for matching interests
            if category == "connection":
                for agent in roster:
                    topics = [t.lower() for t in agent.get("topics", [])]
                    curiosities = [c.lower() for c in agent.get("curiosities", [])]
                    combined = topics + curiosities
                    if any(kw in item for kw in title_lower.split() for item in combined):
                        suggestions.append({
                            "goal_id": goal["goal_id"],
                            "type": "connection_match",
                            "agent_id": agent.get("agent_id", ""),
                            "detail": f"Shared interest with {agent.get('name', agent.get('agent_id', ''))}",
                            "rtc_cost": RTC_COST_SUGGEST_ACTIONS,
                        })

            # RTC goals: check demand signals for earning opportunities
            if category == "rtc":
                for skill, count in demand.items():
                    if count >= 2 and any(kw in skill for kw in title_lower.split()):
                        suggestions.append({
                            "goal_id": goal["goal_id"],
                            "type": "demand_match",
                            "detail": f"'{skill}' has {count} demand signals — potential RTC opportunity",
                            "rtc_cost": RTC_COST_SUGGEST_ACTIONS,
                        })

        return suggestions

    def auto_create_from_gaps(
        self,
        skill_gaps: Optional[List[str]] = None,
        demand: Optional[Dict[str, int]] = None,
    ) -> List[str]:
        """Auto-create goals from detected skill gaps. Premium: 1.0 RTC.

        Returns list of created goal_ids.
        """
        skill_gaps = skill_gaps or []
        demand = demand or {}
        created = []

        # Only create goals for skills with real demand
        existing_titles = {g["title"].lower() for g in self._goals.values()}

        for skill in skill_gaps:
            candidate_title = f"Learn {skill}".lower()
            if candidate_title in existing_titles or skill.lower() in existing_titles:
                continue
            count = demand.get(skill, 0)
            if count < 2:
                continue
            gid = self.dream(
                title=f"Learn {skill}",
                description=f"Auto-created: {count} demand signals detected for '{skill}'",
                category="skill",
            )
            created.append(gid)

        return created
