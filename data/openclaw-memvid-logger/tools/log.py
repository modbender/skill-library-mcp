#!/usr/bin/env python3
"""
Unified Conversation Logger for OpenClaw - Monthly Rotation Edition v1.2.0
====================================================================

Logs every conversation turn to both JSONL (backup) and Memvid (searchable memory).
Uses monthly rotation files to stay under free tier limits.

Features:
- Dual-output logging (JSONL + Memvid)
- Monthly rotation: memory_YYYY-MM.mv2
- Role tagging: user, assistant, agent:*, system, tool
- Captures everything: messages, tool calls, agent spawns, background tasks

Author: AnToni
Version: 1.2.0 (Full Context Edition)
License: MIT
"""

import json
import sys
import os
import subprocess
import tempfile
import datetime
from datetime import datetime as dt, timezone
from typing import Dict, Optional

# Configuration paths - override with environment variables
# Default paths use user's home directory for portability
HOME_DIR = os.path.expanduser("~")
DEFAULT_WORKSPACE = os.path.join(HOME_DIR, ".openclaw", "workspace")

LOG_PATH = os.environ.get("JSONL_LOG_PATH", 
                          os.path.join(DEFAULT_WORKSPACE, "conversation_log.jsonl"))

# Monthly rotation for Memvid files (stays under 50MB free tier per file)
# Format: memory_YYYY-MM.mv2 (generic, not user-specific)
MEMVID_BASE = os.environ.get("MEMVID_PATH", 
                             os.path.join(DEFAULT_WORKSPACE, "memory.mv2"))
MEMORY_DIR = os.path.dirname(MEMVID_BASE) or DEFAULT_WORKSPACE

# Check for mode: 'single' (one file) or 'monthly' (rotating)
MEMVID_MODE = os.environ.get("MEMVID_MODE", "monthly")  # 'single' for API mode, 'monthly' for free/sharding

if MEMVID_MODE == "monthly":
    current_month = dt.now().strftime("%Y-%m")
    MEMVID_PATH = os.path.join(MEMORY_DIR, f"memory_{current_month}.mv2")
else:
    MEMVID_PATH = MEMVID_BASE

# Try to find memvid in PATH, fallback to common npm global locations
_MEMVID_PATHS = [
    "/usr/local/bin/memvid",
    "/usr/bin/memvid",
    os.path.expanduser("~/.npm-global/bin/memvid"),
    os.path.expanduser("~/.local/bin/memvid"),
]
_DEFAULT_MEMVID = next((p for p in _MEMVID_PATHS if os.path.exists(p)), "memvid")
MEMVID_BIN = os.environ.get("MEMVID_BIN", _DEFAULT_MEMVID)


def ensure_memory_file():
    """Create memory file for current month if it doesn't exist."""
    if not os.path.exists(MEMVID_PATH):
        try:
            subprocess.run(
                [MEMVID_BIN, "create", MEMVID_PATH],
                capture_output=True,
                timeout=30
            )
        except Exception:
            pass  # Silent fail - will try again next message


def get_role_tag(message: Dict) -> str:
    """
    Generate role tag for frame title.
    
    Roles:
    - user: Human input
    - assistant: Main agent response
    - agent:{name}: Sub-agent (researcher, coder, etc.)
    - system: System events, heartbeats, cron
    - tool: Tool execution results
    """
    raw_role = message.get("role", "unknown")
    
    # Check if this is a sub-agent message
    agent_id = message.get("agent_id") or message.get("subagent_id")
    if agent_id:
        return f"agent:{agent_id}"
    
    # Check source field
    source = message.get("source", "")
    if source.startswith("agent:"):
        return source
    
    # Check for system/cron messages
    msg_type = message.get("type", "")
    if msg_type in ["system", "heartbeat", "cron"]:
        return "system"
    
    # Check for tool results
    if "tool_calls" in message and message.get("tool_result"):
        return "tool"
    
    return raw_role


