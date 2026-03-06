#!/usr/bin/env python3
"""
Quick Note Wrapper
Integrates with mcp-note-taker's storage.
"""
import sys
import os
from pathlib import Path
import datetime

# Point to mcp-note-taker's storage (or create our own if preferred, but user asked to integrate)
# Assuming mcp-note-taker uses 'notes.txt' in its root.
NOTE_TAKER_DIR = Path("/Users/guohongbin/mcp-note-taker")
NOTES_FILE = NOTE_TAKER_DIR / "notes.txt"

def add_note(content):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n[{timestamp}] {content}"
    
    with open(NOTES_FILE, "a") as f:
        f.write(entry)
    print(f"✅ Note saved to {NOTES_FILE}")

def list_notes(last_n=10):
    if not NOTES_FILE.exists():
        print("No notes found.")
        return

    with open(NOTES_FILE, "r") as f:
        lines = f.readlines()
        
    print(f"--- Last {last_n} Notes ---")
    # Simple parsing assuming one-line notes or separated by newlines
    # mcp-note-taker format might be simple text
    print("".join(lines[-last_n:]))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: note <text> | note --list")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "--list":
        list_notes()
    else:
        # Join all arguments as the note content
        content = " ".join(sys.argv[1:])
        add_note(content)
