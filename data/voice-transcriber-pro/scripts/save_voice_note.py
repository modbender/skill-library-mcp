#!/usr/bin/env python3
"""
Save a voice note with transcript to the founder journal.
Stores both the audio file reference and full transcript.

Usage:
  save_voice_note.py <audio_path> <transcript_text> [--date 2026-02-15]
"""
import argparse
import os
import shutil
from datetime import datetime

VOICE_DIR = os.path.expanduser("~/.openclaw/workspace/memory/voice-notes")
JOURNAL_DIR = os.path.expanduser("~/.openclaw/workspace/memory/founder-journal")

def save(audio_path: str, transcript: str, date: str = None):
    date = date or datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H%M")
    
    # Copy audio to voice-notes archive
    ext = os.path.splitext(audio_path)[1] or ".ogg"
    audio_dest = os.path.join(VOICE_DIR, f"{date}_{time_str}{ext}")
    if os.path.exists(audio_path):
        shutil.copy2(audio_path, audio_dest)
        print(f"Audio saved: {audio_dest}")
    
    # Append to daily journal
    journal_path = os.path.join(JOURNAL_DIR, f"{date}.md")
    existed = os.path.exists(journal_path)
    
    with open(journal_path, "a") as f:
        if not existed:
            f.write(f"# Founder Journal — {date}\n\n")
        f.write(f"## Voice Note ({datetime.now().strftime('%I:%M %p')})\n")
        f.write(f"**Audio:** `{audio_dest}`\n\n")
        f.write(f"**Transcript:**\n{transcript}\n\n")
        f.write("---\n\n")
    
    print(f"Journal updated: {journal_path}")
    return journal_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio_path")
    parser.add_argument("transcript", nargs="?", default="[No transcript available]")
    parser.add_argument("--date")
    args = parser.parse_args()
    save(args.audio_path, args.transcript, args.date)
