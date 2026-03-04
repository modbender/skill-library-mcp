"""task_store.py — CRUD for JSON files, atomic writes, index management, file locking."""

from __future__ import annotations

import json
import logging
import os
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import (
    Task, Subtask, IndexEntry,
    TERMINAL_TASK_STATUSES,
)

logger = logging.getLogger("task_engine")

# --- Paths ---

SKILL_ROOT = Path(__file__).resolve().parent.parent.parent
_env_tasks_dir = os.environ.get("TASK_ENGINE_TASKS_DIR")
TASKS_DIR = Path(_env_tasks_dir) if _env_tasks_dir else SKILL_ROOT.parent.parent / "tasks"


def get_tasks_dir() -> Path:
    """Return the runtime tasks directory, creating it if needed."""
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    return TASKS_DIR


def get_task_dir(task_id: str) -> Path:
    return get_tasks_dir() / task_id


def get_index_path() -> Path:
    return get_tasks_dir() / "index.json"


def get_archive_dir() -> Path:
    d = get_tasks_dir() / "archive"
    d.mkdir(parents=True, exist_ok=True)
    return d


# --- Atomic write ---

def atomic_write(path: Path, data: dict):
    """Write JSON atomically (temp file + rename)."""
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.rename(path)


def append_log(task_dir: Path, entry: dict):
    """Append a single JSON line to log.jsonl."""
    log_path = task_dir / "log.jsonl"
    line = json.dumps(entry, ensure_ascii=False) + "\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)


# --- Platform-aware file locking ---

