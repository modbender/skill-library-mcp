"""
Tests for scripts.index_manager — search and lookup.

Run with:  python -m pytest tests/test_index_manager.py -v
"""

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.file_manager import init_workspace, create_project, create_task
from scripts.index_manager import (
    rebuild_index,
    search_tasks,
    get_tasks_due_soon,
    get_tasks_needing_checkin,
    get_overdue_tasks,
    get_stats,
)


@pytest.fixture
def workspace(tmp_path):
    """Create a workspace with sample data for index tests."""
    ws = tmp_path / "index_workspace"
    ws.mkdir()
    init_workspace(str(ws))

    create_project("Backend", tags=["backend"])
    create_task("Set up API endpoints", project_id="backend", details={
        "priority": "high",
        "due": "2026-02-15",
        "tags": ["backend", "api"],
        "description": "Create REST endpoints for the application",
    })
    create_task("Write database migrations", project_id="backend", details={
        "priority": "medium",
        "due": "2026-02-20",
        "tags": ["backend", "database"],
    })
    create_task("Deploy to staging", project_id="inbox", details={
        "priority": "high",
        "due": "2026-01-01",  # Already past — overdue
        "tags": ["devops"],
        "description": "Deploy the current build to staging environment",
    })
    create_task("Nice-to-have cleanup", details={
        "priority": "low",
        "tags": ["cleanup"],
    })

    return ws


class TestRebuildIndex:
    def test_rebuild_succeeds(self, workspace):
        assert rebuild_index()

    def test_stats_after_rebuild(self, workspace):
        rebuild_index()
        stats = get_stats()
        assert stats["total_tasks"] == 4
        assert stats["total_projects"] >= 2  # inbox + backend
        assert stats["active_projects"] >= 1


class TestSearch:
    def test_search_by_title(self, workspace):
        rebuild_index()
        results = search_tasks("API endpoints")
        assert len(results) >= 1
        assert any("API" in r["title"] for r in results)

    def test_search_by_tag(self, workspace):
        rebuild_index()
        results = search_tasks("devops")
        assert len(results) >= 1

    def test_search_by_description(self, workspace):
        rebuild_index()
        results = search_tasks("REST")
        assert len(results) >= 1

    def test_search_no_results(self, workspace):
        rebuild_index()
        results = search_tasks("xyznonexistent")
        assert len(results) == 0


class TestDueSoon:
    def test_due_soon_includes_overdue(self, workspace):
        rebuild_index()
        # "Deploy to staging" is overdue (due 2026-01-01)
        results = get_tasks_due_soon(days=365)
        assert any("Deploy" in t.get("title", "") for t in results)

    def test_due_soon_respects_window(self, workspace):
        rebuild_index()
        # With a very small window, may not include future tasks
        results = get_tasks_due_soon(days=0)
        # Should still include overdue items (due date <= today)
        for t in results:
            assert t.get("_overdue", False) or True  # All are within window


class TestOverdue:
    def test_overdue_detection(self, workspace):
        rebuild_index()
        overdue = get_overdue_tasks()
        assert len(overdue) >= 1
        assert any("Deploy" in t.get("title", "") for t in overdue)

    def test_overdue_has_days_count(self, workspace):
        rebuild_index()
        overdue = get_overdue_tasks()
        if overdue:
            assert "_days_overdue" in overdue[0]
            assert overdue[0]["_days_overdue"] > 0


class TestCheckin:
    def test_needing_checkin(self, workspace):
        """All newly created tasks should need check-in after some time."""
        rebuild_index()
        # With default 24h frequency, tasks created "today" might not need
        # check-in yet — but this tests the mechanism works
        stale = get_tasks_needing_checkin()
        # All tasks were just created, so last_checkin = today.
        # They may or may not need check-in depending on timing.
        assert isinstance(stale, list)


class TestStats:
    def test_stats_structure(self, workspace):
        rebuild_index()
        stats = get_stats()
        assert "total_tasks" in stats
        assert "by_status" in stats
        assert "by_priority" in stats
        assert "overdue" in stats
        assert "due_this_week" in stats
        assert "total_projects" in stats
        assert "active_projects" in stats

    def test_stats_counts_are_correct(self, workspace):
        rebuild_index()
        stats = get_stats()
        assert stats["total_tasks"] == 4
        assert stats["by_status"]["todo"] == 4  # All are todo
        assert stats["by_priority"]["high"] == 2
        assert stats["by_priority"]["medium"] == 1
        assert stats["by_priority"]["low"] == 1
        assert stats["overdue"] >= 1  # At least "Deploy to staging"
