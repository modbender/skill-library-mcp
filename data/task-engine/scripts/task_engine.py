#!/usr/bin/env python3
"""task_engine.py — Task orchestration CLI for multi-agent workflows."""

import argparse
import json
import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path

# Add parent to path so engine package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine.models import (
    TASK_STATUSES, TERMINAL_TASK_STATUSES,
    SUBTASK_STATUSES, TERMINAL_SUBTASK_STATUSES,
    PRIORITIES, SUBTASK_TYPES, IndexEntry,
)
from engine.state_machine import (
    validate_task_transition,
    validate_subtask_transition,
    get_valid_task_events,
    get_valid_subtask_events,
    check_auto_transition,
)
from engine.task_store import (
    create_task, read_task, save_task, list_tasks,
    create_subtask, read_subtask, save_subtask, read_all_subtasks,
    archive_task, update_index_entry, count_done_subtasks,
    append_log, get_task_dir, task_lock,
    get_tasks_dir, read_index, write_index, atomic_write,
)
from engine.checker import check_all_tasks, check_single_task
from engine.discord_formatter import (
    format_task_created, format_status_update, format_transition,
    format_alert, format_completion_summary, format_heartbeat_digest,
)
from engine.dispatcher import (
    select_agent, build_dispatch_context, generate_dispatch_prompt,
    check_dispatch_readiness, get_active_agent_count, AGENT_REGISTRY,
)

logger = logging.getLogger("task_engine")


def setup_logging(verbose: bool = False):
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    root = logging.getLogger("task_engine")
    root.setLevel(logging.DEBUG if verbose else logging.WARNING)
    root.addHandler(handler)


def _json_ok(use_json: bool, **kwargs) -> bool:
    """Print JSON success response if --json flag is set. Returns True if printed."""
    if not use_json:
        return False
    result = {"ok": True}
    result.update(kwargs)
    print(json.dumps(result, ensure_ascii=False))
    return True


def _json_error(use_json: bool, error: str) -> bool:
    """Print JSON error response if --json flag is set. Returns True if printed."""
    if not use_json:
        return False
    print(json.dumps({"ok": False, "error": error}, ensure_ascii=False))
    return True


# --- Commands ---

def cmd_create(args):
    """Create a new task."""
    task = create_task(
        title=args.title,
        priority=args.priority,
        plan_text=args.plan,
    )
    if _json_ok(args.json, task_id=task.id, status=task.status,
                message=f"Created {task.id}"):
        return
    print(f"Created {task.id}: {task.title} [{task.priority}] — {task.status}")


def cmd_status(args):
    """View task status."""
    if args.task_id:
        # Detailed view of one task
        task = read_task(args.task_id)
        if task is None:
            if _json_error(args.json, f"Task {args.task_id} not found"):
                sys.exit(1)
            print(f"Task {args.task_id} not found", file=sys.stderr)
            sys.exit(1)

        if args.json:
            print(json.dumps(task.to_dict(), indent=2, ensure_ascii=False))
            return

        subtasks = read_all_subtasks(args.task_id)
        done = sum(1 for s in subtasks if s.status == "DONE")

        print(f"{'=' * 60}")
        print(f"  {task.id}: {task.title}")
        print(f"  Status: {task.status}  |  Priority: {task.priority}")
        print(f"  Created: {task.created}")
        print(f"  Updated: {task.updated}")

        if task.plan.get("summary"):
            print(f"  Plan: {task.plan['summary']}")

        if task.timeline.get("eta"):
            print(f"  ETA: {task.timeline['eta']}")

        if task.metadata.get("blocked_reason"):
            print(f"  Blocked: {task.metadata['blocked_reason']}")

        if subtasks:
            print(f"\n  Subtasks ({done}/{len(subtasks)} done):")
            for s in subtasks:
                agent = s.assignment.get("agent", "unassigned") if s.assignment else "unassigned"
                pct = s.progress.get("percent", 0) if s.progress else 0
                marker = "+" if s.status == "DONE" else ">" if s.status == "IN_PROGRESS" else "-"
                print(f"    [{marker}] {s.id} {s.title[:40]}")
                print(f"        {s.status} | {agent} | {pct}%")
                if s.blocked_by:
                    print(f"        blocked_by: {', '.join(s.blocked_by)}")

        if task.history:
            print(f"\n  Recent history:")
            for h in task.history[-5:]:
                note = f" — {h.get('note', '')}" if h.get('note') else ""
                ts = h.get("time", "")[:19]
                print(f"    {ts} {h.get('event', '?')}{note}")

        print(f"{'=' * 60}")
        valid = get_valid_task_events(task.status)
        if valid:
            print(f"  Valid transitions: {', '.join(valid)}")
    else:
        # Summary of all tasks
        tasks = list_tasks(include_terminal=args.all)

        if args.json:
            print(json.dumps(tasks, indent=2, ensure_ascii=False))
            return

        if not tasks:
            print("No active tasks.")
            return

        print(f"{'ID':<12} {'Status':<14} {'Pri':<4} {'Subtasks':<10} {'Title'}")
        print(f"{'-' * 12} {'-' * 14} {'-' * 4} {'-' * 10} {'-' * 30}")
        for t in tasks:
            sc = t.get("subtask_count", 0)
            sd = t.get("subtasks_done", 0)
            sub = f"{sd}/{sc}" if sc > 0 else "-"
            print(f"{t['id']:<12} {t['status']:<14} {t['priority']:<4} {sub:<10} {t['title'][:40]}")


