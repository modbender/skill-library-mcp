#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

usage() {
  cat <<'USAGE'
Usage: project_actions.sh <command> [args]

Commands:
  list [--status active|blocked|paused|archived] [--limit N]
  activity [--when today|yesterday|both] [--limit N] [--evidence N] [--include-archived] [--all-signals] [--ignore-scope] [--json]
  focus [--limit N]
  stale [--days N] [--limit N]
  weekly [--days N] [--limit N]
  notify [--period daily|weekly]
  blockers [--limit N]
  inbox --text "<note text>" [--project <id|name>] [--no-create]
  checkin --project <id|name> [--done "<done>"] [--next "<next>"] [--blocker "<blocker>"]
  create --name "<name>" [--summary "<what>"] [--next "<next step>"] [--status now|later|blocked|done]
  resume --project <id|name> [--evidence N]
  simple-status --project <id|name> --status <now|later|blocked|done>
  duplicates [--limit N]
  merge --keep <id|name> --drop <id|name>
  ask --text "<natural command>"
  set-status --project <id|name> --status <active|blocked|paused|archived>
  set-next --project <id|name> --text "<next action>"
  add-update --project <id|name> --text "<update text>"
  add-next --project <id|name> --text "<next step>"
  add-blocker --project <id|name> --text "<blocker>"
  add-reminder --project <id|name> --text "<reminder text>" [--due YYYY-MM-DD]
  add-idea --project <id|name> --text "<idea text>"
  track --project <id|name>
  mute --project <id|name>
  untrack --project <id|name>
  scope [--set <id|name> ...] [--limit N]
  list-items [--project <id|name>] [--kind update|next|reminder|idea|blocker] [--status open|done|dismissed|all] [--limit N]
  set-item --item <id> --status <open|done|dismissed>

Examples:
  project_actions.sh list --limit 60
  project_actions.sh activity --when both
  project_actions.sh focus --limit 3
  project_actions.sh inbox --text "remind me to ship on 2026-03-01"
  project_actions.sh set-status --project "project-os" --status blocked
  project_actions.sh add-next --project 23 --text "Validate dashboard edit flow"
  project_actions.sh set-item --item 101 --status done
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

cmd="${1:-}"
if [[ -z "$cmd" ]]; then
  usage
  exit 1
fi
shift || true

case "$cmd" in
  list)
    status=""
    limit="80"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --status) status="${2:-}"; shift 2 ;;
        --limit) limit="${2:-80}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    if [[ -n "$status" ]]; then
      project_os_cli list-projects --status "$status" --limit "$limit"
    else
      project_os_cli list-projects --limit "$limit"
    fi
    ;;
  activity)
    when="both"
    limit="80"
    evidence="2"
    include_archived=0
    all_signals=0
    ignore_scope=0
    json_mode=0
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --when) when="${2:-both}"; shift 2 ;;
        --limit) limit="${2:-80}"; shift 2 ;;
        --evidence) evidence="${2:-2}"; shift 2 ;;
        --include-archived) include_archived=1; shift ;;
        --all-signals) all_signals=1; shift ;;
        --ignore-scope) ignore_scope=1; shift ;;
        --json) json_mode=1; shift ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    args=(activity-report --when "$when" --limit "$limit" --evidence "$evidence")
    if [[ "$include_archived" -eq 1 ]]; then
      args+=(--include-archived)
    fi
    if [[ "$all_signals" -eq 1 ]]; then
      args+=(--all-signals)
    fi
    if [[ "$ignore_scope" -eq 1 ]]; then
      args+=(--ignore-scope)
    fi
    if [[ "$json_mode" -eq 1 ]]; then
      args+=(--json)
    fi
    project_os_cli "${args[@]}"
    ;;
  track)
    project=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project) project="${2:-}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    require_value "project" "$project"
    project_os_cli set-tracking --project "$project" --mode track
    ;;
  mute)
    project=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project) project="${2:-}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    require_value "project" "$project"
    project_os_cli set-tracking --project "$project" --mode mute
    ;;
  untrack)
    project=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project) project="${2:-}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    require_value "project" "$project"
    project_os_cli set-tracking --project "$project" --mode auto
    ;;
  scope)
    limit="300"
    mode="list"
    projects=()
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --set)
          mode="set"
          shift
          while [[ $# -gt 0 && "${1:0:2}" != "--" ]]; do
            projects+=("$1")
            shift
          done
          ;;
        --limit) limit="${2:-300}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    if [[ "$mode" == "set" ]]; then
      if [[ "${#projects[@]}" -eq 0 ]]; then
        printf 'Missing required project names after --set\n' >&2
        exit 1
      fi
      args=(set-tracking-scope)
      for project in "${projects[@]}"; do
        args+=(--project "$project")
      done
      project_os_cli "${args[@]}"
    else
      project_os_cli list-tracking --limit "$limit"
    fi
    ;;
  focus)
    limit="3"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --limit) limit="${2:-3}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    project_os_cli focus-list --limit "$limit"
    ;;
  stale)
    days="14"
    limit="20"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --days) days="${2:-14}"; shift 2 ;;
        --limit) limit="${2:-20}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    project_os_cli stale-nudges --days "$days" --limit "$limit"
    ;;
  weekly)
    days="7"
    limit="12"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --days) days="${2:-7}"; shift 2 ;;
        --limit) limit="${2:-12}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    project_os_cli weekly-review --days "$days" --limit "$limit"
    ;;
  notify)
    period="daily"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --period) period="${2:-daily}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    project_os_cli notification-summary --period "$period"
    ;;
  blockers)
    limit="80"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --limit) limit="${2:-80}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    project_os_cli blocker-report --limit "$limit"
    ;;
  inbox)
    text=""
    project=""
    no_create=0
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --text) text="${2:-}"; shift 2 ;;
        --project) project="${2:-}"; shift 2 ;;
        --no-create) no_create=1; shift ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    require_value "text" "$text"
    args=(inbox-capture --text "$text")
    if [[ -n "$project" ]]; then
      args+=(--project "$project")
    fi
    if [[ "$no_create" -eq 1 ]]; then
      args+=(--no-create)
    fi
    project_os_cli "${args[@]}"
    ;;
  checkin)
    project=""
    done_text=""
    next_text=""
    blocker_text=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project) project="${2:-}"; shift 2 ;;
        --done) done_text="${2:-}"; shift 2 ;;
        --next) next_text="${2:-}"; shift 2 ;;
        --blocker) blocker_text="${2:-}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    require_value "project" "$project"
    args=(daily-checkin --project "$project")
    if [[ -n "$done_text" ]]; then
      args+=(--done "$done_text")
    fi
    if [[ -n "$next_text" ]]; then
      args+=(--next-step "$next_text")
    fi
    if [[ -n "$blocker_text" ]]; then
      args+=(--blocker "$blocker_text")
    fi
    project_os_cli "${args[@]}"
    ;;
  create)
    name=""
    summary=""
    next_text=""
    status="now"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --name) name="${2:-}"; shift 2 ;;
        --summary) summary="${2:-}"; shift 2 ;;
        --next) next_text="${2:-}"; shift 2 ;;
        --status) status="${2:-now}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    require_value "name" "$name"
    args=(create-project --name "$name" --status "$status")
    if [[ -n "$summary" ]]; then
      args+=(--summary "$summary")
    fi
    if [[ -n "$next_text" ]]; then
      args+=(--next-action "$next_text")
    fi
    project_os_cli "${args[@]}"
    ;;
  resume)
    project=""
    evidence="3"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project) project="${2:-}"; shift 2 ;;
        --evidence) evidence="${2:-3}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    require_value "project" "$project"
    project_os_cli resume-pack --project "$project" --evidence "$evidence"
    ;;
  simple-status)
    project=""
    status=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project) project="${2:-}"; shift 2 ;;
        --status) status="${2:-}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    require_value "project" "$project"
    require_value "status" "$status"
    project_os_cli set-simple-status --project "$project" --status "$status"
    ;;
  duplicates)
    limit="50"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --limit) limit="${2:-50}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    project_os_cli detect-duplicates --limit "$limit"
    ;;
  merge)
    keep=""
    drop=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --keep) keep="${2:-}"; shift 2 ;;
        --drop) drop="${2:-}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    require_value "keep" "$keep"
    require_value "drop" "$drop"
    project_os_cli merge-projects --keep "$keep" --drop "$drop"
    ;;
  ask)
    text=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --text) text="${2:-}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    require_value "text" "$text"
    project_os_cli quick-command --text "$text"
    ;;
  set-status)
    project=""
    status=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project) project="${2:-}"; shift 2 ;;
        --status) status="${2:-}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    require_value "project" "$project"
    require_value "status" "$status"
    project_os_cli set-status --project "$project" --status "$status"
    ;;
  set-next)
    project=""
    text=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project) project="${2:-}"; shift 2 ;;
        --text) text="${2:-}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    require_value "project" "$project"
    require_value "text" "$text"
    project_os_cli set-next-action --project "$project" --next-action "$text"
    ;;
  add-update|add-next|add-reminder|add-idea|add-blocker)
    project=""
    text=""
    due=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project) project="${2:-}"; shift 2 ;;
        --text) text="${2:-}"; shift 2 ;;
        --due) due="${2:-}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    require_value "project" "$project"
    require_value "text" "$text"
    case "$cmd" in
      add-update) project_os_cli add-update --project "$project" --text "$text" ;;
      add-next) project_os_cli add-next --project "$project" --text "$text" ;;
      add-idea) project_os_cli add-idea --project "$project" --text "$text" ;;
      add-blocker) project_os_cli add-item --project "$project" --kind blocker --text "$text" ;;
      add-reminder)
        if [[ -n "$due" ]]; then
          project_os_cli add-reminder --project "$project" --text "$text" --due "$due"
        else
          project_os_cli add-reminder --project "$project" --text "$text"
        fi
        ;;
    esac
    ;;
  list-items)
    project=""
    kind=""
    status="open"
    limit="40"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project) project="${2:-}"; shift 2 ;;
        --kind) kind="${2:-}"; shift 2 ;;
        --status) status="${2:-open}"; shift 2 ;;
        --limit) limit="${2:-40}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    args=(list-items --status "$status" --limit "$limit")
    if [[ -n "$project" ]]; then
      args+=(--project "$project")
    fi
    if [[ -n "$kind" ]]; then
      args+=(--kind "$kind")
    fi
    project_os_cli "${args[@]}"
    ;;
  set-item)
    item=""
    status=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --item) item="${2:-}"; shift 2 ;;
        --status) status="${2:-}"; shift 2 ;;
        *) printf 'Unknown arg: %s\n' "$1" >&2; exit 1 ;;
      esac
    done
    require_value "item" "$item"
    require_value "status" "$status"
    project_os_cli set-item-status --item-id "$item" --status "$status"
    ;;
  --help|-h|help)
    usage
    ;;
  *)
    printf 'Unknown command: %s\n' "$cmd" >&2
    usage >&2
    exit 1
    ;;
esac
