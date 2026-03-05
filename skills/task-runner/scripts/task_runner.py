#!/usr/bin/env python3
"""
Task Runner - Manage tasks and projects across sessions
Usage: python3 task_runner.py add "task description" [project] [priority]
       python3 task_runner.py list [project]
       python3 task_runner.py complete <task_id>
       python3 task_runner.py priority <task_id> <low|medium|high>
       python3 task_runner.py export <project> <output_file>
"""

import json
import sys
from pathlib import Path
from datetime import datetime

DB_PATH = Path.home() / ".openclaw" / "workspace" / "tasks_db.json"
DEFAULT_PROJECT = "general"

def load_db():
    """Load tasks database from JSON file."""
    if not DB_PATH.exists():
        return {"tasks": [], "next_id": 1}
    try:
        with open(DB_PATH, 'r') as f:
            return json.load(f)
    except:
        return {"tasks": [], "next_id": 1}

def save_db(db):
    """Save tasks database to JSON file."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=2)

def add(description, project=DEFAULT_PROJECT, priority="medium"):
    """Add a new task."""
    db = load_db()
    
    task_id = db["next_id"]
    db["next_id"] += 1
    
    task = {
        "id": task_id,
        "description": description,
        "project": project,
        "priority": priority,
        "status": "pending",
        "created": datetime.now().isoformat(),
        "completed": None
    }
    
    db["tasks"].append(task)
    save_db(db)
    print(f"✓ Added task #{task_id} to project '{project}' [{priority} priority]")
    return task_id

def list_tasks(project=None):
    """List tasks, optionally filtered by project."""
    db = load_db()
    
    if not db["tasks"]:
        print("No tasks yet.")
        return
    
    tasks = db["tasks"]
    if project:
        tasks = [t for t in tasks if t["project"] == project]
        if not tasks:
            print(f"No tasks found in project '{project}'")
            return
    
    # Sort: pending first, then by priority, then by creation date
    priority_order = {"high": 0, "medium": 1, "low": 2}
    tasks.sort(key=lambda t: (t["status"] != "pending", priority_order.get(t["priority"], 1), t["created"]))
    
    print(f"\n📋 Tasks" + (f" - {project}" if project else ""))
    print("-" * 70)
    
    for task in tasks:
        status_icon = "✅" if task["status"] == "completed" else "⏳"
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task["priority"], "⚪")
        created = task["created"][:10]
        
        status_text = f"{status_icon} [{task['project']}]"
        print(f"{status_text:30} #{task['id']:4d} {priority_emoji} {created}")
        print(f"{'':31}     {task['description']}")
        if task["completed"]:
            print(f"{'':31}     (completed: {task['completed'][:10]})")
        print()
    
    # Summary
    pending = [t for t in tasks if t["status"] == "pending"]
    completed = [t for t in tasks if t["status"] == "completed"]
    print(f"\nTotal: {len(tasks)} tasks ({len(pending)} pending, {len(completed)} completed)\n")

def complete(task_id):
    """Mark a task as completed."""
    db = load_db()
    
    for task in db["tasks"]:
        if task["id"] == task_id:
            task["status"] = "completed"
            task["completed"] = datetime.now().isoformat()
            save_db(db)
            print(f"✓ Completed task #{task_id}: {task['description']}")
            return True
    
    print(f"Task #{task_id} not found")
    return False

def set_priority(task_id, priority):
    """Set task priority."""
    db = load_db()
    
    valid_priorities = ["low", "medium", "high"]
    if priority not in valid_priorities:
        print(f"Invalid priority. Use: {', '.join(valid_priorities)}")
        return False
    
    for task in db["tasks"]:
        if task["id"] == task_id:
            task["priority"] = priority
            save_db(db)
            print(f"✓ Task #{task_id} priority set to {priority}")
            return True
    
    print(f"Task #{task_id} not found")
    return False

def is_safe_path(filepath):
    """Check if file path is within safe directories (workspace, home, or /tmp)."""
    try:
        path = Path(filepath).expanduser().resolve()
        workspace = Path.home() / ".openclaw" / "workspace"
        home = Path.home()
        tmp = Path("/tmp")
        
        # Convert to strings for comparison
        path_str = str(path)
        workspace_str = str(workspace.resolve())
        home_str = str(home.resolve())
        tmp_str = str(tmp.resolve())
        
        # Allow workspace, home, and /tmp
        in_workspace = path_str.startswith(workspace_str)
        in_home = path_str.startswith(home_str)
        in_tmp = path_str.startswith(tmp_str)
        
        # Block system paths
        system_dirs = ["/etc", "/usr", "/var", "/root", "/bin", "/sbin", "/lib", "/lib64", "/opt", "/boot", "/proc", "/sys"]
        blocked = any(path_str.startswith(d) for d in system_dirs)
        
        # Block sensitive dotfiles in home directory
        sensitive_patterns = [".ssh", ".bashrc", ".zshrc", ".profile", ".bash_profile", ".config/autostart"]
        for pattern in sensitive_patterns:
            if pattern in path_str:
                blocked = True
                break
        
        # Allow workspace, /tmp, or home (excluding blocked paths)
        allowed = (in_workspace or in_tmp or in_home) and not blocked
        return allowed
    except Exception as e:
        # On any error, deny access (fail-safe)
        return False

def export_project(project, output_file):
    """Export a project's tasks to markdown."""
    db = load_db()
    tasks = [t for t in db["tasks"] if t["project"] == project]
    
    if not tasks:
        print(f"No tasks found in project '{project}'")
        return False
    
    # Security: Validate output path
    output_path = Path(output_file)
    if not is_safe_path(output_path):
        print(f"❌ Security error: Cannot write to '{output_path}'")
        print("   Path must be within workspace or home directory (not system paths)")
        return False
    
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    pending = [t for t in tasks if t["status"] == "pending"]
    completed = [t for t in tasks if t["status"] == "completed"]
    
    md = f"# Project: {project}\n\n"
    md += f"**Total Tasks:** {len(tasks)} ({len(pending)} pending, {len(completed)} completed)\n\n"
    
    if pending:
        md += "## ⏳ Pending Tasks\n\n"
        for task in sorted(pending, key=lambda t: t["created"]):
            priority = task["priority"].upper()
            md += f"- [ ] **#{task['id']}** [{priority}] {task['description']}\n"
            md += f"  Created: {task['created'][:10]}\n\n"
    
    if completed:
        md += "## ✅ Completed Tasks\n\n"
        for task in sorted(completed, key=lambda t: t["completed"], reverse=True):
            md += f"- [x] **#{task['id']}** {task['description']}\n"
            md += f"  Completed: {task['completed'][:10]}\n\n"
    
    output_path.write_text(md)
    print(f"✓ Exported project '{project}' to {output_path}")
    return True

