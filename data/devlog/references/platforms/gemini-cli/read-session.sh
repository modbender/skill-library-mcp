#!/usr/bin/env bash
# read-session.sh — Extract a clean, blog-ready transcript from a Gemini CLI session JSON.
#
# Usage:
#   ./read-session.sh <path-to-session.json>
#
# Gemini CLI stores sessions as JSON files in:
#   ~/.gemini/tmp/<project_hash>/chats/session-*.json
# Each file contains a ConversationRecord with a messages array.
# Message types: "user", "gemini", "info", "error", "warning".
# Gemini messages may include toolCalls, thoughts, and token metadata.
#
# Output: Filtered human-agent dialogue to stdout in MY HUMAN / ME format.
# Requires: python3

set -euo pipefail

JSON_FILE="${1:-}"

if [[ -z "$JSON_FILE" || ! -f "$JSON_FILE" ]]; then
  echo "Usage: read-session.sh <path-to-session.json>" >&2
  exit 1
fi

exec python3 - "$JSON_FILE" << 'EOF'
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

def extract_text(content):
    """Extract plain text from a PartListUnion (string, Part, or Part[])."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, dict):
        return (content.get("text") or "").strip()
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict):
                t = p.get("text", "")
                if t:
                    parts.append(t)
        return " ".join(parts).strip()
    return ""

def extract_tool_path(name, args):
    """Extract the most relevant path/query from tool call arguments."""
    if not isinstance(args, dict):
        return ""
    # Common argument patterns across Gemini CLI tools
    path = (args.get("file_path") or args.get("path") or args.get("directory")
            or args.get("pattern") or args.get("query") or args.get("regex")
            or args.get("url") or "")
    # For shell commands, extract the command string
    if not path and name in ("run_shell_command", "shell"):
        path = args.get("command", "")
    if isinstance(path, str) and len(path) > 120:
        path = path[:120] + "..."
    return path

def extract_tool_result_text(result):
    """Extract a short text summary from a tool call result."""
    if result is None:
        return ""
    if isinstance(result, str):
        return result.strip()
    if isinstance(result, list):
        for item in result:
            if isinstance(item, dict):
                fr = item.get("functionResponse", {})
                if isinstance(fr, dict):
                    resp = fr.get("response", {})
                    if isinstance(resp, dict):
                        output = resp.get("output", "")
                        if output:
                            return str(output).strip()
    return ""

# Parse the session file
try:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
except (json.JSONDecodeError, OSError) as e:
    print(f"Error reading session file: {e}", file=sys.stderr)
    sys.exit(1)

messages = data.get("messages", [])
first_ts_printed = False

for msg in messages:
    msg_type = msg.get("type", "")
    ts = msg.get("timestamp", "")
    content = msg.get("content", "")

    # ── User message ──
    if msg_type == "user":
        text = extract_text(content)
        if not text:
            continue
        prefix = ""
        if not first_ts_printed and ts:
            prefix = format_ts(ts) + " "
            first_ts_printed = True
        print(f"\n{prefix}MY HUMAN: {truncate(text)}")

    # ── Gemini (assistant) message ──
    elif msg_type == "gemini":
        text = extract_text(content)
        if text:
            first_ts_printed = True
            print(f"\nME: {truncate(text)}")

        # Process tool calls
        tool_calls = msg.get("toolCalls", [])
        for tc in tool_calls:
            name = tc.get("name", "?")
            display_name = tc.get("displayName", name)
            args = tc.get("args", {})
            status = tc.get("status", "")

            path = extract_tool_path(name, args)

            if path:
                print(f"  {ARROW} {display_name}: {path}")
            else:
                print(f"  {ARROW} {display_name}")

            # Note errors
            if status in ("error", "FAILED"):
                result_text = tc.get("resultDisplay", "")
                if not result_text:
                    result_text = extract_tool_result_text(tc.get("result"))
                if result_text:
                    short = result_text.splitlines()[0][:200]
                    print(f"  {CROSS} ERROR: {short}")
                else:
                    print(f"  {CROSS} ERROR: tool call failed")

    # ── Error message ──
    elif msg_type == "error":
        text = extract_text(content)
        if text:
            first_ts_printed = True
            print(f"  {CROSS} ERROR: {truncate(text, 200)}")
EOF
