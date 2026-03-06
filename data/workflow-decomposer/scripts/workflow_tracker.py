#!/usr/bin/env python3
"""
Workflow State Tracker

Manages workflow state in JSON format for progress tracking across steps.
"""

import json
import os
from datetime import datetime
from pathlib import Path

WORKFLOW_STATE_FILE = "workflow-state.json"

def get_state_path(workspace_root):
    """Get the path to the workflow state file."""
    return Path(workspace_root) / "memory" / WORKFLOW_STATE_FILE

def load_state(workspace_root):
    """Load current workflow state."""
    state_path = get_state_path(workspace_root)
    if state_path.exists():
        with open(state_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_state(workspace_root, state):
    """Save workflow state."""
    state_path = get_state_path(workspace_root)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def create_workflow(decomposition_model, steps, workspace_root):
    """Create a new workflow state."""
    state = {
        "created": datetime.now().isoformat(),
        "decomposition_model": decomposition_model,
        "current_step_index": 0,
        "status": "in-progress",
        "steps": [
            {
                "index": i,
                "name": step.get("name", f"Step {i+1}"),
                "description": step.get("description", ""),
                "model": step.get("model", "default"),
                "status": "pending",
                "started": None,
                "completed": None,
                "error": None
            }
            for i, step in enumerate(steps)
        ]
    }
    save_state(workspace_root, state)
    return state

def advance_step(workspace_root):
    """Mark current step as complete and move to next."""
    state = load_state(workspace_root)
    if not state:
        return {"error": "No active workflow"}
    
    current_idx = state["current_step_index"]
    if current_idx >= len(state["steps"]):
        state["status"] = "completed"
        save_state(workspace_root, state)
        return state
    
    # Mark current step complete
    state["steps"][current_idx]["status"] = "completed"
    state["steps"][current_idx]["completed"] = datetime.now().isoformat()
    
    # Move to next step
    state["current_step_index"] += 1
    if state["current_step_index"] < len(state["steps"]):
        state["steps"][state["current_step_index"]]["status"] = "in-progress"
        state["steps"][state["current_step_index"]]["started"] = datetime.now().isoformat()
    else:
        state["status"] = "completed"
    
    save_state(workspace_root, state)
    return state

def report_stuck(workspace_root, issue, cause, solutions, recommendation):
    """Report a stuck step with issue details."""
    state = load_state(workspace_root)
    if not state:
        return {"error": "No active workflow"}
    
    current_idx = state["current_step_index"]
    state["steps"][current_idx]["status"] = "blocked"
    state["steps"][current_idx]["error"] = {
        "issue": issue,
        "cause": cause,
        "solutions": solutions,
        "recommendation": recommendation,
        "reported": datetime.now().isoformat()
    }
    state["status"] = "blocked"
    
    save_state(workspace_root, state)
    return state

def get_status(workspace_root):
    """Get current workflow status summary."""
    state = load_state(workspace_root)
    if not state:
        return {"active": False}
    
    current_step = state["steps"][state["current_step_index"]] if state["current_step_index"] < len(state["steps"]) else None
    
    return {
        "active": True,
        "decomposition_model": state["decomposition_model"],
        "current_step": state["current_step_index"] + 1,
        "total_steps": len(state["steps"]),
        "status": state["status"],
        "current_step_name": current_step["name"] if current_step else "N/A",
        "current_step_model": current_step["model"] if current_step else "N/A"
    }

def format_status_markdown(state):
    """Format workflow state as markdown status."""
    if not state:
        return "No active workflow"
    
    lines = [
        "## Workflow Status",
        "",
        f"**Decomposition Model:** `{state['decomposition_model']}`",
        f"**Current Step:** {state['current_step_index'] + 1} of {len(state['steps'])}",
        f"**Status:** {state['status']}",
        "",
        "### Steps",
        ""
    ]
    
    for step in state["steps"]:
        checkbox = {
            "pending": "- [ ]",
            "in-progress": "- [~]",
            "completed": "- [x]",
            "blocked": "- [!]"
        }.get(step["status"], "- [ ]")
        
        status_emoji = {
            "pending": "",
            "in-progress": " 🔄",
            "completed": " ✅",
            "blocked": " ⚠️"
        }.get(step["status"], "")
        
        model_info = f" - Model: `{step['model']}`"
        lines.append(f"{checkbox} **Step {step['index'] + 1}:** {step['name']}{status_emoji}{model_info}")
    
    return "\n".join(lines)

if __name__ == "__main__":
    import sys
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    action = sys.argv[2] if len(sys.argv) > 2 else "status"
    
    if action == "status":
        state = load_state(workspace)
        print(format_status_markdown(state))
    elif action == "init":
        # Would need more args for full init
        print("Use create_workflow() function directly")
