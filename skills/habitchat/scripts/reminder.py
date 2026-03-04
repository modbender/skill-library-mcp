#!/usr/bin/env python3
"""
HabitChat Reminder System - Sets up platform-appropriate reminders.
No external dependencies - stdlib only.
"""

import argparse
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path.home() / ".habitchat"
HABITS_FILE = DATA_DIR / "habits.json"
REMINDERS_LOG = DATA_DIR / "reminders.log"
REMINDER_STATE = DATA_DIR / "reminder_state.json"


def load_json(path, default=None):
    if default is None:
        default = {}
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def find_habit(habits, query):
    query_lower = query.lower().strip()
    for h in habits:
        if h["id"] == query_lower or h["id"].startswith(query_lower):
            return h
    for h in habits:
        if h["name"].lower() == query_lower:
            return h
    for h in habits:
        if query_lower in h["name"].lower():
            return h
    return None


def detect_platform():
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "linux":
        # Check for common notification tools
        if os.path.exists("/usr/bin/notify-send") or os.path.exists("/usr/local/bin/notify-send"):
            return "linux-desktop"
        return "linux-headless"
    elif system == "windows":
        return "windows"
    return "unknown"


def log_reminder(habit_name, message):
    """Append to reminders.log as a fallback notification method."""
    REMINDERS_LOG.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(REMINDERS_LOG, "a") as f:
        f.write(f"[{timestamp}] {habit_name}: {message}\n")


# --- SETUP ---

def cmd_setup(args):
    habits_data = load_json(HABITS_FILE, {"habits": []})
    state = load_json(REMINDER_STATE, {"reminders": {}})

    habit = find_habit(habits_data["habits"], args.habit)
    if not habit:
        print(json.dumps({"status": "error", "message": f"Habit not found: {args.habit}"}))
        sys.exit(1)

    plat = detect_platform()
    reminder_time = habit.get("time", "09:00")
    hour, minute = reminder_time.split(":")

    result = {
        "habit": habit["name"],
        "time": reminder_time,
        "platform": plat,
        "method": None,
        "instructions": None,
    }

    if plat == "macos":
        # Create a launchd plist or use osascript-based reminder
        script_content = f'''#!/bin/bash
osascript -e 'display notification "Time for: {habit["name"]}" with title "HabitChat Reminder"'
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] {habit["name"]}: Reminder fired" >> "{REMINDERS_LOG}"
'''
        script_path = DATA_DIR / f"reminder_{habit['id']}.sh"
        script_path.write_text(script_content)
        os.chmod(script_path, 0o755)

        result["method"] = "macos-notification"
        result["script"] = str(script_path)
        result["instructions"] = (
            f"Reminder script created at {script_path}. "
            f"To activate, add a cron job: crontab -e and add:\n"
            f"{minute} {hour} * * * {script_path}"
        )
        result["cron_line"] = f"{minute} {hour} * * * {script_path}"

    elif plat == "linux-desktop":
        script_content = f'''#!/bin/bash
notify-send "HabitChat" "Time for: {habit["name"]}" --icon=dialog-information
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] {habit["name"]}: Reminder fired" >> "{REMINDERS_LOG}"
'''
        script_path = DATA_DIR / f"reminder_{habit['id']}.sh"
        script_path.write_text(script_content)
        os.chmod(script_path, 0o755)

        result["method"] = "linux-notify-send"
        result["script"] = str(script_path)
        result["instructions"] = (
            f"Reminder script created at {script_path}. "
            f"To activate, add a cron job: crontab -e and add:\n"
            f"{minute} {hour} * * * DISPLAY=:0 {script_path}"
        )
        result["cron_line"] = f"{minute} {hour} * * * DISPLAY=:0 {script_path}"

    else:
        # Headless / unknown - log file only
        result["method"] = "log-file"
        result["instructions"] = (
            f"No desktop notification available. Reminders will be logged to {REMINDERS_LOG}. "
            f"To set up a cron job that logs reminders:\n"
            f'{minute} {hour} * * * echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] {habit["name"]}: Reminder" >> "{REMINDERS_LOG}"'
        )

    # Save state
    state["reminders"][habit["id"]] = {
        "habit_name": habit["name"],
        "time": reminder_time,
        "method": result["method"],
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    save_json(REMINDER_STATE, state)

    print(json.dumps({"status": "ok", "reminder": result}))


# --- LIST ---

def cmd_list(_args):
    state = load_json(REMINDER_STATE, {"reminders": {}})
    habits_data = load_json(HABITS_FILE, {"habits": []})

    reminders = []
    for hid, r in state.get("reminders", {}).items():
        habit = next((h for h in habits_data["habits"] if h["id"] == hid), None)
        reminders.append({
            "habit_id": hid,
            "habit_name": r.get("habit_name", "Unknown"),
            "time": r.get("time"),
            "method": r.get("method"),
            "active": r.get("active", False),
            "habit_exists": habit is not None,
        })

    print(json.dumps({"status": "ok", "reminders": reminders}))


# --- DISABLE ---

def cmd_disable(args):
    habits_data = load_json(HABITS_FILE, {"habits": []})
    state = load_json(REMINDER_STATE, {"reminders": {}})

    habit = find_habit(habits_data["habits"], args.habit)
    if not habit:
        print(json.dumps({"status": "error", "message": f"Habit not found: {args.habit}"}))
        sys.exit(1)

    if habit["id"] in state.get("reminders", {}):
        state["reminders"][habit["id"]]["active"] = False
        save_json(REMINDER_STATE, state)

        # Clean up script file
        script_path = DATA_DIR / f"reminder_{habit['id']}.sh"
        if script_path.exists():
            script_path.unlink()

    print(json.dumps({
        "status": "ok",
        "message": f"Reminder disabled for '{habit['name']}'. "
                   f"Remember to also remove the cron job if you added one: crontab -e",
    }))


# --- CHECK (for agent to call at interaction time) ---

def cmd_check(_args):
    """Check for any pending reminders that fired since last check."""
    if not REMINDERS_LOG.exists():
        print(json.dumps({"status": "ok", "pending": []}))
        return

    state = load_json(REMINDER_STATE, {"reminders": {}, "last_check": None})
    last_check = state.get("last_check")

    pending = []
    with open(REMINDERS_LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Parse: [timestamp] habit_name: message
            try:
                ts_str = line.split("]")[0].strip("[")
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if last_check:
                    last_dt = datetime.fromisoformat(last_check.replace("Z", "+00:00"))
                    if ts <= last_dt:
                        continue
                rest = line.split("]", 1)[1].strip()
                pending.append({"timestamp": ts_str, "message": rest})
            except (ValueError, IndexError):
                continue

    state["last_check"] = datetime.now(timezone.utc).isoformat()
    save_json(REMINDER_STATE, state)

    print(json.dumps({"status": "ok", "pending": pending}))


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="HabitChat Reminders")
    sub = parser.add_subparsers(dest="command")

    p_setup = sub.add_parser("setup")
    p_setup.add_argument("--habit", required=True)

    sub.add_parser("list")

    p_disable = sub.add_parser("disable")
    p_disable.add_argument("--habit", required=True)

    sub.add_parser("check")

    args = parser.parse_args()

    commands = {
        "setup": cmd_setup,
        "list": cmd_list,
        "disable": cmd_disable,
        "check": cmd_check,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
