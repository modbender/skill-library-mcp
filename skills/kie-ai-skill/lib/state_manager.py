#!/usr/bin/env python3
"""
State manager for kie.ai tasks
Tracks active tasks to prevent duplicates and enable resume
"""

import json
import os
import time
from pathlib import Path

STATE_FILE = Path(__file__).parent.parent / ".task-state.json"


def load_state():
    """Load task state from disk"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    if not STATE_FILE.exists():
        return {}
    
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_state(state):
    """Save task state to disk"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def add_task(task_id, prompt, model="nano-banana-pro", metadata=None):
    """Add a new task to state"""
    state = load_state()
    
    state[task_id] = {
        "prompt": prompt,
        "model": model,
        "status": "pending",
        "created_at": int(time.time()),
        "updated_at": int(time.time()),
        "metadata": metadata or {}
    }
    
    save_state(state)


def update_task(task_id, status, result_data=None):
    """Update task status"""
    state = load_state()
    
    if task_id not in state:
        return False
    
    state[task_id]["status"] = status
    state[task_id]["updated_at"] = int(time.time())
    
    if result_data:
        state[task_id]["result"] = result_data
    
    save_state(state)
    return True


def get_task(task_id):
    """Get task info"""
    state = load_state()
    return state.get(task_id)


def list_active_tasks():
    """List all non-completed tasks"""
    state = load_state()
    active = []
    
    for task_id, data in state.items():
        if data["status"] not in ["success", "failed"]:
            active.append((task_id, data))
    
    return active


def cleanup_old_tasks(max_age_days=7):
    """Remove old completed tasks"""
    state = load_state()
    now = int(time.time())
    max_age_seconds = max_age_days * 86400
    
    cleaned = {}
    for task_id, data in state.items():
        age = now - data.get("updated_at", 0)
        if data["status"] not in ["success", "failed"] or age < max_age_seconds:
            cleaned[task_id] = data
    
    save_state(cleaned)
    return len(state) - len(cleaned)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: state-manager.py <command> [args]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        tasks = list_active_tasks()
        if not tasks:
            print("No active tasks")
        else:
            print(f"Active tasks: {len(tasks)}")
            for task_id, data in tasks:
                print(f"  {task_id[:16]}... - {data['status']} - {data['prompt'][:50]}")
    
    elif cmd == "cleanup":
        removed = cleanup_old_tasks()
        print(f"Removed {removed} old tasks")
    
    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: state-manager.py get <task-id>")
            sys.exit(1)
        
        task_id = sys.argv[2]
        task = get_task(task_id)
        
        if task:
            print(json.dumps(task, indent=2))
        else:
            print(f"Task {task_id} not found")
            sys.exit(1)
