#!/usr/bin/env python3
"""
Olympic Event Alert Script
Sends alerts 30 minutes before scheduled events.
Events are loaded from events.json in the same directory.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
EVENTS_FILE = SCRIPT_DIR / "events.json"
STATE_DIR = Path(os.path.expanduser("~/.config/olympic-alert"))
STATE_FILE = STATE_DIR / "state.json"

def load_events():
    """Load events from events.json"""
    if not EVENTS_FILE.exists():
        return {"country": "Unknown", "events": [], "links": {}}
    with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"notified": []}

def save_state(state):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def check_upcoming():
    data = load_events()
    events = data.get("events", [])
    links = data.get("links", {})
    country_flag = data.get("flag", "🏅")
    
    now = datetime.now()
    state = load_state()
    alerts = []
    
    for event in events:
        event_time_str = event["time"]
        event_name = event["name"]
        athletes = event.get("athletes", "")
        
        event_time = datetime.strptime(event_time_str, "%Y-%m-%d %H:%M")
        event_id = f"{event_time_str}_{event_name}"
        
        time_until = event_time - now
        minutes_until = time_until.total_seconds() / 60
        
        if 0 <= minutes_until <= 15 and event_id not in state["notified"]:
            mins = int(minutes_until)
            time_msg = "지금 시작!" if mins == 0 else f"{mins}분 후"
            
            alert = f"{country_flag} {time_msg}\n{event_name}"
            if athletes:
                alert += f"\n👤 {athletes}"
            
            # Add streaming links
            if links:
                link_parts = [f"[{name}]({url})" for name, url in links.items()]
                alert += f"\n\n📺 {' | '.join(link_parts)}"
            
            alerts.append(alert)
            state["notified"].append(event_id)
    
    if alerts:
        save_state(state)
    
    return alerts

def list_upcoming():
    """List upcoming events"""
    data = load_events()
    events = data.get("events", [])
    
    now = datetime.now()
    upcoming = []
    
    for event in events:
        event_time = datetime.strptime(event["time"], "%Y-%m-%d %H:%M")
        if event_time > now:
            time_until = event_time - now
            days = time_until.days
            hours = time_until.seconds // 3600
            
            if days > 0:
                time_str = f"D-{days}"
            elif hours > 0:
                time_str = f"{hours}시간 후"
            else:
                mins = time_until.seconds // 60
                time_str = f"{mins}분 후"
            
            line = f"• {event_time.strftime('%m/%d %H:%M')} {event['name']}"
            if event.get("athletes"):
                line += f" ({event['athletes']})"
            upcoming.append((event_time, line))
    
    upcoming.sort(key=lambda x: x[0])
    return [line for _, line in upcoming[:15]]

def add_event(time_str: str, name: str, athletes: str = ""):
    """Add a new event to events.json"""
    data = load_events()
    data["events"].append({
        "time": time_str,
        "name": name,
        "athletes": athletes
    })
    # Sort by time
    data["events"].sort(key=lambda x: x["time"])
    with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Added: {time_str} {name}")

def remove_event(name_pattern: str):
    """Remove events matching pattern"""
    data = load_events()
    original_count = len(data["events"])
    data["events"] = [e for e in data["events"] if name_pattern.lower() not in e["name"].lower()]
    removed = original_count - len(data["events"])
    with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Removed {removed} event(s) matching '{name_pattern}'")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default: check for alerts
        alerts = check_upcoming()
        if alerts:
            for alert in alerts:
                print(alert)
                print()
        else:
            print("알림 없음")
    elif sys.argv[1] == "list":
        events = list_upcoming()
        if events:
            print("📅 다가오는 경기:\n")
            print("\n".join(events))
        else:
            print("남은 경기 없음")
    elif sys.argv[1] == "add" and len(sys.argv) >= 4:
        # add "2026-02-10 18:00" "Event Name" "Athletes (optional)"
        athletes = sys.argv[4] if len(sys.argv) > 4 else ""
        add_event(sys.argv[2], sys.argv[3], athletes)
    elif sys.argv[1] == "remove" and len(sys.argv) >= 3:
        remove_event(sys.argv[2])
    else:
        print("Usage:")
        print("  check_olympic.py          # Check for upcoming alerts")
        print("  check_olympic.py list     # List upcoming events")
        print("  check_olympic.py add <time> <name> [athletes]")
        print("  check_olympic.py remove <name_pattern>")
