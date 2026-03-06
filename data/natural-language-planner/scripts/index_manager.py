"""
Search and fast-lookup optimisation for the Natural Language Planner.

Builds an in-memory index from the markdown files so that queries,
due-date checks, and check-in lookups are fast even with many tasks.
"""

import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from .utils import parse_frontmatter, safe_read_file, safe_write_file, ensure_directory
from .config_manager import load_config

logger = logging.getLogger("nlplanner.index")

# In-memory index
_index: dict[str, Any] = {"tasks": {}, "projects": {}, "built_at": ""}


# ── Public API ─────────────────────────────────────────────────────

def rebuild_index() -> bool:
    """
    Rebuild the in-memory index by scanning all markdown files.

    Also persists the index to .nlplanner/index.json for faster cold starts.

    Returns:
        True if the index was built successfully.

    Example:
        >>> rebuild_index()
        True
        >>> len(search_tasks("backend"))
        3
    """
    root = _workspace_root()
    if root is None:
        return False

    global _index
    _index = {"tasks": {}, "projects": {}, "built_at": datetime.now().isoformat()}

    # Index projects
    projects_dir = root / "projects"
    if projects_dir.exists():
        for readme in projects_dir.glob("*/README.md"):
            raw = safe_read_file(readme)
            if raw is None:
                continue
            meta, body = parse_frontmatter(raw)
            pid = meta.get("id", readme.parent.name)
            _index["projects"][pid] = {
                **meta,
                "_body": body,
                "_path": str(readme),
            }

    # Index tasks
    for task_file in projects_dir.glob("*/tasks/task-*.md"):
        raw = safe_read_file(task_file)
        if raw is None:
            continue
        meta, body = parse_frontmatter(raw)
        tid = meta.get("id", task_file.stem)
        _index["tasks"][tid] = {
            **meta,
            "_body": body,
            "_path": str(task_file),
        }

    # Also index archived tasks for search
    archive_dir = root / "archive"
    if archive_dir.exists():
        for task_file in archive_dir.glob("*/tasks/task-*.md"):
            raw = safe_read_file(task_file)
            if raw is None:
                continue
            meta, body = parse_frontmatter(raw)
            tid = meta.get("id", task_file.stem)
            _index["tasks"][tid] = {
                **meta,
                "_body": body,
                "_path": str(task_file),
                "_archived": True,
            }

    # Persist to disk
    _persist_index(root)

    task_count = len(_index["tasks"])
    project_count = len(_index["projects"])
    logger.info("Index rebuilt: %d tasks, %d projects.", task_count, project_count)
    return True


def search_tasks(query: str, include_archived: bool = False) -> list[dict[str, Any]]:
    """
    Search tasks by a text query.

    Matches against title, description body, tags, and project name.
    Case-insensitive substring matching.

    Args:
        query: Search string.
        include_archived: Whether to include archived tasks in results.

    Returns:
        List of matching task metadata dicts, sorted by relevance (title
        matches first, then body matches).

    Example:
        >>> results = search_tasks("deploy")
        >>> [r["title"] for r in results]
        ['Deploy to staging', 'Set up deploy pipeline']
    """
    _ensure_index()
    query_lower = query.lower()
    title_matches = []
    other_matches = []

    for tid, task in _index["tasks"].items():
        if not include_archived and task.get("_archived"):
            continue
        if task.get("status") == "archived" and not include_archived:
            continue

        title = (task.get("title") or "").lower()
        body = (task.get("_body") or "").lower()
        tags = " ".join(task.get("tags") or []).lower()
        project = (task.get("project") or "").lower()

        searchable = f"{title} {body} {tags} {project}"

        if query_lower in title:
            title_matches.append(_clean_task(task))
        elif query_lower in searchable:
            other_matches.append(_clean_task(task))

    return title_matches + other_matches


def get_tasks_due_soon(days: int = 7) -> list[dict[str, Any]]:
    """
    Return active tasks with due dates within the next N days.

    Args:
        days: Number of days to look ahead.

    Returns:
        List of task metadata dicts sorted by due date (soonest first).

    Example:
        >>> upcoming = get_tasks_due_soon(3)
        >>> [t["title"] for t in upcoming]
        ['Submit report', 'Review PR']
    """
    _ensure_index()
    today = date.today()
    horizon = today + timedelta(days=days)
    results = []

    for tid, task in _index["tasks"].items():
        if task.get("status") in ("done", "archived"):
            continue
        due_str = task.get("due", "")
        if not due_str:
            continue
        try:
            due_date = date.fromisoformat(str(due_str))
        except (ValueError, TypeError):
            continue

        if due_date <= horizon:
            entry = _clean_task(task)
            entry["_due_date"] = due_date.isoformat()
            entry["_overdue"] = due_date < today
            results.append(entry)

    results.sort(key=lambda t: t.get("_due_date", "9999"))
    return results


