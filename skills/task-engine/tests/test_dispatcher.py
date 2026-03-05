"""Tests for dispatcher.py — agent selection, readiness, context building."""

import pytest

from engine.dispatcher import (
    select_agent, build_dispatch_context, generate_dispatch_prompt,
    check_dispatch_readiness, get_active_agent_count, AGENT_REGISTRY,
)
from engine.task_store import (
    create_task, create_subtask, save_task, save_subtask,
    update_index_entry, read_all_subtasks, get_tasks_dir,
)


class TestSelectAgent:
    def test_dev_type_selects_claude_code(self):
        assert select_agent("dev") == "claude-code"

    def test_test_type_selects_eva(self):
        assert select_agent("test") == "eva"

    def test_validate_type_selects_eva(self):
        assert select_agent("validate") == "eva"

    def test_preferred_agent_override_capable(self):
        # claude-code has "docs" in capabilities, so preferred override works
        assert select_agent("docs", preferred_agent="claude-code") == "claude-code"

    def test_preferred_agent_incapable_falls_back(self):
        # claude-code doesn't have "test" in capabilities, so falls back
        result = select_agent("test", preferred_agent="claude-code")
        assert result == "eva"

    def test_unknown_type_fallback(self):
        assert select_agent("unknown_type") == "eva"


class TestBuildDispatchContext:
    def test_basic_context(self, tasks_dir):
        task = create_task(title="Context test")
        st = create_subtask(task.id, "Do work", agent="claude-code")

        task_dict = task.to_dict()
        # Re-read task to get updated subtasks list
        from engine.task_store import read_task
        task = read_task(task.id)
        task_dict = task.to_dict()
        all_st = [s.to_dict() for s in read_all_subtasks(task.id)]

        context = build_dispatch_context(task_dict, all_st[0], all_st)
        assert context["task_id"] == task.id
        assert context["subtask_id"] == st.id
        assert context["agent"] == "claude-code"

    def test_context_includes_deps(self, tasks_dir):
        task = create_task(title="Dep test")
        st1 = create_subtask(task.id, "First")
        st2 = create_subtask(task.id, "Second", deps=["subtask_01"])

        from engine.task_store import read_task
        task = read_task(task.id)
        all_st = [s.to_dict() for s in read_all_subtasks(task.id)]
        st2_dict = [s for s in all_st if s["id"] == "subtask_02"][0]

        context = build_dispatch_context(task.to_dict(), st2_dict, all_st)
        assert len(context["dependencies"]) == 1
        assert context["dependencies"][0]["id"] == "subtask_01"


class TestGenerateDispatchPrompt:
    def test_prompt_not_empty(self, tasks_dir):
        task = create_task(title="Prompt test")
        st = create_subtask(task.id, "Work item", agent="claude-code")

        from engine.task_store import read_task
        task = read_task(task.id)
        all_st = [s.to_dict() for s in read_all_subtasks(task.id)]
        context = build_dispatch_context(task.to_dict(), all_st[0], all_st)
        prompt = generate_dispatch_prompt(context)
        assert len(prompt) > 0
        assert "Work item" in prompt
        assert "openclaw system event" in prompt


class TestCheckDispatchReadiness:
    def test_ready_subtask(self, tasks_dir):
        task = create_task(title="Ready test")
        task.status = "APPROVED"
        save_task(task)
        st = create_subtask(task.id, "Work", agent="claude-code")

        from engine.task_store import read_task
        task = read_task(task.id)
        all_st = [s.to_dict() for s in read_all_subtasks(task.id)]

        # ASSIGNED subtask with APPROVED task should be ready
        ready, reason = check_dispatch_readiness(task.to_dict(), all_st[0], all_st)
        assert ready

    def test_not_ready_wrong_task_status(self, tasks_dir):
        task = create_task(title="Not ready")
        st = create_subtask(task.id, "Work")

        from engine.task_store import read_task
        task = read_task(task.id)
        all_st = [s.to_dict() for s in read_all_subtasks(task.id)]

        ready, reason = check_dispatch_readiness(task.to_dict(), all_st[0], all_st)
        assert not ready
        assert "PLANNING" in reason

    def test_not_ready_unmet_deps(self, tasks_dir):
        task = create_task(title="Dep test")
        task.status = "APPROVED"
        save_task(task)
        st1 = create_subtask(task.id, "First")
        st2 = create_subtask(task.id, "Second", deps=["subtask_01"])

        from engine.task_store import read_task
        task = read_task(task.id)
        all_st = [s.to_dict() for s in read_all_subtasks(task.id)]
        st2_dict = [s for s in all_st if s["id"] == "subtask_02"][0]

        ready, reason = check_dispatch_readiness(task.to_dict(), st2_dict, all_st)
        assert not ready
        # Subtask is BLOCKED due to deps, so readiness check catches that
        assert "BLOCKED" in reason or "subtask_01" in reason


class TestGetActiveAgentCount:
    def test_no_active(self, tasks_dir):
        assert get_active_agent_count("claude-code", tasks_dir) == 0

    def test_counts_in_progress(self, tasks_dir):
        task = create_task(title="Count test")
        st = create_subtask(task.id, "Working", agent="claude-code")
        st.status = "IN_PROGRESS"
        save_subtask(st)

        count = get_active_agent_count("claude-code", tasks_dir)
        assert count == 1

    def test_ignores_other_agents(self, tasks_dir):
        task = create_task(title="Agent test")
        st = create_subtask(task.id, "Eva work", agent="eva")
        st.status = "IN_PROGRESS"
        save_subtask(st)

        assert get_active_agent_count("claude-code", tasks_dir) == 0
        assert get_active_agent_count("eva", tasks_dir) == 1