def cmd_dispatch(args):
    """Create and assign a subtask."""
    task = read_task(args.task_id)
    if task is None:
        if _json_error(args.json, f"Task {args.task_id} not found"):
            sys.exit(1)
        print(f"Task {args.task_id} not found", file=sys.stderr)
        sys.exit(1)

    # Parse deps
    deps = None
    if args.deps:
        deps = [d.strip() for d in args.deps.split(",")]

    with task_lock(args.task_id):
        subtask = create_subtask(
            task_id=args.task_id,
            title=args.title,
            agent=args.agent,
            subtask_type=args.type,
            deps=deps,
            context=args.context,
        )

        # Auto-transition APPROVED -> IN_PROGRESS on first dispatch
        task = read_task(args.task_id)  # re-read after subtask creation
        if task.status == "APPROVED":
            old = task.status
            task.status = "IN_PROGRESS"
            task.timeline["started_at"] = datetime.now().isoformat()
            task.add_history("transition", actor="system",
                             from_status=old, to_status="IN_PROGRESS",
                             note="Auto-started on first dispatch")
            save_task(task)
            update_index_entry(args.task_id, status="IN_PROGRESS")

            append_log(get_task_dir(args.task_id), {
                "time": datetime.now().isoformat(),
                "event": "task.auto_transition",
                "task": args.task_id,
                "from": old,
                "to": "IN_PROGRESS",
            })

    if _json_ok(args.json, task_id=args.task_id, subtask_id=subtask.id,
                status=subtask.status, message=f"Dispatched {subtask.id}"):
        return
    print(f"Dispatched {subtask.id} in {args.task_id}: {subtask.title}")
    print(f"  Agent: {args.agent or 'unassigned'}  |  Type: {args.type}  |  Status: {subtask.status}")
    if deps:
        print(f"  Dependencies: {', '.join(deps)}")


def cmd_transition(args):
    """Manually advance task state."""
    with task_lock(args.task_id):
        task = read_task(args.task_id)
        if task is None:
            if _json_error(args.json, f"Task {args.task_id} not found"):
                sys.exit(1)
            print(f"Task {args.task_id} not found", file=sys.stderr)
            sys.exit(1)

        new_status = validate_task_transition(task.status, args.event)
        if new_status is None:
            valid = get_valid_task_events(task.status)
            err = f"Invalid transition: {task.status} + '{args.event}'"
            if _json_error(args.json, err):
                sys.exit(1)
            print(err, file=sys.stderr)
            print(f"Valid events for {task.status}: {', '.join(valid) if valid else 'none (terminal)'}", file=sys.stderr)
            sys.exit(1)

        old_status = task.status
        task.status = new_status
        task.add_history("transition", actor="user",
                         from_status=old_status, to_status=new_status,
                         note=args.note)

        # Side effects for specific transitions
        if new_status == "APPROVED" and args.note:
            task.plan["approved_by"] = "human"
            task.plan["approved_at"] = datetime.now().isoformat()

        if new_status in ("BLOCKED",) and args.note:
            task.metadata["blocked_reason"] = args.note

        if new_status == "IN_PROGRESS" and old_status == "BLOCKED":
            task.metadata["blocked_reason"] = None

        if new_status in TERMINAL_TASK_STATUSES:
            task.timeline["completed_at"] = datetime.now().isoformat()

        save_task(task)
        update_index_entry(args.task_id, status=new_status)

        # Log
        append_log(get_task_dir(args.task_id), {
            "time": datetime.now().isoformat(),
            "event": f"task.{args.event}",
            "task": args.task_id,
            "from": old_status,
            "to": new_status,
            "actor": "user",
            "note": args.note,
        })

    if _json_ok(args.json, task_id=args.task_id, status=new_status,
                message=f"{old_status} -> {new_status}"):
        return
    print(f"{args.task_id}: {old_status} -> {new_status} (event: {args.event})")


