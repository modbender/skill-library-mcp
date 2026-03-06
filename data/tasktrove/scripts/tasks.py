#!/usr/bin/env python3
"""
Tasktrove CLI - Manage tasks via the Tasktrove API.

Usage:
  python3 tasks.py list [--today|--overdue|--week|--all]
  python3 tasks.py add "Task title" [--due YYYY-MM-DD] [--priority 1-4]
  python3 tasks.py complete <task-id>
  python3 tasks.py search "query"

Environment:
  TASKTROVE_HOST  - Base URL of your Tasktrove instance (required)
  TASKTROVE_TOKEN - API token for authentication (optional)
"""

import argparse
import json
import os
import sys
import urllib.request
from datetime import date, timedelta

HOST = os.environ.get("TASKTROVE_HOST", "").rstrip("/")
TOKEN = os.environ.get("TASKTROVE_TOKEN", "")

if not HOST:
    print("Error: TASKTROVE_HOST environment variable is not set")
    print("Example: export TASKTROVE_HOST='http://localhost:3333'")
    sys.exit(1)

API = f"{HOST}/api/v1"


def _make_request(url, data=None, method="GET"):
    """Make an API request with optional auth."""
    headers = {"Content-Type": "application/json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode() if data else None,
        headers=headers,
        method=method
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)


def fetch_tasks():
    """Fetch all tasks from API."""
    return _make_request(f"{API}/tasks")["tasks"]


def list_tasks(filter_type="today"):
    """List tasks with optional filter."""
    tasks = fetch_tasks()
    today = date.today().isoformat()
    week_end = (date.today() + timedelta(days=7)).isoformat()
    
    if filter_type == "today":
        tasks = [t for t in tasks if not t["completed"] and t.get("dueDate") == today]
    elif filter_type == "overdue":
        tasks = [t for t in tasks if not t["completed"] and t.get("dueDate") and t["dueDate"] < today]
    elif filter_type == "week":
        tasks = [t for t in tasks if not t["completed"] and t.get("dueDate") and t["dueDate"] <= week_end]
    elif filter_type == "incomplete":
        tasks = [t for t in tasks if not t["completed"]]
    # "all" returns everything
    
    # Sort by due date, then priority
    tasks.sort(key=lambda x: (x.get("dueDate") or "9999", x.get("priority", 4)))
    
    for t in tasks:
        due = t.get("dueDate", "no date")
        p = f"P{t.get('priority', 4)}"
        status = "✓" if t["completed"] else "○"
        print(f"{status} {due} {p}: {t['title']} [{t['id'][:8]}]")
    
    if not tasks:
        print("No tasks found.")
    return tasks


def add_task(title, due_date=None, priority=4):
    """Create a new task."""
    import uuid
    from datetime import datetime
    
    data = {
        "id": str(uuid.uuid4()),
        "title": title,
        "priority": priority,
        "completed": False,
        "labels": [],
        "subtasks": [],
        "comments": [],
        "createdAt": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "recurringMode": "dueDate"
    }
    if due_date:
        data["dueDate"] = due_date
    
    _make_request(f"{API}/tasks", data=data, method="POST")
    print(f"Created: {title}")


def complete_task(task_id):
    """Mark a task as complete."""
    # Find full ID if partial
    if len(task_id) < 36:
        tasks = fetch_tasks()
        matches = [t for t in tasks if t["id"].startswith(task_id)]
        if len(matches) == 1:
            task_id = matches[0]["id"]
        elif len(matches) > 1:
            print(f"Multiple matches for '{task_id}'. Be more specific.")
            return None
        else:
            print(f"No task found matching '{task_id}'")
            return None
    
    # Get task title for confirmation message
    tasks = fetch_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    task_title = task["title"] if task else task_id
    
    # API uses PATCH on collection endpoint with ID in body
    _make_request(f"{API}/tasks", data={"id": task_id, "completed": True}, method="PATCH")
    print(f"Completed: {task_title}")


def search_tasks(query):
    """Search tasks by title."""
    tasks = fetch_tasks()
    query_lower = query.lower()
    matches = [t for t in tasks if query_lower in t["title"].lower()]
    
    for t in matches:
        due = t.get("dueDate", "no date")
        p = f"P{t.get('priority', 4)}"
        status = "✓" if t["completed"] else "○"
        print(f"{status} {due} {p}: {t['title']} [{t['id'][:8]}]")
    
    if not matches:
        print(f"No tasks matching '{query}'")
    return matches


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tasktrove CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # List
    list_p = subparsers.add_parser("list", help="List tasks")
    list_p.add_argument("--today", action="store_true", help="Due today")
    list_p.add_argument("--overdue", action="store_true", help="Overdue tasks")
    list_p.add_argument("--week", action="store_true", help="Due this week")
    list_p.add_argument("--all", action="store_true", help="All tasks")
    list_p.add_argument("--incomplete", action="store_true", help="All incomplete")
    
    # Add
    add_p = subparsers.add_parser("add", help="Add a task")
    add_p.add_argument("title", help="Task title")
    add_p.add_argument("--due", help="Due date (YYYY-MM-DD)")
    add_p.add_argument("--priority", type=int, default=4, help="Priority 1-4")
    
    # Complete
    comp_p = subparsers.add_parser("complete", help="Complete a task")
    comp_p.add_argument("task_id", help="Task ID (or prefix)")
    
    # Search
    search_p = subparsers.add_parser("search", help="Search tasks")
    search_p.add_argument("query", help="Search query")
    
    args = parser.parse_args()
    
    if args.command == "list":
        if args.overdue:
            list_tasks("overdue")
        elif args.week:
            list_tasks("week")
        elif args.all:
            list_tasks("all")
        elif args.incomplete:
            list_tasks("incomplete")
        else:
            list_tasks("today")
    elif args.command == "add":
        add_task(args.title, args.due, args.priority)
    elif args.command == "complete":
        complete_task(args.task_id)
    elif args.command == "search":
        search_tasks(args.query)
