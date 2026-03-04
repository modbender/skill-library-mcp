#!/usr/bin/env python3
"""
Waste Reminder - Main Script
Token-efficient reminder system for waste container collection.
Uses single schedule.json file with multi-channel support.
"""

import json
import os
import sys
from datetime import datetime, timedelta

SKILL_DIR = "/data/.openclaw/workspace/data/waste-reminder"
CONFIG_FILE = os.path.join(SKILL_DIR, "config.json")
SCHEDULE_FILE = os.path.join(SKILL_DIR, "schedule.json")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    os.makedirs(SKILL_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_schedule():
    if not os.path.exists(SCHEDULE_FILE):
        return {}
    with open(SCHEDULE_FILE, 'r') as f:
        return json.load(f)

def save_schedule(schedule):
    os.makedirs(SKILL_DIR, exist_ok=True)
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(schedule, f, indent=2)

def confirm_container(container, date, confirmed_by=None):
    """Confirm a container has been put outside."""
    schedule = load_schedule()
    
    if date not in schedule or container not in schedule[date]:
        return f"No pickup scheduled for {container} on {date}"
    
    schedule[date][container]["confirmed"] = True
    schedule[date][container]["confirmedBy"] = confirmed_by or "user"
    schedule[date][container]["confirmedAt"] = datetime.now().isoformat()
    
    save_schedule(schedule)
    
    config = load_config()
    container_info = config.get("containers", {}).get(container, {})
    container_name = container_info.get("name", container)
    
    return f"✅ Confirmed: {container_name} on {date}"

def add_pickup(container, date):
    """Add a new pickup date."""
    schedule = load_schedule()
    
    if date not in schedule:
        schedule[date] = {}
    
    if container in schedule[date]:
        return f"Pickup already scheduled for {container} on {date}"
    
    schedule[date][container] = {
        "confirmed": False,
        "addedAt": datetime.now().isoformat()
    }
    
    save_schedule(schedule)
    
    config = load_config()
    container_info = config.get("containers", {}).get(container, {})
    container_name = container_info.get("name", container)
    
    return f"✅ Added: {container_name} pickup on {date}"

def remove_pickup(container, date):
    """Remove a pickup date."""
    schedule = load_schedule()
    
    if date not in schedule or container not in schedule[date]:
        return f"No pickup scheduled for {container} on {date}"
    
    del schedule[date][container]
    if not schedule[date]:
        del schedule[date]
    
    save_schedule(schedule)
    
    return f"✅ Removed pickup for {container} on {date}"

def list_schedule(upcoming_days=30):
    """List upcoming pickups."""
    config = load_config()
    if not config:
        return "No config found."
    
    schedule = load_schedule()
    today = datetime.now().strftime("%Y-%m-%d")
    upcoming = []
    
    sorted_dates = sorted(schedule.keys())
    
    for date in sorted_dates:
        if date < today:
            continue
        
        days_until = (datetime.strptime(date, "%Y-%m-%d") - datetime.now()).days
        if days_until > upcoming_days:
            break
        
        for container, status in schedule[date].items():
            if not status.get("confirmed", False):
                container_info = config.get("containers", {}).get(container, {})
                container_name = container_info.get("name", container)
                container_emoji = container_info.get("emoji", "🗑️")
                
                day_name = datetime.strptime(date, "%Y-%m-%d").strftime("%a")
                upcoming.append(f"{day_name} {date}: {container_emoji} {container_name}")
    
    if not upcoming:
        return "No upcoming pickups scheduled."
    
    return "📅 Upcoming pickups:\n" + "\n".join(upcoming)

def show_status():
    """Show current status of all pending reminders."""
    config = load_config()
    if not config:
        return "No config found."
    
    schedule = load_schedule()
    today = datetime.now().strftime("%Y-%m-%d")
    status_lines = ["📋 Pending reminders:"]
    
    sorted_dates = sorted(schedule.keys())
    
    for date in sorted_dates:
        if date < today:
            continue
        
        for container, stat in schedule[date].items():
            if not stat.get("confirmed", False):
                container_info = config.get("containers", {}).get(container, {})
                container_name = container_info.get("name", container)
                container_emoji = container_info.get("emoji", "🗑️")
                
                reminders = []
                for key, value in stat.items():
                    if key.startswith("reminded_") and value:
                        time = key.replace("reminded_", "")
                        reminders.append(time)
                
                reminder_text = ", ".join(reminders) if reminders else "no reminders yet"
                status_lines.append(f"  {date}: {container_emoji} {container_name} [{reminder_text}]")
    
    return "\n".join(status_lines) if len(status_lines) > 1 else "No pending reminders"

# CLI Interface
if __name__ == "__main__":
    argv = [a for a in sys.argv if not a.startswith('-')]
    
    if len(argv) < 2:
        print("Waste Reminder CLI")
        print("")
        print("Commands:")
        print("  confirm <container> <date> [name]   - Confirm container is out")
        print("  add <container> <date>            - Add pickup date")
        print("  remove <container> <date>          - Remove pickup date")
        print("  schedule                         - Show upcoming pickups")
        print("  status                           - Show pending reminders")
        sys.exit(1)
    
    cmd = argv[1]
    
    try:
        if cmd == "confirm":
            if len(argv) < 4:
                print("Usage: waste_reminder.py confirm <container> <date> [name]")
                sys.exit(1)
            container, date, name = argv[2], argv[3], argv[4] if len(argv) == 5 else None
            print(confirm_container(container, date, name))
        
        elif cmd == "add":
            if len(argv) != 4:
                print("Usage: waste_reminder.py add <container> <date>")
                sys.exit(1)
            container, date = argv[2], argv[3]
            print(add_pickup(container, date))
        
        elif cmd == "remove":
            if len(argv) != 4:
                print("Usage: waste_reminder.py remove <container> <date>")
                sys.exit(1)
            container, date = argv[2], argv[3]
            print(remove_pickup(container, date))
        
        elif cmd == "schedule":
            print(list_schedule())
        
        elif cmd == "status":
            print(show_status())
        
        else:
            print(f"Unknown command: {cmd}")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
