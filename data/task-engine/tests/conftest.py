"""Shared fixtures for task-engine tests."""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Make engine importable
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def tasks_dir(tmp_path):
    """Temporary tasks directory."""
    d = tmp_path / "tasks"
    d.mkdir()
    return d


@pytest.fixture(autouse=True)
def patch_tasks_dir(tasks_dir):
    """Patch TASKS_DIR in task_store so all tests use the tmp directory."""
    import engine.task_store as ts
    original = ts.TASKS_DIR
    ts.TASKS_DIR = tasks_dir
    yield tasks_dir
    ts.TASKS_DIR = original


@pytest.fixture
def sample_task(tasks_dir):
    """Create a sample task with subtasks for testing."""
    from engine.task_store import create_task, create_subtask

    task = create_task(title="Test task", priority="P1", plan_text="Test plan")

    # Create two subtasks
    st1 = create_subtask(
        task_id=task.id,
        title="Dev subtask",
        agent="claude-code",
        subtask_type="dev",
    )
    st2 = create_subtask(
        task_id=task.id,
        title="Test subtask",
        agent="eva",
        subtask_type="test",
    )

    return task, st1, st2
