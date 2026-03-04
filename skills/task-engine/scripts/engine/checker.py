"""checker.py — Heartbeat check integration.

Called every 30 minutes by heartbeat. Scans active tasks, detects stuck/overdue
subtasks, evaluates auto-transitions, and returns alerts.

Designed for minimal token cost: reads index.json first, only loads task.json
and subtask files for non-terminal tasks.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import TERMINAL_TASK_STATUSES, TERMINAL_SUBTASK_STATUSES
from .state_machine import validate_task_transition, check_auto_transition
from .task_store import (
    read_index, read_task, save_task, read_all_subtasks,
    update_index_entry, append_log, get_task_dir, task_lock,
    count_done_subtasks,
)

logger = logging.getLogger("task_engine")


def _load_config() -> dict:
    """Load heartbeat config from settings.yaml (stdlib only, no pyyaml)."""
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "settings.yaml"
    defaults = {
        "stale_beats": 3,
        "progress_threshold": 5,
        "auto_transition": True,
    }
    if not config_path.exists():
        return defaults

    # Minimal YAML parse for the heartbeat section (flat key: value lines)
    try:
        text = config_path.read_text(encoding="utf-8")
        in_heartbeat = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped == "heartbeat:":
                in_heartbeat = True
                continue
            if in_heartbeat:
                if stripped and not stripped.startswith("#") and ":" in stripped:
                    # Check indent — heartbeat keys are indented
                    if line[0] not in (" ", "\t"):
                        break  # left a section
                    key, val = stripped.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    if key in defaults:
                        if val.lower() in ("true", "false"):
                            defaults[key] = val.lower() == "true"
                        else:
                            try:
                                defaults[key] = int(val)
                            except ValueError:
                                pass
    except Exception:
        pass
    return defaults


def detect_stuck(subtask_data: dict, config: dict) -> str:
    """Analyze subtask for stuck state.

    Returns: "normal" | "slow" | "stuck"

    Compares heartbeat history entries — if progress hasn't changed across
    stale_beats consecutive checks, the subtask is stuck.
    """
    history = [h for h in subtask_data.get("history", [])
               if h.get("event") == "heartbeat"]

    stale_beats = config.get("stale_beats", 3)
    if len(history) < stale_beats:
        return "normal"

    recent = history[-stale_beats:]
    first_progress = recent[0].get("progress", 0)
    last_progress = recent[-1].get("progress", 0)
    delta = (last_progress or 0) - (first_progress or 0)

    context_changed = recent[-1].get("context") != recent[0].get("context")

    if delta == 0 and not context_changed:
        return "stuck"

    threshold = config.get("progress_threshold", 5)
    if 0 < delta < threshold:
        return "slow"

    return "normal"


def detect_overdue(task_data: dict) -> bool:
    """Check if a task is past its ETA."""
    eta = task_data.get("timeline", {}).get("eta")
    if not eta:
        return False
    try:
        # Handle both date-only ("2026-03-02") and datetime strings
        now_str = datetime.now().strftime("%Y-%m-%d")
        return now_str > eta[:10]
    except (TypeError, ValueError):
        return False


def _record_heartbeat(subtask_data: dict) -> dict:
    """Build a heartbeat history entry for a subtask."""
    progress = subtask_data.get("progress", {})
    return {
        "time": datetime.now().isoformat(),
        "event": "heartbeat",
        "progress": progress.get("percent", 0),
        "context": progress.get("checkpoint"),
    }


def check_single_task(task_id: str, config: dict) -> dict:
    """Check a single task and its subtasks.

    Returns: {"task_id": str, "status": str, "alerts": [...], "subtask_summary": str}
    """
    if config is None:
        config = _load_config()

    task = read_task(task_id)
    if task is None:
        return {"task_id": task_id, "status": "NOT_FOUND",
                "alerts": [f"{task_id}: task not found"], "subtask_summary": "?"}

    task_data = task.to_dict()
    alerts = []
    subtasks = read_all_subtasks(task_id)
    subtask_dicts = [s.to_dict() for s in subtasks]

    done_count = sum(1 for s in subtasks if s.status == "DONE")
    failed_count = sum(1 for s in subtasks if s.status == "FAILED")
    total = len(subtasks)

    # --- Overdue detection ---
    if detect_overdue(task_data):
        alerts.append(f"{task_id}: OVERDUE (past ETA {task_data['timeline'].get('eta')})")

    # --- Per-subtask checks ---
    active_subtask_statuses = {"ASSIGNED", "IN_PROGRESS"}
    for st in subtasks:
        if st.status not in active_subtask_statuses:
            continue

        st_data = st.to_dict()
        stuck_status = detect_stuck(st_data, config)

        if stuck_status == "stuck":
            agent = st.assignment.get("agent", "unknown") if st.assignment else "unknown"
            alerts.append(
                f"{task_id}/{st.id}: STUCK — no progress across "
                f"{config.get('stale_beats', 3)} heartbeats (agent: {agent})"
            )

        elif stuck_status == "slow":
            alerts.append(f"{task_id}/{st.id}: SLOW progress")

        # Record heartbeat entry in subtask history
        st.history.append(_record_heartbeat(st_data))
        from .task_store import save_subtask
        save_subtask(st)

    # --- Failed subtask alerts ---
    for st in subtasks:
        if st.status == "FAILED":
            error = st.result.get("error", "") if st.result else ""
            alerts.append(f"{task_id}/{st.id}: FAILED — {error or 'no reason given'}")

    # --- Auto-transition check ---
    if config.get("auto_transition", True):
        auto = check_auto_transition(task.status, subtask_dicts)
        if auto:
            event, reason = auto
            new_status = validate_task_transition(task.status, event)
            if new_status:
                with task_lock(task_id):
                    # Re-read under lock
                    task = read_task(task_id)
                    if task is None:
                        pass
                    else:
                        recheck = check_auto_transition(task.status,
                                                         [s.to_dict() for s in read_all_subtasks(task_id)])
                        if recheck:
                            old_status = task.status
                            task.status = new_status
                            task.add_history("transition", actor="heartbeat",
                                             from_status=old_status,
                                             to_status=new_status,
                                             note=f"Auto: {reason}")
                            save_task(task)
                            update_index_entry(task_id, status=new_status)

                            append_log(get_task_dir(task_id), {
                                "time": datetime.now().isoformat(),
                                "event": "task.auto_transition",
                                "task": task_id,
                                "from": old_status,
                                "to": new_status,
                                "reason": reason,
                                "actor": "heartbeat",
                            })
                            alerts.append(
                                f"{task_id}: auto-transition {old_status} → {new_status} ({reason})"
                            )

    # --- Update index done count ---
    update_index_entry(task_id,
                       subtasks_done=done_count,
                       subtask_count=total)

    # --- Log heartbeat event ---
    append_log(get_task_dir(task_id), {
        "time": datetime.now().isoformat(),
        "event": "heartbeat.check",
        "task": task_id,
        "status": task.status,
        "subtasks_done": f"{done_count}/{total}",
    })

    subtask_summary = f"{done_count}/{total} done"
    if failed_count:
        subtask_summary += f", {failed_count} failed"

    return {
        "task_id": task_id,
        "status": task.status,
        "alerts": alerts,
        "subtask_summary": subtask_summary,
    }


def check_all_tasks(tasks_dir: Optional[Path] = None, config: dict = None) -> dict:
    """Check all active tasks. Called by heartbeat every 30 minutes.

    Args:
        tasks_dir: Unused (kept for interface compatibility). Tasks dir
                   is determined by task_store.
        config: Heartbeat config dict. If None, loaded from settings.yaml.

    Returns:
        {
            "alerts": [...],
            "summary": "2 active, 0 stuck",
            "all_ok": bool,
            "active_count": int,
            "stuck_count": int,
            "tasks": [...]   # per-task results
        }
    """
    if config is None:
        config = _load_config()

    index = read_index()
    active_entries = [
        e for e in index.get("tasks", [])
        if e.get("status") not in TERMINAL_TASK_STATUSES
    ]

    all_alerts = []
    task_results = []

    for entry in active_entries:
        task_id = entry["id"]
        try:
            result = check_single_task(task_id, config)
            task_results.append(result)
            all_alerts.extend(result.get("alerts", []))
        except Exception as e:
            logger.warning("Check failed for %s: %s", task_id, e)
            all_alerts.append(f"{task_id}: check error — {e}")
            task_results.append({
                "task_id": task_id,
                "status": "ERROR",
                "alerts": [f"{task_id}: check error — {e}"],
                "subtask_summary": "error",
            })

    active_count = len(active_entries)
    stuck_count = sum(1 for a in all_alerts if "STUCK" in a)

    summary = f"{active_count} active, {stuck_count} stuck"
    if any("OVERDUE" in a for a in all_alerts):
        overdue_count = sum(1 for a in all_alerts if "OVERDUE" in a)
        summary += f", {overdue_count} overdue"

    return {
        "alerts": all_alerts,
        "summary": summary,
        "all_ok": len(all_alerts) == 0,
        "active_count": active_count,
        "stuck_count": stuck_count,
        "tasks": task_results,
    }
