#!/usr/bin/env bash
# read-session.sh — Extract a clean, blog-ready transcript from a Claude Code session JSONL.
#
# Usage:
#   ./read-session.sh <path-to-session.jsonl>
#
# Claude Code stores sessions as JSONL files in ~/.claude/projects/{slug}/.
# Entry types: "user", "assistant", "system", "progress", "file-history-snapshot".
# Content blocks use snake_case: "tool_use", "tool_result".
#
# Output: Filtered human-agent dialogue to stdout in MY HUMAN / ME format.
# Requires: python3

set -euo pipefail

JSONL_FILE="${1:-}"

if [[ -z "$JSONL_FILE" || ! -f "$JSONL_FILE" ]]; then
  echo "Usage: read-session.sh <path-to-session.jsonl>" >&2
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

def extract_text(content):
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts).strip()
    return ""

def extract_tools(content):
    if not isinstance(content, list):
        return []
    tools = []
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_use":
            name = block.get("name", "?")
            inp = block.get("input", {})
            path = inp.get("file_path") or inp.get("command", "")
            if not path:
                path = inp.get("pattern") or inp.get("query") or inp.get("url", "")
            if isinstance(path, str) and len(path) > 120:
                path = path[:120] + "..."
            tools.append(f"  {ARROW} {name}: {path}" if path else f"  {ARROW} {name}")
    return tools

def extract_errors(content):
    if not isinstance(content, list):
        return []
    errors = []
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_result" and block.get("is_error"):
            err = block.get("content", "")
            if isinstance(err, str):
                errors.append(f"  {CROSS} ERROR: {err.strip().splitlines()[0][:200]}")
    return errors

def format_ts(ts):
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("[%Y-%m-%d %H:%M]")
    except Exception:
        return ""

with open(filepath, "r", encoding="utf-8") as f:
    first_ts = True
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue

        etype = entry.get("type", "")
        if etype not in ("user", "assistant"):
            continue

        msg = entry.get("message", {})
        if not isinstance(msg, dict):
            continue

        role = msg.get("role", "")
        content = msg.get("content", [])
        ts = entry.get("timestamp", "")

        prefix = ""
        if first_ts and ts:
            prefix = format_ts(ts) + " "
            first_ts = False

        if role == "user":
            text = extract_text(content)
            errs = extract_errors(content)
            if text:
                print(f"\n{prefix}MY HUMAN: {truncate(text)}")
            for e in errs:
                print(e)

        elif role == "assistant":
            text = extract_text(content)
            tools = extract_tools(content)
            if text:
                print(f"\nME: {truncate(text)}")
            for t in tools:
                print(t)
EOF
