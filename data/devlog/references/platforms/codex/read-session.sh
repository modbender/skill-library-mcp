#!/usr/bin/env bash
# read-session.sh — Extract a clean, blog-ready transcript from a Codex rollout JSONL.
#
# Usage:
#   ./read-session.sh <path-to-rollout.jsonl>
#
# Codex stores sessions as rollout JSONL files in ~/.codex/sessions/YYYY/MM/DD/.
# Each line is a RolloutLine: {"timestamp": "...", "type": "...", "payload": {...}}
# Line types: "session_meta", "response_item", "event_msg", "turn_context", "compacted".
# Text messages come from event_msg (user_message, agent_message).
# Tool calls come from response_item (local_shell_call, function_call, custom_tool_call).
#
# Output: Filtered human-agent dialogue to stdout in MY HUMAN / ME format.
# Requires: python3

set -euo pipefail

JSONL_FILE="${1:-}"

if [[ -z "$JSONL_FILE" || ! -f "$JSONL_FILE" ]]; then
  echo "Usage: read-session.sh <path-to-rollout.jsonl>" >&2
  exit 1
fi

exec python3 - "$JSONL_FILE" << 'EOF'
# -*- coding: utf-8 -*-
import json
import sys
from datetime import datetime

filepath = sys.argv[1]
ARROW = "\u2192"
CROSS = "\u2717"

def truncate(text, max_len=500):
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."

def format_ts(ts_str):
    try:
        ts_str = ts_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts_str)
        return dt.strftime("[%Y-%m-%d %H:%M]")
    except Exception:
        return ""

def extract_response_text(content):
    """Extract text from response_item message content blocks."""
    if not isinstance(content, list):
        return ""
    parts = []
    for block in content:
        if not isinstance(block, dict):
            continue
        btype = block.get("type", "")
        # Codex uses input_text / output_text; handle plain "text" as fallback
        if btype in ("input_text", "output_text", "text"):
            text = block.get("text", "")
            if text:
                parts.append(text)
    return "\n".join(parts).strip()

def extract_shell_command(action):
    """Extract readable command from local_shell_call action."""
    if not isinstance(action, dict):
        return ""
    if action.get("type") == "exec":
        cmd = action.get("command", [])
        if isinstance(cmd, list) and cmd:
            # ["bash", "-c", "npm test"] -> "npm test"
            if len(cmd) >= 3 and cmd[0] in ("bash", "sh", "/bin/bash", "/bin/sh") and cmd[1] == "-c":
                return " ".join(cmd[2:])
            return " ".join(cmd)
    return ""

def extract_function_path(name, arguments_str):
    """Extract the most relevant path/query from a function call's arguments."""
    try:
        args = json.loads(arguments_str) if isinstance(arguments_str, str) else {}
    except (json.JSONDecodeError, TypeError):
        return ""
    if not isinstance(args, dict):
        return ""
    # Common argument patterns across tools
    path = (args.get("path") or args.get("file_path") or args.get("command")
            or args.get("pattern") or args.get("query") or args.get("url") or "")
    if isinstance(path, str) and len(path) > 120:
        path = path[:120] + "..."
    return path

# Track last seen text to deduplicate between event_msg and response_item
last_user_text = None
last_agent_text = None
first_ts_printed = False

with open(filepath, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue

        ts = entry.get("timestamp", "")
        line_type = entry.get("type", "")
        payload = entry.get("payload", {})
        if not isinstance(payload, dict):
            continue

        ptype = payload.get("type", "")

        # ── event_msg entries ──
        if line_type == "event_msg":

            # User message
            if ptype == "user_message":
                text = payload.get("message", "").strip()
                if text and text != last_user_text:
                    prefix = ""
                    if not first_ts_printed and ts:
                        prefix = format_ts(ts) + " "
                        first_ts_printed = True
                    print(f"\n{prefix}MY HUMAN: {truncate(text)}")
                    last_user_text = text

            # Agent message
            elif ptype == "agent_message":
                text = payload.get("message", "").strip()
                if text and text != last_agent_text:
                    first_ts_printed = True
                    print(f"\nME: {truncate(text)}")
                    last_agent_text = text

            # Patch apply — file writes/edits
            elif ptype == "patch_apply_begin":
                changes = payload.get("changes", {})
                if isinstance(changes, dict):
                    for fpath in sorted(changes.keys()):
                        short = fpath
                        if len(short) > 80:
                            short = "..." + short[-77:]
                        print(f"  {ARROW} ApplyPatch: {short}")

            # Patch apply failure
            elif ptype == "patch_apply_end":
                if not payload.get("success", True):
                    stderr = payload.get("stderr", "").strip()
                    msg = stderr.splitlines()[0][:200] if stderr else "patch failed"
                    print(f"  {CROSS} ERROR: {msg}")

            # Error event
            elif ptype == "error":
                msg = payload.get("message", "unknown error")
                print(f"  {CROSS} ERROR: {truncate(msg, 200)}")

            # MCP tool call
            elif ptype == "mcp_tool_call_begin":
                name = payload.get("name", "mcp-tool")
                print(f"  {ARROW} {name}")

        # ── response_item entries ──
        elif line_type == "response_item":

            # Message (user or assistant) — fallback if no event_msg was seen
            if ptype == "message":
                role = payload.get("role", "")
                content = payload.get("content", [])
                text = extract_response_text(content)

                if role == "user" and text and text != last_user_text:
                    prefix = ""
                    if not first_ts_printed and ts:
                        prefix = format_ts(ts) + " "
                        first_ts_printed = True
                    print(f"\n{prefix}MY HUMAN: {truncate(text)}")
                    last_user_text = text

                elif role == "assistant" and text and text != last_agent_text:
                    first_ts_printed = True
                    print(f"\nME: {truncate(text)}")
                    last_agent_text = text

            # Shell command
            elif ptype == "local_shell_call":
                action = payload.get("action", {})
                cmd = extract_shell_command(action)
                if cmd:
                    if len(cmd) > 120:
                        cmd = cmd[:120] + "..."
                    print(f"  {ARROW} Shell: {cmd}")

            # Function call
            elif ptype == "function_call":
                name = payload.get("name", "?")
                args_str = payload.get("arguments", "{}")
                path = extract_function_path(name, args_str)
                if path:
                    print(f"  {ARROW} {name}: {path}")
                else:
                    print(f"  {ARROW} {name}")

            # Custom tool call (MCP, etc.)
            elif ptype == "custom_tool_call":
                name = payload.get("name", "?")
                print(f"  {ARROW} {name}")
EOF
