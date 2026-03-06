#!/usr/bin/env bash
# read-session.sh — Extract a clean, blog-ready transcript from an OpenClaw session JSONL.
#
# Usage:
#   ./read-session.sh <path-to-session.jsonl>
#
# OpenClaw stores sessions as JSONL files in ~/.openclaw/agents/{agent}/sessions/.
# Entry type is "message" with role in message object. Tool calls use camelCase "toolCall".
# "toolResult" is a separate role (not nested in content).
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
        if block.get("type") == "toolCall":
            name = block.get("name", "?")
            args = block.get("arguments", {})
            path = args.get("file_path") or args.get("command") or args.get("query", "")
            if isinstance(path, str) and len(path) > 120:
                path = path[:120] + "..."
            tools.append(f"  {ARROW} {name}: {path}" if path else f"  {ARROW} {name}")
    return tools

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
        if etype != "message":
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
            if text:
                print(f"\n{prefix}MY HUMAN: {truncate(text)}")

        elif role == "assistant":
            text = extract_text(content)
            tools = extract_tools(content)
            if text:
                print(f"\nME: {truncate(text)}")
            for t in tools:
                print(t)

        elif role == "toolResult":
            text = extract_text(content)
            if text and any(kw in text.lower() for kw in ["error", "failed", "exception"]):
                print(f"  {CROSS} ERROR: {text.strip().splitlines()[0][:200]}")
EOF
