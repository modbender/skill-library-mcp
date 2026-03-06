"""Tests for task_store.py — CRUD, atomic writes, index management."""

import json
import pytest

from engine.task_store import (
    create_task, read_task, save_task, list_tasks,
    create_subtask, read_subtask, save_subtask, read_all_subtasks,
    archive_task, update_index_entry, count_done_subtasks,
    read_index, write_index, atomic_write,
    get_task_dir, get_tasks_dir,
)
from engine.models import Task, TERMINAL_TASK_STATUSES


class TestCreateTask:
    def test_create_task_basic(self, tasks_dir):
        task = create_task(title="My task", priority="P0")
        assert task.id == "TASK-001"
        assert task.title == "My task"
        assert task.priority == "P0"
        assert task.status == "PLANNING"

    def test_create_task_with_plan(self, tasks_dir):
        task = create_task(title="Planned task", plan_text="Do X then Y")
        assert task.plan["summary"] == "Do X then Y"

    def test_create_task_files_exist(self, tasks_dir):
        task = create_task(title="File test")
        task_dir = tasks_dir / task.id
        assert (task_dir / "task.json").exists()
        assert (task_dir / "log.jsonl").exists()

    def test_create_multiple_tasks_sequential_ids(self, tasks_dir):
        t1 = create_task(title="First")
        t2 = create_task(title="Second")
        t3 = create_task(title="Third")
        assert t1.id == "TASK-001"
        assert t2.id == "TASK-002"
        assert t3.id == "TASK-003"


class TestReadSaveTask:
    def test_read_task_roundtrip(self, tasks_dir):
        original = create_task(title="Roundtrip test")
        loaded = read_task(original.id)
        assert loaded is not None
        assert loaded.id == original.id
        assert loaded.title == original.title

    def test_read_nonexistent_task(self, tasks_dir):
        assert read_task("TASK-999") is None

    def test_save_task_updates(self, tasks_dir):
        task = create_task(title="Save test")
        task.status = "APPROVED"
        save_task(task)
        reloaded = read_task(task.id)
        assert reloaded.status == "APPROVED"


class TestListTasks:
    def test_list_tasks_empty(self, tasks_dir):
        assert list_tasks() == []

    def test_list_tasks_filters_terminal(self, tasks_dir):
        t1 = create_task(title="Active")
        t2 = create_task(title="Done")
        t2.status = "COMPLETED"
        save_task(t2)
        update_index_entry(t2.id, status="COMPLETED")

        active = list_tasks(include_terminal=False)
        assert len(active) == 1
        assert active[0]["id"] == t1.id

        all_tasks = list_tasks(include_terminal=True)
        assert len(all_tasks) == 2

    def test_list_tasks_includes_all(self, tasks_dir):
        create_task(title="A")
        create_task(title="B")
        assert len(list_tasks()) == 2


class TestIndex:
    def test_index_created_on_task_create(self, tasks_dir):
        create_task(title="Index test")
        index = read_index()
        assert len(index["tasks"]) == 1
        assert index["tasks"][0]["id"] == "TASK-001"

    def test_update_index_entry(self, tasks_dir):
        create_task(title="Update test")
        update_index_entry("TASK-001", status="APPROVED")
        index = read_index()
        assert index["tasks"][0]["status"] == "APPROVED"

    def test_rebuild_index(self, tasks_dir):
        t1 = create_task(title="Task A")
        t2 = create_task(title="Task B")

        # Corrupt index
        write_index({"version": 1, "tasks": []})
        assert len(read_index()["tasks"]) == 0

        # Rebuild by reading task dirs
        new_entries = []
        for d in sorted(tasks_dir.iterdir()):
            if d.is_dir() and d.name.startswith("TASK-"):
                tp = d / "task.json"
                if tp.exists():
                    data = json.loads(tp.read_text())
                    new_entries.append({
                        "id": data["id"],
                        "title": data["title"],
                        "status": data.get("status", "PLANNING"),
                        "priority": data.get("priority", "P1"),
                        "created": data.get("created", ""),
                        "subtask_count": 0,
                        "subtasks_done": 0,
                    })
        write_index({"version": 1, "tasks": new_entries})
        assert len(read_index()["tasks"]) == 2


class TestSubtaskCrud:
    def test_create_subtask(self, tasks_dir):
        task = create_task(title="Parent")
        st = create_subtask(task.id, "Child subtask", agent="claude-code")
        assert st.id == "subtask_01"
        assert st.parent_task == task.id

    def test_read_subtask(self, tasks_dir):
        task = create_task(title="Parent")
        create_subtask(task.id, "Child")
        loaded = read_subtask(task.id, "subtask_01")
        assert loaded is not None
        assert loaded.title == "Child"

    def test_read_nonexistent_subtask(self, tasks_dir):
        task = create_task(title="Parent")
        assert read_subtask(task.id, "subtask_99") is None

    def test_read_all_subtasks(self, tasks_dir):
        task = create_task(title="Parent")
        create_subtask(task.id, "A")
        create_subtask(task.id, "B")
        create_subtask(task.id, "C")
        all_st = read_all_subtasks(task.id)
        assert len(all_st) == 3

    def test_subtask_with_deps_is_blocked(self, tasks_dir):
        task = create_task(title="Parent")
        st1 = create_subtask(task.id, "First")
        st2 = create_subtask(task.id, "Second", deps=["subtask_01"])
        assert st2.status == "BLOCKED"

    def test_count_done_subtasks(self, tasks_dir):
        task = create_task(title="Parent")
        st = create_subtask(task.id, "Work", agent="claude-code")
        assert count_done_subtasks(task.id) == 0

        st.status = "DONE"
        save_subtask(st)
        assert count_done_subtasks(task.id) == 1


class TestArchive:
    def test_archive_completed_task(self, tasks_dir):
        task = create_task(title="Archive me")
        task.status = "COMPLETED"
        save_task(task)
        update_index_entry(task.id, status="COMPLETED")

        assert archive_task(task.id)
        assert (tasks_dir / "archive" / task.id / "task.json").exists()
        assert not (tasks_dir / task.id).exists()

        # Removed from index
        index = read_index()
        assert all(e["id"] != task.id for e in index["tasks"])

    def test_archive_non_terminal_fails(self, tasks_dir):
        task = create_task(title="Still active")
        assert not archive_task(task.id)

    def test_read_archived_task(self, tasks_dir):
        task = create_task(title="Archive read test")
        task.status = "COMPLETED"
        save_task(task)
        update_index_entry(task.id, status="COMPLETED")
        archive_task(task.id)

        loaded = read_task(task.id)
        assert loaded is not None
        assert loaded.title == "Archive read test"


class TestAtomicWrite:
    def test_atomic_write_creates_file(self, tmp_path):
        path = tmp_path / "test.json"
        atomic_write(path, {"key": "value"})
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["key"] == "value"

    def test_atomic_write_no_partial(self, tmp_path):
        path = tmp_path / "test.json"
        atomic_write(path, {"first": True})
        atomic_write(path, {"second": True})
        data = json.loads(path.read_text())
        assert "second" in data
        # No tmp file left
        assert not path.with_suffix(".tmp").exists()
