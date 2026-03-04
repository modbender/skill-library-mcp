#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

usage() {
  cat <<'USAGE'
Project Organizer Easy Mode (for non-technical users)

Usage:
  easy_mode.sh setup [quick|full]
  easy_mode.sh sync
  easy_mode.sh projects [limit]
  easy_mode.sh all [limit]
  easy_mode.sh focus [limit]
  easy_mode.sh stale [days] [limit]
  easy_mode.sh weekly
  easy_mode.sh notify [daily|weekly]
  easy_mode.sh today
  easy_mode.sh yesterday
  easy_mode.sh activity
  easy_mode.sh dashboard [start|status|stop]
  easy_mode.sh memory
  easy_mode.sh inbox "<freeform note>" [project-name-or-id]
  easy_mode.sh checkin "<project>" "<done>" "<next>" ["<blocker>"]
  easy_mode.sh create "<project>" ["<what it is>"] ["<next step>"]
  easy_mode.sh resume "<project>"
  easy_mode.sh duplicates
  easy_mode.sh merge <keep-id> <drop-id>
  easy_mode.sh ask "<plain language command>"
  easy_mode.sh blockers [limit]
  easy_mode.sh items [project-name-or-id]
  easy_mode.sh update "<project>" "<what changed>"
  easy_mode.sh next "<project>" "<next step>"
  easy_mode.sh blocker "<project>" "<what is blocking>"
  easy_mode.sh remind "<project>" "<reminder text>" [YYYY-MM-DD]
  easy_mode.sh idea "<project>" "<idea text>"
  easy_mode.sh status "<project>" <now|later|blocked|done>
  easy_mode.sh done <item-id>

Examples:
  easy_mode.sh setup
  easy_mode.sh projects 20
  easy_mode.sh focus
  easy_mode.sh inbox "idea: add auth to landing page"
  easy_mode.sh checkin "project-os" "fixed dashboard filters" "run smoke tests"
  easy_mode.sh today
  easy_mode.sh update "project-os" "Fixed dashboard filtering"
  easy_mode.sh next "project-os" "Test OpenClaw skill end to end"
  easy_mode.sh blocker "project-os" "Waiting on API key"
  easy_mode.sh remind "project-os" "Ship MVP to first users" 2026-03-01
  easy_mode.sh done 42
USAGE
}

require_value() {
  local label="$1"
  local value="${2:-}"
  if [[ -z "$value" ]]; then
    printf 'Missing required %s\n' "$label" >&2
    exit 1
  fi
}

is_number() {
  [[ "$1" =~ ^[0-9]+$ ]]
}

resolve_project_ref() {
  local raw="$1"
  if is_number "$raw"; then
    printf '%s\n' "$raw"
    return 0
  fi

  local root py result status
  root="$(project_os_root)"
  py="$(project_os_python "$root")"

  set +e
  result="$(
    "$py" - "$PROJECT_OS_DB" "$raw" <<'PY'
import sqlite3
import sys
from pathlib import Path

db_path = str(Path(sys.argv[1]).expanduser())
raw = sys.argv[2].strip()
needle = raw.lower()

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

def fetch(query, params):
    return conn.execute(query, params).fetchall()

exact_rows = fetch(
    """
    SELECT id, name, status, COALESCE(last_activity_at, updated_at) AS sort_key
    FROM projects
    WHERE lower(name) = ? OR lower(canonical_key) = ?
    ORDER BY sort_key DESC
    """,
    (needle, needle),
)

if len(exact_rows) == 1:
    print(exact_rows[0]["id"])
    raise SystemExit(0)

if len(exact_rows) > 1:
    for row in exact_rows[:10]:
        print(f"{row['id']} | {row['name']} | {row['status']}")
    raise SystemExit(2)

like = f"%{needle}%"
partial_rows = fetch(
    """
    SELECT id, name, status, COALESCE(last_activity_at, updated_at) AS sort_key
    FROM projects
    WHERE lower(name) LIKE ? OR lower(canonical_key) LIKE ?
    ORDER BY sort_key DESC
    LIMIT 10
    """,
    (like, like),
)

if len(partial_rows) == 1:
    print(partial_rows[0]["id"])
    raise SystemExit(0)

if partial_rows:
    for row in partial_rows:
        print(f"{row['id']} | {row['name']} | {row['status']}")
    raise SystemExit(2)

raise SystemExit(3)
PY
  )"
  status=$?
  set -e

  if [[ "$status" -eq 0 ]]; then
    printf '%s\n' "$result"
    return 0
  fi

  if [[ "$status" -eq 2 ]]; then
    printf 'Project name is ambiguous: "%s"\n' "$raw" >&2
    printf 'Use one of these project IDs:\n' >&2
    while IFS= read -r line; do
      [[ -n "$line" ]] || continue
      printf -- '- %s\n' "$line" >&2
    done <<<"$result"
    return 1
  fi

  printf 'Project not found: "%s"\n' "$raw" >&2
  printf 'Tip: run `easy_mode.sh projects` or `easy_mode.sh all` to find the right name/id.\n' >&2
  return 1
}

