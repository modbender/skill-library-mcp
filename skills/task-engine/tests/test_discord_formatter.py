"""Tests for discord_formatter.py — all format_* functions."""

import pytest

from engine.discord_formatter import (
    format_task_created,
    format_status_update,
    format_transition,
    format_alert,
    format_completion_summary,
    format_heartbeat_digest,
    _progress_bar,
)


class TestProgressBar:
    def test_zero_percent(self):
        bar = _progress_bar(0, width=10)
        assert "0%" in bar
        assert bar.count("█") == 0

    def test_fifty_percent(self):
        bar = _progress_bar(50, width=10)
        assert "50%" in bar
        assert bar.count("█") == 5

    def test_hundred_percent(self):
        bar = _progress_bar(100, width=10)
        assert "100%" in bar
        assert bar.count("█") == 10


class TestFormatTaskCreated:
    def test_non_empty(self):
        task = {"id": "TASK-001", "title": "Test", "priority": "P0", "status": "PLANNING"}
        result = format_task_created(task)
        assert len(result) > 0
        assert "TASK-001" in result
        assert "Test" in result

    def test_includes_plan(self):
        task = {"id": "TASK-001", "title": "Test", "priority": "P0", "status": "PLANNING",
                "plan": {"summary": "My plan here"}}
        result = format_task_created(task)
        assert "My plan" in result


class TestFormatStatusUpdate:
    def test_non_empty(self):
        task = {"id": "TASK-001", "title": "Test", "status": "IN_PROGRESS", "timeline": {}}
        subtasks = [
            {"id": "subtask_01", "type": "dev", "status": "IN_PROGRESS",
             "progress": {"percent": 50}},
        ]
        result = format_status_update(task, subtasks)
        assert len(result) > 0
        assert "TASK-001" in result

    def test_empty_subtasks(self):
        task = {"id": "TASK-001", "title": "Test", "status": "PLANNING", "timeline": {}}
        result = format_status_update(task, [])
        assert len(result) > 0


class TestFormatTransition:
    def test_non_empty(self):
        result = format_transition("TASK-001", "approve", "PLANNING", "APPROVED", "human")
        assert len(result) > 0
        assert "TASK-001" in result
        assert "PLANNING" in result
        assert "APPROVED" in result


class TestFormatAlert:
    def test_stuck_alert(self):
        alert = {
            "type": "stuck",
            "task_id": "TASK-001",
            "subtask_id": "subtask_01",
            "message": "No progress",
            "agent": "claude-code",
            "progress": "50%",
        }
        result = format_alert(alert)
        assert len(result) > 0
        assert "TASK-001" in result

    def test_alert_includes_human_ping(self):
        # We can't easily test with a real human_user_id, but we can ensure the function works
        alert = {"type": "stuck", "task_id": "TASK-001", "subtask_id": "",
                 "message": "stuck", "agent": "", "progress": ""}
        result = format_alert(alert)
        assert "STUCK" in result


class TestFormatCompletionSummary:
    def test_non_empty(self):
        task = {"id": "TASK-001", "title": "Done task", "priority": "P1",
                "created": "2026-01-01T00:00:00",
                "timeline": {"completed_at": "2026-01-02T00:00:00"}}
        subtasks = [
            {"id": "subtask_01", "title": "Work", "status": "DONE"},
        ]
        result = format_completion_summary(task, subtasks)
        assert len(result) > 0
        assert "TASK-001" in result
        assert "1/1" in result

    def test_with_failures(self):
        task = {"id": "TASK-001", "title": "Mixed", "priority": "P1",
                "created": "2026-01-01", "timeline": {"completed_at": "2026-01-02"}}
        subtasks = [
            {"id": "subtask_01", "title": "A", "status": "DONE"},
            {"id": "subtask_02", "title": "B", "status": "FAILED"},
        ]
        result = format_completion_summary(task, subtasks)
        assert "failed" in result.lower()


class TestFormatHeartbeatDigest:
    def test_no_tasks(self):
        result = format_heartbeat_digest({"tasks": [], "alerts": [], "all_ok": True, "active_count": 0})
        assert "No active tasks" in result

    def test_with_tasks(self, tasks_dir):
        from engine.task_store import create_task
        task = create_task(title="Digest test")

        check_result = {
            "tasks": [{"task_id": task.id, "status": "PLANNING", "alerts": [], "subtask_summary": "0/0"}],
            "alerts": [],
            "all_ok": True,
            "active_count": 1,
        }
        result = format_heartbeat_digest(check_result)
        assert len(result) > 0
        assert task.id in result
