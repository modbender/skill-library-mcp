"""dispatcher.py — Multi-agent dispatch logic.

Selects appropriate agents for subtasks, builds dispatch context,
and generates payloads for Eva to execute via OpenClaw tools.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .models import Subtask, SUBTASK_TYPES
from .task_store import get_tasks_dir, read_task, read_all_subtasks, read_subtask


# --- Agent Registry ---

AGENT_REGISTRY: dict[str, dict] = {
    "claude-code": {
        "name": "Claude Code",
        "capabilities": ["dev", "refactor", "debug", "docs"],
        "preferred_types": ["dev"],
        "max_parallel": 3,
        "dispatch_method": "cli",
    },
    "eva": {
        "name": "Eva",
        "capabilities": ["test", "validate", "system-ops", "docs"],
        "preferred_types": ["test", "validate"],
        "max_parallel": 1,
        "dispatch_method": "self",
    },
}


def select_agent(subtask_type: str, preferred_agent: str | None = None,
                 config: dict = None) -> str:
    """Select best agent for a subtask type.

    Priority:
    1. If preferred_agent is specified and capable -> use it
    2. Match by preferred_types
    3. Match by capabilities
    4. Fallback to "eva"

    Returns agent key (e.g. "claude-code", "eva")
    """
    registry = AGENT_REGISTRY

    # 1. Preferred agent if capable
    if preferred_agent and preferred_agent in registry:
        agent_info = registry[preferred_agent]
        if subtask_type in agent_info["capabilities"]:
            return preferred_agent

    # 2. Match by preferred_types
    for agent_key, agent_info in registry.items():
        if subtask_type in agent_info["preferred_types"]:
            return agent_key

    # 3. Match by capabilities
    for agent_key, agent_info in registry.items():
        if subtask_type in agent_info["capabilities"]:
            return agent_key

    # 4. Fallback
    return "eva"


def build_dispatch_context(task: dict, subtask: dict,
                           all_subtasks: list[dict]) -> dict:
    """Build complete context package for an agent.

    Returns a dict with all info an agent needs to execute the subtask.
    """
    # Resolve dependencies with their status and results
    dependencies = []
    for dep_id in subtask.get("dependencies", []):
        for st in all_subtasks:
            if st["id"] == dep_id:
                dep_info = {
                    "id": dep_id,
                    "status": st.get("status", "PENDING"),
                    "title": st.get("title", ""),
                }
                result = st.get("result", {})
                if result and result.get("summary"):
                    dep_info["result"] = result["summary"]
                dependencies.append(dep_info)
                break

    # Build constraints from task metadata
    constraints = []
    tags = task.get("metadata", {}).get("tags", [])
    if tags:
        constraints.extend(tags)

    # Determine agent
    assigned_agent = subtask.get("assignment", {}).get("agent")
    agent = assigned_agent or select_agent(subtask.get("type", "dev"))
    agent_config = AGENT_REGISTRY.get(agent, AGENT_REGISTRY["eva"])

    return {
        "task_id": task["id"],
        "subtask_id": subtask["id"],
        "title": subtask.get("title", ""),
        "description": subtask.get("description", ""),
        "acceptance_criteria": subtask.get("acceptance_criteria", []),
        "workspace": {
            "branch": f"{task['id'].lower()}-{subtask['id']}",
            "paths": [],
        },
        "dependencies": dependencies,
        "constraints": constraints,
        "agent": agent,
        "agent_config": {
            "name": agent_config["name"],
            "dispatch_method": agent_config["dispatch_method"],
            "max_parallel": agent_config["max_parallel"],
        },
    }


def generate_dispatch_prompt(context: dict) -> str:
    """Generate a prompt string for CLI-based agents (Claude Code, Codex).

    Takes the dispatch context and produces a clear, structured prompt
    that the agent can execute independently.
    """
    lines = []

    lines.append(f"## Task: {context['title']}")
    lines.append("")

    # Context section
    lines.append("### Context")
    lines.append(f"Parent task: {context['task_id']}")
    if context.get("description"):
        lines.append(f"Description: {context['description']}")
    if context["dependencies"]:
        lines.append("")
        lines.append("Completed dependencies:")
        for dep in context["dependencies"]:
            status = dep.get("status", "?")
            result = dep.get("result", "")
            result_text = f" — {result}" if result else ""
            lines.append(f"- {dep['id']} ({dep.get('title', '')}): {status}{result_text}")
    lines.append("")

    # Assignment section
    lines.append("### Your Assignment")
    lines.append(f"Subtask: {context['subtask_id']}")
    lines.append(f"Title: {context['title']}")
    if context.get("description"):
        lines.append(context["description"])
    lines.append("")

    # Acceptance criteria
    if context.get("acceptance_criteria"):
        lines.append("### Acceptance Criteria")
        for criterion in context["acceptance_criteria"]:
            lines.append(f"- {criterion}")
        lines.append("")

    # Constraints
    if context.get("constraints"):
        lines.append("### Constraints")
        for constraint in context["constraints"]:
            lines.append(f"- {constraint}")
        lines.append("")

    # When done
    lines.append("### When Done")
    lines.append(f'Run: openclaw system event --text "Done: {context["subtask_id"]} <brief summary>" --mode now')

    return "\n".join(lines)


def check_dispatch_readiness(task: dict, subtask: dict,
                             all_subtasks: list[dict]) -> tuple[bool, str]:
    """Check if a subtask is ready to be dispatched.

    Checks:
    - Subtask status is PENDING or ASSIGNED
    - All dependencies are DONE
    - Agent is available (not at max_parallel)
    - Task is in dispatchable state (APPROVED or IN_PROGRESS)

    Returns: (ready: bool, reason: str)
    """
    # Task must be in a dispatchable state
    if task.get("status") not in ("APPROVED", "IN_PROGRESS"):
        return (False, f"Task status is {task.get('status')}, must be APPROVED or IN_PROGRESS")

    # Subtask must be PENDING or ASSIGNED
    subtask_status = subtask.get("status", "")
    if subtask_status not in ("PENDING", "ASSIGNED"):
        return (False, f"Subtask status is {subtask_status}, must be PENDING or ASSIGNED")

    # All dependencies must be DONE
    deps = subtask.get("dependencies", [])
    for dep_id in deps:
        for st in all_subtasks:
            if st["id"] == dep_id:
                if st.get("status") != "DONE":
                    return (False, f"Dependency {dep_id} not DONE (status: {st.get('status')})")
                break
        else:
            return (False, f"Dependency {dep_id} not found")

    # Check agent capacity
    assigned_agent = subtask.get("assignment", {}).get("agent")
    agent = assigned_agent or select_agent(subtask.get("type", "dev"))
    agent_info = AGENT_REGISTRY.get(agent, AGENT_REGISTRY["eva"])
    max_parallel = agent_info["max_parallel"]

    active_count = get_active_agent_count(agent, get_tasks_dir())
    if active_count >= max_parallel:
        return (False, f"Agent {agent} at capacity ({active_count}/{max_parallel})")

    return (True, "All dependencies met")


def get_active_agent_count(agent: str, tasks_dir: Path) -> int:
    """Count how many subtasks are currently IN_PROGRESS for an agent across all tasks.

    Reads index.json + active tasks to count IN_PROGRESS subtasks per agent.
    """
    index_path = tasks_dir / "index.json"
    if not index_path.exists():
        return 0

    index = json.loads(index_path.read_text(encoding="utf-8"))
    count = 0

    for entry in index.get("tasks", []):
        task_id = entry["id"]
        task_dir = tasks_dir / task_id
        if not task_dir.exists():
            continue

        # Read task to get subtask list
        task_path = task_dir / "task.json"
        if not task_path.exists():
            continue

        task_data = json.loads(task_path.read_text(encoding="utf-8"))
        for subtask_id in task_data.get("subtasks", []):
            st_path = task_dir / f"{subtask_id}.json"
            if not st_path.exists():
                continue
            st_data = json.loads(st_path.read_text(encoding="utf-8"))
            if (st_data.get("status") == "IN_PROGRESS" and
                    st_data.get("assignment", {}).get("agent") == agent):
                count += 1

    return count