ensure_ready() {
  if [[ -f "$PROJECT_OS_DB" && -f "$PROJECT_OS_CONFIG" ]]; then
    return 0
  fi
  printf 'First-time setup: preparing your project organizer. This may take a minute...\n'
  "$SCRIPT_DIR/bootstrap.sh" --compact --no-status
}

dashboard_status() {
  local listening="no"
  local pid=""
  if command -v lsof >/dev/null 2>&1; then
    pid="$(lsof -ti "tcp:$PROJECT_OS_PORT" 2>/dev/null | head -n 1 || true)"
    if [[ -n "$pid" ]]; then
      listening="yes"
    fi
  fi
  printf 'Dashboard URL: http://%s:%s\n' "$PROJECT_OS_HOST" "$PROJECT_OS_PORT"
  printf 'Port listening: %s\n' "$listening"
  if [[ -n "$pid" ]]; then
    printf 'Dashboard PID: %s\n' "$pid"
  fi
}

cmd="${1:-help}"
if [[ $# -gt 0 ]]; then
  shift
fi

case "$cmd" in
  setup)
    mode="${1:-full}"
    case "$mode" in
      quick)
        "$SCRIPT_DIR/bootstrap.sh" --quick --compact --no-status
        ;;
      full)
        "$SCRIPT_DIR/bootstrap.sh" --compact --no-status
        ;;
      *)
        printf 'Unknown setup mode: %s (use quick or full)\n' "$mode" >&2
        exit 1
        ;;
    esac
    ;;

  sync)
    ensure_ready
    "$SCRIPT_DIR/run_refresh.sh" --compact
    "$SCRIPT_DIR/write_memory.sh"
    printf 'Sync complete.\n'
    ;;

  projects)
    ensure_ready
    limit="${1:-40}"
    if ! is_number "$limit"; then
      printf 'Limit must be a number.\n' >&2
      exit 1
    fi
    "$SCRIPT_DIR/project_actions.sh" list --status active --limit "$limit"
    ;;

  all)
    ensure_ready
    limit="${1:-80}"
    if ! is_number "$limit"; then
      printf 'Limit must be a number.\n' >&2
      exit 1
    fi
    "$SCRIPT_DIR/project_actions.sh" list --limit "$limit"
    ;;

  today)
    ensure_ready
    "$SCRIPT_DIR/project_actions.sh" activity --when today --limit 80 --evidence 2
    ;;

  yesterday)
    ensure_ready
    "$SCRIPT_DIR/project_actions.sh" activity --when yesterday --limit 80 --evidence 2
    ;;

  activity)
    ensure_ready
    "$SCRIPT_DIR/project_actions.sh" activity --when both --limit 80 --evidence 2
    ;;

  focus)
    ensure_ready
    limit="${1:-3}"
    if ! is_number "$limit"; then
      printf 'Limit must be a number.\n' >&2
      exit 1
    fi
    "$SCRIPT_DIR/project_actions.sh" focus --limit "$limit"
    ;;

  stale)
    ensure_ready
    days="${1:-14}"
    limit="${2:-20}"
    if ! is_number "$days" || ! is_number "$limit"; then
      printf 'Days and limit must be numbers.\n' >&2
      exit 1
    fi
    "$SCRIPT_DIR/project_actions.sh" stale --days "$days" --limit "$limit"
    ;;

  weekly)
    ensure_ready
    "$SCRIPT_DIR/project_actions.sh" weekly --days 7 --limit 12
    ;;

  notify)
    ensure_ready
    period="${1:-daily}"
    "$SCRIPT_DIR/project_actions.sh" notify --period "$period"
    ;;

  dashboard)
    ensure_ready
    action="${1:-start}"
    case "$action" in
      start)
        "$SCRIPT_DIR/start_dashboard.sh" --detach --restart
        dashboard_status
        ;;
      status)
        dashboard_status
        ;;
      stop)
        pid=""
        if command -v lsof >/dev/null 2>&1; then
          pid="$(lsof -ti "tcp:$PROJECT_OS_PORT" 2>/dev/null | head -n 1 || true)"
        fi
        if [[ -n "$pid" ]]; then
          kill "$pid"
          printf 'Stopped dashboard PID %s\n' "$pid"
        else
          printf 'Dashboard is not running.\n'
        fi
        ;;
      *)
        printf 'Unknown dashboard action: %s (use start, status, stop)\n' "$action" >&2
        exit 1
        ;;
    esac
    ;;

  memory)
    ensure_ready
    "$SCRIPT_DIR/write_memory.sh"
    printf 'Memory file: %s\n' "$PROJECT_OS_MEMORY"
    ;;

  inbox)
    ensure_ready
    text="${1:-}"
    project="${2:-}"
    require_value "text" "$text"
    if [[ -n "$project" ]]; then
      resolved_project="$(resolve_project_ref "$project")"
      "$SCRIPT_DIR/project_actions.sh" inbox --text "$text" --project "$resolved_project"
    else
      "$SCRIPT_DIR/project_actions.sh" inbox --text "$text"
    fi
    ;;

  checkin)
    ensure_ready
    project="${1:-}"
    done_text="${2:-}"
    next_text="${3:-}"
    blocker_text="${4:-}"
    require_value "project" "$project"
    require_value "done" "$done_text"
    require_value "next" "$next_text"
    resolved_project="$(resolve_project_ref "$project")"
    args=(checkin --project "$resolved_project" --done "$done_text" --next "$next_text")
    if [[ -n "$blocker_text" ]]; then
      args+=(--blocker "$blocker_text")
    fi
    "$SCRIPT_DIR/project_actions.sh" "${args[@]}"
    ;;

  create)
    ensure_ready
    name="${1:-}"
    summary="${2:-}"
    next_text="${3:-}"
    require_value "project name" "$name"
    args=(create --name "$name")
    if [[ -n "$summary" ]]; then
      args+=(--summary "$summary")
    fi
    if [[ -n "$next_text" ]]; then
      args+=(--next "$next_text")
    fi
    "$SCRIPT_DIR/project_actions.sh" "${args[@]}"
    ;;

  resume)
    ensure_ready
    project="${1:-}"
    require_value "project" "$project"
    resolved_project="$(resolve_project_ref "$project")"
    "$SCRIPT_DIR/project_actions.sh" resume --project "$resolved_project" --evidence 3
    ;;

  duplicates)
    ensure_ready
    "$SCRIPT_DIR/project_actions.sh" duplicates --limit 40
    ;;

  merge)
    ensure_ready
    keep="${1:-}"
    drop="${2:-}"
    require_value "keep project id" "$keep"
    require_value "drop project id" "$drop"
    "$SCRIPT_DIR/project_actions.sh" merge --keep "$keep" --drop "$drop"
    ;;

  ask)
    ensure_ready
    text="${1:-}"
    require_value "text" "$text"
    "$SCRIPT_DIR/project_actions.sh" ask --text "$text"
    ;;

  blockers)
    ensure_ready
    limit="${1:-40}"
    if ! is_number "$limit"; then
      printf 'Limit must be a number.\n' >&2
      exit 1
    fi
    "$SCRIPT_DIR/project_actions.sh" blockers --limit "$limit"
    ;;

  items)
    ensure_ready
    project="${1:-}"
    if [[ -n "$project" ]]; then
      resolved_project="$(resolve_project_ref "$project")"
      "$SCRIPT_DIR/project_actions.sh" list-items --project "$resolved_project" --status open --limit 80
    else
      "$SCRIPT_DIR/project_actions.sh" list-items --status open --limit 80
    fi
    ;;

  update|next|idea|blocker)
    ensure_ready
    project="${1:-}"
    text="${2:-}"
    require_value "project" "$project"
    require_value "text" "$text"
    resolved_project="$(resolve_project_ref "$project")"
    case "$cmd" in
      update) "$SCRIPT_DIR/project_actions.sh" add-update --project "$resolved_project" --text "$text" ;;
      next) "$SCRIPT_DIR/project_actions.sh" add-next --project "$resolved_project" --text "$text" ;;
      idea) "$SCRIPT_DIR/project_actions.sh" add-idea --project "$resolved_project" --text "$text" ;;
      blocker) "$SCRIPT_DIR/project_actions.sh" add-blocker --project "$resolved_project" --text "$text" ;;
    esac
    ;;

  remind)
    ensure_ready
    project="${1:-}"
    text="${2:-}"
    due="${3:-}"
    require_value "project" "$project"
    require_value "text" "$text"
    resolved_project="$(resolve_project_ref "$project")"
    if [[ -n "$due" ]]; then
      "$SCRIPT_DIR/project_actions.sh" add-reminder --project "$resolved_project" --text "$text" --due "$due"
    else
      "$SCRIPT_DIR/project_actions.sh" add-reminder --project "$resolved_project" --text "$text"
    fi
    ;;

  status)
    ensure_ready
    project="${1:-}"
    state="${2:-}"
    require_value "project" "$project"
    require_value "status" "$state"
    resolved_project="$(resolve_project_ref "$project")"
    "$SCRIPT_DIR/project_actions.sh" simple-status --project "$resolved_project" --status "$state"
    ;;

  done)
    ensure_ready
    item_id="${1:-}"
    require_value "item-id" "$item_id"
    "$SCRIPT_DIR/project_actions.sh" set-item --item "$item_id" --status done
    ;;

  help|--help|-h)
    usage
    ;;

  *)
    printf 'Unknown command: %s\n' "$cmd" >&2
    usage >&2
    exit 1
    ;;
esac
