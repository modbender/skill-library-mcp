#!/usr/bin/env python3
"""Todo/Task operations for CalDAV."""

import sys
from pathlib import Path
from datetime import datetime, date
from typing import Optional

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))

from utils import get_client, print_result, parse_datetime


def find_calendar(client, calendar_name: str):
    """Find calendar by name or ID."""
    principal = client.principal()
    for cal in principal.calendars():
        cal_id = str(cal.url).rstrip("/").split("/")[-1]
        if cal_id == calendar_name or cal.name == calendar_name:
            return cal
    return None


def format_todo(todo) -> dict:
    """Format todo for display."""
    data = {
        "uid": todo.icalendar_component.get("uid", "unknown"),
        "url": str(todo.url) if todo.url else None,
    }

    vtodo = todo.icalendar_component

    # Summary
    if vtodo.get("summary"):
        data["summary"] = str(vtodo["summary"])

    # Description
    if vtodo.get("description"):
        data["description"] = str(vtodo["description"])

    # Status
    if vtodo.get("status"):
        data["status"] = str(vtodo["status"])
        data["completed"] = vtodo["status"] == "COMPLETED"

    # Priority
    if vtodo.get("priority"):
        data["priority"] = int(vtodo["priority"])

    # Due date
    if vtodo.get("due"):
        due = vtodo["due"].dt
        if hasattr(due, "isoformat"):
            data["due"] = due.isoformat()
        else:
            data["due"] = str(due)

    # Completed date
    if vtodo.get("completed"):
        completed = vtodo["completed"].dt
        if hasattr(completed, "isoformat"):
            data["completed_date"] = completed.isoformat()
        else:
            data["completed_date"] = str(completed)

    # Categories
    if vtodo.get("categories"):
        cats = vtodo["categories"]
        if isinstance(cats, str):
            data["categories"] = [c.strip() for c in cats.split(",")]
        elif isinstance(cats, list):
            data["categories"] = [str(c) for c in cats]

    # Check if overdue
    if vtodo.get("due") and not data.get("completed"):
        due = vtodo["due"].dt
        now = datetime.now() if hasattr(due, "hour") else date.today()
        if due < now:
            data["overdue"] = True

    return data


def cmd_list(args):
    """List todos."""
    client = get_client()
    principal = client.principal()

    all_todos = []

    if args.calendar:
        calendars = [find_calendar(client, args.calendar)]
        calendars = [c for c in calendars if c]
    else:
        calendars = principal.calendars()

    for cal in calendars:
        if not cal:
            continue

        try:
            todos = cal.todos()
            for todo in todos:
                todo_data = format_todo(todo)
                todo_data["calendar"] = cal.name

                # Filter by completed status
                if not args.completed and todo_data.get("completed"):
                    continue

                # Filter by overdue
                if args.overdue and not todo_data.get("overdue"):
                    continue

                all_todos.append(todo_data)
        except Exception as e:
            # Calendar might not support todos
            pass

    # Sort by due date, then priority
    def sort_key(t):
        due = t.get("due", "")
        priority = t.get("priority", 5) or 5
        return (due or "zzz", priority)

    all_todos.sort(key=sort_key)

    print_result(True, f"Found {len(all_todos)} todo(s)", {"todos": all_todos})


def cmd_create(args):
    """Create a new todo."""
    client = get_client()

    calendar = find_calendar(client, args.calendar)
    if not calendar:
        print_result(False, f"Calendar '{args.calendar}' not found")
        return

    try:
        kwargs = {
            "summary": args.summary,
        }

        if args.due:
            due = parse_datetime(args.due)
            # If only date provided, use it as date (not datetime)
            if "T" not in args.due and " " not in args.due:
                due = due.date() if hasattr(due, "date") else due
            kwargs["due"] = due

        if args.description:
            kwargs["description"] = args.description

        if args.priority:
            kwargs["priority"] = args.priority

        if args.categories:
            kwargs["categories"] = [c.strip() for c in args.categories.split(",")]

        todo = calendar.save_todo(**kwargs)
        todo_data = format_todo(todo)

        print_result(True, "Todo created", todo_data)

    except Exception as e:
        print_result(False, f"Failed to create todo: {e}")


def cmd_complete(args):
    """Mark a todo as complete."""
    client = get_client()

    todo = None

    # Find todo
    if args.calendar:
        calendar = find_calendar(client, args.calendar)
        if calendar:
            try:
                todo = calendar.todo_by_uid(args.uid)
            except Exception:
                pass

    if not todo:
        principal = client.principal()
        for cal in principal.calendars():
            try:
                todo = cal.todo_by_uid(args.uid)
                break
            except Exception:
                pass

    if not todo:
        print_result(False, f"Todo '{args.uid}' not found")
        return

    try:
        # Mark complete
        vtodo = todo.icalendar_component
        vtodo["status"] = "COMPLETED"
        vtodo["completed"] = datetime.now()
        todo.save()

        todo_data = format_todo(todo)
        print_result(True, "Todo marked as complete", todo_data)

    except Exception as e:
        print_result(False, f"Failed to complete todo: {e}")


def cmd_delete(args):
    """Delete a todo."""
    client = get_client()

    todo = None

    # Find todo
    if args.calendar:
        calendar = find_calendar(client, args.calendar)
        if calendar:
            try:
                todo = calendar.todo_by_uid(args.uid)
            except Exception:
                pass

    if not todo:
        principal = client.principal()
        for cal in principal.calendars():
            try:
                todo = cal.todo_by_uid(args.uid)
                break
            except Exception:
                pass

    if not todo:
        print_result(False, f"Todo '{args.uid}' not found")
        return

    if not args.force:
        try:
            confirm = input(f"Delete todo '{args.uid}'? [y/N] ")
            if confirm.lower() != "y":
                print_result(False, "Cancelled")
                return
        except EOFError:
            print_result(False, "Use --force to skip confirmation")
            return

    try:
        todo.delete()
        print_result(True, f"Todo '{args.uid}' deleted")
    except Exception as e:
        print_result(False, f"Failed to delete todo: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Todo operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # List
    list_cmd = subparsers.add_parser("list", help="List todos")
    list_cmd.add_argument("--calendar", "-c", help="Filter by calendar")
    list_cmd.add_argument("--completed", action="store_true", help="Show completed")
    list_cmd.add_argument("--overdue", action="store_true", help="Show overdue only")

    # Create
    create = subparsers.add_parser("create", help="Create a todo")
    create.add_argument("--calendar", "-c", required=True, help="Target calendar")
    create.add_argument("--summary", "-s", required=True, help="Todo title")
    create.add_argument("--due", help="Due date")
    create.add_argument("--description", "-d", help="Description")
    create.add_argument("--priority", type=int, help="Priority (1-9, 1=highest)")
    create.add_argument("--categories", help="Comma-separated categories")

    # Complete
    complete = subparsers.add_parser("complete", help="Mark todo complete")
    complete.add_argument("--uid", required=True, help="Todo UID")
    complete.add_argument("--calendar", "-c", help="Calendar")

    # Delete
    delete = subparsers.add_parser("delete", help="Delete a todo")
    delete.add_argument("--uid", required=True, help="Todo UID")
    delete.add_argument("--calendar", "-c", help="Calendar")
    delete.add_argument("--force", action="store_true", help="Skip confirmation")

    args = parser.parse_args()
    globals()[f"cmd_{args.command}"](args)


if __name__ == "__main__":
    main()
