#!/usr/bin/env python3
"""
Helper function to append events to today's daily log.
Can be imported by other scripts or called directly.
"""

import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/Users/brianq/.openclaw/workspace")
DIARY_ROOT = WORKSPACE / "memory/diary"

def append_to_daily(title, details=""):
    """
    Append an event to today's daily log.
    
    Args:
        title: Event title
        details: Optional event details
    """
    now = datetime.now()
    year = now.strftime("%Y")
    date = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    
    daily_dir = DIARY_ROOT / year / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    
    today_path = daily_dir / f"{date}.md"
    
    # Create file if it doesn't exist
    if not today_path.exists():
        weekday = now.strftime("%A")
        today_path.write_text(f"# {date} ({weekday})\n\n", encoding="utf-8")
    
    # Append event
    event = f"\n## {time_str} - {title}\n"
    if details:
        event += f"{details}\n"
    
    with open(today_path, "a", encoding="utf-8") as f:
        f.write(event)
    
    print(f"✅ Logged to daily: {title}")
    return today_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: append_to_daily.py <title> [details]")
        sys.exit(1)
    
    title = sys.argv[1]
    details = sys.argv[2] if len(sys.argv) > 2 else ""
    
    append_to_daily(title, details)
