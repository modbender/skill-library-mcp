"""End-to-end CLI tests via subprocess."""

import json
import os
import subprocess
import sys
import pytest
from pathlib import Path

SCRIPT = str(Path(__file__).resolve().parent.parent / "scripts" / "task_engine.py")

_cli_tasks_dir = None


def run_cli(*args, expect_fail=False):
    """Run task_engine.py with args. Returns (returncode, stdout, stderr)."""
    env = os.environ.copy()
    if _cli_tasks_dir:
        env["TASK_ENGINE_TASKS_DIR"] = str(_cli_tasks_dir)
    cmd = [sys.executable, SCRIPT] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
    if not expect_fail and result.returncode != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    return result.returncode, result.stdout, result.stderr


def run_json(*args, expect_fail=False):
    """Run CLI with --json and parse output."""
    rc, stdout, stderr = run_cli(*args, expect_fail=expect_fail)
    if stdout.strip():
        try:
            return rc, json.loads(stdout.strip().split("\n")[-1]), stderr
        except json.JSONDecodeError:
            return rc, {"raw": stdout}, stderr
    return rc, {}, stderr


@pytest.fixture(autouse=True)
def cli_tasks_dir(tmp_path):
    """Set CLI tasks dir to a temp directory for subprocess isolation."""
    global _cli_tasks_dir
    d = tmp_path / "cli_tasks"
    d.mkdir()
    _cli_tasks_dir = d
    yield d
    _cli_tasks_dir = None


class TestCLILifecycle:
    """Full lifecycle: create -> approve -> dispatch -> start -> done -> archive."""

    def test_full_lifecycle(self):
        # Create
        rc, out, _ = run_json("create", "E2E test", "--priority", "P1", "--json")
        assert rc == 0
        assert out.get("ok") is True
        task_id = out["task_id"]

        # Status (list)
        rc, stdout, _ = run_cli("status", "--json")
        assert rc == 0
        tasks = json.loads(stdout)
        assert any(t["id"] == task_id for t in tasks)

        # Transition: approve
        rc, out, _ = run_json("transition", task_id, "approve", "--json")
        assert rc == 0
        assert out["status"] == "APPROVED"

        # Dispatch subtask
        rc, out, _ = run_json("dispatch", task_id, "Dev work",
                              "--agent", "claude-code", "--type", "dev", "--json")
        assert rc == 0
        assert out.get("ok") is True
        subtask_id = out["subtask_id"]

        # Subtask start
        rc, out, _ = run_json("subtask", task_id, subtask_id, "start",
                              "--progress", "50", "--json")
        assert rc == 0
        assert out["status"] == "IN_PROGRESS"

        # Subtask done
        rc, out, _ = run_json("subtask", task_id, subtask_id, "done", "--json")
        assert rc == 0
        assert out["status"] == "DONE"

        # Check
        rc, stdout, _ = run_cli("check", "--json")
        assert rc == 0

        # Transition to review and complete
        rc, _, _ = run_json("transition", task_id, "review", "--json")
        assert rc == 0
        rc, out, _ = run_json("transition", task_id, "complete", "--json")
        assert rc == 0
        assert out["status"] == "COMPLETED"

        # Archive
        rc, out, _ = run_json("archive", task_id, "--json")
        assert rc == 0
        assert out.get("ok") is True

        # Rebuild index
        rc, out, _ = run_json("rebuild-index", "--json")
        assert rc == 0
        assert out.get("ok") is True


class TestCLIJsonOutput:
    """Test --json flag on various commands."""

    def test_create_json(self):
        rc, out, _ = run_json("create", "JSON test", "--json")
        assert rc == 0
        assert out["ok"] is True
        assert "task_id" in out

    def test_transition_json(self):
        run_cli("create", "Trans test")
        rc, out, _ = run_json("transition", "TASK-001", "approve", "--json")
        assert rc == 0
        assert out["ok"] is True

    def test_dispatch_json(self):
        run_cli("create", "Disp test")
        run_cli("transition", "TASK-001", "approve")
        rc, out, _ = run_json("dispatch", "TASK-001", "Work",
                              "--agent", "claude-code", "--json")
        assert rc == 0
        assert out["ok"] is True

    def test_archive_json(self):
        run_cli("create", "Arch test")
        run_cli("transition", "TASK-001", "reject")
        rc, out, _ = run_json("archive", "TASK-001", "--json")
        assert rc == 0
        assert out["ok"] is True


class TestCLIErrors:
    """Test error cases return non-zero exit code."""

    def test_invalid_transition(self):
        run_cli("create", "Error test")
        rc, out, _ = run_json("transition", "TASK-001", "complete", "--json",
                              expect_fail=True)
        assert rc != 0

    def test_task_not_found(self):
        rc, out, _ = run_json("transition", "TASK-999", "approve", "--json",
                              expect_fail=True)
        assert rc != 0

    def test_archive_non_terminal(self):
        run_cli("create", "Not done")
        rc, out, _ = run_json("archive", "TASK-001", "--json", expect_fail=True)
        assert rc != 0


class TestRebuildIndex:
    """Test rebuild-index command."""

    def test_rebuild_index_json(self):
        run_cli("create", "Rebuild A")
        run_cli("create", "Rebuild B")

        rc, out, _ = run_json("rebuild-index", "--json")
        assert rc == 0
        assert out["ok"] is True
        assert out["rebuilt"] == 2

    def test_rebuild_empty(self):
        rc, out, _ = run_json("rebuild-index", "--json")
        assert rc == 0
        assert out["rebuilt"] == 0
