#!/usr/bin/env python3
"""
HabitChat AI Coach - Analyzes patterns and generates coaching insights.
No external dependencies - stdlib only.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA_DIR = Path.home() / ".habitchat"
HABITS_FILE = DATA_DIR / "habits.json"
LOGS_FILE = DATA_DIR / "logs.json"
STREAKS_FILE = DATA_DIR / "streaks.json"


def load_json(path, default=None):
    if default is None:
        default = {}
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


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


# --- INSIGHTS ---

def cmd_insights(args):
    habits_data = load_json(HABITS_FILE, {"habits": []})
    logs_data = load_json(LOGS_FILE, {"logs": []})
    streaks_data = load_json(STREAKS_FILE, {"streaks": {}})

    today = datetime.now(timezone.utc).date()
    insights = []

    for habit in habits_data["habits"]:
        if not habit.get("active", True) or habit.get("paused", False):
            continue

        hid = habit["id"]
        h_logs = [l for l in logs_data["logs"] if l["habit_id"] == hid]
        streak = streaks_data.get("streaks", {}).get(hid, {})

        # 1. Streak at risk
        current = streak.get("current", 0)
        last_done = streak.get("last_completed")
        if current >= 3 and last_done:
            last_date = datetime.strptime(last_done, "%Y-%m-%d").date()
            gap = (today - last_date).days
            if gap >= 1:
                insights.append({
                    "type": "streak_at_risk",
                    "habit": habit["name"],
                    "streak": current,
                    "days_since_last": gap,
                    "message": f"Your {current}-day streak for '{habit['name']}' is at risk! Last logged {gap} day(s) ago.",
                    "priority": "high",
                })

        # 2. Milestone approaching
        for milestone in [7, 14, 21, 30, 50, 100, 200, 365]:
            if current < milestone <= current + 3:
                remaining = milestone - current
                insights.append({
                    "type": "milestone_approaching",
                    "habit": habit["name"],
                    "current_streak": current,
                    "target": milestone,
                    "remaining": remaining,
                    "message": f"'{habit['name']}' is {remaining} day(s) away from a {milestone}-day streak!",
                    "priority": "medium",
                })
                break

        # 3. Declining trend (compare last 7 days vs previous 7 days)
        recent_7 = [l for l in h_logs
                    if 0 <= (today - datetime.strptime(l["date"], "%Y-%m-%d").date()).days < 7]
        prev_7 = [l for l in h_logs
                  if 7 <= (today - datetime.strptime(l["date"], "%Y-%m-%d").date()).days < 14]

        recent_rate = (sum(1 for l in recent_7 if l["status"] == "done") / max(len(recent_7), 1)) * 100
        prev_rate = (sum(1 for l in prev_7 if l["status"] == "done") / max(len(prev_7), 1)) * 100

        if prev_rate > 0 and recent_rate < prev_rate - 20:
            insights.append({
                "type": "declining_trend",
                "habit": habit["name"],
                "recent_rate": round(recent_rate, 1),
                "previous_rate": round(prev_rate, 1),
                "message": f"'{habit['name']}' completion dropped from {round(prev_rate)}% to {round(recent_rate)}% this week.",
                "priority": "medium",
            })

        # 4. Weak days pattern
        dow_counts = {i: {"done": 0, "total": 0} for i in range(7)}
        for l in h_logs:
            d = datetime.strptime(l["date"], "%Y-%m-%d").date()
            dow = d.weekday()
            dow_counts[dow]["total"] += 1
            if l["status"] == "done":
                dow_counts[dow]["done"] += 1

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weak_days = []
        for i, name in enumerate(day_names):
            t = dow_counts[i]["total"]
            if t >= 3:
                rate = dow_counts[i]["done"] / t * 100
                if rate < 50:
                    weak_days.append({"day": name, "rate": round(rate, 1)})

        if weak_days:
            day_list = ", ".join(d["day"] for d in weak_days)
            insights.append({
                "type": "weak_days",
                "habit": habit["name"],
                "days": weak_days,
                "message": f"'{habit['name']}' tends to slip on {day_list}. Consider adjusting your routine for those days.",
                "priority": "low",
            })

        # 5. Consistency champion
        if current >= 14:
            insights.append({
                "type": "consistency_champion",
                "habit": habit["name"],
                "streak": current,
                "message": f"Incredible consistency on '{habit['name']}'! {current} days and counting.",
                "priority": "positive",
            })

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "positive": 2, "low": 3}
    insights.sort(key=lambda x: priority_order.get(x["priority"], 99))

    print(json.dumps({"status": "ok", "insights": insights, "date": str(today)}))


# --- MOTIVATE ---

def cmd_motivate(args):
    habits_data = load_json(HABITS_FILE, {"habits": []})
    logs_data = load_json(LOGS_FILE, {"logs": []})
    streaks_data = load_json(STREAKS_FILE, {"streaks": {}})

    habit = find_habit(habits_data["habits"], args.habit)
    if not habit:
        print(json.dumps({"status": "error", "message": f"Habit not found: {args.habit}"}))
        sys.exit(1)

    hid = habit["id"]
    streak = streaks_data.get("streaks", {}).get(hid, {})
    current = streak.get("current", 0)
    longest = streak.get("longest", 0)

    h_logs = [l for l in logs_data["logs"] if l["habit_id"] == hid]
    today = datetime.now(timezone.utc).date()

    recent_7 = [l for l in h_logs
                if 0 <= (today - datetime.strptime(l["date"], "%Y-%m-%d").date()).days < 7]
    week_rate = round(
        sum(1 for l in recent_7 if l["status"] == "done") / max(len(recent_7), 1) * 100, 1
    )

    # Build motivation context
    context = {
        "habit_name": habit["name"],
        "current_streak": current,
        "longest_streak": longest,
        "week_completion_rate": week_rate,
        "total_completions": sum(1 for l in h_logs if l["status"] == "done"),
        "days_tracked": len(set(l["date"] for l in h_logs)),
    }

    # Determine motivation type
    if current == 0:
        context["motivation_type"] = "fresh_start"
        context["suggestion"] = "Start small. Even 1 minute counts. The hardest part is showing up."
    elif current < 7:
        context["motivation_type"] = "building_momentum"
        context["suggestion"] = "You're building the foundation. Each day makes the next one easier."
    elif current < 21:
        context["motivation_type"] = "habit_forming"
        context["suggestion"] = "Research shows habits solidify around 21 days. You're in the critical zone."
    elif current < longest:
        remaining = longest - current
        context["motivation_type"] = "chasing_record"
        context["suggestion"] = f"You're {remaining} days from beating your personal best of {longest} days!"
    else:
        context["motivation_type"] = "record_holder"
        context["suggestion"] = "You're in uncharted territory - every day is a new personal record!"

    # Identify friction points
    if week_rate < 70:
        context["friction"] = "This week's been tough. What's getting in the way? Maybe adjust the time or make it easier."
    elif week_rate < 100:
        context["friction"] = "Almost perfect week! One small tweak could make it consistent."

    print(json.dumps({"status": "ok", "motivation": context}))


# --- ANALYZE ---

def cmd_analyze(args):
    habits_data = load_json(HABITS_FILE, {"habits": []})
    logs_data = load_json(LOGS_FILE, {"logs": []})
    streaks_data = load_json(STREAKS_FILE, {"streaks": {}})

    today = datetime.now(timezone.utc).date()
    days = int(args.days) if args.days else 30
    cutoff = today - timedelta(days=days)

    analysis = {
        "period": f"Last {days} days",
        "habits": [],
        "overall": {},
        "recommendations": [],
    }

    total_done = 0
    total_possible = 0

    for habit in habits_data["habits"]:
        if not habit.get("active", True):
            continue

        hid = habit["id"]
        h_logs = [l for l in logs_data["logs"]
                  if l["habit_id"] == hid
                  and datetime.strptime(l["date"], "%Y-%m-%d").date() > cutoff]

        done = sum(1 for l in h_logs if l["status"] == "done")
        skip = sum(1 for l in h_logs if l["status"] == "skip")
        miss = sum(1 for l in h_logs if l["status"] == "miss")
        total = done + skip + miss
        rate = round(done / total * 100, 1) if total > 0 else 0

        total_done += done
        total_possible += total

        streak = streaks_data.get("streaks", {}).get(hid, {})

        # Trend: compare first half vs second half of period
        mid = cutoff + timedelta(days=days // 2)
        first_half = [l for l in h_logs
                      if datetime.strptime(l["date"], "%Y-%m-%d").date() <= mid]
        second_half = [l for l in h_logs
                       if datetime.strptime(l["date"], "%Y-%m-%d").date() > mid]

        first_rate = (sum(1 for l in first_half if l["status"] == "done")
                      / max(len(first_half), 1) * 100)
        second_rate = (sum(1 for l in second_half if l["status"] == "done")
                       / max(len(second_half), 1) * 100)

        if second_rate > first_rate + 10:
            trend = "improving"
        elif second_rate < first_rate - 10:
            trend = "declining"
        else:
            trend = "stable"

        analysis["habits"].append({
            "name": habit["name"],
            "completion_rate": rate,
            "done": done,
            "skipped": skip,
            "missed": miss,
            "current_streak": streak.get("current", 0),
            "longest_streak": streak.get("longest", 0),
            "trend": trend,
        })

    # Overall stats
    overall_rate = round(total_done / max(total_possible, 1) * 100, 1)
    analysis["overall"] = {
        "completion_rate": overall_rate,
        "total_completions": total_done,
        "total_tracked": total_possible,
        "active_habits": len(analysis["habits"]),
    }

    # Generate recommendations
    for h in analysis["habits"]:
        if h["completion_rate"] < 30:
            analysis["recommendations"].append({
                "habit": h["name"],
                "type": "consider_removing",
                "message": f"'{h['name']}' has a very low completion rate ({h['completion_rate']}%). Consider making it easier, changing the time, or removing it if it no longer serves you.",
            })
        elif h["trend"] == "declining":
            analysis["recommendations"].append({
                "habit": h["name"],
                "type": "needs_attention",
                "message": f"'{h['name']}' is trending downward. Try habit stacking (pair it with something you already do) or reduce the commitment size.",
            })
        elif h["completion_rate"] > 90 and h["current_streak"] >= 21:
            analysis["recommendations"].append({
                "habit": h["name"],
                "type": "level_up",
                "message": f"'{h['name']}' is solid at {h['completion_rate']}%! Ready to level up? Increase duration, add intensity, or stack a new habit on top.",
            })

    if overall_rate > 80:
        analysis["recommendations"].append({
            "type": "general",
            "message": "Your overall consistency is excellent! You might be ready to add a new habit.",
        })
    elif overall_rate < 50:
        analysis["recommendations"].append({
            "type": "general",
            "message": "Focus on fewer habits. Drop the ones with the lowest rates and master 1-2 before adding more. Less is more.",
        })

    print(json.dumps({"status": "ok", "analysis": analysis}))


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="HabitChat Coach")
    sub = parser.add_subparsers(dest="command")

    # insights
    p_insights = sub.add_parser("insights")
    p_insights.add_argument("--user-data", default=str(DATA_DIR))

    # motivate
    p_motivate = sub.add_parser("motivate")
    p_motivate.add_argument("--habit", required=True)

    # analyze
    p_analyze = sub.add_parser("analyze")
    p_analyze.add_argument("--days", default="30")

    args = parser.parse_args()

    commands = {
        "insights": cmd_insights,
        "motivate": cmd_motivate,
        "analyze": cmd_analyze,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
