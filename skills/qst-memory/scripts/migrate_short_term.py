#!/usr/bin/env python3
"""
QST Memory Migration: Short-term → Long-term
Migrates significant entries from daily logs to permanent memory.
"""
import os
import json
from datetime import datetime, timedelta

MEMORY_DIR = "/root/.openclaw/workspace/memory"
LONG_TERM_FILE = "/root/.openclaw/workspace/MEMORY.md"

def get_recent_days(n=7):
    """Get list of recent daily memory files."""
    files = []
    for i in range(n):
        date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        path = os.path.join(MEMORY_DIR, f"{date}.md")
        if os.path.exists(path):
            files.append(path)
    return files

def read_file(path):
    """Read file contents."""
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return ""

def migrate_to_long_term():
    """Main migration logic."""
    # Read recent daily logs
    recent_files = get_recent_days(7)
    all_content = []

    for path in recent_files:
        content = read_file(path)
        if content:
            all_content.append(f"## {os.path.basename(path)}\n{content}")

    # Agent would use LLM reasoning here to identify:
    # - Key decisions
    # - Important facts
    # - User preferences
    # - Project updates

    # For now, append raw content (agent reasoning handles filtering)
    print(f"Found {len(recent_files)} daily memory files to consolidate")
    return "\n\n".join(all_content)

if __name__ == "__main__":
    migrate_to_long_term()
