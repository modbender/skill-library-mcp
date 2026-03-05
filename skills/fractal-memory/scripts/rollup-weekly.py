#!/usr/bin/env python3
"""
Weekly Rollup Script - Fractal Memory System

Reads this week's summary, compresses to themes/trajectory/milestones,
and appends to this month's summary.

Run: python3 rollup-weekly.py
Cron: 0 23 * * 0 cd ~/.openclaw/workspace && python3 rollup-weekly.py
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
DIARY_DIR = MEMORY_DIR / "diary"
STATE_FILE = MEMORY_DIR / "rollup-state.json"

def get_week_number(date):
    """Get ISO week number (YYYY-Wnn format)"""
    return date.strftime("%Y-W%V")

def load_state():
    """Load rollup state from JSON"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    """Save rollup state to JSON"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def read_weekly_file(date):
    """Read weekly summary file"""
    year = date.strftime("%Y")
    week = get_week_number(date)
    weekly_file = DIARY_DIR / year / "weekly" / f"{week}.md"
    
    if not weekly_file.exists():
        return None
    
    with open(weekly_file, 'r', encoding='utf-8') as f:
        return f.read()

def compress_weekly(content):
    """
    Compress weekly content to themes, trajectory, milestones.
    
    Simple heuristic-based compression.
    For production, consider using LLM for better compression.
    """
    if not content or len(content.strip()) < 50:
        return None
    
    lines = content.split('\n')
    themes = []
    milestones = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Extract milestones
        if any(marker in line.lower() for marker in ['created', 'implemented', 'completed', 'launched', 'published']):
            milestones.append(line)
        # Extract themes
        elif any(marker in line.lower() for marker in ['learned', 'discovered', 'realized', 'understood']):
            themes.append(line)
    
    result = []
    if themes:
        result.append("**Themes & Learnings:**")
        result.extend(themes[:5])  # Top 5
    if milestones:
        result.append("\n**Milestones:**")
        result.extend(milestones[:5])  # Top 5
    
    return '\n'.join(result) if result else None

def append_to_monthly(date, summary):
    """Append weekly summary to monthly file"""
    year = date.strftime("%Y")
    month = date.strftime("%Y-%m")
    monthly_dir = DIARY_DIR / year / "monthly"
    monthly_dir.mkdir(parents=True, exist_ok=True)
    
    monthly_file = monthly_dir / f"{month}.md"
    
    # Create or append
    if not monthly_file.exists():
        header = f"# {date.strftime('%B %Y')}\n\n"
        with open(monthly_file, 'w', encoding='utf-8') as f:
            f.write(header)
    
    # Append weekly summary
    week = get_week_number(date)
    with open(monthly_file, 'a', encoding='utf-8') as f:
        f.write(f"\n## Week {week}\n\n")
        f.write(summary)
        f.write("\n")

def main():
    """Main rollup logic"""
    print("🧠 Weekly Rollup - Fractal Memory System")
    print("=" * 50)
    
    # Load state
    state = load_state()
    
    # Determine which week to process
    today = datetime.now()
    target_date = today.date()
    
    # Check if we already processed this week
    last_rollup = state.get("lastWeeklyRollup")
    current_week = get_week_number(target_date)
    
    if last_rollup:
        last_date = datetime.fromisoformat(last_rollup).date()
        last_week = get_week_number(last_date)
        if last_week == current_week:
            print(f"✓ Already processed week {current_week}")
            return
    
    print(f"📅 Processing: Week {current_week}")
    
    # Read weekly file
    content = read_weekly_file(target_date)
    if not content:
        print(f"⚠️  No weekly file found for {current_week}")
        return
    
    print(f"📖 Read {len(content)} characters from weekly file")
    
    # Compress to monthly summary
    summary = compress_weekly(content)
    if not summary:
        print("⚠️  No significant content to compress")
        return
    
    print(f"✨ Compressed summary ({len(summary)} characters)")
    
    # Append to monthly
    append_to_monthly(target_date, summary)
    month = target_date.strftime("%Y-%m")
    print(f"✓ Appended to monthly summary: {month}")
    
    # Update state
    state["lastWeeklyRollup"] = today.isoformat()
    save_state(state)
    
    print("✓ State saved")
    print("=" * 50)
    print("✓ Weekly rollup complete!")

if __name__ == "__main__":
    main()