@contextmanager
def task_lock(task_id: str):
    """Per-task file lock. Uses fcntl on Unix, msvcrt on Windows."""
    lock_dir = get_tasks_dir() / ".locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / f"{task_id}.lock"

    fd = open(lock_path, "w")
    try:
        if sys.platform == "win32":
            import msvcrt
            msvcrt.locking(fd.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(fd.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        if sys.platform == "win32":
            import msvcrt
            try:
                msvcrt.locking(fd.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
        else:
            import fcntl
            fcntl.flock(fd.fileno(), fcntl.LOCK_UN)
        fd.close()


# --- Index operations ---

def read_index() -> dict:
    """Read index.json, returning default structure if missing."""
    path = get_index_path()
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"version": 1, "tasks": []}


def write_index(data: dict):
    """Write index.json atomically."""
    atomic_write(get_index_path(), data)


def next_task_id() -> str:
    """Generate next TASK-NNN id from index."""
    index = read_index()
    # Also check archive for used IDs
    existing_nums = []
    for entry in index["tasks"]:
        num = int(entry["id"].split("-")[1])
        existing_nums.append(num)
    # Check archive directory too
    archive = get_archive_dir()
    for d in archive.iterdir():
        if d.is_dir() and d.name.startswith("TASK-"):
            try:
                num = int(d.name.split("-")[1])
                existing_nums.append(num)
            except (ValueError, IndexError):
                pass
    next_num = max(existing_nums, default=0) + 1
    return f"TASK-{next_num:03d}"


def add_to_index(task: Task):
    """Add a task to index.json."""
    index = read_index()
    entry = IndexEntry.from_task(task)
    index["tasks"].append(entry.to_dict())
    write_index(index)


def update_index_entry(task_id: str, **kwargs):
    """Update fields on an index entry."""
    index = read_index()
    for entry in index["tasks"]:
        if entry["id"] == task_id:
            entry.update(kwargs)
            break
    write_index(index)


def remove_from_index(task_id: str):
    """Remove a task from index.json."""
    index = read_index()
    index["tasks"] = [e for e in index["tasks"] if e["id"] != task_id]
    write_index(index)


# --- Task CRUD ---

def create_task(title: str, priority: str = "P1", plan_text: str = None,
                description: str = "") -> Task:
    """Create a new task with directory, task.json, and log.jsonl."""
    task_id = next_task_id()
    task_dir = get_task_dir(task_id)
    task_dir.mkdir(parents=True, exist_ok=True)

    task = Task(
        id=task_id,
        title=title,
        priority=priority,
        description=description,
    )

    if plan_text:
        task.plan["summary"] = plan_text

    task.add_history("created", actor="eva", to_status="PLANNING",
                     note="Task created")

    # Write task.json
    atomic_write(task_dir / "task.json", task.to_dict())

    # Create empty log.jsonl with creation event
    append_log(task_dir, {
        "time": datetime.now().isoformat(),
        "event": "task.created",
        "task": task_id,
        "actor": "eva",
    })

    # Update index
    add_to_index(task)

    logger.info("Created task %s: %s", task_id, title)
    return task


def read_task(task_id: str) -> Optional[Task]:
    """Read a task from its task.json."""
    task_dir = get_task_dir(task_id)
    task_path = task_dir / "task.json"
    if not task_path.exists():
        # Check archive
        archive_path = get_archive_dir() / task_id / "task.json"
        if archive_path.exists():
            data = json.loads(archive_path.read_text(encoding="utf-8"))
            return Task.from_dict(data)
        return None
    data = json.loads(task_path.read_text(encoding="utf-8"))
    return Task.from_dict(data)


def save_task(task: Task):
    """Save task.json atomically."""
    task.updated = datetime.now().isoformat()
    task_dir = get_task_dir(task.id)
    task_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(task_dir / "task.json", task.to_dict())


def list_tasks(include_terminal: bool = False) -> list[dict]:
    """List tasks from index.json."""
    index = read_index()
    tasks = index["tasks"]
    if not include_terminal:
        tasks = [t for t in tasks if t["status"] not in TERMINAL_TASK_STATUSES]
    return tasks


# --- Subtask CRUD ---

def create_subtask(task_id: str, title: str, agent: str = None,
                   subtask_type: str = "dev", deps: list[str] = None,
                   context: str = None, description: str = "") -> Subtask:
    """Create a new subtask for a task."""
    task = read_task(task_id)
    if task is None:
        raise ValueError(f"Task {task_id} not found")

    # Determine next subtask number
    existing_nums = []
    for sid in task.subtasks:
        try:
            num = int(sid.split("_")[1])
            existing_nums.append(num)
        except (ValueError, IndexError):
            pass
    next_num = max(existing_nums, default=0) + 1
    subtask_id = f"subtask_{next_num:02d}"

    subtask = Subtask(
        id=subtask_id,
        parent_task=task_id,
        title=title,
        description=description,
        type=subtask_type,
        priority=task.priority,
    )

    if deps:
        subtask.blocked_by = deps
        subtask.dependencies = deps

    # If agent specified, auto-assign
    if agent:
        subtask.status = "ASSIGNED"
        subtask.assignment = {
            "agent": agent,
            "instance_id": None,
            "assigned_at": datetime.now().isoformat(),
            "dispatch_context": context,
        }
        subtask.add_history("assigned", actor="eva",
                            note=f"Dispatched to {agent}")
    else:
        subtask.add_history("created", actor="eva",
                            note="Subtask created")

    # Check if blocked by dependencies
    if deps:
        task_dir = get_task_dir(task_id)
        for dep_id in deps:
            dep_path = task_dir / f"{dep_id}.json"
            if dep_path.exists():
                dep_data = json.loads(dep_path.read_text(encoding="utf-8"))
                if dep_data.get("status") not in ("DONE",):
                    subtask.status = "BLOCKED"
                    subtask.add_history("block", actor="system",
                                        note=f"Blocked by {dep_id}")
                    break

    # Write subtask JSON
    task_dir = get_task_dir(task_id)
    atomic_write(task_dir / f"{subtask_id}.json", subtask.to_dict())

    # Update parent task
    task.subtasks.append(subtask_id)
    save_task(task)

    # Update index subtask count
    update_index_entry(task_id, subtask_count=len(task.subtasks))

    # Log event
    append_log(task_dir, {
        "time": datetime.now().isoformat(),
        "event": "subtask.dispatched",
        "task": task_id,
        "subtask": subtask_id,
        "agent": agent,
    })

    logger.info("Created subtask %s/%s: %s", task_id, subtask_id, title)
    return subtask


def read_subtask(task_id: str, subtask_id: str) -> Optional[Subtask]:
    """Read a subtask JSON."""
    task_dir = get_task_dir(task_id)
    path = task_dir / f"{subtask_id}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return Subtask.from_dict(data)


def save_subtask(subtask: Subtask):
    """Save subtask JSON atomically."""
    task_dir = get_task_dir(subtask.parent_task)
    atomic_write(task_dir / f"{subtask.id}.json", subtask.to_dict())


def read_all_subtasks(task_id: str) -> list[Subtask]:
    """Read all subtasks for a task."""
    task = read_task(task_id)
    if task is None:
        return []
    subtasks = []
    for sid in task.subtasks:
        st = read_subtask(task_id, sid)
        if st:
            subtasks.append(st)
    return subtasks


# --- Archive ---

def archive_task(task_id: str) -> bool:
    """Move a terminal-state task to archive/."""
    task = read_task(task_id)
    if task is None:
        logger.error("Task %s not found", task_id)
        return False

    if task.status not in TERMINAL_TASK_STATUSES:
        logger.error("Task %s is in state %s, not terminal — cannot archive",
                      task_id, task.status)
        return False

    src = get_task_dir(task_id)
    dst = get_archive_dir() / task_id

    if not src.exists():
        logger.error("Task directory %s does not exist", src)
        return False

    # Move directory
    src.rename(dst)

    # Remove from index
    remove_from_index(task_id)

    # Log
    append_log(dst, {
        "time": datetime.now().isoformat(),
        "event": "task.archived",
        "task": task_id,
    })

    logger.info("Archived task %s", task_id)
    return True


def count_done_subtasks(task_id: str) -> int:
    """Count how many subtasks are DONE."""
    return sum(1 for s in read_all_subtasks(task_id) if s.status == "DONE")
