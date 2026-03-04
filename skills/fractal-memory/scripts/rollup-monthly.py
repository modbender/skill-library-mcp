#!/usr/bin/env python3
"""
Monthly Rollup Script - Fractal Memory System

Reads this month's summary, distills major themes/lessons/changes,
and updates MEMORY.md with key insights.

Run: python3 rollup-monthly.py
Cron: 0 23 28-31 * * cd ~/.openclaw/workspace && python3 rollup-monthly.py
"""

import os
import json
from datetime import datetime
from pathlib import Path

# Configuration
WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
DIARY_DIR = MEMORY_DIR / "diary"
STATE_FILE = MEMORY_DIR / "rollup-state.json"
MEMORY_FILE = WORKSPACE / "MEMORY.md"

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

def read_monthly_file(date):
    """Read monthly summary file"""
    year = date.strftime("%Y")
    month = date.strftime("%Y-%m")
    monthly_file = DIARY_DIR / year / "monthly" / f"{month}.md"
    
    if not monthly_file.exists():
        return None
    
    with open(monthly_file, 'r', encoding='utf-8') as f:
        return f.read()

def distill_monthly(content):
    """
    Distill monthly content to major themes, lessons learned, significant changes.
    
    Simple heuristic-based distillation.
    For production, consider using LLM for better distillation.
    """
    if not content or len(content.strip()) < 50:
        return None
    
    lines = content.split('\n')
    insights = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Extract high-value insights
        if any(marker in line.lower() for marker in [
            'learned', 'discovered', 'realized', 'breakthrough',
            'created', 'implemented', 'launched', 'published',
            'important', 'critical', 'key insight', 'lesson'
        ]):
            insights.append(line)
    
    if not insights:
        return None
    
    # Take top insights
    return '\n'.join(insights[:10])

def update_memory_md(date, summary):
    """Update MEMORY.md with monthly insights"""
    month_name = date.strftime("%B %Y")
    
    # Read existing MEMORY.md
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "# MEMORY.md - Long-Term Memory\n\n"
    
    # Append monthly insights
    new_section = f"\n## {month_name}\n\n{summary}\n"
    
    with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
        f.write(new_section)

def main():
    """Main rollup logic"""
    print("🧠 Monthly Rollup - Fractal Memory System")
    print("=" * 50)
    
    # Load state
    state = load_state()
    
    # Determine which month to process
    today = datetime.now()
    target_date = today.date()
    current_month = target_date.strftime("%Y-%m")
    
    # Only run on last day of month
    next_day = target_date.replace(day=target_date.day + 1) if target_date.day < 28 else None
    if next_day and next_day.month == target_date.month:
        print(f"⏭️  Not last day of month yet")
        return
    
    # Check if we already processed this month
    last_rollup = state.get("lastMonthlyRollup")
    if last_rollup:
        last_date = datetime.fromisoformat(last_rollup).date()
        last_month = last_date.strftime("%Y-%m")
        if last_month == current_month:
            print(f"✓ Already processed month {current_month}")
            return
    
    print(f"📅 Processing: {current_month}")
    
    # Read monthly file
    content = read_monthly_file(target_date)
    if not content:
        print(f"⚠️  No monthly file found for {current_month}")
        return
    
    print(f"📖 Read {len(content)} characters from monthly file")
    
    # Distill to key insights
    summary = distill_monthly(content)
    if not summary:
        print("⚠️  No significant insights to distill")
        return
    
    print(f"✨ Distilled insights ({len(summary)} characters)")
    
    # Update MEMORY.md
    update_memory_md(target_date, summary)
    print(f"✓ Updated MEMORY.md")
    
    # Update state
    state["lastMonthlyRollup"] = today.isoformat()
    save_state(state)
    
    print("✓ State saved")
    print("=" * 50)
    print("✓ Monthly rollup complete!")

if __name__ == "__main__":
    main()
