"""discord_formatter.py — Pure formatting for Discord messages.

Generates formatted strings for Discord notifications. No side effects, no API calls.
Eva sends these via OpenClaw's `message` tool.
"""

from __future__ import annotations

from pathlib import Path


# --- Config ---

def _load_discord_config() -> dict:
    """Load discord config from settings.yaml (minimal YAML parse, stdlib only)."""
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "settings.yaml"
    defaults = {
        "guild_id": "",
        "human_user_id": "",
        "progress_bar_width": 10,
        "max_subtasks_shown": 10,
    }
    if not config_path.exists():
        return defaults

    try:
        text = config_path.read_text(encoding="utf-8")
        in_discord = False
        in_formatting = False
        for line in text.splitlines():
            stripped = line.strip()
            # Top-level discord: section
            if stripped == "discord:":
                in_discord = True
                in_formatting = False
                continue
            if in_discord:
                if stripped and not stripped.startswith("#") and ":" in stripped:
                    if line[0] not in (" ", "\t"):
                        break  # left discord section
                    key, val = stripped.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key == "guild_id":
                        defaults["guild_id"] = val
                    elif key == "human_user_id":
                        defaults["human_user_id"] = val
                    elif key == "formatting:":
                        in_formatting = True
                        continue
                    if key == "progress_bar_width":
                        try:
                            defaults["progress_bar_width"] = int(val)
                        except ValueError:
                            pass
                    elif key == "max_subtasks_shown":
                        try:
                            defaults["max_subtasks_shown"] = int(val)
                        except ValueError:
                            pass
    except Exception:
        pass
    return defaults


_CONFIG = None


def _get_config() -> dict:
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = _load_discord_config()
    return _CONFIG


# --- Status emoji mapping ---

_TASK_STATUS_EMOJI = {
    "PLANNING": "📝",
    "APPROVED": "✅",
    "IN_PROGRESS": "🔄",
    "TESTING": "🧪",
    "REVIEW": "👁️",
    "COMPLETED": "✅",
    "FAILED": "❌",
    "REJECTED": "🚫",
    "BLOCKED": "⏸️",
}

_SUBTASK_STATUS_EMOJI = {
    "PENDING": "⏳",
    "ASSIGNED": "📋",
    "IN_PROGRESS": "🔄",
    "DONE": "✅",
    "FAILED": "❌",
    "BLOCKED": "⏸️",
}


def _progress_bar(percent: int, width: int = None) -> str:
    """Generate a text progress bar: [████░░░░░░] 40%"""
    if width is None:
        width = _get_config().get("progress_bar_width", 10)
    filled = round(width * percent / 100)
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}] {percent}%"


def _compute_overall_progress(subtasks: list[dict]) -> int:
    """Compute weighted overall progress from subtasks."""
    if not subtasks:
        return 0
    total = 0
    for s in subtasks:
        pct = s.get("progress", {}).get("percent", 0) or 0
        total += pct
    return round(total / len(subtasks))


def _format_eta(task: dict) -> str:
    """Format ETA string if available."""
    eta = task.get("timeline", {}).get("eta")
    if eta:
        return f"ETA: {eta}"
    return ""


# --- Public formatting functions ---

def format_task_created(task: dict) -> str:
    """Format a task creation notification message."""
    priority = task.get("priority", "P1")
    title = task.get("title", "Untitled")
    task_id = task.get("id", "???")
    status = task.get("status", "PLANNING")
    emoji = _TASK_STATUS_EMOJI.get(status, "📝")

    lines = [
        f"🆕 **New Task Created**",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"",
        f"**{task_id}** | `{title}`",
        f"Priority: **{priority}** | Status: {emoji} {status}",
    ]

    plan = task.get("plan", {}).get("summary")
    if plan:
        lines.append(f"Plan: {plan[:200]}")

    return "\n".join(lines)


def format_status_update(task: dict, subtasks: list[dict]) -> str:
    """Format a heartbeat status update for a task."""
    config = _get_config()
    task_id = task.get("id", "???")
    title = task.get("title", "Untitled")
    status = task.get("status", "?")
    emoji = _TASK_STATUS_EMOJI.get(status, "❓")

    overall = _compute_overall_progress(subtasks)
    bar = _progress_bar(overall)
    eta = _format_eta(task)

    lines = [
        f"**{task_id}** | `{title}` | {emoji} {status}",
        f"{bar}" + (f" | {eta}" if eta else ""),
    ]

    max_shown = config.get("max_subtasks_shown", 10)
    if subtasks:
        shown = subtasks[:max_shown]
        for i, s in enumerate(shown):
            is_last = (i == len(shown) - 1) and len(subtasks) <= max_shown
            prefix = "└" if is_last else "├"
            s_emoji = _SUBTASK_STATUS_EMOJI.get(s.get("status", "?"), "❓")
            s_type = s.get("type", "dev")
            s_status = s.get("status", "?")
            s_pct = s.get("progress", {}).get("percent", 0) or 0
            s_id = s.get("id", "?")

            detail = s_status
            if s_status == "IN_PROGRESS":
                detail = f"{s_status} {s_pct}%"
            elif s_status == "DONE":
                detail = "DONE"

            lines.append(f"{prefix} {s_emoji} {s_id} ({s_type}) — {detail}")

        if len(subtasks) > max_shown:
            remaining = len(subtasks) - max_shown
            lines.append(f"└ ... and {remaining} more")

    return "\n".join(lines)


