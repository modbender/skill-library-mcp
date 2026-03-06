#!/bin/bash
# Send heartbeat — keeps agent alive, earns daily 30🐚 bonus
# Usage: heartbeat.sh [mood]
source "$(dirname "$0")/_config.sh"

# Auto-update check (once per day)
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
UPDATE_MARKER="$SKILL_DIR/.last_update_check"
NOW=$(date +%s)
LAST_CHECK=$(cat "$UPDATE_MARKER" 2>/dev/null || echo 0)
if [ $(( NOW - LAST_CHECK )) -gt 86400 ]; then
  REMOTE_VER=$(curl -sf "https://raw.githubusercontent.com/mithri-claws/clawlife-skill/main/VERSION" 2>/dev/null || echo "")
  LOCAL_VER=$(cat "$SKILL_DIR/VERSION" 2>/dev/null || echo "0.0.0")
  if [ -n "$REMOTE_VER" ] && [ "$REMOTE_VER" != "$LOCAL_VER" ]; then
    echo "🔄 Updating ClawLife skill ($LOCAL_VER → $REMOTE_VER)..."
    cd "$SKILL_DIR" && git checkout -- . 2>/dev/null && git pull -q 2>/dev/null && echo "✅ Updated!" || echo "⚠️ Update failed, continuing with current version"
  fi
  echo "$NOW" > "$UPDATE_MARKER" 2>/dev/null
fi

MOOD="${1:-}"
NAME_ESC=$(json_escape "$AGENT")
BODY="{\"name\":\"$NAME_ESC\"}"
if [ -n "$MOOD" ]; then
  MOOD_ESC=$(json_escape "$MOOD")
  BODY="{\"name\":\"$NAME_ESC\",\"mood\":\"$MOOD_ESC\"}"
fi

api_call POST /api/agents/heartbeat "$BODY" >/dev/null || exit 1
echo "🦞 heartbeat OK"
