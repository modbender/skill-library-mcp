#!/usr/bin/env python3
"""
Waste Reminder - Cron Runner
Checks every 15 minutes if any reminders need to be sent.
Uses single schedule.json file with multi-channel support.
"""

import json
import os
from datetime import datetime, timedelta

SKILL_DIR = "/data/.openclaw/workspace/data/waste-reminder"
CONFIG_FILE = os.path.join(SKILL_DIR, "config.json")
SCHEDULE_FILE = os.path.join(SKILL_DIR, "schedule.json")

def load_config():
    """Load configuration from JSON file."""
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def load_schedule():
    """Load schedule from single JSON file."""
    if not os.path.exists(SCHEDULE_FILE):
        return {}
    with open(SCHEDULE_FILE, 'r') as f:
        return json.load(f)

def save_schedule(schedule):
    """Save schedule to single JSON file."""
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(schedule, f, indent=2)

def get_target_info(targets, key):
    """Get target info, handling both old string format and new object format."""
    target = targets.get(key, {})
    
    # Old format: "key": "value" (string)
    if isinstance(target, str):
        return {"id": target, "channel": "whatsapp"}
    
    # New format: "key": {"id": "...", "channel": "..."}
    return target

def check_reminders():
    """
    Check if any reminders need to be sent now.
    Returns list of dicts with recipient, message, channel, container, date.
    """
    config = load_config()
    if not config:
        return []
    
    schedule = load_schedule()
    
    # Get current time
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%Y-%m-%d")
    
    # Get reminder times from config
    reminder_times = config.get("reminder_times", {})
    targets = config.get("targets", {})
    
    reminders_to_send = []
    
    # Check each date in schedule
    for date, containers in schedule.items():
        # Skip past dates
        if date < current_date:
            continue
        
        for container, status in containers.items():
            # Skip if already confirmed
            if status.get("confirmed", False):
                continue
            
            # Get container info
            container_info = config.get("containers", {}).get(container, {})
            
            # Check each reminder time
            for time_slot, reminder_config in reminder_times.items():
                # Check if it's time for this reminder
                if time_slot != current_time:
                    continue
                
                # Check if already reminded at this time
                reminder_key = f"reminded_{time_slot}"
                if status.get(reminder_key, False):
                    continue
                
                # Build message
                template = reminder_config.get("template", "Reminder: {container_name}")
                container_emoji = container_info.get("emoji", "🗑️")
                container_name = container_info.get("name", container)
                
                message = template.replace("{container_emoji}", container_emoji)
                message = message.replace("{container_name}", container_name)
                message = message.replace("{date}", date)
                
                # Get recipient info
                target_key = reminder_config.get("target", "group_whatsapp")
                
                # Target name now includes channel (e.g., group_whatsapp, me_telegram)
                # Extract channel from target name if not specified in reminder_config
                target_info = get_target_info(targets, target_key)
                recipient_id = target_info.get("id")
                
                # Use channel from target info, or try to extract from target name
                channel = target_info.get("channel")
                if not channel:
                    # Extract channel from target key (e.g., group_whatsapp -> whatsapp)
                    if "_" in target_key:
                        channel = target_key.split("_")[-1]
                    else:
                        channel = "whatsapp"
                
                if recipient_id:
                    reminders_to_send.append({
                        "recipient": recipient_id,
                        "channel": channel,
                        "message": message,
                        "container": container,
                        "date": date,
                        "time_slot": time_slot
                    })
    
    return reminders_to_send

def mark_reminded(container, date, time_slot):
    """Mark that a reminder was sent."""
    schedule = load_schedule()
    
    if date in schedule and container in schedule[date]:
        reminder_key = f"reminded_{time_slot}"
        schedule[date][container][reminder_key] = True
        save_schedule(schedule)

if __name__ == "__main__":
    reminders = check_reminders()
    
    if reminders:
        print(f"FOUND: {len(reminders)} reminder(s)")
        
        for r in reminders:
            # Mark as reminded first
            mark_reminded(r["container"], r["date"], r["time_slot"])
            
            # Output for automation
            print(f"SEND_TO:{r['recipient']}")
            print(f"CHANNEL:{r['channel']}")
            print(r["message"])
            print("---")
    else:
        print("NO_REMINDERS")
