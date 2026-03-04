"""state_machine.py — Transition validation tables from DESIGN.md Section 3."""

from __future__ import annotations

import logging
from datetime import datetime

logger = logging.getLogger("task_engine")


# --- Task transition table ---
# Maps (from_status, event) → to_status

TASK_TRANSITIONS: dict[tuple[str, str], str] = {
    ("PLANNING", "approve"):    "APPROVED",
    ("PLANNING", "reject"):     "REJECTED",
    ("APPROVED", "start"):      "IN_PROGRESS",
    ("IN_PROGRESS", "test"):    "TESTING",
    ("IN_PROGRESS", "block"):   "BLOCKED",
    ("IN_PROGRESS", "fail"):    "FAILED",
    ("TESTING", "review"):      "REVIEW",
    ("TESTING", "reopen"):      "IN_PROGRESS",
    ("TESTING", "fail"):        "FAILED",
    ("REVIEW", "complete"):     "COMPLETED",
    ("REVIEW", "reopen"):       "IN_PROGRESS",
    ("REVIEW", "fail"):         "FAILED",
    ("BLOCKED", "unblock"):     "IN_PROGRESS",
    ("BLOCKED", "fail"):        "FAILED",
}


# --- Subtask transition table ---
# Maps (from_status, event) → to_status

SUBTASK_TRANSITIONS: dict[tuple[str, str], str] = {
    ("PENDING", "assign"):      "ASSIGNED",
    ("ASSIGNED", "start"):      "IN_PROGRESS",
    ("IN_PROGRESS", "done"):    "DONE",
    ("IN_PROGRESS", "fail"):    "FAILED",
    ("IN_PROGRESS", "block"):   "BLOCKED",
    ("ASSIGNED", "block"):      "BLOCKED",
    ("BLOCKED", "unblock"):     "ASSIGNED",
}


def validate_task_transition(current_status: str, event: str) -> str | None:
    """Validate a task transition. Returns new status or None if invalid."""
    return TASK_TRANSITIONS.get((current_status, event))


def validate_subtask_transition(current_status: str, event: str) -> str | None:
    """Validate a subtask transition. Returns new status or None if invalid."""
    return SUBTASK_TRANSITIONS.get((current_status, event))


def get_valid_task_events(status: str) -> list[str]:
    """Return list of valid events for a given task status."""
    return [event for (s, event) in TASK_TRANSITIONS if s == status]


def get_valid_subtask_events(status: str) -> list[str]:
    """Return list of valid events for a given subtask status."""
    return [event for (s, event) in SUBTASK_TRANSITIONS if s == status]


def check_auto_transition(task_status: str, subtasks: list[dict]) -> tuple[str, str] | None:
    """Check if a task should auto-transition based on subtask states.

    Returns (event, reason) if auto-transition should happen, else None.
    """
    if not subtasks:
        return None

    if task_status == "IN_PROGRESS":
        dev_subtasks = [s for s in subtasks if s.get("type") == "dev"]
        if dev_subtasks and all(s.get("status") == "DONE" for s in dev_subtasks):
            return ("test", "All dev subtasks completed")

    if task_status == "TESTING":
        test_subtasks = [s for s in subtasks if s.get("type") in ("test", "validate")]
        if test_subtasks and all(s.get("status") == "DONE" for s in test_subtasks):
            return ("review", "All test subtasks completed")

    return None