def format_transition(task_id: str, event: str, from_status: str,
                      to_status: str, actor: str = "system") -> str:
    """Format a state transition notification."""
    from_emoji = _TASK_STATUS_EMOJI.get(from_status, "❓")
    to_emoji = _TASK_STATUS_EMOJI.get(to_status, "❓")

    return "\n".join([
        f"🔀 **State Transition** — `{task_id}`",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"",
        f"{from_emoji} {from_status} → {to_emoji} {to_status}",
        f"Event: `{event}` | Actor: {actor}",
    ])


def format_alert(alert: dict) -> str:
    """Format an urgent alert (stuck/overdue/failed).

    alert dict keys: type, task_id, subtask_id, message, agent, progress
    """
    alert_type = alert.get("type", "unknown").upper()
    task_id = alert.get("task_id", "???")
    subtask_id = alert.get("subtask_id", "")
    message = alert.get("message", "")
    agent = alert.get("agent", "")
    progress = alert.get("progress", "")

    config = _get_config()
    human_id = config.get("human_user_id", "")

    emoji_map = {
        "STUCK": "🔴",
        "OVERDUE": "🟡",
        "FAILED": "⚫",
        "SLOW": "🟠",
    }
    emoji = emoji_map.get(alert_type, "⚠️")

    target = f"`{task_id}`"
    if subtask_id:
        target += f" {subtask_id}"

    lines = [
        f"{emoji} **{alert_type} ALERT** — {target}",
    ]

    if message:
        lines.append(message)
    if progress:
        lines.append(f"Progress: {progress}")
    if agent:
        lines.append(f"Agent: {agent}")

    # Ping human for urgent alerts
    if alert_type in ("STUCK", "FAILED") and human_id:
        lines.append(f"<@{human_id}>")

    return "\n".join(lines)


def format_completion_summary(task: dict, subtasks: list[dict]) -> str:
    """Format a task completion summary."""
    task_id = task.get("id", "???")
    title = task.get("title", "Untitled")
    priority = task.get("priority", "P1")

    total = len(subtasks)
    done = sum(1 for s in subtasks if s.get("status") == "DONE")
    failed = sum(1 for s in subtasks if s.get("status") == "FAILED")

    created = (task.get("created") or "")[:10]
    completed = (task.get("timeline", {}).get("completed_at") or "")[:10]

    lines = [
        f"🎉 **Task Completed** — `{task_id}`",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"",
        f"**{title}**",
        f"Priority: {priority} | {done}/{total} subtasks done",
    ]

    if failed:
        lines.append(f"⚠️ {failed} subtask(s) failed")

    if created and completed:
        lines.append(f"Timeline: {created} → {completed}")

    if subtasks:
        lines.append("")
        for s in subtasks:
            s_emoji = _SUBTASK_STATUS_EMOJI.get(s.get("status", "?"), "❓")
            s_id = s.get("id", "?")
            s_title = s.get("title", "")[:40]
            lines.append(f"{s_emoji} {s_id} — {s_title}")

    return "\n".join(lines)


def format_heartbeat_digest(check_result: dict) -> str:
    """Format the full heartbeat check result as a Discord digest message.

    Takes output from checker.check_all_tasks().
    """
    lines = [
        f"📊 **Task Engine — Heartbeat Digest**",
        f"━━━━━━━━━━━━━━━━━━━━",
    ]

    tasks = check_result.get("tasks", [])
    if not tasks:
        lines.append("")
        lines.append("No active tasks.")
        return "\n".join(lines)

    # Import here to avoid circular imports at module level
    from .task_store import read_task, read_all_subtasks

    for t in tasks:
        task_id = t.get("task_id", "???")
        status = t.get("status", "?")
        emoji = _TASK_STATUS_EMOJI.get(status, "❓")

        # Load full task and subtasks for detail
        task = read_task(task_id)
        if task is None:
            lines.append(f"")
            lines.append(f"**{task_id}** | {emoji} {status} — (not found)")
            continue

        title = task.title[:30]
        subtasks = read_all_subtasks(task_id)
        overall = _compute_overall_progress([s.to_dict() for s in subtasks])
        bar = _progress_bar(overall)
        eta = _format_eta(task.to_dict())

        lines.append(f"")
        lines.append(f"**{task_id}** | `{title}` | {emoji} {status}")
        lines.append(f"{bar}" + (f" | {eta}" if eta else ""))

        config = _get_config()
        max_shown = config.get("max_subtasks_shown", 10)
        shown = subtasks[:max_shown]
        for i, s in enumerate(shown):
            is_last = (i == len(shown) - 1) and len(subtasks) <= max_shown
            prefix = "└" if is_last else "├"
            s_emoji = _SUBTASK_STATUS_EMOJI.get(s.status, "❓")
            s_type = s.type
            s_status = s.status
            s_pct = s.progress.get("percent", 0) if s.progress else 0

            detail = s_status
            if s_status == "IN_PROGRESS":
                detail = f"{s_status} {s_pct}%"

            lines.append(f"{prefix} {s_emoji} {s.id} ({s_type}) — {detail}")

        if len(subtasks) > max_shown:
            remaining = len(subtasks) - max_shown
            lines.append(f"└ ... and {remaining} more")

    # Alerts section
    alerts = check_result.get("alerts", [])
    lines.append(f"")
    if alerts:
        lines.append(f"⚠️ **Alerts:** {len(alerts)}")
        for a in alerts:
            lines.append(f"  • {a}")
    else:
        lines.append(f"⚠️ **Alerts:** None")

    active_count = check_result.get("active_count", len(tasks))
    all_ok = check_result.get("all_ok", True)
    if all_ok:
        lines.append(f"")
        lines.append(f"✅ All {active_count} active task(s) healthy")
    else:
        stuck = check_result.get("stuck_count", 0)
        lines.append(f"")
        lines.append(f"🔍 {active_count} active, {stuck} stuck")

    return "\n".join(lines)
