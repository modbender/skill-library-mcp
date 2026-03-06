#!/usr/bin/env python3
"""Water Coach CLI - Unified command interface.

Usage:
    python3 water_coach.py <namespace> <command> [options]
    
Namespaces:
    water   - Water tracking commands
    body    - Body metrics commands  
    analytics - Reports and briefings
    
Examples:
    python3 water_coach.py water status
    python3 water_coach.py water log 500
    python3 water_coach.py body log --weight=80
    python3 water_coach.py analytics week
    python3 water_coach.py analytics month
"""
import json
import sys
from pathlib import Path

# ============================================================================
# SETUP
# ============================================================================

SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

# Import all modules
from water import (
    get_today_status,
    log_water,
    should_send_extra_notification,
    get_dynamic_threshold,
    increment_extra_notifications,
    reset_daily_counters,
    get_daily_goal,
    load_config,
    is_user_setup,
    update_user_weight,
    calculate_expected_percent,
    get_week_stats,
    log_body_metrics,
    get_latest_body_metrics,
    get_body_metrics_history,
    get_entry_by_message_id,
    get_entries_by_date,
    calculate_cumulative_for_date,
    get_current_message_id,
    get_message_context
)

# ============================================================================
# ANALYTICS MODULE
# ============================================================================

def analytics_week():
    """Get weekly analytics."""
    stats = get_week_stats(7)
    
    # Calculate summary
    total_days = len(stats.get("days", []))
    if total_days == 0:
        return {"summary": "No data this week"}
    
    avg_daily = stats["total_ml"] // total_days
    goal_hits = stats["goal_hits"]
    
    # Build message with table format
    message = f"📊 **Weekly Water Report**\n\n"
    message += f"**This Week:**\n"
    message += f"- Total: {stats['total_ml']}ml\n"
    message += f"- Average: {avg_daily}ml/day\n"
    message += f"- Goal hits: {goal_hits}/{total_days} days\n\n"
    
    message += f"**Daily Breakdown:**\n"
    message += f"| Dia | ML | % | Status |\n"
    message += f"| -----|-----|-----|-------- |\n"
    
    # Portuguese day names (Python weekday: Mon=0, Sun=6)
    day_names = {"0": "Seg", "1": "Ter", "2": "Qua", "3": "Qui", "4": "Sex", "5": "Sáb", "6": "Dom"}
    import datetime as dt
    
    for day in stats.get("days", []):
        pct = day.get("percentage", 0)
        ml = day.get("ml", 0)
        date_str = day.get("date", "")
        
        # Get day name
        try:
            d = dt.datetime.strptime(date_str, "%Y-%m-%d")
            day_name = day_names.get(str(d.weekday()), date_str)
            date_display = f"{day_name} {d.day}"
        except:
            date_display = date_str
        
        emoji = "✅" if pct >= 100 else "⚠️" if pct >= 50 else "❌"
        message += f"| {date_display} | {ml}ml | {pct:.1f}% | {emoji} |\n"
    
    return {"message": message, "stats": stats}

def analytics_month():
    """Get monthly analytics."""
    stats = get_week_stats(30)
    
    total_days = len(stats.get("days", []))
    if total_days == 0:
        return {"summary": "No data this month"}
    
    avg_daily = stats["total_ml"] // total_days
    goal_hits = stats["goal_hits"]
    
    # Calculate trend (compare last week to previous week)
    last_week = stats["days"][:7] if len(stats["days"]) >= 7 else stats["days"]
    prev_week = stats["days"][7:14] if len(stats["days"]) >= 14 else []
    
    last_week_avg = sum(d["ml"] for d in last_week) // max(1, len(last_week))
    prev_week_avg = sum(d["ml"] for d in prev_week) // max(1, len(prev_week))
    
    trend = "📈 Improving" if last_week_avg > prev_week_avg else "📉 Declining" if last_week_avg < prev_week_avg else "➡️ Stable"
    
    message = f"📊 **Monthly Water Report**\n\n"
    message += f"**This Month:**\n"
    message += f"- Total: {stats['total_ml']}ml\n"
    message += f"- Average: {avg_daily}ml/day\n"
    message += f"- Goal hits: {goal_hits}/{total_days} days\n"
    message += f"- Trend: {trend}\n\n"
    
    message += f"**Recent Days:**\n"
    for day in stats["days"][:7]:
        pct = day.get("percentage", 0)
        ml = day.get("ml", 0)
        emoji = "✅" if pct >= 100 else "⚠️" if pct >= 50 else "❌"
        message += f"{emoji} {day['date']}: {ml}ml ({pct}%)\n"
    
    return {"message": message, "stats": stats}