def cmd_subtask(args):
    """Update subtask state/progress."""
    with task_lock(args.task_id):
        subtask = read_subtask(args.task_id, args.subtask_id)
        if subtask is None:
            if _json_error(args.json, f"Subtask {args.subtask_id} not found in {args.task_id}"):
                sys.exit(1)
            print(f"Subtask {args.subtask_id} not found in {args.task_id}", file=sys.stderr)
            sys.exit(1)

        new_status = validate_subtask_transition(subtask.status, args.event)
        if new_status is None:
            valid = get_valid_subtask_events(subtask.status)
            err = f"Invalid subtask transition: {subtask.status} + '{args.event}'"
            if _json_error(args.json, err):
                sys.exit(1)
            print(err, file=sys.stderr)
            print(f"Valid events for {subtask.status}: {', '.join(valid) if valid else 'none (terminal)'}", file=sys.stderr)
            sys.exit(1)

        old_status = subtask.status
        subtask.status = new_status

        # Update progress
        if args.progress is not None:
            subtask.progress["percent"] = args.progress
            subtask.progress["last_update"] = datetime.now().isoformat()

        if args.note:
            subtask.progress["checkpoint"] = args.note

        # Set progress to 100 on done
        if new_status == "DONE":
            subtask.progress["percent"] = 100
            subtask.progress["last_update"] = datetime.now().isoformat()
            subtask.result["status"] = "success"
            if args.note:
                subtask.result["summary"] = args.note

        if new_status == "FAILED":
            subtask.result["status"] = "failed"
            if args.note:
                subtask.result["error"] = args.note

        subtask.add_history(args.event, actor="agent",
                            note=args.note,
                            progress=args.progress)

        save_subtask(subtask)

        # Log
        append_log(get_task_dir(args.task_id), {
            "time": datetime.now().isoformat(),
            "event": f"subtask.{args.event}",
            "task": args.task_id,
            "subtask": args.subtask_id,
            "from": old_status,
            "to": new_status,
        })

        # Update index done count
        done_count = count_done_subtasks(args.task_id)
        task = read_task(args.task_id)
        update_index_entry(args.task_id,
                           subtasks_done=done_count,
                           subtask_count=len(task.subtasks))

        auto_msg = None
        # Check auto-transition for parent task
        if new_status in ("DONE", "FAILED"):
            all_subtasks = [s.to_dict() for s in read_all_subtasks(args.task_id)]
            auto = check_auto_transition(task.status, all_subtasks)
            if auto:
                event, reason = auto
                new_task_status = validate_task_transition(task.status, event)
                if new_task_status:
                    old_task_status = task.status
                    task.status = new_task_status
                    task.add_history("transition", actor="system",
                                     from_status=old_task_status,
                                     to_status=new_task_status,
                                     note=f"Auto: {reason}")
                    save_task(task)
                    update_index_entry(args.task_id, status=new_task_status)

                    append_log(get_task_dir(args.task_id), {
                        "time": datetime.now().isoformat(),
                        "event": "task.auto_transition",
                        "task": args.task_id,
                        "from": old_task_status,
                        "to": new_task_status,
                        "reason": reason,
                    })
                    auto_msg = f"Auto-transition: {args.task_id} {old_task_status} -> {new_task_status} ({reason})"

        # Unblock dependents if this subtask is now DONE
        if new_status == "DONE":
            _unblock_dependents(args.task_id, args.subtask_id)

    if _json_ok(args.json, task_id=args.task_id, subtask_id=args.subtask_id,
                status=new_status, message=f"{old_status} -> {new_status}"):
        return
    if auto_msg:
        print(f"  {auto_msg}")
    print(f"{args.task_id}/{args.subtask_id}: {old_status} -> {new_status} (event: {args.event})")


