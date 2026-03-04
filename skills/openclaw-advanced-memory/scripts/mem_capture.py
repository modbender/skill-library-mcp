#!/usr/bin/env python3
"""
mem-capture: Watches OpenClaw session transcript files and buffers new turns to Redis.
Runs as a systemd service. Monitors all active session transcript files.

OpenClaw transcript format: JSONL with entries like:
  {"type": "message", "id": "...", "timestamp": "...", "message": {"role": "user|assistant", "content": [{"type": "text", "text": "..."}]}}

Redis key: mem:watts:turns (list of JSON-encoded turns)
"""

import json
import os
import sys
import time
import hashlib
import redis
from datetime import datetime, timezone
from pathlib import Path

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_KEY = "mem:watts:turns"

# Where OpenClaw stores session transcripts
SESSION_DIR = os.path.expanduser("~/.openclaw/agents/spark/sessions")
SESSIONS_JSON = os.path.join(SESSION_DIR, "sessions.json")

# Track file positions
TRACKER_FILE = os.path.expanduser("~/.openclaw/mem-capture-positions.json")

# How often to scan for new content (seconds)
POLL_INTERVAL = 30

# Skip turns matching these patterns (noise)
NOISE_PATTERNS = [
    "data:;base64",
    "<!doctype html>",
    "__OPENCLAW_REDACTED__",
    "HEARTBEAT_OK",
]

# Skip these roles entirely
SKIP_ROLES = ["toolResult", "toolUse", "tool"]

# Min text length to bother saving
MIN_TEXT_LENGTH = 15


def load_positions() -> dict:
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {}


def save_positions(positions: dict):
    os.makedirs(os.path.dirname(TRACKER_FILE), exist_ok=True)
    with open(TRACKER_FILE, "w") as f:
        json.dump(positions, f)


def is_noise(text: str) -> bool:
    text_lower = text.lower().strip()
    if len(text_lower) < MIN_TEXT_LENGTH:
        return True
    for pattern in NOISE_PATTERNS:
        if pattern.lower() in text_lower:
            return True
    # Skip if it's mostly metadata/JSON
    if text_lower.startswith("conversation info (untrusted"):
        return True
    if text_lower.startswith("<<<external_untrusted"):
        return True
    if text_lower == "no_reply":
        return True
    return False


def extract_text_from_content(content) -> str:
    """Extract text from OpenClaw message content (can be string or array of parts)."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        texts = []
        for part in content:
            if isinstance(part, dict):
                if part.get("type") == "text" and "text" in part:
                    texts.append(part["text"])
                elif "text" in part:
                    texts.append(part["text"])
            elif isinstance(part, str):
                texts.append(part)
        return "\n".join(texts).strip()
    return ""


def get_active_sessions() -> dict:
    """Get active session file paths from sessions.json."""
    sessions = {}
    if not os.path.exists(SESSIONS_JSON):
        return sessions
    
    try:
        with open(SESSIONS_JSON) as f:
            data = json.load(f)
        
        for key, val in data.items():
            if isinstance(val, dict):
                filepath = val.get("sessionFile") or val.get("transcriptFile")
                if filepath and os.path.exists(filepath):
                    sessions[key] = filepath
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading sessions.json: {e}", file=sys.stderr)
    
    return sessions


def process_new_lines(filepath: str, session_key: str, start_pos: int) -> tuple[list[dict], int]:
    """Read new lines from a transcript file, return turns and new position."""
    turns = []
    
    try:
        with open(filepath, "r", errors="replace") as f:
            f.seek(start_pos)
            new_content = f.read()
            new_pos = f.tell()
    except IOError:
        return [], start_pos
    
    if not new_content.strip():
        return [], new_pos
    
    for line in new_content.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        
        # Only process message entries
        if obj.get("type") != "message":
            continue
        
        msg = obj.get("message", {})
        if not isinstance(msg, dict):
            continue
        
        role = msg.get("role", "")
        
        # Skip tool results and other non-conversation roles
        if role in SKIP_ROLES or not role:
            continue
        
        # Extract text content
        text = extract_text_from_content(msg.get("content", ""))
        
        if not text or is_noise(text):
            continue
        
        # Cap text length
        text = text[:2000]
        
        # Get timestamp from the entry
        ts = obj.get("timestamp", datetime.now(timezone.utc).isoformat())
        
        # Detect channel from session key
        channel = "unknown"
        if "discord" in session_key:
            channel = "discord"
        elif "slack" in session_key:
            channel = "slack"
        elif "main" in session_key:
            channel = "main"
        elif "cron" in session_key:
            channel = "cron"
        
        turns.append({
            "role": role,
            "text": text,
            "timestamp": ts,
            "session_id": session_key,
            "channel": channel,
            "captured_at": datetime.now(timezone.utc).isoformat(),
        })
    
    return turns, new_pos


def capture_cycle(r: redis.Redis, positions: dict) -> int:
    """One capture cycle: scan all active sessions for new turns."""
    count = 0
    sessions = get_active_sessions()
    
    for session_key, filepath in sessions.items():
        try:
            stat = os.stat(filepath)
            last_pos = positions.get(filepath, 0)
            
            # Skip if file hasn't grown
            if stat.st_size <= last_pos:
                continue
            
            turns, new_pos = process_new_lines(filepath, session_key, last_pos)
            
            for turn in turns:
                # Dedup: skip if we've seen this exact content recently
                chash = hashlib.md5(turn["text"].encode()).hexdigest()[:16]
                dedup_key = f"mem:watts:seen:{chash}"
                if not r.exists(dedup_key):
                    r.rpush(REDIS_KEY, json.dumps(turn))
                    r.setex(dedup_key, 86400, "1")  # 24h dedup window
                    count += 1
            
            positions[filepath] = new_pos
            
        except Exception as e:
            print(f"Error processing {session_key}: {e}", file=sys.stderr)
    
    return count


def main():
    print(f"⚡ mem-capture starting")
    print(f"   Sessions: {SESSION_DIR}")
    print(f"   Redis: {REDIS_HOST}:{REDIS_PORT} key={REDIS_KEY}")
    print(f"   Poll: every {POLL_INTERVAL}s")
    
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.ping()
    print("   Redis: connected ✅")
    
    positions = load_positions()
    
    # Initial scan to set positions (don't capture old history)
    if not positions:
        print("   First run: indexing current file positions (skipping existing content)")
        sessions = get_active_sessions()
        for key, filepath in sessions.items():
            try:
                positions[filepath] = os.path.getsize(filepath)
            except OSError:
                pass
        save_positions(positions)
        print(f"   Indexed {len(positions)} session files")
    
    print("   Watching for new turns...")
    
    while True:
        try:
            new_count = capture_cycle(r, positions)
            if new_count > 0:
                save_positions(positions)
                total = r.llen(REDIS_KEY)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] +{new_count} turns (buffer: {total})")
            
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\nShutting down...")
            save_positions(positions)
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
