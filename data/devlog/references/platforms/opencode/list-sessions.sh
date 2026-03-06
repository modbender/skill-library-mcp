#!/usr/bin/env bash
# list-sessions.sh — Scan OpenCode sessions and output a session index.
#
# Usage:
#   ./list-sessions.sh <project-name> [--since <days>d]
#
# Output: JSON array to stdout with session metadata for matching projects.
# Requires: python3

set -euo pipefail

PROJECT="${1:-}"
SINCE_DAYS=""

shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --since) SINCE_DAYS="${2%d}"; shift 2 ;;
    *) echo "Unknown flag: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$PROJECT" ]]; then
  echo "Usage: list-sessions.sh <project-name> [--since Nd]" >&2
  exit 1
fi

exec python3 - "$PROJECT" "$SINCE_DAYS" << 'EOF'
import json
import os
import sys
import time
from pathlib import Path

project_query = sys.argv[1].lower()
since_days = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] else 0

xdg_data = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
storage_root = Path(xdg_data) / "opencode" / "storage"

if not storage_root.is_dir():
    print("[]")
    sys.exit(0)

cutoff_ms = 0
if since_days > 0:
    cutoff_ms = (time.time() - since_days * 86400) * 1000

# Step 1: Find matching projects
project_dir = storage_root / "project"
matching_projects = []

if project_dir.is_dir():
    for pf in project_dir.iterdir():
        if not pf.suffix == ".json":
            continue
        try:
            proj = json.loads(pf.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        worktree = proj.get("worktree", "").lower()
        proj_id = proj.get("id", "")
        if project_query in worktree or project_query in proj_id:
            matching_projects.append(proj)

if not matching_projects:
    print("[]")
    sys.exit(0)

# Step 2: List sessions for matching projects
results = []

for proj in matching_projects:
    proj_id = proj["id"]
    session_dir = storage_root / "session" / proj_id
    if not session_dir.is_dir():
        continue

    for sf in sorted(session_dir.iterdir()):
        if not sf.suffix == ".json":
            continue
        try:
            ses = json.loads(sf.read_text())
        except (json.JSONDecodeError, OSError):
            continue

        # Skip child/subagent sessions
        if ses.get("parentID"):
            continue

        # Skip archived sessions
        if ses.get("time", {}).get("archived"):
            continue

        updated = ses.get("time", {}).get("updated", 0)

        # Apply time filter
        if cutoff_ms > 0 and updated < cutoff_ms:
            continue

        ses_id = ses["id"]

        # Step 3: Get first and last user messages
        msg_dir = storage_root / "message" / ses_id
        first_user_text = ""
        last_user_text = ""

        if msg_dir.is_dir():
            msg_files = sorted(msg_dir.iterdir())
            user_msgs = []
            for mf in msg_files:
                if not mf.suffix == ".json":
                    continue
                try:
                    msg = json.loads(mf.read_text())
                except (json.JSONDecodeError, OSError):
                    continue
                if msg.get("role") == "user":
                    user_msgs.append(msg)

            # Get text from first user message's parts
            if user_msgs:
                first_parts_dir = storage_root / "part" / user_msgs[0]["id"]
                if first_parts_dir.is_dir():
                    for pp in sorted(first_parts_dir.iterdir()):
                        try:
                            part = json.loads(pp.read_text())
                        except (json.JSONDecodeError, OSError):
                            continue
                        if part.get("type") == "text":
                            first_user_text = part.get("text", "")[:200]
                            break

            if len(user_msgs) > 1:
                last_parts_dir = storage_root / "part" / user_msgs[-1]["id"]
                if last_parts_dir.is_dir():
                    for pp in sorted(last_parts_dir.iterdir()):
                        try:
                            part = json.loads(pp.read_text())
                        except (json.JSONDecodeError, OSError):
                            continue
                        if part.get("type") == "text":
                            last_user_text = part.get("text", "")[:200]
                            break

        # Count messages as a size proxy
        msg_count = len(list(msg_dir.iterdir())) if msg_dir.is_dir() else 0

        summary = ses.get("summary", {})
        results.append({
            "file": str(session_dir / f"{ses_id}.json"),
            "platform": "opencode",
            "project_slug": f"{proj.get('worktree', '')}",
            "session_id": ses_id,
            "title": ses.get("title", ""),
            "modified": ses.get("time", {}).get("updated", 0),
            "messages": msg_count,
            "additions": summary.get("additions", 0),
            "deletions": summary.get("deletions", 0),
            "files_changed": summary.get("files", 0),
            "first_user_message": first_user_text,
            "last_user_message": last_user_text,
        })

# Sort by updated time descending
results.sort(key=lambda x: x["modified"], reverse=True)

# Convert epoch ms to ISO for display
from datetime import datetime, timezone
for r in results:
    ts = r["modified"]
    if ts:
        r["modified"] = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

print(json.dumps(results, indent=2))
EOF