def _unblock_dependents(task_id: str, completed_subtask_id: str):
    """Check if completing this subtask unblocks others."""
    all_subtasks = read_all_subtasks(task_id)
    for st in all_subtasks:
        if completed_subtask_id in st.blocked_by and st.status == "BLOCKED":
            st.blocked_by.remove(completed_subtask_id)
            if not st.blocked_by:
                # All blockers resolved — unblock
                if st.assignment.get("agent"):
                    st.status = "ASSIGNED"
                else:
                    st.status = "PENDING"
                st.add_history("unblock", actor="system",
                               note=f"Unblocked: {completed_subtask_id} completed")
                save_subtask(st)
                logger.info("Unblocked %s/%s", task_id, st.id)
            else:
                save_subtask(st)


def cmd_check(args):
    """Heartbeat-triggered state check."""
    if args.task_id:
        # Check a single task
        result = check_single_task(args.task_id, config=None)
        results = {"alerts": result["alerts"], "summary": result["subtask_summary"],
                   "all_ok": len(result["alerts"]) == 0, "tasks": [result]}
    else:
        results = check_all_tasks()

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    if args.discord:
        print(format_heartbeat_digest(results))
        return

    if args.quiet:
        # Minimal output for cron/heartbeat
        if results["all_ok"]:
            print(f"OK: {results.get('summary', 'all clear')}")
        else:
            for alert in results["alerts"]:
                print(f"ALERT: {alert}")
        return

    # Verbose output
    tasks = results.get("tasks", [])
    if not tasks:
        print("No active tasks.")
        return

    print(f"Task Engine Check — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'=' * 60}")

    for t in tasks:
        status_marker = "!" if t.get("alerts") else "."
        print(f"  [{status_marker}] {t['task_id']}: {t['status']} ({t.get('subtask_summary', '-')})")

    alerts = results.get("alerts", [])
    if alerts:
        print(f"\nAlerts ({len(alerts)}):")
        for a in alerts:
            print(f"  ! {a}")
    else:
        print(f"\nAll clear.")

    print(f"{'=' * 60}")
    print(f"Summary: {results.get('summary', '-')}")


def cmd_notify(args):
    """Generate Discord-formatted notification messages."""
    if args.notify_type == "digest":
        # Full heartbeat digest
        results = check_all_tasks()
        print(format_heartbeat_digest(results))
        return

    # All other types need a task_id
    task_id = args.task_id
    if not task_id:
        print("Task ID required for this notification type", file=sys.stderr)
        sys.exit(1)

    task = read_task(task_id)
    if task is None:
        print(f"Task {task_id} not found", file=sys.stderr)
        sys.exit(1)

    if args.notify_type == "created":
        print(format_task_created(task.to_dict()))

    elif args.notify_type == "transition":
        # Find last transition in history
        event = args.event
        if not event:
            # Find from history
            for h in reversed(task.history):
                if h.get("event") == "transition":
                    event = "transition"
                    from_s = h.get("from_status", "?")
                    to_s = h.get("to_status", "?")
                    actor = h.get("actor", "system")
                    print(format_transition(task_id, event, from_s, to_s, actor))
                    return
            print("No transition found in history and no --event specified", file=sys.stderr)
            sys.exit(1)

        # Find a matching transition in history for this event
        for h in reversed(task.history):
            if h.get("event") == "transition":
                from_s = h.get("from_status", "?")
                to_s = h.get("to_status", "?")
                actor = h.get("actor", "system")
                print(format_transition(task_id, event, from_s, to_s, actor))
                return
        # Fallback: show current status
        print(format_transition(task_id, event, "?", task.status, "system"))

    elif args.notify_type == "status":
        subtasks = read_all_subtasks(task_id)
        print(format_status_update(task.to_dict(), [s.to_dict() for s in subtasks]))

    elif args.notify_type == "completed":
        subtasks = read_all_subtasks(task_id)
        print(format_completion_summary(task.to_dict(), [s.to_dict() for s in subtasks]))

    elif args.notify_type == "alert":
        alert_type = args.type or "stuck"
        subtask_id = args.subtask_id or ""
        agent = ""
        progress = ""
        if subtask_id:
            st = read_subtask(task_id, subtask_id)
            if st:
                agent = st.assignment.get("agent", "") if st.assignment else ""
                pct = st.progress.get("percent", 0) if st.progress else 0
                progress = f"{pct}%"
        alert = {
            "type": alert_type,
            "task_id": task_id,
            "subtask_id": subtask_id,
            "message": f"Alert triggered for {task_id}" + (f"/{subtask_id}" if subtask_id else ""),
            "agent": agent,
            "progress": progress,
        }
        print(format_alert(alert))

    else:
        print(f"Unknown notification type: {args.notify_type}", file=sys.stderr)
        sys.exit(1)


