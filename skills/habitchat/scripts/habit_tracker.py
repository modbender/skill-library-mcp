#!/usr/bin/env python3
"""
HabitChat Core Tracker - Manages habits, logs, and streaks.
No external dependencies - stdlib only.
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA_DIR = Path.home() / ".habitchat"
HABITS_FILE = DATA_DIR / "habits.json"
LOGS_FILE = DATA_DIR / "logs.json"
STREAKS_FILE = DATA_DIR / "streaks.json"
CONFIG_FILE = DATA_DIR / "config.json"


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


def get_config():
    return load_json(CONFIG_FILE, {
        "timezone": "UTC",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })


def today_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def generate_id():
    return uuid.uuid4().hex[:8]


# --- INIT ---

def cmd_init(_args):
    if DATA_DIR.exists():
        print(json.dumps({"status": "already_initialized", "path": str(DATA_DIR)}))
        return

    DATA_DIR.mkdir(parents=True)
    save_json(HABITS_FILE, {"habits": []})
    save_json(LOGS_FILE, {"logs": []})
    save_json(STREAKS_FILE, {"streaks": {}})
    save_json(CONFIG_FILE, {
        "timezone": "UTC",
        "coaching_style": "friendly",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    print(json.dumps({"status": "initialized", "path": str(DATA_DIR)}))


# --- ADD ---

def cmd_add(args):
    data = load_json(HABITS_FILE, {"habits": []})
    habit_id = generate_id()

    days = args.days.split(",") if args.days else [
        "mon", "tue", "wed", "thu", "fri", "sat", "sun"
    ]

    habit = {
        "id": habit_id,
        "name": args.name,
        "time": args.time or "09:00",
        "days": [d.strip().lower()[:3] for d in days],
        "active": True,
        "paused": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    data["habits"].append(habit)
    save_json(HABITS_FILE, data)

    # Initialize streak
    streaks = load_json(STREAKS_FILE, {"streaks": {}})
    streaks["streaks"][habit_id] = {
        "current": 0,
        "longest": 0,
        "longest_start": None,
        "longest_end": None,
        "last_completed": None,
    }
    save_json(STREAKS_FILE, streaks)

    print(json.dumps({"status": "added", "habit": habit}))


# --- LOG ---

def cmd_log(args):
    data = load_json(HABITS_FILE, {"habits": []})
    logs = load_json(LOGS_FILE, {"logs": []})
    streaks = load_json(STREAKS_FILE, {"streaks": {}})

    # Find habit by name or id
    habit = find_habit(data["habits"], args.habit)
    if not habit:
        print(json.dumps({"status": "error", "message": f"Habit not found: {args.habit}"}))
        sys.exit(1)

    date = args.date or today_str()
    status = args.status  # done, skip, miss

    # Check for duplicate log
    existing = [l for l in logs["logs"]
                if l["habit_id"] == habit["id"] and l["date"] == date]
    if existing:
        existing[0]["status"] = status
        existing[0]["updated_at"] = datetime.now(timezone.utc).isoformat()
    else:
        logs["logs"].append({
            "habit_id": habit["id"],
            "date": date,
            "status": status,
            "logged_at": datetime.now(timezone.utc).isoformat(),
        })

    save_json(LOGS_FILE, logs)

    # Update streak
    streak = update_streak(habit["id"], logs["logs"])
    streaks["streaks"][habit["id"]] = streak
    save_json(STREAKS_FILE, streaks)

    print(json.dumps({
        "status": "logged",
        "habit": habit["name"],
        "log_status": status,
        "date": date,
        "streak": streak,
    }))


# --- LIST ---

def cmd_list(_args):
    data = load_json(HABITS_FILE, {"habits": []})
    logs = load_json(LOGS_FILE, {"logs": []})
    streaks = load_json(STREAKS_FILE, {"streaks": {}})
    date = today_str()

    result = []
    for h in data["habits"]:
        if not h.get("active", True):
            continue

        today_log = next(
            (l for l in logs["logs"]
             if l["habit_id"] == h["id"] and l["date"] == date),
            None
        )
        streak_data = streaks.get("streaks", {}).get(h["id"], {})

        result.append({
            "id": h["id"],
            "name": h["name"],
            "time": h.get("time", "--"),
            "days": h.get("days", []),
            "paused": h.get("paused", False),
            "today": today_log["status"] if today_log else "pending",
            "current_streak": streak_data.get("current", 0),
            "longest_streak": streak_data.get("longest", 0),
        })

    print(json.dumps({"status": "ok", "habits": result, "date": date}))


# --- STATS ---

def cmd_stats(args):
    data = load_json(HABITS_FILE, {"habits": []})
    logs = load_json(LOGS_FILE, {"logs": []})
    streaks = load_json(STREAKS_FILE, {"streaks": {}})

    habit = find_habit(data["habits"], args.habit)
    if not habit:
        print(json.dumps({"status": "error", "message": f"Habit not found: {args.habit}"}))
        sys.exit(1)

    days = int(args.days) if args.days else 30
    habit_logs = sorted(
        [l for l in logs["logs"] if l["habit_id"] == habit["id"]],
        key=lambda x: x["date"]
    )

    today = datetime.now(timezone.utc).date()
    streak_data = streaks.get("streaks", {}).get(habit["id"], {})

    # Compute rates
    last_7 = compute_rate(habit_logs, today, 7)
    last_30 = compute_rate(habit_logs, today, 30)
    all_time = compute_rate(habit_logs, today, 9999)

    # Day-of-week breakdown
    dow_stats = compute_day_of_week_stats(habit_logs)

    # Calendar grid (last N days)
    calendar = build_calendar(habit_logs, today, days)

    print(json.dumps({
        "status": "ok",
        "habit": habit["name"],
        "current_streak": streak_data.get("current", 0),
        "longest_streak": streak_data.get("longest", 0),
        "longest_start": streak_data.get("longest_start"),
        "longest_end": streak_data.get("longest_end"),
        "last_7_days": last_7,
        "last_30_days": last_30,
        "all_time": all_time,
        "day_of_week": dow_stats,
        "calendar": calendar,
    }))


# --- OVERVIEW ---

def cmd_overview(_args):
    data = load_json(HABITS_FILE, {"habits": []})
    logs = load_json(LOGS_FILE, {"logs": []})
    streaks = load_json(STREAKS_FILE, {"streaks": {}})
    date = today_str()
    today = datetime.now(timezone.utc).date()

    habits_status = []
    total_done = 0
    total_active = 0

    for h in data["habits"]:
        if not h.get("active", True) or h.get("paused", False):
            continue
        total_active += 1

        today_log = next(
            (l for l in logs["logs"]
             if l["habit_id"] == h["id"] and l["date"] == date),
            None
        )
        streak_data = streaks.get("streaks", {}).get(h["id"], {})
        current = streak_data.get("current", 0)
        longest = streak_data.get("longest", 0)

        is_done = today_log and today_log["status"] == "done"
        if is_done:
            total_done += 1

        # Check for approaching milestones
        milestone = None
        for m in [7, 14, 21, 30, 50, 100, 200, 365]:
            if current < m <= current + 3:
                milestone = f"{m - current} more days to hit {m}!"
                break

        habits_status.append({
            "name": h["name"],
            "today": today_log["status"] if today_log else "pending",
            "current_streak": current,
            "longest_streak": longest,
            "milestone": milestone,
        })

    # Sort by streak length descending
    habits_status.sort(key=lambda x: x["current_streak"], reverse=True)

    # Overall 7-day completion rate
    week_logs = [l for l in logs["logs"]
                 if (today - datetime.strptime(l["date"], "%Y-%m-%d").date()).days < 7]
    week_done = sum(1 for l in week_logs if l["status"] == "done")
    week_total = len(week_logs) if week_logs else 1

    print(json.dumps({
        "status": "ok",
        "date": date,
        "today_done": total_done,
        "today_total": total_active,
        "week_completion_rate": round(week_done / week_total * 100, 1),
        "habits": habits_status,
    }))


# --- EDIT ---

def cmd_edit(args):
    data = load_json(HABITS_FILE, {"habits": []})
    habit = find_habit(data["habits"], args.habit)
    if not habit:
        print(json.dumps({"status": "error", "message": f"Habit not found: {args.habit}"}))
        sys.exit(1)

    if args.name:
        habit["name"] = args.name
    if args.time:
        habit["time"] = args.time
    if args.days:
        habit["days"] = [d.strip().lower()[:3] for d in args.days.split(",")]

    habit["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_json(HABITS_FILE, data)
    print(json.dumps({"status": "updated", "habit": habit}))


# --- PAUSE / RESUME ---

def cmd_pause(args):
    data = load_json(HABITS_FILE, {"habits": []})
    habit = find_habit(data["habits"], args.habit)
    if not habit:
        print(json.dumps({"status": "error", "message": f"Habit not found: {args.habit}"}))
        sys.exit(1)

    habit["paused"] = True
    habit["paused_at"] = datetime.now(timezone.utc).isoformat()
    save_json(HABITS_FILE, data)
    print(json.dumps({"status": "paused", "habit": habit}))


def cmd_resume(args):
    data = load_json(HABITS_FILE, {"habits": []})
    habit = find_habit(data["habits"], args.habit)
    if not habit:
        print(json.dumps({"status": "error", "message": f"Habit not found: {args.habit}"}))
        sys.exit(1)

    habit["paused"] = False
    habit.pop("paused_at", None)
    save_json(HABITS_FILE, data)
    print(json.dumps({"status": "resumed", "habit": habit}))


# --- DELETE ---

def cmd_delete(args):
    data = load_json(HABITS_FILE, {"habits": []})
    habit = find_habit(data["habits"], args.habit)
    if not habit:
        print(json.dumps({"status": "error", "message": f"Habit not found: {args.habit}"}))
        sys.exit(1)

    data["habits"] = [h for h in data["habits"] if h["id"] != habit["id"]]
    save_json(HABITS_FILE, data)

    # Clean up streaks
    streaks = load_json(STREAKS_FILE, {"streaks": {}})
    streaks["streaks"].pop(habit["id"], None)
    save_json(STREAKS_FILE, streaks)

    print(json.dumps({"status": "deleted", "habit": habit}))


# --- HELPERS ---

def find_habit(habits, query):
    """Find a habit by ID prefix or name (case-insensitive partial match)."""
    query_lower = query.lower().strip()

    # Exact ID match
    for h in habits:
        if h["id"] == query_lower:
            return h

    # ID prefix match
    for h in habits:
        if h["id"].startswith(query_lower):
            return h

    # Exact name match
    for h in habits:
        if h["name"].lower() == query_lower:
            return h

    # Partial name match
    for h in habits:
        if query_lower in h["name"].lower():
            return h

    return None


def update_streak(habit_id, all_logs):
    """Recalculate streak from logs."""
    habit_logs = sorted(
        [l for l in all_logs if l["habit_id"] == habit_id],
        key=lambda x: x["date"],
        reverse=True
    )

    current = 0
    longest = 0
    longest_start = None
    longest_end = None
    last_completed = None

    # Calculate current streak (consecutive done days ending today or yesterday)
    today = datetime.now(timezone.utc).date()
    check_date = today

    for _i in range(len(habit_logs) + 2):
        date_str = check_date.strftime("%Y-%m-%d")
        log = next((l for l in habit_logs if l["date"] == date_str), None)

        if log and log["status"] == "done":
            current += 1
            if last_completed is None:
                last_completed = date_str
        elif log and log["status"] == "skip":
            # Skips don't break streaks but don't count
            pass
        elif check_date == today:
            # Today not logged yet - that's ok, don't break streak
            pass
        else:
            break

        check_date -= timedelta(days=1)

    # Calculate longest streak from all logs
    done_dates = sorted(set(
        l["date"] for l in habit_logs if l["status"] == "done"
    ))

    if done_dates:
        run_start = done_dates[0]
        run_length = 1

        for i in range(1, len(done_dates)):
            prev = datetime.strptime(done_dates[i - 1], "%Y-%m-%d").date()
            curr = datetime.strptime(done_dates[i], "%Y-%m-%d").date()

            if (curr - prev).days == 1:
                run_length += 1
            else:
                if run_length > longest:
                    longest = run_length
                    longest_start = run_start
                    longest_end = done_dates[i - 1]
                run_start = done_dates[i]
                run_length = 1

        if run_length > longest:
            longest = run_length
            longest_start = run_start
            longest_end = done_dates[-1]

    if current > longest:
        longest = current

    return {
        "current": current,
        "longest": longest,
        "longest_start": longest_start,
        "longest_end": longest_end,
        "last_completed": last_completed,
    }


def compute_rate(habit_logs, today, days):
    """Completion rate for the last N days."""
    cutoff = today - timedelta(days=days)
    relevant = [l for l in habit_logs
                if datetime.strptime(l["date"], "%Y-%m-%d").date() > cutoff]
    done = sum(1 for l in relevant if l["status"] == "done")
    total = len(relevant) if relevant else 0
    rate = round(done / total * 100, 1) if total > 0 else 0
    return {"done": done, "total": total, "rate": rate}


def compute_day_of_week_stats(habit_logs):
    """Completion rate by day of week."""
    days = {i: {"done": 0, "total": 0} for i in range(7)}
    for l in habit_logs:
        d = datetime.strptime(l["date"], "%Y-%m-%d").date()
        dow = d.weekday()
        days[dow]["total"] += 1
        if l["status"] == "done":
            days[dow]["done"] += 1

    names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    result = {}
    for i, name in enumerate(names):
        t = days[i]["total"]
        d = days[i]["done"]
        result[name] = {
            "done": d,
            "total": t,
            "rate": round(d / t * 100, 1) if t > 0 else 0,
        }
    return result


def build_calendar(habit_logs, today, days):
    """Build a calendar grid for the last N days."""
    log_map = {l["date"]: l["status"] for l in habit_logs}
    calendar = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        date_str = d.strftime("%Y-%m-%d")
        calendar.append({
            "date": date_str,
            "dow": d.strftime("%a")[:3],
            "status": log_map.get(date_str, "none"),
        })
    return calendar


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="HabitChat Tracker")
    sub = parser.add_subparsers(dest="command")

    # init
    sub.add_parser("init")

    # add
    p_add = sub.add_parser("add")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--time", default="09:00")
    p_add.add_argument("--days", default=None)

    # log
    p_log = sub.add_parser("log")
    p_log.add_argument("--habit", required=True)
    p_log.add_argument("--status", required=True, choices=["done", "skip", "miss"])
    p_log.add_argument("--date", default=None)

    # list
    sub.add_parser("list")

    # stats
    p_stats = sub.add_parser("stats")
    p_stats.add_argument("--habit", required=True)
    p_stats.add_argument("--days", default="30")

    # overview
    sub.add_parser("overview")

    # edit
    p_edit = sub.add_parser("edit")
    p_edit.add_argument("--habit", required=True)
    p_edit.add_argument("--name", default=None)
    p_edit.add_argument("--time", default=None)
    p_edit.add_argument("--days", default=None)

    # pause
    p_pause = sub.add_parser("pause")
    p_pause.add_argument("--habit", required=True)

    # resume
    p_resume = sub.add_parser("resume")
    p_resume.add_argument("--habit", required=True)

    # delete
    p_delete = sub.add_parser("delete")
    p_delete.add_argument("--habit", required=True)

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "add": cmd_add,
        "log": cmd_log,
        "list": cmd_list,
        "stats": cmd_stats,
        "overview": cmd_overview,
        "edit": cmd_edit,
        "pause": cmd_pause,
        "resume": cmd_resume,
        "delete": cmd_delete,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
