"""Project registry — tracks threads, owners, participants, and descriptions."""

import json
import os
import fcntl
from datetime import datetime, timezone

PROJECTS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "projects.json"
)

def _load():
    if not os.path.exists(PROJECTS_FILE):
        return {"threads": {}}
    with open(PROJECTS_FILE, "r") as f:
        return json.load(f)

def _save(data):
    os.makedirs(os.path.dirname(PROJECTS_FILE), exist_ok=True)
    tmp = PROJECTS_FILE + ".tmp"
    with open(tmp, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
        fcntl.flock(f, fcntl.LOCK_UN)
    os.replace(tmp, PROJECTS_FILE)

def register_thread(thread_id, name, owner, participants, forum_id, description=""):
    """Register a new project thread."""
    data = _load()
    data["threads"][str(thread_id)] = {
        "name": name,
        "description": description,
        "owner": owner,
        "participants": sorted(set(participants)),
        "status": "active",
        "forum": str(forum_id),
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "nextAction": "",
    }
    _save(data)

def archive_thread(thread_id):
    """Mark a thread as archived."""
    data = _load()
    tid = str(thread_id)
    if tid in data["threads"]:
        data["threads"][tid]["status"] = "archived"
        data["threads"][tid]["archived_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        _save(data)
        return True
    return False

def add_participant(thread_id, agent_id):
    """Add a participant to a project."""
    data = _load()
    tid = str(thread_id)
    if tid not in data["threads"]:
        return False
    participants = data["threads"][tid].get("participants", [])
    if agent_id not in participants:
        participants.append(agent_id)
        data["threads"][tid]["participants"] = sorted(participants)
        _save(data)
    return True

def remove_participant(thread_id, agent_id):
    """Remove a participant from a project."""
    data = _load()
    tid = str(thread_id)
    if tid not in data["threads"]:
        return False
    participants = data["threads"][tid].get("participants", [])
    if agent_id in participants:
        participants.remove(agent_id)
        data["threads"][tid]["participants"] = sorted(participants)
        _save(data)
    return True

def get_thread(thread_id):
    """Get project info for a thread."""
    data = _load()
    return data["threads"].get(str(thread_id))

def list_projects(status=None):
    """List all projects, optionally filtered by status."""
    data = _load()
    results = {}
    for tid, info in data["threads"].items():
        if status is None or info.get("status") == status:
            results[tid] = info
    return results

def update_description(thread_id, description):
    """Update a project's description."""
    data = _load()
    tid = str(thread_id)
    if tid in data["threads"]:
        data["threads"][tid]["description"] = description
        _save(data)
        return True
    return False

def update_next_action(thread_id, next_action):
    """Update a project's next action."""
    data = _load()
    tid = str(thread_id)
    if tid in data["threads"]:
        data["threads"][tid]["nextAction"] = next_action
        _save(data)
        return True
    return False

def list_by_agent(agent_id, status=None):
    """List projects where agent is owner or participant."""
    data = _load()
    results = {}
    for tid, info in data["threads"].items():
        if status and info.get("status") != status:
            continue
        if info.get("owner") == agent_id or agent_id in info.get("participants", []):
            role = "owner" if info.get("owner") == agent_id else "participant"
            results[tid] = {**info, "role": role}
    return results
