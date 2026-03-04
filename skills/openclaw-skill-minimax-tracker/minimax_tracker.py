#!/usr/bin/env python3
"""
MiniMax Usage Tracker
- Track API usage in real-time
- Calculate reset time based on rules
- Display progress bar status
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Config
CONFIG = {
    "max_prompts": 40,           # 40 prompts per month
    "reset_hour_start": 15,       # 15:00 UTC+8
    "reset_hour_end": 20,        # 20:00 UTC+8
    "check_interval_hours": 3,    # Check every 3 hours
}

DATA_FILE = os.path.expanduser("~/.openclaw/workspace/minimax_usage_data.json")

def load_data():
    """Load usage data from file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        "usage_records": [],
        "current_usage": 0,
        "last_reset": None,
        "last_check": None
    }

def save_data(data):
    """Save usage data to file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_next_reset_time():
    """Calculate next reset time"""
    now = datetime.now()
    
    # Reset time is between 15:00-20:00 UTC+8
    # For simplicity, use 18:00 as average reset time
    reset_hour = 18
    reset_minute = 0
    
    today_reset = now.replace(hour=reset_hour, minute=reset_minute, second=0, microsecond=0)
    
    if now < today_reset:
        return today_reset
    else:
        # Next day
        return today_reset + timedelta(days=1)

def time_until_reset():
    """Calculate time until next reset"""
    now = datetime.now()
    next_reset = get_next_reset_time()
    delta = next_reset - now
    
    hours = int(delta.total_seconds() // 3600)
    minutes = int((delta.total_seconds() % 3600) // 60)
    
    return f"{hours}h{minutes}m"

def format_progress_bar(percentage, length=20):
    """Format progress bar"""
    filled = int(length * percentage / 100)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}]"

def add_usage(prompts_used=1):
    """Record a new usage"""
    data = load_data()
    
    now = datetime.now().isoformat()
    data["usage_records"].append({
        "time": now,
        "prompts": prompts_used
    })
    
    data["current_usage"] += prompts_used
    data["last_check"] = now
    
    # Check if reset needed
    next_reset = get_next_reset_time()
    if data.get("last_reset"):
        last_reset = datetime.fromisoformat(data["last_reset"])
        if datetime.now() > last_reset + timedelta(hours=24):
            # More than 24h since last reset, auto reset
            data["current_usage"] = 0
            data["last_reset"] = next_reset.isoformat()
    else:
        data["last_reset"] = next_reset.isoformat()
    
    save_data(data)
    return data["current_usage"]

def get_status():
    """Get current status"""
    data = load_data()
    
    used = data.get("current_usage", 0)
    max_prompts = CONFIG["max_prompts"]
    remaining = max_prompts - used
    
    # Calculate percentage
    used_pct = min(100, (used / max_prompts) * 100)
    remaining_pct = 100 - used_pct
    
    # Time info
    next_reset = get_next_reset_time()
    time_left = time_until_reset()
    
    # Next reminder time (3 hours from now)
    next_reminder = datetime.now() + timedelta(hours=CONFIG["check_interval_hours"])
    
    return {
        "used": used,
        "remaining": remaining,
        "max": max_prompts,
        "used_pct": used_pct,
        "remaining_pct": remaining_pct,
        "reset_time": next_reset.strftime("%H:%M"),
        "time_left": time_left,
        "next_reminder": next_reminder.strftime("%H:%M"),
        "package": "Starter",
        "last_reset": data.get("last_reset", "N/A"),
    }

def display_status():
    """Display status in compact format"""
    status = get_status()
    
    # Compact single-line format
    bar = format_progress_bar(status["remaining_pct"])
    
    output = (
        f"📊 MiniMax Usage: {bar} {status['remaining_pct']:.0f}% "
        f"RST:{status['reset_time']} "
        f"TTL:{status['time_left']} "
        f"PKG:{status['package']} "
        f"USE:{status['used']}/{status['max']} "
        f"REM:{status['remaining']} "
        f"NXT:{status['next_reminder']}"
    )
    
    print(output)
    return output

def display_detailed():
    """Display detailed status"""
    status = get_status()
    
    print("=" * 60)
    print("📊 MiniMax Usage Status")
    print("=" * 60)
    print(f"Package: {status['package']} ({status['max']} prompts/month)")
    print(f"Used: {status['used']} prompts")
    print(f"Remaining: {status['remaining']} prompts")
    print(f"Progress: {format_progress_bar(status['remaining_pct'])} {status['remaining_pct']:.1f}%")
    print(f"Reset Time: {status['reset_time']} (UTC+8)")
    print(f"Time Until Reset: {status['time_left']}")
    print(f"Next Reminder: {status['next_reminder']}")
    print("=" * 60)
    
    return status

# Command line interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "add":
            # Add usage
            prompts = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            used = add_usage(prompts)
            print(f"Added {prompts} prompts. Total used: {used}")
            display_status()
        elif sys.argv[1] == "status":
            display_detailed()
        elif sys.argv[1] == "compact":
            display_status()
        else:
            print("Usage: minimax_tracker.py [add|status|compact]")
    else:
        display_status()
