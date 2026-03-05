#!/usr/bin/env bash
# read-session.sh — Extract a clean, blog-ready transcript from an OpenCode session.
#
# Usage:
#   ./read-session.sh <session-id>
#
# OpenCode stores sessions as a hierarchy of JSON files, not JSONL.
# This script assembles the transcript from message and part files.
#
# Output: Filtered human-agent dialogue to stdout in MY HUMAN / ME format.
# Requires: python3

set -euo pipefail

SESSION_ID="${1:-}"

if [[ -z "$SESSION_ID" ]]; then
  echo "Usage: read-session.sh <session-id>" >&2
  echo "  session-id: e.g., ses_45696cb60ffeN0NAV9hXkbbBPq" >&2
  exit 1
fi

exec python3 - "$SESSION_ID" << 'EOF'
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

session_id = sys.argv[1]
ARROW = "\u2192"
CROSS = "\u2717"

xdg_data = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
storage_root = Path(xdg_data) / "opencode" / "storage"

msg_dir = storage_root / "message" / session_id
if not msg_dir.is_dir():
    print(f"No messages found for session {session_id}", file=sys.stderr)
    print(f"Looked in: {msg_dir}", file=sys.stderr)
    sys.exit(1)

def truncate(text, max_len=500):
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."

def format_ts(epoch_ms):
    try:
        dt = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
        return dt.strftime("[%Y-%m-%d %H:%M]")
    except Exception:
        return ""

def get_parts(message_id):
    """Read all parts for a message, sorted chronologically."""
    part_dir = storage_root / "part" / message_id
    if not part_dir.is_dir():
        return []
    parts = []
    for pf in sorted(part_dir.iterdir()):
        if not pf.suffix == ".json":
            continue
        try:
            parts.append(json.loads(pf.read_text()))
        except (json.JSONDecodeError, OSError):
            continue
    return parts

# Read all messages sorted chronologically (IDs encode timestamp)
messages = []
for mf in sorted(msg_dir.iterdir()):
    if not mf.suffix == ".json":
        continue
    try:
        messages.append(json.loads(mf.read_text()))
    except (json.JSONDecodeError, OSError):
        continue

first_ts_shown = False

for msg in messages:
    role = msg.get("role", "")
    msg_id = msg.get("id", "")
    created = msg.get("time", {}).get("created", 0)

    parts = get_parts(msg_id)

    # Collect text and tool info from parts
    text_parts = []
    tool_lines = []
    error_lines = []

    for part in parts:
        ptype = part.get("type", "")

        if ptype == "text":
            text = part.get("text", "").strip()
            if text:
                text_parts.append(text)

        elif ptype == "tool":
            tool_name = part.get("tool", "?")
            state = part.get("state", {})
            status = state.get("status", "")
            inp = state.get("input", {})

            # Extract the most relevant identifier from input
            path = inp.get("file_path") or inp.get("filePath") or inp.get("command", "")
            if not path:
                path = inp.get("pattern") or inp.get("query") or inp.get("url", "")
            if isinstance(path, str) and len(path) > 120:
                path = path[:120] + "..."

            tool_lines.append(f"  {ARROW} {tool_name}: {path}" if path else f"  {ARROW} {tool_name}")

            if status == "error":
                err_output = state.get("output", "")
                if err_output:
                    first_line = str(err_output).strip().splitlines()[0][:200]
                    error_lines.append(f"  {CROSS} ERROR: {first_line}")

        # Skip: reasoning, snapshot, patch, step-start, step-finish, compaction, subtask, file

    # Format output
    combined_text = "\n".join(text_parts)
    if not combined_text and not tool_lines:
        continue

    ts_prefix = ""
    if not first_ts_shown and created:
        ts_prefix = format_ts(created) + " "
        first_ts_shown = True

    if role == "user":
        if combined_text:
            print(f"\n{ts_prefix}MY HUMAN: {truncate(combined_text)}")

    elif role == "assistant":
        if combined_text:
            print(f"\nME: {truncate(combined_text)}")
        for tl in tool_lines:
            print(tl)
        for el in error_lines:
            print(el)
EOF
