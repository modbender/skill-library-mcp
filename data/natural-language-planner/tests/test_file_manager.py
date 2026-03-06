"""
Tests for scripts.file_manager — core CRUD operations.

Run with:  python -m pytest tests/test_file_manager.py -v
"""

import sys
import os
import tempfile
import shutil

import pytest

# Ensure the project root is on sys.path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.file_manager import (
    init_workspace,
    create_project,
    get_project,
    list_projects,
    update_project,
    archive_project,
    create_task,
    get_task,
    list_tasks,
    update_task,
    archive_task,
    move_task,
    link_tasks,
    add_attachment,
)
from scripts.config_manager import set_config_path


@pytest.fixture
def workspace(tmp_path):
    """Create a temporary workspace for each test."""
    ws = tmp_path / "test_workspace"
    ws.mkdir()
    init_workspace(str(ws))
    return ws


class TestInitWorkspace:
    def test_creates_directory_structure(self, workspace):
        assert (workspace / ".nlplanner" / "config.json").exists()
        assert (workspace / "projects" / "inbox" / "tasks").is_dir()
        assert (workspace / "projects" / "inbox" / "README.md").exists()
        assert (workspace / "archive").is_dir()

    def test_idempotent(self, workspace):
        """Running init twice should not break anything."""
        assert init_workspace(str(workspace))
        assert (workspace / ".nlplanner" / "config.json").exists()


class TestProjects:
    def test_create_project(self, workspace):
        pid = create_project("My Project", description="A test project")
        assert pid == "my-project"
        assert (workspace / "projects" / "my-project" / "README.md").exists()
        assert (workspace / "projects" / "my-project" / "tasks").is_dir()
        assert (workspace / "projects" / "my-project" / "attachments").is_dir()

    def test_get_project(self, workspace):
        create_project("Read Me", description="Hello world")
        proj = get_project("read-me")
        assert proj is not None
        assert proj["meta"]["title"] == "Read Me"
        assert "Hello world" in proj["body"]

    def test_list_projects(self, workspace):
        create_project("Alpha")
        create_project("Beta")
        projects = list_projects()
        titles = [p["title"] for p in projects]
        assert "Alpha" in titles
        assert "Beta" in titles
        # Inbox should also be present
        assert "Inbox" in titles

    def test_update_project(self, workspace):
        create_project("Updatable")
        assert update_project("updatable", {"tags": ["test", "demo"]})
        proj = get_project("updatable")
        assert "test" in proj["meta"]["tags"]

    def test_archive_project(self, workspace):
        create_project("Archivable")
        assert archive_project("archivable")
        assert not (workspace / "projects" / "archivable").exists()
        assert (workspace / "archive" / "archivable" / "README.md").exists()

    def test_create_duplicate_project_returns_existing_id(self, workspace):
        pid1 = create_project("Same Name")
        pid2 = create_project("Same Name")
        assert pid1 == pid2


class TestTasks:
    def test_create_task_in_inbox(self, workspace):
        tid = create_task("My first task")
        assert tid is not None
        assert tid.startswith("task-")
        task = get_task(tid)
        assert task is not None
        assert task["meta"]["title"] == "My first task"
        assert task["meta"]["project"] == "inbox"

    def test_create_task_in_project(self, workspace):
        create_project("Work")
        tid = create_task("Do something", project_id="work", details={
            "priority": "high",
            "due": "2026-03-01",
            "tags": ["urgent"],
            "description": "Important work item",
        })
        task = get_task(tid)
        assert task["meta"]["priority"] == "high"
        assert task["meta"]["due"] == "2026-03-01"
        assert "urgent" in task["meta"]["tags"]

    def test_update_task_status(self, workspace):
        tid = create_task("Update me")
        assert update_task(tid, {"status": "in-progress"})
        task = get_task(tid)
        assert task["meta"]["status"] == "in-progress"

    def test_update_task_invalid_status_ignored(self, workspace):
        tid = create_task("Bad status")
        assert update_task(tid, {"status": "invalid-status"})
        task = get_task(tid)
        # Should remain the original status since 'invalid-status' is rejected
        assert task["meta"]["status"] == "todo"

    def test_list_tasks_no_filter(self, workspace):
        create_task("Task A")
        create_task("Task B")
        tasks = list_tasks()
        assert len(tasks) >= 2

    def test_list_tasks_with_filter(self, workspace):
        create_task("High prio", details={"priority": "high"})
        create_task("Low prio", details={"priority": "low"})
        high = list_tasks(filter_by={"priority": "high"})
        assert all(t["priority"] == "high" for t in high)

    def test_list_tasks_by_project(self, workspace):
        create_project("Proj A")
        create_task("In A", project_id="proj-a")
        create_task("In inbox")
        proj_tasks = list_tasks(project_id="proj-a")
        assert len(proj_tasks) == 1
        assert proj_tasks[0]["title"] == "In A"

    def test_archive_task(self, workspace):
        tid = create_task("Archivable task")
        assert archive_task(tid)
        # Should not appear in normal listing
        tasks = list_tasks(filter_by={"status": "todo"})
        assert not any(t["id"] == tid for t in tasks)

    def test_move_task(self, workspace):
        create_project("Destination")
        tid = create_task("Movable")
        assert move_task(tid, "destination")
        task = get_task(tid)
        assert task["meta"]["project"] == "destination"

    def test_sequential_task_ids(self, workspace):
        t1 = create_task("First")
        t2 = create_task("Second")
        t3 = create_task("Third")
        # IDs should be sequential
        assert t1 == "task-001"
        assert t2 == "task-002"
        assert t3 == "task-003"


class TestTaskDependencies:
    def test_link_tasks(self, workspace):
        t1 = create_task("Prerequisite")
        t2 = create_task("Dependent")
        assert link_tasks(t2, t1)
        task = get_task(t2)
        assert t1 in task["meta"]["dependencies"]

    def test_circular_dependency_prevented(self, workspace):
        t1 = create_task("Task A")
        t2 = create_task("Task B")
        assert link_tasks(t1, t2)  # A depends on B
        assert not link_tasks(t2, t1)  # B depends on A → circular

    def test_duplicate_link_is_idempotent(self, workspace):
        t1 = create_task("A")
        t2 = create_task("B")
        assert link_tasks(t1, t2)
        assert link_tasks(t1, t2)  # Should succeed without duplicating
        task = get_task(t1)
        assert task["meta"]["dependencies"].count(t2) == 1


class TestAttachments:
    def test_add_attachment(self, workspace, tmp_path):
        create_project("Attach Test")
        # Create a temporary file to attach
        src = tmp_path / "diagram.png"
        src.write_bytes(b"fake png data")

        rel = add_attachment("attach-test", str(src))
        assert rel is not None
        assert "diagram.png" in rel
        assert (workspace / "projects" / "attach-test" / "attachments" / "diagram.png").exists()

    def test_add_attachment_missing_source(self, workspace):
        create_project("No File")
        result = add_attachment("no-file", "/nonexistent/file.png")
        assert result is None