def get_frame_title(log_entry: Dict) -> str:
    """Build descriptive title for memvid frame."""
    role = log_entry.get("role_tag", "unknown")
    content = log_entry.get("content", "")
    agent_name = log_entry.get("agent_name", "")
    
    # Get preview
    content_preview = content[:80].replace('\n', ' ').strip()
    
    # Build title based on role
    if role == "user":
        return f"[user] {content_preview}..."
    elif role == "assistant":
        return f"[assistant] {content_preview}..."
    elif role.startswith("agent:"):
        agent = role.split(":")[1] if ":" in role else "unknown"
        return f"[agent:{agent}] {content_preview}..."
    elif role == "system":
        return f"[system] {content_preview}..."
    elif role == "tool":
        tool_name = log_entry.get("tool_name", "unknown")
        return f"[tool:{tool_name}] {content_preview}..."
    else:
        return f"[{role}] {content_preview}..."


def build_tags(log_entry: Dict) -> list:
    """Build KEY=VALUE tags for memvid."""
    tags = []
    
    # Role tag
    role = log_entry.get("role_tag", "unknown")
    tags.append(f"role={role}")
    
    # Source tag
    if log_entry.get("source"):
        tags.append(f"source={log_entry.get('source')}")
    
    # Agent tag
    if log_entry.get("agent_id"):
        tags.append(f"agent={log_entry.get('agent_id')}")
    
    # Tool tag
    if log_entry.get("tool_calls"):
        tags.append("has_tools=true")
    
    # Session tag
    session = log_entry.get("session_id", "")[:8]
    if session:
        tags.append(f"session={session}")
    
    # Event type
    if log_entry.get("event_type"):
        tags.append(f"event={log_entry.get('event_type')}")
    
    return tags if tags else ["source=openclaw"]


def log_to_jsonl(log_entry: Dict) -> bool:
    """Append conversation turn to JSONL file."""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            f.flush()
        return True
    except Exception as e:
        print(f"[jsonl-logger error] {e}", file=sys.stderr)
        return False


def log_to_memvid(log_entry: Dict) -> bool:
    """Append conversation turn to Memvid .mv2 file."""
    try:
        ensure_memory_file()
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                         delete=False) as f:
            json.dump(log_entry, f, ensure_ascii=False, indent=2)
            temp_path = f.name
        
        # Build metadata
        title = get_frame_title(log_entry)
        ts = log_entry.get("timestamp", dt.now(timezone.utc).isoformat())
        date_only = ts.split('T')[0] if 'T' in ts else ts[:10]
        tags = build_tags(log_entry)
        
        # Build command with multiple --tag arguments
        cmd = [
            MEMVID_BIN, "put", MEMVID_PATH,
            "--title", title,
            "--timestamp", date_only,
            "--input", temp_path
        ]
        for tag in tags:
            cmd.extend(["--tag", tag])
        
        # Call memvid put
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        os.unlink(temp_path)
        return result.returncode == 0
        
    except Exception:
        return False


def main():
    """
    Main entry point. Reads message JSON from stdin.
    
    Captures:
    - user: Human messages
    - assistant: Main agent responses  
    - agent:*: Sub-agent conversations (researcher, coder, vision, etc.)
    - system: Heartbeats, cron jobs, system events
    - tool: Tool execution results
    """
    try:
        data = sys.stdin.read()
        if not data:
            return
            
        message = json.loads(data)
        
        # Determine role/tag
        role_tag = get_role_tag(message)
        
        # Build comprehensive log entry
        log_entry = {
            "timestamp": message.get("timestamp", 
                                    dt.now(timezone.utc).isoformat()),
            "session_id": message.get("session_id", "unknown"),
            "role": message.get("role", "unknown"),
            "role_tag": role_tag,
            "content": message.get("content", ""),
            "agent_id": message.get("agent_id") or message.get("subagent_id"),
            "agent_name": message.get("agent_name", ""),
            "tool_calls": message.get("tool_calls", None),
            "tool_name": message.get("tool_name", ""),
            "tool_result": message.get("tool_result", None),
            "source": message.get("source", "openclaw_conversation"),
            "type": message.get("type", "message"),
            "memvid_mode": MEMVID_MODE,
            "memvid_file": MEMVID_PATH,
            "logged_at": dt.now(timezone.utc).isoformat()
        }
        
        # Log to both destinations
        log_to_jsonl(log_entry)
        log_to_memvid(log_entry)
        
    except Exception as e:
        print(f"[logger error] {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
