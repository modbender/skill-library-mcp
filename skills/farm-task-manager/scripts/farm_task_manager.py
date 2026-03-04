#!/usr/bin/env python3
"""
Farm Task Manager

Daily, weekly, and seasonal farm chore management with task scheduling,
priorities, and tracking.

Author: IOU (@johstracke)
Version: 1.0.0
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import argparse


# Storage paths
WORKSPACE = Path.home() / ".openclaw" / "workspace"
DATA_DIR = WORKSPACE / "farm-task-manager"
TASKS_FILE = DATA_DIR / "tasks.json"


def is_safe_path(filepath: Path) -> bool:
    """Validate a file path is safe for writing.

    Blocks system paths and sensitive dotfiles.
    Allows workspace and home directories.
    """
    path = Path(filepath).expanduser().resolve()

    # Allow workspace and home
    allowed_paths = [
        WORKSPACE,
        Path.home(),
    ]

    # Block system paths
    blocked_paths = [
        Path("/etc"),
        Path("/usr"),
        Path("/var"),
        Path("/root"),
        Path("/bin"),
        Path("/sbin"),
        Path("/boot"),
        Path("/lib"),
        Path("/opt"),
    ]

    # Block sensitive dotfiles
    sensitive_patterns = [
        ".ssh",
        ".bashrc",
        ".zshrc",
        ".bash_profile",
        ".zprofile",
        ".bash_history",
        ".zsh_history",
        ".aws",
        ".env",
        ".secret",
        ".token",
        ".key",
    ]

    # Check if path is allowed
    is_allowed = any(str(path).startswith(str(allowed)) for allowed in allowed_paths)

    # Check if path is blocked
    is_blocked = any(str(path).startswith(str(blocked)) for blocked in blocked_paths)

    # Check for sensitive dotfiles in path
    has_sensitive = any(f"/{s}/" in str(path) or f"/{s}" in str(path) for s in sensitive_patterns)

    return is_allowed and not is_blocked and not has_sensitive


def load_tasks() -> Dict:
    """Load tasks from JSON file."""
    if not TASKS_FILE.exists():
        return {"tasks": [], "recurring_tasks": [], "next_task_id": 1}

    try:
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        print(f"Error loading tasks from {TASKS_FILE}")
        return {"tasks": [], "recurring_tasks": [], "next_task_id": 1}


def save_tasks(data: Dict) -> bool:
    """Save tasks to JSON file with safety check."""
    if not is_safe_path(TASKS_FILE):
        print(f"Error: Unsafe path {TASKS_FILE}")
        return False

    try:
        TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TASKS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except IOError as e:
        print(f"Error saving tasks: {e}")
        return False


def parse_date(date_str: Optional[str]) -> Optional[str]:
    """Parse date string to ISO format."""
    if not date_str:
        return None

    try:
        # Try YYYY-MM-DD
        if " " not in date_str:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.isoformat()
        # Try YYYY-MM-DD HH:MM
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        return dt.isoformat()
    except ValueError:
        return None


def add_task(args) -> None:
    """Add a new task."""
    data = load_tasks()

    task = {
        "id": data["next_task_id"],
        "name": args.name,
        "description": args.description or "",
        "priority": args.priority or "medium",
        "status": args.status or "pending",
        "category": args.category or "other",
        "due": parse_date(args.due),
        "assignee": args.assignee or "",
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "notes": [],
    }

    data["tasks"].append(task)
    data["next_task_id"] += 1

    if save_tasks(data):
        print(f"✓ Task added: {task['name']} (ID: {task['id']})")
    else:
        print("✗ Failed to add task")


def list_tasks(args) -> None:
    """List tasks with optional filtering."""
    data = load_tasks()
    tasks = data["tasks"]

    # Apply filters
    if args.status:
        tasks = [t for t in tasks if t["status"] == args.status]
    if args.priority:
        tasks = [t for t in tasks if t["priority"] == args.priority]
    if args.category:
        tasks = [t for t in tasks if t["category"] == args.category]
    if args.assignee:
        tasks = [t for t in tasks if t["assignee"].lower() == args.assignee.lower()]

    # Sort by due date if requested
    if args.sort_due:
        def get_due_date(task):
            if not task["due"]:
                return datetime.max
            return datetime.fromisoformat(task["due"])
        tasks = sorted(tasks, key=get_due_date)

    # Display
    if not tasks:
        print("No tasks found matching criteria.")
        return

    print(f"\n{'='*60}")
    print(f"TASKS ({len(tasks)} found)")
    print(f"{'='*60}\n")

    for task in tasks:
        status_icon = {"pending": "○", "in-progress": "◐", "completed": "●"}.get(task["status"], "?")
        priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task["priority"], "")
        due_str = task["due"][:10] if task["due"] else "No due date"

        print(f"{status_icon} {priority_color} [ID:{task['id']}] {task['name']}")
        print(f"   Priority: {task['priority']}")
        print(f"   Category: {task['category']}")
        print(f"   Status: {task['status']}")
        print(f"   Due: {due_str}")
        if task["assignee"]:
            print(f"   Assigned to: {task['assignee']}")
        print()


def show_task(task_id: int) -> None:
    """Show detailed information about a task."""
    data = load_tasks()

    # Find task
    task = next((t for t in data["tasks"] if t["id"] == task_id), None)

    if not task:
        print(f"Task not found: {task_id}")
        return

    # Display task details
    print(f"\n{'='*60}")
    print(f"TASK DETAILS (ID: {task['id']})")
    print(f"{'='*60}\n")

    print(f"Name: {task['name']}")
    if task["description"]:
        print(f"Description: {task['description']}")
    print(f"Priority: {task['priority']}")
    print(f"Status: {task['status']}")
    print(f"Category: {task['category']}")
    print(f"Due: {task['due']}")
    if task["assignee"]:
        print(f"Assigned to: {task['assignee']}")
    print(f"Created: {task['created']}")
    print(f"Updated: {task['updated']}")

    if task["notes"]:
        print(f"\nNotes:")
        for note in task["notes"]:
            print(f"  - [{note['timestamp']}] {note['text']}")


def update_task(args) -> None:
    """Update task status, priority, or add note."""
    data = load_tasks()

    # Find task
    task = next((t for t in data["tasks"] if t["id"] == args.id), None)

    if not task:
        print(f"Task not found: {args.id}")
        return

    # Update fields
    if args.status:
        task["status"] = args.status
    if args.priority:
        task["priority"] = args.priority
    if args.note:
        task["notes"].append({
            "timestamp": datetime.now().isoformat(),
            "text": args.note
        })

    task["updated"] = datetime.now().isoformat()

    if save_tasks(data):
        changes = []
        if args.status:
            changes.append(f"status → {args.status}")
        if args.priority:
            changes.append(f"priority → {args.priority}")
        if args.note:
            changes.append("note added")
        print(f"✓ Task updated: {task['name']} ({', '.join(changes)})")
    else:
        print("✗ Failed to update task")


def complete_task(task_id: int) -> None:
    """Mark a task as completed."""
    data = load_tasks()

    # Find task
    task = next((t for t in data["tasks"] if t["id"] == task_id), None)

    if not task:
        print(f"Task not found: {task_id}")
        return

    task["status"] = "completed"
    task["completed_at"] = datetime.now().isoformat()
    task["updated"] = datetime.now().isoformat()

    if save_tasks(data):
        print(f"✓ Task completed: {task['name']}")
    else:
        print("✗ Failed to complete task")


def delete_task(task_id: int) -> None:
    """Delete a task."""
    data = load_tasks()

    # Find task index
    task_idx = next((i for i, t in enumerate(data["tasks"]) if t["id"] == task_id), None)

    if task_idx is None:
        print(f"Task not found: {task_id}")
        return

    task_name = data["tasks"][task_idx]["name"]
    del data["tasks"][task_idx]

    if save_tasks(data):
        print(f"✓ Task deleted: {task_name}")
    else:
        print("✗ Failed to delete task")


def add_recurring_task(args) -> None:
    """Add a recurring task template."""
    data = load_tasks()

    recurring_task = {
        "id": data["next_task_id"],
        "name": args.name,
        "description": args.description or "",
        "priority": args.priority or "medium",
        "category": args.category or "other",
        "frequency": args.frequency,  # daily, weekly, monthly, seasonal
        "season": args.season,  # MM-DD for seasonal tasks
        "created": datetime.now().isoformat(),
    }

    data["recurring_tasks"].append(recurring_task)
    data["next_task_id"] += 1

    if save_tasks(data):
        print(f"✓ Recurring task added: {recurring_task['name']} (ID: {recurring_task['id']})")
    else:
        print("✗ Failed to add recurring task")


def generate_recurring_task(recurring_id: int) -> Optional[int]:
    """Generate a new task instance from a recurring task template."""
    data = load_tasks()

    # Find recurring task
    recurring = next((t for t in data["recurring_tasks"] if t["id"] == recurring_id), None)

    if not recurring:
        print(f"Recurring task not found: {recurring_id}")
        return None

    # Calculate due date based on frequency
    due_date = None
    now = datetime.now()

    if recurring["frequency"] == "daily":
        due_date = now + timedelta(days=1)
    elif recurring["frequency"] == "weekly":
        due_date = now + timedelta(weeks=1)
    elif recurring["frequency"] == "monthly":
        due_date = now + timedelta(days=30)
    elif recurring["frequency"] == "seasonal" and recurring["season"]:
        # Parse season date (MM-DD)
        season_month, season_day = map(int, recurring["season"].split("-"))
        year = now.year
        if now.month > season_month or (now.month == season_month and now.day > season_day):
            year += 1
        due_date = datetime(year, season_month, season_day)

    if due_date:
        due_str = due_date.isoformat()
    else:
        due_str = None

    # Create task instance
    task = {
        "id": data["next_task_id"],
        "name": recurring["name"],
        "description": recurring["description"],
        "priority": recurring["priority"],
        "status": "pending",
        "category": recurring["category"],
        "due": due_str,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "notes": [],
        "from_recurring": recurring_id,
    }

    data["tasks"].append(task)
    data["next_task_id"] += 1

    if save_tasks(data):
        print(f"✓ Task generated: {task['name']} (due: {due_date})")
        return task["id"]
    else:
        print("✗ Failed to generate task")
        return None


def search_tasks(query: str) -> None:
    """Search across all tasks by name, description, or category."""
    data = load_tasks()

    query_lower = query.lower()

    # Search in tasks
    results = [
        t for t in data["tasks"]
        if query_lower in t["name"].lower()
        or query_lower in (t["description"] or "").lower()
        or query_lower in t["category"].lower()
    ]

    if not results:
        print(f"No tasks found matching: {query}")
        return

    print(f"\nSearch results for '{query}' ({len(results)} found):\n")

    for task in results:
        print(f"  [ID:{task['id']}] {task['name']} - {task['category']}")


def export_tasks(args) -> None:
    """Export tasks to markdown or JSON."""
    data = load_tasks()
    tasks = data["tasks"]

    # Apply filters
    if args.category:
        tasks = [t for t in tasks if t["category"] == args.category]
    if args.after:
        after_date = datetime.fromisoformat(args.after)
        tasks = [t for t in tasks if t["created"] and datetime.fromisoformat(t["created"]) >= after_date]
    if args.before:
        before_date = datetime.fromisoformat(args.before)
        tasks = [t for t in tasks if t["created"] and datetime.fromisoformat(t["created"]) <= before_date]

    # Export format
    format_type = args.format or "markdown"

    if not is_safe_path(args.file):
        print(f"Error: Unsafe path {args.file}")
        return

    try:
        args.file.parent.mkdir(parents=True, exist_ok=True)

        if format_type == "json":
            with open(args.file, 'w') as f:
                json.dump(tasks, f, indent=2)
            print(f"✓ Exported {len(tasks)} tasks to {args.file} (JSON)")
        else:  # markdown
            with open(args.file, 'w') as f:
                f.write(f"# Farm Tasks Export\n")
                f.write(f"\nExported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total tasks: {len(tasks)}\n\n")

                for task in tasks:
                    status_icon = {"pending": "○", "in-progress": "◐", "completed": "●"}.get(task["status"], "?")
                    due_str = task["due"][:10] if task["due"] else "No due date"
                    completed_str = f" (completed: {task['completed_at'][:10]})" if task["status"] == "completed" else ""

                    f.write(f"## {status_icon} {task['name']}\n\n")
                    f.write(f"**ID:** {task['id']}\n")
                    f.write(f"**Priority:** {task['priority']}\n")
                    f.write(f"**Status:** {task['status']}{completed_str}\n")
                    f.write(f"**Category:** {task['category']}\n")
                    f.write(f"**Due:** {due_str}\n")
                    if task["assignee"]:
                        f.write(f"**Assigned to:** {task['assignee']}\n")
                    if task["description"]:
                        f.write(f"**Description:** {task['description']}\n")
                    if task["notes"]:
                        f.write(f"**Notes:**\n")
                        for note in task["notes"]:
                            f.write(f"- [{note['timestamp'][:10]}] {note['text']}\n")
                    f.write("\n---\n\n")

            print(f"✓ Exported {len(tasks)} tasks to {args.file} (markdown)")
    except IOError as e:
        print(f"Error exporting tasks: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Farm Task Manager - Organize daily, weekly, and seasonal farm chores",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('name', help='Task name')
    add_parser.add_argument('--description', help='Task description')
    add_parser.add_argument('--priority', choices=['high', 'medium', 'low'], help='Task priority')
    add_parser.add_argument('--status', choices=['pending', 'in-progress', 'completed'], help='Task status')
    add_parser.add_argument('--category', help='Task category (planting, maintenance, harvesting, equipment, animals, buildings, other)')
    add_parser.add_argument('--due', help='Due date (YYYY-MM-DD or YYYY-MM-DD HH:MM)')
    add_parser.add_argument('--assignee', help='Person assigned to task')

    # List command
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('--status', help='Filter by status')
    list_parser.add_argument('--priority', help='Filter by priority')
    list_parser.add_argument('--category', help='Filter by category')
    list_parser.add_argument('--assignee', help='Filter by assignee')
    list_parser.add_argument('--sort-due', action='store_true', help='Sort by due date')

    # Show command
    show_parser = subparsers.add_parser('show', help='Show task details')
    show_parser.add_argument('id', type=int, help='Task ID')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update task')
    update_parser.add_argument('id', type=int, help='Task ID')
    update_parser.add_argument('--status', choices=['pending', 'in-progress', 'completed'], help='Update status')
    update_parser.add_argument('--priority', choices=['high', 'medium', 'low'], help='Update priority')
    update_parser.add_argument('--note', help='Add a note to task')

    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Mark task as completed')
    complete_parser.add_argument('id', type=int, help='Task ID')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('id', type=int, help='Task ID')

    # Recurring commands
    recurring_parser = subparsers.add_parser('recurring', help='Recurring task operations')
    recurring_subparsers = recurring_parser.add_subparsers(dest='recurring_command')

    # Add recurring task
    add_recurring_parser = recurring_subparsers.add_parser('add', help='Add recurring task')
    add_recurring_parser.add_argument('name', help='Task name')
    add_recurring_parser.add_argument('--description', help='Task description')
    add_recurring_parser.add_argument('--priority', choices=['high', 'medium', 'low'], help='Task priority')
    add_recurring_parser.add_argument('--category', help='Task category')
    add_recurring_parser.add_argument('--frequency', choices=['daily', 'weekly', 'monthly', 'seasonal'], help='Frequency')
    add_recurring_parser.add_argument('--season', help='Season date (MM-DD) for seasonal tasks')

    # Generate recurring task
    generate_parser = recurring_subparsers.add_parser('generate', help='Generate task from recurring template')
    generate_parser.add_argument('id', type=int, help='Recurring task ID')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search tasks')
    search_parser.add_argument('query', help='Search query')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export tasks')
    export_parser.add_argument('--file', type=Path, required=True, help='Output file path')
    export_parser.add_argument('--category', help='Filter by category')
    export_parser.add_argument('--after', help='Include tasks created after date (YYYY-MM-DD)')
    export_parser.add_argument('--before', help='Include tasks created before date (YYYY-MM-DD)')
    export_parser.add_argument('--format', choices=['markdown', 'json'], help='Output format')

    args = parser.parse_args()

    # Execute command
    if args.command == 'add':
        add_task(args)
    elif args.command == 'list':
        list_tasks(args)
    elif args.command == 'show':
        show_task(args.id)
    elif args.command == 'update':
        update_task(args)
    elif args.command == 'complete':
        complete_task(args.id)
    elif args.command == 'delete':
        delete_task(args.id)
    elif args.command == 'recurring':
        if args.recurring_command == 'add':
            add_recurring_task(args)
        elif args.recurring_command == 'generate':
            generate_recurring_task(args.id)
        else:
            recurring_parser.print_help()
    elif args.command == 'search':
        search_tasks(args.query)
    elif args.command == 'export':
        export_tasks(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