def main():
    if len(sys.argv) < 2:
        print("Task Runner - Manage tasks across sessions")
        print("\nCommands:")
        print("  add <description> [project] [priority]  - Add a new task")
        print("  list [project]                           - List tasks (all or by project)")
        print("  complete <task_id>                       - Mark task as completed")
        print("  priority <task_id> <low|medium|high>     - Set task priority")
        print("  export <project> <output_file>           - Export project to markdown")
        print("\nPriorities: low, medium (default), high")
        return
    
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) < 3:
            print("Usage: add <description> [project] [priority]")
            return
        description = sys.argv[2]
        project = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_PROJECT
        priority = sys.argv[4] if len(sys.argv) > 4 else "medium"
        add(description, project, priority)
    
    elif command == "list":
        project = sys.argv[2] if len(sys.argv) > 2 else None
        list_tasks(project)
    
    elif command == "complete":
        if len(sys.argv) < 3:
            print("Usage: complete <task_id>")
            return
        complete(int(sys.argv[2]))
    
    elif command == "priority":
        if len(sys.argv) < 4:
            print("Usage: priority <task_id> <low|medium|high>")
            return
        set_priority(int(sys.argv[2]), sys.argv[3])
    
    elif command == "export":
        if len(sys.argv) < 4:
            print("Usage: export <project> <output_file>")
            return
        export_project(sys.argv[2], sys.argv[3])
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
