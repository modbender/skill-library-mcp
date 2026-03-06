"""Task Lifecycle — bounties become trackable jobs with a state machine."""

import json
import secrets
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import _dir


TASKS_FILE = "tasks.jsonl"

# Valid state transitions for the task lifecycle
TRANSITIONS = {
    "open": ["offered", "cancelled"],
    "offered": ["accepted", "rejected", "cancelled"],
    "accepted": ["delivered", "cancelled"],
    "delivered": ["confirmed", "disputed"],
    "confirmed": ["paid"],
    "disputed": ["confirmed", "cancelled"],
}

# Map of kind -> state for auto-transition
KIND_TO_STATE = {
    "bounty": "open",
    "offer": "offered",
    "accept": "accepted",
    "deliver": "delivered",
    "confirm": "confirmed",
    "pay": "paid",
}


def generate_task_id() -> str:
    """Generate a 12-char hex task ID."""
    return secrets.token_hex(6)


class TaskManager:
    """Track bounties through their full lifecycle: post -> offer -> accept -> deliver -> confirm -> pay."""

    def __init__(self, data_dir: Optional[Path] = None):
        self._dir = data_dir or _dir()

    def _tasks_path(self) -> Path:
        return self._dir / TASKS_FILE

    def _read_all_events(self) -> List[Dict[str, Any]]:
        """Read all task events from the JSONL log."""
        path = self._tasks_path()
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

    def _append_event(self, event: Dict[str, Any]) -> None:
        """Append a task event to our data_dir (not the global ~/.beacon)."""
        path = self._tasks_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, sort_keys=True) + "\n")

    def _build_task_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Rebuild current task state from event log."""
        events = self._read_all_events()
        task_events = [e for e in events if e.get("task_id") == task_id]
        if not task_events:
            return None

        state: Dict[str, Any] = {}
        for evt in task_events:
            state.update(evt)
        return state

    # ── Task operations ──

    def create(self, bounty_envelope: Dict[str, Any]) -> str:
        """Create a new task from a bounty envelope. Returns task_id."""
        task_id = bounty_envelope.get("task_id") or generate_task_id()

        event = {
            "task_id": task_id,
            "state": "open",
            "poster": bounty_envelope.get("agent_id", bounty_envelope.get("from", "")),
            "reward_rtc": bounty_envelope.get("reward_rtc", 0),
            "text": bounty_envelope.get("text", ""),
            "bounty_url": bounty_envelope.get("bounty_url", ""),
            "links": bounty_envelope.get("links", []),
            "ts": int(time.time()),
        }
        self._append_event(event)
        return task_id

    def get(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state of a task."""
        return self._build_task_state(task_id)

    def transition(
        self,
        task_id: str,
        new_state: str,
        envelope: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Validate and record a state transition.

        Raises ValueError for invalid transitions.
        """
        current = self._build_task_state(task_id)
        if current is None:
            raise ValueError(f"Task {task_id} not found")

        current_state = current.get("state", "")
        valid_next = TRANSITIONS.get(current_state, [])

        if new_state not in valid_next:
            raise ValueError(
                f"Invalid transition: {current_state} -> {new_state}. "
                f"Valid: {valid_next}"
            )

        event: Dict[str, Any] = {
            "task_id": task_id,
            "state": new_state,
            "ts": int(time.time()),
        }

        if envelope:
            if new_state == "offered":
                event["worker"] = envelope.get("agent_id", envelope.get("from", ""))
                event["offer_text"] = envelope.get("text", "")
            elif new_state == "accepted":
                event["accepted_worker"] = envelope.get("worker", "")
            elif new_state == "delivered":
                event["delivery_url"] = envelope.get("delivery_url", envelope.get("url", ""))
                event["delivery_text"] = envelope.get("text", "")
            elif new_state == "confirmed":
                event["confirmed_by"] = envelope.get("agent_id", "")
            elif new_state == "paid":
                event["amount_rtc"] = envelope.get("amount_rtc", envelope.get("reward_rtc", 0))
                event["pay_nonce"] = envelope.get("nonce", "")
            elif new_state in ("cancelled", "rejected", "disputed"):
                event["reason"] = envelope.get("reason", envelope.get("text", ""))

        self._append_event(event)
        return event

    def list_tasks(self, state: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all tasks, optionally filtered by current state."""
        events = self._read_all_events()

        # Build task state for each unique task_id
        task_ids = []
        seen = set()
        for evt in events:
            tid = evt.get("task_id", "")
            if tid and tid not in seen:
                task_ids.append(tid)
                seen.add(tid)

        tasks = []
        for tid in task_ids:
            t = self._build_task_state(tid)
            if t is None:
                continue
            if state and t.get("state") != state:
                continue
            tasks.append(t)

        tasks.sort(key=lambda x: x.get("ts", 0), reverse=True)
        return tasks

    def my_tasks(self, my_agent_id: str) -> List[Dict[str, Any]]:
        """List tasks where I'm poster or worker."""
        all_tasks = self.list_tasks()
        return [
            t for t in all_tasks
            if t.get("poster") == my_agent_id or t.get("worker") == my_agent_id
        ]

    def auto_transition_from_envelope(self, envelope: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Automatically transition a task based on an incoming envelope's kind.

        Returns the transition event if successful, None if not applicable.
        """
        kind = envelope.get("kind", "")
        task_id = envelope.get("task_id", "")
        new_state = KIND_TO_STATE.get(kind)

        if not task_id or not new_state:
            return None

        # "open" is handled by create(), not transition()
        if new_state == "open":
            return None

        try:
            return self.transition(task_id, new_state, envelope=envelope)
        except ValueError:
            return None

    def task_summary(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a compact summary of a task."""
        t = self.get(task_id)
        if t is None:
            return None
        return {
            "task_id": task_id,
            "state": t.get("state", "?"),
            "poster": t.get("poster", ""),
            "worker": t.get("worker", ""),
            "reward_rtc": t.get("reward_rtc", 0),
            "ts": t.get("ts", 0),
        }
