#!/usr/bin/env python3
"""
session-to-memory.py — Convert OpenClaw JSONL session logs to searchable Markdown.

Reads all session JSONL files, converts them to clean Markdown transcripts,
saves them to memory/sessions/, and triggers re-indexing by OpenClaw's
memory vector store (which auto-watches memory/*.md files).

Usage:
    python3 scripts/session-to-memory.py [--force]  # Convert all sessions
    python3 scripts/session-to-memory.py --new       # Only new/changed sessions
"""

import json
import glob
import os
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path

SESSIONS_DIR = os.path.expanduser("~/.openclaw/agents/main/sessions")
MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory/sessions")
STATE_FILE = os.path.join(MEMORY_DIR, ".state.json")
MIN_MESSAGES = 5  # Skip tiny sessions (system-only, heartbeats)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def file_hash(path):
    """Quick hash based on size + mtime to detect changes."""
    st = os.stat(path)
    return f"{st.st_size}:{st.st_mtime_ns}"

def extract_text_content(content):
    """Extract readable text from message content (string or array)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(item.get("text", ""))
                elif item.get("type") == "image_url":
                    parts.append("[image]")
                elif item.get("type") == "tool_use":
                    name = item.get("name", "tool")
                    parts.append(f"[tool: {name}]")
                elif item.get("type") == "tool_result":
                    # Skip verbose tool results — just note it happened
                    parts.append(f"[tool result]")
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    return str(content)

def convert_session(jsonl_path):
    """Convert a JSONL session file to a Markdown transcript."""
    entries = []
    session_info = {}
    messages = []
    compactions = []
    
    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            etype = entry.get("type")
            
            if etype == "session":
                session_info = entry
            elif etype == "message":
                msg = entry.get("message", {})
                role = msg.get("role", "unknown")
                content = extract_text_content(msg.get("content", ""))
                timestamp = entry.get("timestamp", "")
                
                # Skip empty messages, pure thinking, and tool-only messages
                if not content.strip() or content.strip() in ["", "\n\n"]:
                    continue
                # Skip system messages (usually injected context)
                if role == "system":
                    continue
                    
                messages.append({
                    "role": role,
                    "content": content.strip(),
                    "timestamp": timestamp,
                })
            elif etype == "compaction":
                summary = entry.get("summary", "")
                if summary:
                    compactions.append({
                        "timestamp": entry.get("timestamp", ""),
                        "summary": summary[:500],  # Keep compaction summaries brief
                    })
    
    if len(messages) < MIN_MESSAGES:
        return None
    
    # Determine session date from first message
    first_ts = session_info.get("timestamp") or (messages[0]["timestamp"] if messages else "")
    try:
        session_dt = datetime.fromisoformat(first_ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        session_dt = datetime.now(timezone.utc)
    
    session_id = session_info.get("id", os.path.basename(jsonl_path).replace(".jsonl", ""))
    date_str = session_dt.strftime("%Y-%m-%d")
    time_str = session_dt.strftime("%H%M")
    
    # Build markdown
    lines = []
    lines.append(f"# Session {date_str} {session_dt.strftime('%H:%M')} UTC")
    lines.append(f"")
    lines.append(f"- **Session ID:** {session_id[:8]}")
    lines.append(f"- **Date:** {date_str}")
    lines.append(f"- **Messages:** {len(messages)}")
    if compactions:
        lines.append(f"- **Compactions:** {len(compactions)}")
    lines.append(f"")
    
    # Add compaction summaries as context headers
    if compactions:
        lines.append("## Compaction Summaries")
        lines.append("")
        for c in compactions[:3]:  # Max 3 to keep size reasonable
            lines.append(f"### {c['timestamp'][:19]}")
            lines.append(f"{c['summary']}")
            lines.append("")
    
    lines.append("## Conversation")
    lines.append("")
    
    prev_role = None
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        
        # Clean up system notifications in user messages
        # Keep them but mark them
        if content.startswith("System:"):
            # Trim long system notifications
            if len(content) > 300:
                content = content[:300] + "..."
            lines.append(f"*[System notification]*: {content}")
            lines.append("")
            continue
        
        # Format based on role
        if role == "user":
            # Try to extract just the human text (after timestamps)
            lines.append(f"**Dirk:** {content}")
        elif role == "assistant":
            # Truncate very long assistant responses (tool outputs, code, etc.)
            if len(content) > 2000:
                content = content[:2000] + "\n\n[...truncated...]"
            lines.append(f"**Faya:** {content}")
        else:
            lines.append(f"**{role}:** {content}")
        
        lines.append("")
        prev_role = role
    
    return {
        "markdown": "\n".join(lines),
        "date_str": date_str,
        "time_str": time_str,
        "session_id": session_id,
        "message_count": len(messages),
    }

def main():
    force = "--force" in sys.argv
    new_only = "--new" in sys.argv
    
    os.makedirs(MEMORY_DIR, exist_ok=True)
    
    state = load_state() if not force else {}
    
    jsonl_files = sorted(glob.glob(os.path.join(SESSIONS_DIR, "*.jsonl")), key=os.path.getmtime)
    
    print(f"Found {len(jsonl_files)} session files")
    
    converted = 0
    skipped_small = 0
    skipped_unchanged = 0
    errors = 0
    
    for jsonl_path in jsonl_files:
        basename = os.path.basename(jsonl_path)
        current_hash = file_hash(jsonl_path)
        
        # Skip if unchanged
        if new_only and basename in state and state[basename] == current_hash:
            skipped_unchanged += 1
            continue
        
        try:
            result = convert_session(jsonl_path)
        except Exception as e:
            print(f"  ERROR {basename[:12]}: {e}")
            errors += 1
            continue
        
        if result is None:
            skipped_small += 1
            state[basename] = current_hash
            continue
        
        # Write markdown file
        out_name = f"session-{result['date_str']}-{result['time_str']}-{result['session_id'][:8]}.md"
        out_path = os.path.join(MEMORY_DIR, out_name)
        
        with open(out_path, "w") as f:
            f.write(result["markdown"])
        
        state[basename] = current_hash
        converted += 1
        
        size_kb = len(result["markdown"]) // 1024
        print(f"  ✓ {out_name} ({result['message_count']} msgs, {size_kb}KB)")
    
    save_state(state)
    
    print(f"\nDone: {converted} converted, {skipped_small} too small, {skipped_unchanged} unchanged, {errors} errors")
    print(f"Markdown files in: {MEMORY_DIR}")
    
    # Count total files
    md_files = glob.glob(os.path.join(MEMORY_DIR, "*.md"))
    total_size = sum(os.path.getsize(f) for f in md_files)
    print(f"Total: {len(md_files)} transcripts, {total_size // 1024}KB")

if __name__ == "__main__":
    main()
