#!/usr/bin/env python3
"""
Ensure today's daily log exists and append events if needed.
Called by heartbeat to maintain daily records.
"""

import os
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/brianq/.openclaw/workspace")
DIARY_ROOT = WORKSPACE / "memory/diary"
STATE_FILE = WORKSPACE / "memory/heartbeat-state.json"

def get_today_path():
    """Get path to today's daily log."""
    now = datetime.now()
    year = now.strftime("%Y")
    date = now.strftime("%Y-%m-%d")
    
    daily_dir = DIARY_ROOT / year / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    
    return daily_dir / f"{date}.md"

def ensure_daily_exists():
    """Create today's daily log if it doesn't exist."""
    today_path = get_today_path()
    
    if not today_path.exists():
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        weekday = now.strftime("%A")
        
        content = f"# {date} ({weekday})\n\n"
        today_path.write_text(content, encoding="utf-8")
        print(f"✅ Created daily log: {today_path}")
        return True
    
    return False

def append_event(title, details=""):
    """Append an event to today's daily log."""
    today_path = get_today_path()
    now = datetime.now()
    time_str = now.strftime("%H:%M")
    
    event = f"\n## {time_str} - {title}\n"
    if details:
        event += f"{details}\n"
    
    with open(today_path, "a", encoding="utf-8") as f:
        f.write(event)
    
    print(f"✅ Appended event: {title}")

def check_pending_events():
    """Check if there are pending events to record from heartbeat state."""
    if not STATE_FILE.exists():
        return []
    
    try:
        state = json.loads(STATE_FILE.read_text())
        pending = state.get("pendingEvents", [])
        
        if pending:
            # Clear pending events after reading
            state["pendingEvents"] = []
            STATE_FILE.write_text(json.dumps(state, indent=2))
        
        return pending
    except Exception as e:
        print(f"⚠️ Error reading state: {e}")
        return []

def main():
    """Main entry point."""
    # Ensure today's file exists
    created = ensure_daily_exists()
    
    # Check for pending events
    pending = check_pending_events()
    
    if pending:
        for event in pending:
            title = event.get("title", "Untitled Event")
            details = event.get("details", "")
            append_event(title, details)
    
    if created or pending:
        print(f"📝 Daily log updated: {get_today_path()}")
    else:
        print(f"✅ Daily log exists: {get_today_path()}")

if __name__ == "__main__":
    main()