# ============================================================================
# CLI DISPATCHER
# ============================================================================

def print_help():
    print(__doc__)

def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    namespace = sys.argv[1] if len(sys.argv) > 1 else None
    command = sys.argv[2] if len(sys.argv) > 2 else None
    args = sys.argv[3:] if len(sys.argv) > 3 else []
    
    # Water namespace
    if namespace == "water":
        if command == "status":
            print(json.dumps(get_today_status()))
        elif command == "log":
            if not args:
                print(json.dumps({"error": "Usage: water log <ml> [--drank-at=ISO] [--message-id=MSG]"}))
            else:
                amount = int(args[0])
                drank_at = None
                message_id = None  # Will auto-fill from session
                for arg in args[1:]:
                    if arg.startswith("--drank-at="):
                        drank_at = arg.split("=")[1]
                    elif arg.startswith("--message-id="):
                        message_id = arg.split("=")[1]
                # Auto-fill message_id if not provided
                if not message_id:
                    message_id = get_current_message_id()
                print(json.dumps(log_water(amount, drank_at=drank_at, message_id=message_id or "")))
        elif command == "dynamic":
            print(json.dumps(should_send_extra_notification()))
        elif command == "threshold":
            print(json.dumps(get_dynamic_threshold()))
        elif command == "setup":
            print(json.dumps(is_user_setup()))
        elif command == "increment":
            print(json.dumps(increment_extra_notifications()))
        elif command == "reset":
            print(json.dumps(reset_daily_counters()))
        elif command == "goal":
            print(json.dumps({"goal_ml": get_daily_goal()}))
        elif command == "set_body_weight":
            if not args:
                print(json.dumps({"error": "Usage: water set_body_weight <kg> [--update-goal]"}))
            else:
                weight = float(args[0])
                update_goal = "--update-goal" in args
                print(json.dumps(update_user_weight(weight, update_goal)))
        elif command == "audit":
            # Get entry by message_id with optional context
            msg_id = args[0] if args else ""
            if not msg_id:
                print(json.dumps({"error": "Usage: water audit <message_id>"}))
            else:
                # Get water entry
                entry = get_entry_by_message_id(msg_id)
                
                # Get message context only if auto-capture is enabled
                config = load_config()
                context = None
                if config.get("settings", {}).get("audit_auto_capture", False):
                    context = get_message_context(msg_id)
                else:
                    context = {"warning": "Message context disabled. Set audit_auto_capture=true in config to enable."}
                
                result = {
                    "entry": entry,
                    "context": context
                }
                print(json.dumps(result, indent=2))
        else:
            print(json.dumps({"error": f"Unknown water command: {command}"}))
    
    # Body namespace
    elif namespace == "body":
        if command == "log":
            kwargs = {}
            for arg in args:
                if arg.startswith("--weight="):
                    kwargs["weight_kg"] = float(arg.split("=")[1])
                elif arg.startswith("--height="):
                    kwargs["height_m"] = float(arg.split("=")[1])
                elif arg.startswith("--body-fat="):
                    kwargs["body_fat_pct"] = float(arg.split("=")[1])
                elif arg.startswith("--muscle="):
                    kwargs["muscle_pct"] = float(arg.split("=")[1])
                elif arg.startswith("--water="):
                    kwargs["water_pct"] = float(arg.split("=")[1])
            print(json.dumps(log_body_metrics(**kwargs)))
        elif command == "latest":
            print(json.dumps(get_latest_body_metrics()))
        elif command == "history":
            days = int(args[0]) if args else 30
            print(json.dumps(get_body_metrics_history(days)))
        else:
            print(json.dumps({"error": f"Unknown body command: {command}"}))
    
    # Analytics namespace
    elif namespace == "analytics":
        if command == "week":
            print(json.dumps(analytics_week()))
        elif command == "month":
            print(json.dumps(analytics_month()))
        else:
            print(json.dumps({"error": f"Unknown analytics command: {command}"}))
    
    # Help
    elif namespace in ["--help", "-h", "help"]:
        print_help()
    
    else:
        print(json.dumps({"error": f"Unknown namespace: {namespace}"}))

if __name__ == "__main__":
    main()
