"""models.py — Task and Subtask dataclasses matching DESIGN.md Section 4."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


# --- Enums as string constants ---

TASK_STATUSES = frozenset({
    "PLANNING", "APPROVED", "IN_PROGRESS", "TESTING",
    "REVIEW", "COMPLETED", "FAILED", "REJECTED", "BLOCKED",
})

TERMINAL_TASK_STATUSES = frozenset({"COMPLETED", "FAILED", "REJECTED"})

SUBTASK_STATUSES = frozenset({
    "PENDING", "ASSIGNED", "IN_PROGRESS", "DONE", "FAILED", "BLOCKED",
})

TERMINAL_SUBTASK_STATUSES = frozenset({"DONE", "FAILED"})

PRIORITIES = ("P0", "P1", "P2")

SUBTASK_TYPES = ("dev", "test", "validate", "docs", "misc")


# --- History entry ---

@dataclass
class HistoryEntry:
    time: str
    event: str
    actor: str = "system"
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    note: Optional[str] = None
    progress: Optional[int] = None
    context: Optional[str] = None

    def to_dict(self) -> dict:
        d = {k: v for k, v in asdict(self).items() if v is not None}
        return d

    @classmethod
    def from_dict(cls, data: dict) -> HistoryEntry:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# --- Task ---

@dataclass
class Task:
    id: str
    title: str
    status: str = "PLANNING"
    priority: str = "P1"
    description: str = ""
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    updated: str = field(default_factory=lambda: datetime.now().isoformat())

    plan: dict = field(default_factory=lambda: {
        "summary": None,
        "approach": None,
        "approved_by": None,
        "approved_at": None,
    })

    subtasks: list[str] = field(default_factory=list)

    discord: dict = field(default_factory=lambda: {
        "channel_id": None,
        "channel_name": None,
        "created_at": None,
    })

    timeline: dict = field(default_factory=lambda: {
        "eta": None,
        "started_at": None,
        "completed_at": None,
    })

    history: list[dict] = field(default_factory=list)

    metadata: dict = field(default_factory=lambda: {
        "source_session": None,
        "tags": [],
        "blocked_reason": None,
    })

    def to_dict(self) -> dict:
        return {
            "$schema": "task-engine/task.v1",
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "created": self.created,
            "updated": self.updated,
            "plan": self.plan,
            "subtasks": self.subtasks,
            "discord": self.discord,
            "timeline": self.timeline,
            "history": self.history,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            title=data["title"],
            status=data.get("status", "PLANNING"),
            priority=data.get("priority", "P1"),
            description=data.get("description", ""),
            created=data.get("created", ""),
            updated=data.get("updated", ""),
            plan=data.get("plan", {}),
            subtasks=data.get("subtasks", []),
            discord=data.get("discord", {}),
            timeline=data.get("timeline", {}),
            history=data.get("history", []),
            metadata=data.get("metadata", {}),
        )

    def add_history(self, event: str, actor: str = "system",
                    from_status: str = None, to_status: str = None,
                    note: str = None):
        entry = HistoryEntry(
            time=datetime.now().isoformat(),
            event=event,
            actor=actor,
            from_status=from_status,
            to_status=to_status,
            note=note,
        )
        self.history.append(entry.to_dict())
        self.updated = datetime.now().isoformat()


# --- Subtask ---

@dataclass
class Subtask:
    id: str
    parent_task: str
    title: str
    description: str = ""
    type: str = "dev"
    status: str = "PENDING"
    priority: str = "P1"

    assignment: dict = field(default_factory=lambda: {
        "agent": None,
        "instance_id": None,
        "assigned_at": None,
        "dispatch_context": None,
    })

    dependencies: list[str] = field(default_factory=list)
    blocked_by: list[str] = field(default_factory=list)

    progress: dict = field(default_factory=lambda: {
        "percent": 0,
        "last_update": None,
        "checkpoint": None,
    })

    result: dict = field(default_factory=lambda: {
        "status": None,
        "summary": None,
        "artifacts": [],
        "error": None,
    })

    history: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "$schema": "task-engine/subtask.v1",
            "id": self.id,
            "parent_task": self.parent_task,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "status": self.status,
            "priority": self.priority,
            "assignment": self.assignment,
            "dependencies": self.dependencies,
            "blocked_by": self.blocked_by,
            "progress": self.progress,
            "result": self.result,
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Subtask:
        return cls(
            id=data["id"],
            parent_task=data["parent_task"],
            title=data["title"],
            description=data.get("description", ""),
            type=data.get("type", "dev"),
            status=data.get("status", "PENDING"),
            priority=data.get("priority", "P1"),
            assignment=data.get("assignment", {}),
            dependencies=data.get("dependencies", []),
            blocked_by=data.get("blocked_by", []),
            progress=data.get("progress", {}),
            result=data.get("result", {}),
            history=data.get("history", []),
        )

    def add_history(self, event: str, actor: str = "system",
                    note: str = None, progress: int = None):
        entry = HistoryEntry(
            time=datetime.now().isoformat(),
            event=event,
            actor=actor,
            note=note,
            progress=progress,
        )
        self.history.append(entry.to_dict())


# --- Index entry ---

@dataclass
class IndexEntry:
    id: str
    title: str
    status: str
    priority: str
    created: str
    discord_channel_id: Optional[str] = None
    subtask_count: int = 0
    subtasks_done: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> IndexEntry:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_task(cls, task: Task) -> IndexEntry:
        return cls(
            id=task.id,
            title=task.title,
            status=task.status,
            priority=task.priority,
            created=task.created,
            discord_channel_id=task.discord.get("channel_id"),
            subtask_count=len(task.subtasks),
            subtasks_done=0,
        )