def cmd_archive(args):
    """Move a terminal-state task to archive/."""
    task = read_task(args.task_id)
    if task is None:
        if _json_error(args.json, f"Task {args.task_id} not found"):
            sys.exit(1)
        print(f"Task {args.task_id} not found", file=sys.stderr)
        sys.exit(1)

    if task.status not in TERMINAL_TASK_STATUSES:
        err = f"Task {args.task_id} is in state {task.status}, not terminal — cannot archive"
        if _json_error(args.json, err):
            sys.exit(1)
        print(err, file=sys.stderr)
        sys.exit(1)

    success = archive_task(args.task_id)
    if success:
        if _json_ok(args.json, task_id=args.task_id, status="archived",
                    message=f"Archived {args.task_id}"):
            return
        print(f"Archived {args.task_id}")
    else:
        if _json_error(args.json, f"Failed to archive {args.task_id}"):
            sys.exit(1)
        print(f"Failed to archive {args.task_id}", file=sys.stderr)
        sys.exit(1)


def cmd_auto_dispatch(args):
    """Auto-dispatch ready subtasks."""
    # Collect task IDs to process
    if args.all:
        task_entries = list_tasks(include_terminal=False)
        task_ids = [t["id"] for t in task_entries]
    elif args.task_id:
        task_ids = [args.task_id]
    else:
        print("Specify a task ID or --all", file=sys.stderr)
        sys.exit(1)

    all_dispatches = []
    all_skipped = []

    for task_id in task_ids:
        task = read_task(task_id)
        if task is None:
            all_skipped.append({
                "task_id": task_id,
                "subtask_id": None,
                "reason": "Task not found",
            })
            continue

        task_dict = task.to_dict()
        subtasks = read_all_subtasks(task_id)
        subtask_dicts = [s.to_dict() for s in subtasks]

        # If --subtask specified, only process that one
        if args.subtask:
            subtask_dicts = [s for s in subtask_dicts if s["id"] == args.subtask]
            if not subtask_dicts:
                print(f"Subtask {args.subtask} not found in {task_id}", file=sys.stderr)
                sys.exit(1)

        all_subtask_dicts = [s.to_dict() for s in read_all_subtasks(task_id)]

        for st_dict in subtask_dicts:
            # --show-context: display full dispatch context and exit
            if args.show_context:
                context = build_dispatch_context(task_dict, st_dict, all_subtask_dicts)
                print(json.dumps(context, indent=2, ensure_ascii=False))
                return

            ready, reason = check_dispatch_readiness(task_dict, st_dict, all_subtask_dicts)

            if not ready:
                all_skipped.append({
                    "task_id": task_id,
                    "subtask_id": st_dict["id"],
                    "reason": reason,
                })
                continue

            # Build context and prompt
            context = build_dispatch_context(task_dict, st_dict, all_subtask_dicts)
            prompt = generate_dispatch_prompt(context)

            dispatch_entry = {
                "task_id": task_id,
                "subtask_id": st_dict["id"],
                "agent": context["agent"],
                "prompt": prompt,
                "ready": True,
                "reason": reason,
            }

            if args.dry_run:
                all_dispatches.append(dispatch_entry)
                continue

            # Actually dispatch: transition subtask to ASSIGNED if PENDING
            with task_lock(task_id):
                subtask_obj = read_subtask(task_id, st_dict["id"])
                if subtask_obj is None:
                    continue

                if subtask_obj.status == "PENDING":
                    subtask_obj.status = "ASSIGNED"
                    subtask_obj.assignment = {
                        "agent": context["agent"],
                        "instance_id": None,
                        "assigned_at": datetime.now().isoformat(),
                        "dispatch_context": prompt[:500],
                    }
                    subtask_obj.add_history("assign", actor="dispatcher",
                                            note=f"Auto-dispatched to {context['agent']}")
                    save_subtask(subtask_obj)

                # Auto-transition APPROVED -> IN_PROGRESS on first dispatch
                current_task = read_task(task_id)
                if current_task and current_task.status == "APPROVED":
                    old = current_task.status
                    current_task.status = "IN_PROGRESS"
                    current_task.timeline["started_at"] = datetime.now().isoformat()
                    current_task.add_history("transition", actor="system",
                                             from_status=old, to_status="IN_PROGRESS",
                                             note="Auto-started on first auto-dispatch")
                    save_task(current_task)
                    update_index_entry(task_id, status="IN_PROGRESS")
                    # Update local task_dict for subsequent subtasks
                    task_dict = current_task.to_dict()

                append_log(get_task_dir(task_id), {
                    "time": datetime.now().isoformat(),
                    "event": "subtask.auto_dispatched",
                    "task": task_id,
                    "subtask": st_dict["id"],
                    "agent": context["agent"],
                })

            all_dispatches.append(dispatch_entry)

    result = {
        "dispatches": all_dispatches,
        "skipped": all_skipped,
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_rebuild_index(args):
    """Rebuild index.json from task directories."""
    tasks_dir = get_tasks_dir()
    found = []
    skipped = []

    # Walk all TASK-* directories (skip archive/)
    for entry in sorted(tasks_dir.iterdir()):
        if not entry.is_dir():
            continue
        if not entry.name.startswith("TASK-"):
            continue

        task_path = entry / "task.json"
        if not task_path.exists():
            skipped.append(entry.name)
            logger.warning("No task.json in %s, skipping", entry.name)
            continue

        try:
            data = json.loads(task_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            skipped.append(entry.name)
            logger.warning("Cannot read %s/task.json: %s", entry.name, e)
            continue

        # Validate minimum required fields
        if "id" not in data or "title" not in data:
            skipped.append(entry.name)
            logger.warning("Invalid task.json in %s (missing id/title), skipping", entry.name)
            continue

        # Count subtasks
        subtask_ids = data.get("subtasks", [])
        done_count = 0
        for sid in subtask_ids:
            st_path = entry / f"{sid}.json"
            if st_path.exists():
                try:
                    st_data = json.loads(st_path.read_text(encoding="utf-8"))
                    if st_data.get("status") == "DONE":
                        done_count += 1
                except (json.JSONDecodeError, OSError):
                    pass

        index_entry = {
            "id": data["id"],
            "title": data["title"],
            "status": data.get("status", "PLANNING"),
            "priority": data.get("priority", "P1"),
            "created": data.get("created", ""),
            "discord_channel_id": data.get("discord", {}).get("channel_id"),
            "subtask_count": len(subtask_ids),
            "subtasks_done": done_count,
        }
        found.append(index_entry)

    # Write new index atomically
    new_index = {"version": 1, "tasks": found}
    write_index(new_index)

    result = {
        "rebuilt": len(found),
        "skipped": len(skipped),
        "task_ids": [e["id"] for e in found],
        "skipped_dirs": skipped,
    }

    if _json_ok(args.json, **result, message=f"Rebuilt index with {len(found)} tasks"):
        return
    print(f"Rebuilt index.json: {len(found)} tasks found, {len(skipped)} skipped")
    for e in found:
        print(f"  {e['id']}: {e['status']} — {e['title'][:40]}")
    if skipped:
        print(f"Skipped: {', '.join(skipped)}")


# --- Main ---

def main():
    parser = argparse.ArgumentParser(
        prog="task_engine",
        description="Task orchestration engine for multi-agent workflows",
    )
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose logging")
    sub = parser.add_subparsers(dest="command")

    # create
    p_create = sub.add_parser("create", help="Create a new task")
    p_create.add_argument("title", help="Task title")
    p_create.add_argument("--priority", choices=PRIORITIES, default="P1",
                          help="Priority (default: P1)")
    p_create.add_argument("--plan", help="Initial plan text")
    p_create.add_argument("--json", action="store_true",
                          help="Machine-readable JSON output")

    # status
    p_status = sub.add_parser("status", help="View task status")
    p_status.add_argument("task_id", nargs="?", help="Task ID for detail view")
    p_status.add_argument("--all", action="store_true",
                          help="Include terminal/archived tasks")
    p_status.add_argument("--json", action="store_true",
                          help="Machine-readable JSON output")

    # dispatch
    p_dispatch = sub.add_parser("dispatch", help="Create and assign a subtask")
    p_dispatch.add_argument("task_id", help="Parent task ID")
    p_dispatch.add_argument("title", help="Subtask title")
    p_dispatch.add_argument("--agent", help="Agent to assign (e.g. claude-code)")
    p_dispatch.add_argument("--type", choices=SUBTASK_TYPES, default="dev",
                            help="Subtask type (default: dev)")
    p_dispatch.add_argument("--deps", help="Comma-separated dependency subtask IDs")
    p_dispatch.add_argument("--context", help="Dispatch context for the agent")
    p_dispatch.add_argument("--json", action="store_true",
                            help="Machine-readable JSON output")

    # check
    p_check = sub.add_parser("check", help="Heartbeat-triggered state check")
    p_check.add_argument("task_id", nargs="?", help="Check a specific task (optional)")
    p_check.add_argument("--quiet", action="store_true",
                         help="Minimal output for cron/heartbeat")
    p_check.add_argument("--json", action="store_true",
                         help="Machine-readable JSON output")
    p_check.add_argument("--discord", action="store_true",
                         help="Output Discord-formatted heartbeat digest")

    # transition
    p_trans = sub.add_parser("transition", help="Advance task state")
    p_trans.add_argument("task_id", help="Task ID")
    p_trans.add_argument("event", help="Transition event (e.g. approve, start, complete)")
    p_trans.add_argument("--note", help="Note for the transition")
    p_trans.add_argument("--json", action="store_true",
                         help="Machine-readable JSON output")

    # subtask
    p_sub = sub.add_parser("subtask", help="Update subtask state/progress")
    p_sub.add_argument("task_id", help="Parent task ID")
    p_sub.add_argument("subtask_id", help="Subtask ID")
    p_sub.add_argument("event", help="Subtask event (start, done, fail, block, unblock)")
    p_sub.add_argument("--note", help="Note for the event")
    p_sub.add_argument("--progress", type=int, help="Progress percent (0-100)")
    p_sub.add_argument("--json", action="store_true",
                       help="Machine-readable JSON output")

    # notify
    p_notify = sub.add_parser("notify", help="Generate Discord-formatted notifications")
    p_notify.add_argument("task_id", nargs="?", help="Task ID (not needed for digest)")
    p_notify.add_argument("notify_type",
                          choices=["created", "transition", "status", "completed", "alert", "digest"],
                          help="Notification type")
    p_notify.add_argument("--event", help="Transition event name (for transition type)")
    p_notify.add_argument("--type", help="Alert type: stuck/overdue/failed (for alert type)")
    p_notify.add_argument("--subtask-id", help="Subtask ID (for alert type)")

    # archive
    p_archive = sub.add_parser("archive", help="Archive a terminal-state task")
    p_archive.add_argument("task_id", help="Task ID to archive")
    p_archive.add_argument("--json", action="store_true",
                           help="Machine-readable JSON output")

    # auto-dispatch
    p_auto = sub.add_parser("auto-dispatch", help="Auto-dispatch ready subtasks")
    p_auto.add_argument("task_id", nargs="?", help="Task ID (optional with --all)")
    p_auto.add_argument("--all", action="store_true",
                        help="Auto-dispatch across all active tasks")
    p_auto.add_argument("--dry-run", action="store_true",
                        help="Show what would be dispatched without acting")
    p_auto.add_argument("--subtask", help="Target a specific subtask")
    p_auto.add_argument("--show-context", action="store_true",
                        help="Show full dispatch context for a subtask")

    # rebuild-index
    p_rebuild = sub.add_parser("rebuild-index", help="Rebuild index.json from task directories")
    p_rebuild.add_argument("--json", action="store_true",
                           help="Machine-readable JSON output")

    args = parser.parse_args()
    setup_logging(verbose=getattr(args, "verbose", False))

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    commands = {
        "create": cmd_create,
        "status": cmd_status,
        "dispatch": cmd_dispatch,
        "check": cmd_check,
        "transition": cmd_transition,
        "subtask": cmd_subtask,
        "archive": cmd_archive,
        "notify": cmd_notify,
        "auto-dispatch": cmd_auto_dispatch,
        "rebuild-index": cmd_rebuild_index,
    }

    # Error handling: catch exceptions and return clean error messages
    use_json = getattr(args, "json", False)
    try:
        commands[args.command](args)
    except SystemExit:
        raise
    except Exception as e:
        logger.debug("Exception in %s: %s", args.command, traceback.format_exc())
        if use_json:
            print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
            sys.exit(1)
        else:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
