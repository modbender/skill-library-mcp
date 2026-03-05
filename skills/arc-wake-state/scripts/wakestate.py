#!/usr/bin/env python3
"""Wake State — Crash Recovery & Persistence for OpenClaw agents.

Persist agent state across crashes, context deaths, and restarts.
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DATA_DIR = os.path.expanduser("~/.openclaw/wake-state")
HEARTBEAT_TIMEOUT_SECONDS = 600  # 10 minutes — if no heartbeat in this window, it was a crash


def get_data_dir(data_dir=None):
    d = Path(data_dir or DEFAULT_DATA_DIR)
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_json(path, default=None):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default or {}


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# === Commands ===

def cmd_save(args):
    d = get_data_dir(args.data_dir)
    state = load_json(d / "state.json", {"custom": {}})

    if args.status:
        state["status"] = args.status
    if args.task:
        state["current_task"] = args.task
    if args.note:
        state.setdefault("notes", []).append({
            "timestamp": now_iso(),
            "content": args.note,
        })
        # Keep last 50 notes
        state["notes"] = state["notes"][-50:]

    state["last_saved"] = now_iso()
    save_json(d / "state.json", state)
    print(f"State saved at {state['last_saved']}")
    if args.status:
        print(f"Status: {args.status}")


def cmd_read(args):
    d = get_data_dir(args.data_dir)
    state = load_json(d / "state.json")

    if not state:
        print("No state saved yet.")
        return

    print(f"=== Wake State ===")
    print(f"Last saved: {state.get('last_saved', 'never')}")
    print(f"Status: {state.get('status', 'unknown')}")

    if state.get("current_task"):
        print(f"Current task: {state['current_task']}")

    custom = state.get("custom", {})
    if custom:
        print(f"\nCustom values:")
        for k, v in custom.items():
            print(f"  {k}: {v}")

    notes = state.get("notes", [])
    if notes:
        print(f"\nRecent notes ({len(notes)} total):")
        for note in notes[-5:]:
            ts = note["timestamp"][:19].replace("T", " ")
            print(f"  [{ts}] {note['content']}")


def cmd_task_add(args):
    d = get_data_dir(args.data_dir)
    tasks = load_json(d / "tasks.json", {"tasks": [], "next_id": 1})

    task = {
        "id": tasks["next_id"],
        "task": args.task,
        "priority": args.priority or "normal",
        "created": now_iso(),
        "status": "pending",
    }
    tasks["tasks"].append(task)
    tasks["next_id"] += 1
    save_json(d / "tasks.json", tasks)
    print(f"Task #{task['id']} added: {args.task} [{args.priority or 'normal'}]")


def cmd_task_done(args):
    d = get_data_dir(args.data_dir)
    tasks = load_json(d / "tasks.json", {"tasks": [], "next_id": 1})

    for t in tasks["tasks"]:
        if t["id"] == args.id:
            t["status"] = "done"
            t["completed"] = now_iso()
            save_json(d / "tasks.json", tasks)
            print(f"Task #{args.id} marked as done: {t['task']}")
            return

    print(f"Task #{args.id} not found.")
    sys.exit(1)


def cmd_tasks(args):
    d = get_data_dir(args.data_dir)
    tasks = load_json(d / "tasks.json", {"tasks": [], "next_id": 1})

    pending = [t for t in tasks["tasks"] if t["status"] == "pending"]
    done = [t for t in tasks["tasks"] if t["status"] == "done"]

    if not pending and not done:
        print("No tasks.")
        return

    if pending:
        print(f"Pending tasks ({len(pending)}):")
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
        pending.sort(key=lambda t: priority_order.get(t.get("priority", "normal"), 2))
        for t in pending:
            pri = f" [{t['priority']}]" if t.get("priority", "normal") != "normal" else ""
            print(f"  #{t['id']}: {t['task']}{pri}")

    if done and args.show_done:
        print(f"\nCompleted ({len(done)}):")
        for t in done[-10:]:
            print(f"  #{t['id']}: {t['task']} (done {t.get('completed', '?')[:10]})")


def cmd_checkpoint(args):
    d = get_data_dir(args.data_dir)
    cp_dir = d / "checkpoints" / args.name
    cp_dir.mkdir(parents=True, exist_ok=True)

    # Copy current state and tasks
    for fname in ["state.json", "tasks.json"]:
        src = d / fname
        if src.exists():
            shutil.copy2(str(src), str(cp_dir / fname))

    meta = {"name": args.name, "created": now_iso()}
    save_json(cp_dir / "meta.json", meta)
    print(f"Checkpoint '{args.name}' created at {meta['created']}")


def cmd_restore(args):
    d = get_data_dir(args.data_dir)
    cp_dir = d / "checkpoints" / args.name

    if not cp_dir.exists():
        print(f"Checkpoint '{args.name}' not found.")
        # List available
        cp_base = d / "checkpoints"
        if cp_base.exists():
            available = [p.name for p in cp_base.iterdir() if p.is_dir()]
            if available:
                print(f"Available: {', '.join(available)}")
        sys.exit(1)

    for fname in ["state.json", "tasks.json"]:
        src = cp_dir / fname
        if src.exists():
            shutil.copy2(str(src), str(d / fname))

    print(f"Restored from checkpoint '{args.name}'")


def cmd_heartbeat(args):
    d = get_data_dir(args.data_dir)
    hb = load_json(d / "heartbeat.json", {"beats": []})

    beat = {"timestamp": now_iso(), "session": args.session or "default"}
    hb["beats"].append(beat)
    hb["beats"] = hb["beats"][-100:]  # Keep last 100
    hb["last_beat"] = beat["timestamp"]
    save_json(d / "heartbeat.json", hb)
    print(f"Heartbeat recorded at {beat['timestamp']}")


def cmd_crash_check(args):
    d = get_data_dir(args.data_dir)
    hb = load_json(d / "heartbeat.json")

    if not hb or not hb.get("last_beat"):
        print("No previous heartbeat found. This appears to be a first boot.")
        return

    last = datetime.fromisoformat(hb["last_beat"])
    now = datetime.now(timezone.utc)
    gap = (now - last).total_seconds()

    if gap > HEARTBEAT_TIMEOUT_SECONDS:
        minutes = int(gap / 60)
        print(f"⚠️  CRASH DETECTED — Last heartbeat was {minutes} minutes ago ({hb['last_beat']})")
        print(f"The previous session likely crashed or was killed.")
    else:
        print(f"✅ Clean restart — Last heartbeat {int(gap)}s ago ({hb['last_beat']})")


def cmd_set(args):
    d = get_data_dir(args.data_dir)
    state = load_json(d / "state.json", {"custom": {}})
    state.setdefault("custom", {})[args.key] = args.value
    state["last_saved"] = now_iso()
    save_json(d / "state.json", state)
    print(f"Set {args.key} = {args.value}")


def cmd_get(args):
    d = get_data_dir(args.data_dir)
    state = load_json(d / "state.json", {"custom": {}})
    value = state.get("custom", {}).get(args.key)
    if value is not None:
        print(value)
    else:
        print(f"Key '{args.key}' not found.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Wake State — Crash Recovery for OpenClaw")
    parser.add_argument("--data-dir", help="Override data directory")
    sub = parser.add_subparsers(dest="command")

    p_save = sub.add_parser("save", help="Save current state")
    p_save.add_argument("--status", help="Current status description")
    p_save.add_argument("--task", help="Current task description")
    p_save.add_argument("--note", help="Add a note")

    sub.add_parser("read", help="Read current state")

    p_ta = sub.add_parser("task-add", help="Add a persistent task")
    p_ta.add_argument("--task", required=True)
    p_ta.add_argument("--priority", choices=["critical", "high", "normal", "low"], default="normal")

    p_td = sub.add_parser("task-done", help="Mark task as done")
    p_td.add_argument("--id", type=int, required=True)

    p_tasks = sub.add_parser("tasks", help="List tasks")
    p_tasks.add_argument("--show-done", action="store_true")

    p_cp = sub.add_parser("checkpoint", help="Create a checkpoint")
    p_cp.add_argument("--name", required=True)

    p_restore = sub.add_parser("restore", help="Restore from checkpoint")
    p_restore.add_argument("--name", required=True)

    p_hb = sub.add_parser("heartbeat", help="Record a heartbeat")
    p_hb.add_argument("--session", help="Session identifier")

    sub.add_parser("crash-check", help="Check if last session crashed")

    p_set = sub.add_parser("set", help="Set a key-value pair")
    p_set.add_argument("--key", required=True)
    p_set.add_argument("--value", required=True)

    p_get = sub.add_parser("get", help="Get a value by key")
    p_get.add_argument("--key", required=True)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "save": cmd_save,
        "read": cmd_read,
        "task-add": cmd_task_add,
        "task-done": cmd_task_done,
        "tasks": cmd_tasks,
        "checkpoint": cmd_checkpoint,
        "restore": cmd_restore,
        "heartbeat": cmd_heartbeat,
        "crash-check": cmd_crash_check,
        "set": cmd_set,
        "get": cmd_get,
    }

    cmds[args.command](args)


if __name__ == "__main__":
    main()
