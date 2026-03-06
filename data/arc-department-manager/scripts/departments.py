#!/usr/bin/env python3
"""Department Manager for OpenClaw agents.

Organize AI workers into departments, assign tasks, track output.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DATA_DIR = os.path.expanduser("~/.openclaw/department-manager")


def get_data_path(data_dir=None):
    d = Path(data_dir or DEFAULT_DATA_DIR)
    d.mkdir(parents=True, exist_ok=True)
    return d / "departments.json"


def load_data(data_dir=None):
    path = get_data_path(data_dir)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"departments": {}, "tasks": [], "next_task_id": 1}


def save_data(data, data_dir=None):
    path = get_data_path(data_dir)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def cmd_create(args, data):
    name = args.name.lower().strip()
    if name in data["departments"]:
        print(f"Department '{name}' already exists.")
        sys.exit(1)

    data["departments"][name] = {
        "name": name,
        "description": args.description or "",
        "model": args.model or "openrouter/free",
        "created": now_iso(),
        "task_count": 0,
        "completed_count": 0,
    }
    save_data(data, args.data_dir)
    print(f"Department '{name}' created.")
    if args.model:
        print(f"  Default model: {args.model}")


def cmd_list(args, data):
    depts = data["departments"]
    if not depts:
        print("No departments created yet.")
        return

    print(f"Departments ({len(depts)}):")
    for name, dept in sorted(depts.items()):
        active = sum(1 for t in data["tasks"] if t["department"] == name and t["status"] == "active")
        completed = dept.get("completed_count", 0)
        print(f"  {name}: {dept.get('description', '')}")
        print(f"    Model: {dept.get('model', 'unset')} | Active: {active} | Completed: {completed}")


def cmd_assign(args, data):
    dept_name = args.dept.lower().strip()
    if dept_name not in data["departments"]:
        print(f"Department '{dept_name}' not found. Create it first.")
        sys.exit(1)

    task = {
        "id": data["next_task_id"],
        "department": dept_name,
        "task": args.task,
        "priority": args.priority or "normal",
        "status": "active",
        "created": now_iso(),
        "output": None,
        "completed_at": None,
    }
    data["tasks"].append(task)
    data["next_task_id"] += 1
    data["departments"][dept_name]["task_count"] = data["departments"][dept_name].get("task_count", 0) + 1
    save_data(data, args.data_dir)
    print(f"Task #{task['id']} assigned to {dept_name}: {args.task} [{args.priority or 'normal'}]")


def cmd_status(args, data):
    dept_name = args.dept.lower().strip()
    if dept_name not in data["departments"]:
        print(f"Department '{dept_name}' not found.")
        sys.exit(1)

    dept = data["departments"][dept_name]
    active_tasks = [t for t in data["tasks"] if t["department"] == dept_name and t["status"] == "active"]
    completed_tasks = [t for t in data["tasks"] if t["department"] == dept_name and t["status"] == "done"]

    print(f"=== {dept_name.upper()} Department ===")
    print(f"Description: {dept.get('description', 'N/A')}")
    print(f"Default model: {dept.get('model', 'unset')}")
    print(f"Active tasks: {len(active_tasks)}")
    print(f"Completed: {len(completed_tasks)}")

    if active_tasks:
        priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
        active_tasks.sort(key=lambda t: priority_order.get(t.get("priority", "normal"), 2))
        print("\nActive:")
        for t in active_tasks:
            pri = f" [{t['priority']}]" if t.get("priority", "normal") != "normal" else ""
            print(f"  #{t['id']}: {t['task']}{pri}")


def cmd_active(args, data):
    active = [t for t in data["tasks"] if t["status"] == "active"]
    if not active:
        print("No active tasks.")
        return

    priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
    active.sort(key=lambda t: (priority_order.get(t.get("priority", "normal"), 2), t["department"]))

    print(f"Active tasks ({len(active)}):")
    for t in active:
        pri = f" [{t['priority']}]" if t.get("priority", "normal") != "normal" else ""
        print(f"  #{t['id']} ({t['department']}): {t['task']}{pri}")


def cmd_complete(args, data):
    for t in data["tasks"]:
        if t["id"] == args.task_id:
            if t["status"] == "done":
                print(f"Task #{args.task_id} is already completed.")
                return
            t["status"] = "done"
            t["completed_at"] = now_iso()
            t["output"] = args.output or ""
            dept_name = t["department"]
            if dept_name in data["departments"]:
                data["departments"][dept_name]["completed_count"] = data["departments"][dept_name].get("completed_count", 0) + 1
            save_data(data, args.data_dir)
            print(f"Task #{args.task_id} completed ({dept_name}): {t['task']}")
            return

    print(f"Task #{args.task_id} not found.")
    sys.exit(1)


def cmd_report(args, data):
    depts = data["departments"]
    if not depts:
        print("No departments to report on.")
        return

    total_active = sum(1 for t in data["tasks"] if t["status"] == "active")
    total_done = sum(1 for t in data["tasks"] if t["status"] == "done")

    print(f"=== Department Report ===")
    print(f"Total departments: {len(depts)}")
    print(f"Active tasks: {total_active}")
    print(f"Completed tasks: {total_done}")
    print()

    for name, dept in sorted(depts.items()):
        active = [t for t in data["tasks"] if t["department"] == name and t["status"] == "active"]
        done = [t for t in data["tasks"] if t["department"] == name and t["status"] == "done"]
        print(f"  {name.upper()}: {len(active)} active, {len(done)} done — {dept.get('description', '')}")
        for t in active:
            pri = f" [{t['priority']}]" if t.get("priority", "normal") != "normal" else ""
            print(f"    → #{t['id']}: {t['task']}{pri}")


def cmd_remove(args, data):
    name = args.name.lower().strip()
    if name not in data["departments"]:
        print(f"Department '{name}' not found.")
        sys.exit(1)

    active = [t for t in data["tasks"] if t["department"] == name and t["status"] == "active"]
    if active:
        print(f"Cannot remove '{name}' — {len(active)} active tasks. Complete or reassign them first.")
        sys.exit(1)

    del data["departments"][name]
    save_data(data, args.data_dir)
    print(f"Department '{name}' removed.")


def main():
    parser = argparse.ArgumentParser(description="Department Manager for OpenClaw")
    parser.add_argument("--data-dir", help="Override data directory")
    sub = parser.add_subparsers(dest="command")

    p_create = sub.add_parser("create", help="Create a department")
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--description", default="")
    p_create.add_argument("--model", default="openrouter/free")

    sub.add_parser("list", help="List departments")

    p_assign = sub.add_parser("assign", help="Assign task to department")
    p_assign.add_argument("--dept", required=True)
    p_assign.add_argument("--task", required=True)
    p_assign.add_argument("--priority", choices=["critical", "high", "normal", "low"], default="normal")

    p_status = sub.add_parser("status", help="Department status")
    p_status.add_argument("--dept", required=True)

    sub.add_parser("active", help="All active tasks")

    p_complete = sub.add_parser("complete", help="Complete a task")
    p_complete.add_argument("--task-id", type=int, required=True)
    p_complete.add_argument("--output", default="")

    sub.add_parser("report", help="Department report")

    p_remove = sub.add_parser("remove", help="Remove a department")
    p_remove.add_argument("--name", required=True)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    data = load_data(args.data_dir)

    cmds = {
        "create": cmd_create,
        "list": cmd_list,
        "assign": cmd_assign,
        "status": cmd_status,
        "active": cmd_active,
        "complete": cmd_complete,
        "report": cmd_report,
        "remove": cmd_remove,
    }

    cmds[args.command](args, data)


if __name__ == "__main__":
    main()