def get_tasks_needing_checkin() -> list[dict[str, Any]]:
    """
    Return active tasks that haven't been checked on recently.

    Uses the configured check-in frequency from config.json.

    Returns:
        List of task metadata dicts that need a check-in.

    Example:
        >>> stale = get_tasks_needing_checkin()
        >>> len(stale)
        2
    """
    _ensure_index()
    config = load_config()
    freq_hours = config.get("settings", {}).get("checkin_frequency_hours", 24)
    cutoff = datetime.now() - timedelta(hours=freq_hours)

    results = []
    for tid, task in _index["tasks"].items():
        status = task.get("status", "")
        if status in ("done", "archived"):
            continue

        last_checkin_str = task.get("last_checkin", "")
        if not last_checkin_str:
            results.append(_clean_task(task))
            continue

        try:
            last_checkin = datetime.fromisoformat(str(last_checkin_str))
        except (ValueError, TypeError):
            # If it's just a date string like "2026-02-09", parse that
            try:
                last_checkin = datetime.fromisoformat(str(last_checkin_str) + "T00:00:00")
            except (ValueError, TypeError):
                results.append(_clean_task(task))
                continue

        if last_checkin < cutoff:
            results.append(_clean_task(task))

    return results


def get_overdue_tasks() -> list[dict[str, Any]]:
    """
    Return all active tasks that are past their due date.

    Returns:
        List of overdue task metadata dicts.
    """
    _ensure_index()
    today = date.today()
    results = []

    for tid, task in _index["tasks"].items():
        if task.get("status") in ("done", "archived"):
            continue
        due_str = task.get("due", "")
        if not due_str:
            continue
        try:
            due_date = date.fromisoformat(str(due_str))
        except (ValueError, TypeError):
            continue
        if due_date < today:
            entry = _clean_task(task)
            entry["_days_overdue"] = (today - due_date).days
            results.append(entry)

    results.sort(key=lambda t: t.get("_days_overdue", 0), reverse=True)
    return results


def get_stats() -> dict[str, Any]:
    """
    Return summary statistics about all tasks and projects.

    Returns:
        Dictionary with counts by status, priority, overdue tasks, etc.
    """
    _ensure_index()
    today = date.today()

    stats: dict[str, Any] = {
        "total_tasks": 0,
        "by_status": {"todo": 0, "in-progress": 0, "done": 0, "archived": 0},
        "by_priority": {"low": 0, "medium": 0, "high": 0},
        "overdue": 0,
        "due_this_week": 0,
        "total_projects": len(_index["projects"]),
        "active_projects": 0,
    }

    for tid, task in _index["tasks"].items():
        stats["total_tasks"] += 1
        status = task.get("status", "todo")
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

        priority = task.get("priority", "medium")
        if priority in stats["by_priority"]:
            stats["by_priority"][priority] += 1

        due_str = task.get("due", "")
        if due_str and status not in ("done", "archived"):
            try:
                due_date = date.fromisoformat(str(due_str))
                if due_date < today:
                    stats["overdue"] += 1
                elif due_date <= today + timedelta(days=7):
                    stats["due_this_week"] += 1
            except (ValueError, TypeError):
                pass

    for pid, proj in _index["projects"].items():
        if proj.get("status") == "active":
            stats["active_projects"] += 1

    return stats


# ── Internal helpers ───────────────────────────────────────────────

def _workspace_root() -> Optional[Path]:
    """Get workspace root from config."""
    config = load_config()
    ws = config.get("workspace_path", "")
    if not ws:
        logger.error("Workspace not configured.")
        return None
    return Path(ws)


def _ensure_index() -> None:
    """Rebuild the index if it hasn't been built yet."""
    if not _index["tasks"] and not _index["projects"]:
        rebuild_index()


def _clean_task(task: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of task metadata without internal fields."""
    return {k: v for k, v in task.items() if not k.startswith("_")}


def _persist_index(root: Path) -> None:
    """Save the index to disk for faster cold starts."""
    index_path = root / ".nlplanner" / "index.json"
    ensure_directory(index_path.parent)

    # Strip body text to keep the index file small
    slim = {
        "built_at": _index["built_at"],
        "tasks": {
            tid: {k: v for k, v in t.items() if k != "_body"}
            for tid, t in _index["tasks"].items()
        },
        "projects": {
            pid: {k: v for k, v in p.items() if k != "_body"}
            for pid, p in _index["projects"].items()
        },
    }

    try:
        content = json.dumps(slim, indent=2, default=str, ensure_ascii=False)
        safe_write_file(index_path, content)
    except (TypeError, ValueError) as e:
        logger.warning("Failed to persist index: %s", e)
