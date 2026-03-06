#!/usr/bin/env bash
# task-heartbeat.sh — Heartbeat updater and stalled task detector
# Part of the Task-Specialist skill for OpenClaw/Clawdbot
# No eval(), no external APIs, no crypto.

set -euo pipefail

_REAL_SCRIPT="$(readlink -f "$0")"
_SCRIPT_DIR="$(dirname "$_REAL_SCRIPT")"
DB="${TASK_DB:-$(dirname "$_SCRIPT_DIR")/tasks.db}"

die() { printf '\033[1;31mError:\033[0m %s\n' "$1" >&2; exit 1; }
ok()  { printf '\033[1;32m✓\033[0m %s\n' "$1"; }
warn(){ printf '\033[1;33m⚠\033[0m %s\n' "$1"; }

# Strict integer-only validation — guards ALL IDs before SQL interpolation
require_int() {
  local val="$1"
  local name="${2:-argument}"
  [[ "$val" =~ ^[0-9]+$ ]] || die "$name must be a positive integer (got: '$val')"
}

sql() { echo "$1" | sqlite3 -batch "$DB"; }

[ -f "$DB" ] || die "Database not found at '$DB'. Run install.sh first."

# ── Mode 1: Heartbeat a specific task ────────────────────────────────────────

if [ $# -ge 1 ]; then
  TASK_ID="$1"
  require_int "$TASK_ID" "TASK_ID"

  # Validate task exists and is in_progress
  local_status=$(sql "SELECT status FROM tasks WHERE id = $TASK_ID;" 2>/dev/null) || true

  if [ -z "$local_status" ]; then
    die "Task #$TASK_ID not found"
  fi

  if [ "$local_status" != "in_progress" ]; then
    warn "Task #$TASK_ID is '$local_status', not 'in_progress'. Heartbeat skipped."
    exit 0
  fi

  sql "UPDATE tasks SET last_updated = datetime('now') WHERE id = $TASK_ID;"
  ok "Heartbeat: task #$TASK_ID updated"
  exit 0
fi

# ── Mode 2: Report stalled tasks (no args) ───────────────────────────────────

stalled=$(printf '.mode column\n.headers on\n.width 4 40 20\n%s\n' \
  "SELECT id, request_text AS description, last_updated FROM tasks WHERE status = 'in_progress' AND last_updated < datetime('now', '-30 minutes') ORDER BY last_updated ASC;" \
  | sqlite3 -batch "$DB")

if [ -z "$stalled" ]; then
  ok "No stalled tasks."
else
  warn "⏰ Tasks needing attention (inactive >30 min):"
  echo "$stalled"
  exit 1
fi
