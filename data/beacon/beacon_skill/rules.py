"""Rules Engine — declarative "when X happens, do Y" for autonomous agent behavior."""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import _dir, append_jsonl


RULES_FILE = "rules.json"
RULES_LOG_FILE = "rules_log.jsonl"
COOLDOWN_S = 60


class RulesEngine:
    """Evaluate events against declarative rules and execute matching actions."""

    def __init__(self, rules_path: Optional[Path] = None):
        self._rules_path = rules_path or (_dir() / RULES_FILE)
        self._rules: List[Dict[str, Any]] = []
        self._cooldowns: Dict[str, float] = {}  # (rule_name, agent_id) -> last_fire_ts
        self._load()

    def _load(self) -> None:
        if self._rules_path.exists():
            try:
                data = json.loads(self._rules_path.read_text(encoding="utf-8"))
                self._rules = data.get("rules", [])
            except Exception:
                self._rules = []

    def _save(self) -> None:
        self._rules_path.parent.mkdir(parents=True, exist_ok=True)
        self._rules_path.write_text(
            json.dumps({"rules": self._rules}, indent=2) + "\n",
            encoding="utf-8",
        )

    def rules(self) -> List[Dict[str, Any]]:
        """Return all rules."""
        return list(self._rules)

    def add_rule(self, rule: Dict[str, Any]) -> None:
        """Add a new rule."""
        self._rules.append(rule)
        self._save()

    def remove_rule(self, name: str) -> bool:
        """Remove a rule by name."""
        before = len(self._rules)
        self._rules = [r for r in self._rules if r.get("name") != name]
        if len(self._rules) < before:
            self._save()
            return True
        return False

    def enable_rule(self, name: str) -> bool:
        """Enable a rule by name."""
        for r in self._rules:
            if r.get("name") == name:
                r.pop("disabled", None)
                self._save()
                return True
        return False

    def disable_rule(self, name: str) -> bool:
        """Disable a rule by name."""
        for r in self._rules:
            if r.get("name") == name:
                r["disabled"] = True
                self._save()
                return True
        return False

    # ── Condition matching ──

    def _match_condition(
        self,
        when: Dict[str, Any],
        event: Dict[str, Any],
        trust_mgr: Any = None,
        values_mgr: Any = None,
        goal_mgr: Any = None,
    ) -> bool:
        """Check if an event matches a rule's 'when' conditions."""
        env = event.get("envelope") or event

        # kind: exact or list
        if "kind" in when:
            expected = when["kind"]
            actual = env.get("kind", "")
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False

        # agent_id: exact or list
        if "agent_id" in when:
            expected = when["agent_id"]
            actual = env.get("agent_id", "")
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False

        # RTC range
        rtc = env.get("reward_rtc", 0) or 0
        if "min_rtc" in when and rtc < when["min_rtc"]:
            return False
        if "max_rtc" in when and rtc > when["max_rtc"]:
            return False

        # Trust range
        if trust_mgr and ("min_trust" in when or "max_trust" in when):
            agent_id = env.get("agent_id", "")
            if agent_id:
                trust_info = trust_mgr.score(agent_id)
                trust_val = trust_info.get("score", 0)
                if "min_trust" in when and trust_val < when["min_trust"]:
                    return False
                if "max_trust" in when and trust_val > when["max_trust"]:
                    return False

        # Feed score threshold
        if "min_score" in when:
            score = event.get("score", 0)
            if score < when["min_score"]:
                return False

        # Topic matching (keywords in text/links)
        if "topic_match" in when:
            topics = when["topic_match"]
            if isinstance(topics, str):
                topics = [topics]
            text_blob = " ".join([
                str(env.get("text", "")),
                " ".join(env.get("links", [])),
                str(env.get("bounty_url", "")),
            ]).lower()
            if not any(t.lower() in text_blob for t in topics):
                return False

        # Verified filter
        if "verified" in when and when["verified"] is not None:
            if event.get("verified") != when["verified"]:
                return False

        # Platform filter
        if "platform" in when:
            if event.get("platform") != when["platform"]:
                return False

        # Task state filter
        if "task_state" in when:
            if env.get("state") != when["task_state"]:
                return False

        # Beacon 2.1 Soul: values_match condition
        if "values_match" in when and values_mgr is not None:
            min_compat = when["values_match"]
            other_values = env.get("values", {})
            if other_values:
                compat = values_mgr.compatibility(other_values)
                if compat < min_compat:
                    return False

        # Beacon 2.2: goal_active condition — only fire if I have active goals
        if "goal_active" in when and goal_mgr is not None:
            active = goal_mgr.active_goals()
            if when["goal_active"] and not active:
                return False
            if not when["goal_active"] and active:
                return False

        # Beacon 2.2: goal_progress condition — fire if a goal title keyword matches
        if "goal_progress" in when and goal_mgr is not None:
            keyword = when["goal_progress"].lower()
            active = goal_mgr.active_goals()
            if not any(keyword in g.get("title", "").lower() for g in active):
                return False

        return True

    # ── Variable substitution ──

    def _substitute(self, text: str, event: Dict[str, Any]) -> str:
        """Replace $variables in action text with event values."""
        env = event.get("envelope") or event
        replacements = {
            "$from": str(env.get("from", "")),
            "$agent_id": str(env.get("agent_id", "")),
            "$kind": str(env.get("kind", "")),
            "$nonce": str(env.get("nonce", "")),
            "$reward_rtc": str(env.get("reward_rtc", "")),
            "$task_id": str(env.get("task_id", "")),
            "$text": str(env.get("text", "")),
            "$name": str(env.get("name", "")),
        }
        result = text
        for var, val in replacements.items():
            result = result.replace(var, val)
        return result

    # ── Cooldown ──

    def _cooldown_key(self, rule_name: str, agent_id: str) -> str:
        return f"{rule_name}:{agent_id}"

    def _is_cooled_down(self, rule_name: str, agent_id: str) -> bool:
        """Check if a rule+agent pair is in cooldown."""
        key = self._cooldown_key(rule_name, agent_id)
        last = self._cooldowns.get(key, 0)
        return (time.time() - last) < COOLDOWN_S

    def _mark_fired(self, rule_name: str, agent_id: str) -> None:
        key = self._cooldown_key(rule_name, agent_id)
        self._cooldowns[key] = time.time()

    # ── Evaluation ──

    def evaluate(
        self,
        event: Dict[str, Any],
        trust_mgr: Any = None,
        values_mgr: Any = None,
        goal_mgr: Any = None,
    ) -> List[Dict[str, Any]]:
        """Find all rules matching this event. Returns list of (rule, action) dicts."""
        env = event.get("envelope") or event
        agent_id = env.get("agent_id", "")
        matches = []

        # Beacon 2.1 Soul: auto-enforce boundaries before rule evaluation
        if values_mgr is not None:
            violated = values_mgr.check_boundaries(env)
            if violated:
                matches.append({
                    "rule": "_boundary_enforcement",
                    "action": {"action": "log", "message": f"Boundary violated: {violated}"},
                    "event": event,
                    "boundary_violated": violated,
                })
                return matches  # Stop processing — boundary takes precedence

        for rule in self._rules:
            if rule.get("disabled"):
                continue
            name = rule.get("name", "unnamed")
            when = rule.get("when", {})
            then = rule.get("then", {})

            if not self._match_condition(when, event, trust_mgr, values_mgr=values_mgr, goal_mgr=goal_mgr):
                continue

            if self._is_cooled_down(name, agent_id):
                continue

            matches.append({"rule": name, "action": dict(then), "event": event})

        return matches

    def execute(
        self,
        action: Dict[str, Any],
        event: Dict[str, Any],
        identity: Any = None,
        cfg: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Execute a single action. Returns result dict."""
        action_type = action.get("action", "log")
        env = event.get("envelope") or event

        if action_type == "log":
            message = self._substitute(action.get("message", "Rule fired"), event)
            entry = {"ts": int(time.time()), "message": message, "event_kind": env.get("kind")}
            append_jsonl(RULES_LOG_FILE, entry)
            return {"action": "log", "message": message}

        if action_type == "reply":
            reply_kind = action.get("kind", "hello")
            text = self._substitute(action.get("text", ""), event)
            reply = {
                "kind": reply_kind,
                "to": env.get("agent_id", env.get("from", "")),
                "text": text,
                "ts": int(time.time()),
            }
            if "task_id" in action:
                reply["task_id"] = self._substitute(action["task_id"], event)
            return {"action": "reply", "envelope": reply}

        if action_type == "block":
            reason = self._substitute(action.get("reason", "auto-blocked by rule"), event)
            return {"action": "block", "agent_id": env.get("agent_id", ""), "reason": reason}

        if action_type == "rate":
            outcome = action.get("outcome", "ok")
            return {"action": "rate", "agent_id": env.get("agent_id", ""), "outcome": outcome}

        if action_type == "mark_read":
            return {"action": "mark_read", "nonce": env.get("nonce", "")}

        if action_type == "emit":
            data = {}
            for k, v in action.items():
                if k == "action":
                    continue
                data[k] = self._substitute(str(v), event) if isinstance(v, str) else v
            return {"action": "emit", "data": data}

        return {"action": action_type, "error": "unknown_action"}

    def process(
        self,
        event: Dict[str, Any],
        identity: Any = None,
        cfg: Optional[Dict] = None,
        trust_mgr: Any = None,
        values_mgr: Any = None,
        goal_mgr: Any = None,
    ) -> List[Dict[str, Any]]:
        """Full pipeline: evaluate rules then execute all matching actions."""
        matches = self.evaluate(event, trust_mgr=trust_mgr, values_mgr=values_mgr, goal_mgr=goal_mgr)
        results = []

        for match in matches:
            rule_name = match["rule"]
            env = event.get("envelope") or event
            agent_id = env.get("agent_id", "")

            result = self.execute(match["action"], event, identity=identity, cfg=cfg)
            result["rule"] = rule_name
            results.append(result)

            self._mark_fired(rule_name, agent_id)

        return results
