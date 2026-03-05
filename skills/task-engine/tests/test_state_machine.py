"""Tests for state_machine.py — all valid/invalid transitions."""

import pytest

from engine.state_machine import (
    validate_task_transition,
    validate_subtask_transition,
    get_valid_task_events,
    get_valid_subtask_events,
    check_auto_transition,
    TASK_TRANSITIONS,
    SUBTASK_TRANSITIONS,
)
from engine.models import TASK_STATUSES, SUBTASK_STATUSES, TERMINAL_TASK_STATUSES


class TestTaskTransitions:
    """Test all valid task transitions."""

    @pytest.mark.parametrize("from_status,event,expected", [
        ("PLANNING", "approve", "APPROVED"),
        ("PLANNING", "reject", "REJECTED"),
        ("APPROVED", "start", "IN_PROGRESS"),
        ("IN_PROGRESS", "test", "TESTING"),
        ("IN_PROGRESS", "block", "BLOCKED"),
        ("IN_PROGRESS", "fail", "FAILED"),
        ("TESTING", "review", "REVIEW"),
        ("TESTING", "reopen", "IN_PROGRESS"),
        ("TESTING", "fail", "FAILED"),
        ("REVIEW", "complete", "COMPLETED"),
        ("REVIEW", "reopen", "IN_PROGRESS"),
        ("REVIEW", "fail", "FAILED"),
        ("BLOCKED", "unblock", "IN_PROGRESS"),
        ("BLOCKED", "fail", "FAILED"),
    ])
    def test_valid_transitions(self, from_status, event, expected):
        assert validate_task_transition(from_status, event) == expected

    @pytest.mark.parametrize("from_status,event", [
        ("PLANNING", "start"),
        ("PLANNING", "complete"),
        ("APPROVED", "approve"),
        ("APPROVED", "complete"),
        ("IN_PROGRESS", "approve"),
        ("IN_PROGRESS", "complete"),
        ("COMPLETED", "approve"),
        ("COMPLETED", "start"),
        ("FAILED", "start"),
        ("REJECTED", "approve"),
    ])
    def test_invalid_transitions(self, from_status, event):
        assert validate_task_transition(from_status, event) is None

    def test_terminal_states_have_no_transitions(self):
        for status in TERMINAL_TASK_STATUSES:
            events = get_valid_task_events(status)
            assert events == [], f"{status} should have no valid events, got {events}"

    def test_get_valid_events_planning(self):
        events = get_valid_task_events("PLANNING")
        assert set(events) == {"approve", "reject"}

    def test_get_valid_events_in_progress(self):
        events = get_valid_task_events("IN_PROGRESS")
        assert set(events) == {"test", "block", "fail"}


class TestSubtaskTransitions:
    """Test all valid subtask transitions."""

    @pytest.mark.parametrize("from_status,event,expected", [
        ("PENDING", "assign", "ASSIGNED"),
        ("ASSIGNED", "start", "IN_PROGRESS"),
        ("IN_PROGRESS", "done", "DONE"),
        ("IN_PROGRESS", "fail", "FAILED"),
        ("IN_PROGRESS", "block", "BLOCKED"),
        ("ASSIGNED", "block", "BLOCKED"),
        ("BLOCKED", "unblock", "ASSIGNED"),
    ])
    def test_valid_transitions(self, from_status, event, expected):
        assert validate_subtask_transition(from_status, event) == expected

    @pytest.mark.parametrize("from_status,event", [
        ("PENDING", "start"),
        ("PENDING", "done"),
        ("ASSIGNED", "done"),
        ("DONE", "start"),
        ("FAILED", "start"),
    ])
    def test_invalid_transitions(self, from_status, event):
        assert validate_subtask_transition(from_status, event) is None

    def test_terminal_states_have_no_events(self):
        for status in ("DONE", "FAILED"):
            events = get_valid_subtask_events(status)
            assert events == []


class TestAutoTransition:
    """Test auto-transition logic."""

    def test_no_subtasks_returns_none(self):
        assert check_auto_transition("IN_PROGRESS", []) is None

    def test_all_dev_done_triggers_test(self):
        subtasks = [
            {"type": "dev", "status": "DONE"},
            {"type": "dev", "status": "DONE"},
        ]
        result = check_auto_transition("IN_PROGRESS", subtasks)
        assert result == ("test", "All dev subtasks completed")

    def test_partial_dev_done_no_transition(self):
        subtasks = [
            {"type": "dev", "status": "DONE"},
            {"type": "dev", "status": "IN_PROGRESS"},
        ]
        assert check_auto_transition("IN_PROGRESS", subtasks) is None

    def test_all_test_done_triggers_review(self):
        subtasks = [
            {"type": "test", "status": "DONE"},
            {"type": "validate", "status": "DONE"},
        ]
        result = check_auto_transition("TESTING", subtasks)
        assert result == ("review", "All test subtasks completed")

    def test_wrong_task_status_no_transition(self):
        subtasks = [{"type": "dev", "status": "DONE"}]
        assert check_auto_transition("PLANNING", subtasks) is None
        assert check_auto_transition("APPROVED", subtasks) is None

    def test_mixed_types_only_checks_relevant(self):
        subtasks = [
            {"type": "dev", "status": "DONE"},
            {"type": "test", "status": "PENDING"},
        ]
        result = check_auto_transition("IN_PROGRESS", subtasks)
        assert result == ("test", "All dev subtasks completed")
