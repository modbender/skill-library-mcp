#!/usr/bin/env bash
# DevChronicle — Data Gatherer
# Usage: gather.sh [date] [days]
# Example: gather.sh 2026-02-19 1    (single day)
#          gather.sh 2026-02-19 7    (week ending on date)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG="$SKILL_DIR/config.json"

DATE="${1:-$(date +%Y-%m-%d)}"
DAYS="${2:-1}"

# Cross-platform date math (macOS + Linux)
date_add() {
  local base="$1" offset="$2"
  if date -v+0d &>/dev/null; then
    # macOS
    date -v"${offset}d" -j -f "%Y-%m-%d" "$base" +%Y-%m-%d
  else
    # Linux
    date -d "$base ${offset} days" +%Y-%m-%d
  fi
}

START_DATE=$(date_add "$DATE" "-$DAYS")
# Include end date in git log
END_NEXT=$(date_add "$DATE" "+1")

# Read config (or defaults)
if [ -f "$CONFIG" ]; then
  PROJECT_DIRS=$(python3 -c "
import json, os
c = json.load(open('$CONFIG'))
for d in c.get('projectDirs', ['~/Projects']):
    print(os.path.expanduser(d))
" 2>/dev/null || echo "$HOME/Projects")
  PROJECT_DEPTH=$(python3 -c "import json; print(json.load(open('$CONFIG')).get('projectDepth', 3))" 2>/dev/null || echo 3)
  MEMORY_DIR=$(python3 -c "
import json, os
c = json.load(open('$CONFIG'))
d = c.get('memoryDir')
print(os.path.expanduser(d) if d else '')
" 2>/dev/null || echo "")
  SESSIONS_DIR=$(python3 -c "
import json, os
c = json.load(open('$CONFIG'))
d = c.get('sessionsDir')
print(os.path.expanduser(d) if d else '')
" 2>/dev/null || echo "")
else
  PROJECT_DIRS="$HOME/Projects"
  PROJECT_DEPTH=3
  MEMORY_DIR=""
  SESSIONS_DIR=""
fi

# Auto-detect OpenClaw dirs if not configured
if [ -z "$MEMORY_DIR" ]; then
  for candidate in "$HOME/.openclaw/workspace/memory" "$HOME/.claude/workspace/memory"; do
    [ -d "$candidate" ] && MEMORY_DIR="$candidate" && break
  done
fi
if [ -z "$SESSIONS_DIR" ]; then
  for candidate in "$HOME/.openclaw/agents/main/sessions" "$HOME/.claude/agents/main/sessions"; do
    [ -d "$candidate" ] && SESSIONS_DIR="$candidate" && break
  done
fi

echo "=== DEVCHRONICLE DATA GATHER ==="
echo "Period: $START_DATE → $DATE"
echo ""

# ── Git History ──
echo "## GIT COMMITS"
echo ""
while IFS= read -r proj_dir; do
  [ -d "$proj_dir" ] || continue
  find "$proj_dir" -maxdepth "$PROJECT_DEPTH" -name ".git" -type d 2>/dev/null | sort | while read -r gitdir; do
    repo=$(dirname "$gitdir")
    name=$(basename "$repo")
    log=$(git -C "$repo" log --after="$START_DATE" --before="$END_NEXT" --format="%h | %s | %ai" --all 2>/dev/null || true)
    if [ -n "$log" ]; then
      count=$(echo "$log" | wc -l | tr -d ' ')
      echo "### $name ($count commits)"
      echo "$log"
      echo ""
    fi
  done
done <<< "$PROJECT_DIRS"

# ── Memory Files ──
if [ -n "$MEMORY_DIR" ] && [ -d "$MEMORY_DIR" ]; then
  echo "## MEMORY FILES"
  echo ""
  current="$START_DATE"
  while [[ "$current" < "$END_NEXT" ]]; do
    memfile="$MEMORY_DIR/$current.md"
    if [ -f "$memfile" ]; then
      echo "### $current"
      cat "$memfile"
      echo ""
    fi
    current=$(date_add "$current" "+1")
  done
fi

# ── Session Metadata ──
if [ -n "$SESSIONS_DIR" ] && [ -d "$SESSIONS_DIR" ]; then
  echo "## SESSIONS"
  echo ""
  python3 -c "
import os, json, glob, sys
sdir = '$SESSIONS_DIR'
start, end = '$START_DATE', '$DATE'
found = 0
for f in sorted(glob.glob(os.path.join(sdir, '*.jsonl'))):
    if f.endswith('.lock'): continue
    try:
        with open(f) as fh:
            d = json.loads(fh.readline())
        ts = d.get('timestamp','')[:10]
        if ts >= start and ts <= end:
            lines = sum(1 for _ in open(f))
            sid = os.path.basename(f).replace('.jsonl','')
            print(f'- {sid[:12]}... | {ts} | {lines} lines')
            found += 1
    except: pass
if not found:
    print('(no sessions found for this period)')
" 2>/dev/null || echo "(python3 not available — skipping sessions)"
fi

echo ""
echo "=== END GATHER ==="
