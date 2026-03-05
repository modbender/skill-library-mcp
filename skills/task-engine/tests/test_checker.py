"""Tests for checker.py — stuck, overdue, auto-transition detection."""

import json
import pytest
from datetime import datetime, timedelta

from engine.checker import (
    detect_stuck, detect_overdue, check_single_task, check_all_tasks,
)
from engine.task_store import (
    create_task, save_task, create_subtask, save_subtask,
    update_index_entry, read_subtask,
)
from engine.state_machine import validate_task_transition


@pytest.fixture
def config():
    return {
        "stale_beats": 3,
        "progress_threshold": 5,
        "auto_transition": True,
    }


class TestDetectStuck:
    def test_normal_no_history(self, config):
        subtask = {"history": []}
        assert detect_stuck(subtask, config) == "normal"

    def test_normal_insufficient_beats(self, config):
        subtask = {"history": [
            {"event": "heartbeat", "progress": 10},
            {"event": "heartbeat", "progress": 20},
        ]}
        assert detect_stuck(subtask, config) == "normal"

    def test_stuck_no_progress(self, config):
        subtask = {"history": [
            {"event": "heartbeat", "progress": 50, "context": "same"},
            {"event": "heartbeat", "progress": 50, "context": "same"},
            {"event": "heartbeat", "progress": 50, "context": "same"},
        ]}
        assert detect_stuck(subtask, config) == "stuck"

    def test_normal_with_progress(self, config):
        subtask = {"history": [
            {"event": "heartbeat", "progress": 50, "context": "a"},
            {"event": "heartbeat", "progress": 60, "context": "b"},
            {"event": "heartbeat", "progress": 70, "context": "c"},
        ]}
        assert detect_stuck(subtask, config) == "normal"

    def test_slow_progress(self, config):
        subtask = {"history": [
            {"event": "heartbeat", "progress": 50, "context": "a"},
            {"event": "heartbeat", "progress": 51, "context": "a"},
            {"event": "heartbeat", "progress": 52, "context": "a"},
        ]}
        assert detect_stuck(subtask, config) == "slow"

    def test_context_change_not_stuck(self, config):
        subtask = {"history": [
            {"event": "heartbeat", "progress": 50, "context": "old"},
            {"event": "heartbeat", "progress": 50, "context": "old"},
            {"event": "heartbeat", "progress": 50, "context": "new"},
        ]}
        assert detect_stuck(subtask, config) == "normal"


class TestDetectOverdue:
    def test_no_eta(self):
        assert detect_overdue({"timeline": {}}) is False

    def test_not_overdue(self):
        future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        assert detect_overdue({"timeline": {"eta": future}}) is False

    def test_overdue(self):
        past = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        assert detect_overdue({"timeline": {"eta": past}}) is True


class TestCheckSingleTask:
    def test_not_found(self, tasks_dir, config):
        result = check_single_task("TASK-999", config)
        assert result["status"] == "NOT_FOUND"
        assert len(result["alerts"]) > 0

    def test_healthy_task(self, tasks_dir, config):
        task = create_task(title="Healthy")
        result = check_single_task(task.id, config)
        assert len(result["alerts"]) == 0
        assert "0/0 done" in result["subtask_summary"]

    def test_overdue_alert(self, tasks_dir, config):
        task = create_task(title="Overdue")
        past = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        task.timeline["eta"] = past
        task.status = "IN_PROGRESS"
        save_task(task)
        update_index_entry(task.id, status="IN_PROGRESS")

        result = check_single_task(task.id, config)
        assert any("OVERDUE" in a for a in result["alerts"])


class TestCheckAllTasks:
    def test_no_active_tasks(self, tasks_dir):
        result = check_all_tasks(config={"stale_beats": 3, "progress_threshold": 5, "auto_transition": True})
        assert result["all_ok"] is True
        assert result["active_count"] == 0

    def test_with_active_task(self, tasks_dir):
        task = create_task(title="Active")
        task.status = "IN_PROGRESS"
        save_task(task)
        update_index_entry(task.id, status="IN_PROGRESS")

        result = check_all_tasks(config={"stale_beats": 3, "progress_threshold": 5, "auto_transition": True})
        assert result["active_count"] == 1

    def test_auto_transition_on_check(self, tasks_dir):
        task = create_task(title="Auto")
        task.status = "IN_PROGRESS"
        save_task(task)
        update_index_entry(task.id, status="IN_PROGRESS")

        # Create a dev subtask and mark it DONE
        st = create_subtask(task.id, "Dev work", agent="claude-code", subtask_type="dev")
        st.status = "DONE"
        save_subtask(st)

        config = {"stale_beats": 3, "progress_threshold": 5, "auto_transition": True}
        result = check_all_tasks(config=config)
        # Should have auto-transitioned to TESTING
        assert any("auto-transition" in a for a in result["alerts"])
