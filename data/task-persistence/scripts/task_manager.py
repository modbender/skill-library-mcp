#!/usr/bin/env python3
"""
Task Manager CLI - Unified interface for task-persistence skill
Wraps TaskQueueManager and TaskPersistenceManager into a single CLI entry point.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add parent scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))

from task_queue import TaskQueueManager
from task_persistence import TaskPersistenceManager


def get_workspace():
    return os.getenv("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))


def main():
    parser = argparse.ArgumentParser(description="Task Manager - task-persistence skill")
    parser.add_argument(
        "--action",
        choices=["list", "add", "resume", "pause", "cancel", "complete", "status", "recover"],
        required=True,
        help="Action to perform"
    )
    parser.add_argument("--task-id", help="Task identifier")
    parser.add_argument("--task-type", help="Task type")
    parser.add_argument("--description", help="Task description")
    parser.add_argument("--priority", choices=["high", "normal", "low"], default="normal")
    parser.add_argument("--data", help="Task data as JSON string")
    parser.add_argument("--workspace", help="Workspace path", default=None)

    args = parser.parse_args()
    workspace = args.workspace or get_workspace()

    queue = TaskQueueManager(workspace)
    manager = TaskPersistenceManager(workspace)

    if args.action == "list":
        tasks = queue.task_queue
        active = manager.get_active_tasks()
        all_tasks = tasks + [t for t in active if t["id"] not in {x["id"] for x in tasks}]
        if not all_tasks:
            print("No active tasks.")
        else:
            print(json.dumps(all_tasks, indent=2, ensure_ascii=False))

    elif args.action == "add":
        if not args.task_id or not args.description:
            print("Error: --task-id and --description required for add action")
            sys.exit(1)
        data = json.loads(args.data) if args.data else {}
        ok = queue.add_task(
            task_id=args.task_id,
            task_type=args.task_type or "generic",
            description=args.description,
            priority=args.priority,
            data=data
        )
        manager.register_task(args.task_id, {"description": args.description, **data})
        print(f"Task added: {ok}")

    elif args.action == "resume":
        if not args.task_id:
            print("Error: --task-id required for resume action")
            sys.exit(1)
        ok = queue.start_task(args.task_id)
        manager.update_task(args.task_id, status="running")
        print(f"Task resumed: {ok}")

    elif args.action == "pause":
        if not args.task_id:
            print("Error: --task-id required for pause action")
            sys.exit(1)
        ok = manager.update_task(args.task_id, status="paused")
        print(f"Task paused: {ok}")

    elif args.action == "cancel":
        if not args.task_id:
            print("Error: --task-id required for cancel action")
            sys.exit(1)
        ok_queue = queue.fail_task(args.task_id, "cancelled by user")
        ok_mgr = manager.complete_task(args.task_id)
        print(f"Task cancelled: {ok_queue or ok_mgr}")

    elif args.action == "complete":
        if not args.task_id:
            print("Error: --task-id required for complete action")
            sys.exit(1)
        ok_queue = queue.complete_task(args.task_id)
        ok_mgr = manager.complete_task(args.task_id)
        print(f"Task completed: {ok_queue or ok_mgr}")

    elif args.action == "status":
        status = queue.get_queue_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))

    elif args.action == "recover":
        recovered = queue.recover_from_crash()
        restart = manager.detect_gateway_restart()
        suggestions = manager.get_recovery_suggestions()
        print(json.dumps({
            "recovered_tasks": recovered,
            "restart_detected": restart,
            "suggestions": suggestions
        }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
