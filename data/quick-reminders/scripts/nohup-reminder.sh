#!/usr/bin/env bash
set -euo pipefail

# --- config (env overrides) ---
REMINDERS_JSON="${REMINDERS_JSON:-$(pwd)/reminders.json}"
REMINDER_TARGET="${REMINDER_TARGET:-}"
SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
LOCK_DIR="${REMINDERS_LOCK_DIR:-${REMINDERS_JSON}.lock}"
LOCK_HELD=0
WORKSPACE_KEY="$(printf '%s' "$REMINDERS_JSON" | cksum | awk '{print $1}')"

die() { echo "error: $*" >&2; exit 2; }

check_deps() {
  command -v jq >/dev/null 2>&1 || die "jq not found (brew install jq)"
  command -v openclaw >/dev/null 2>&1 || die "openclaw not found in PATH"
}

ensure_json() { [[ -f "$REMINDERS_JSON" ]] || echo '[]' > "$REMINDERS_JSON"; }

acquire_lock() {
  local attempts=0 max_attempts=200
  while ! mkdir "$LOCK_DIR" 2>/dev/null; do
    attempts=$((attempts + 1))
    (( attempts < max_attempts )) || die "timed out waiting for lock: $LOCK_DIR"
    sleep 0.05
  done
  LOCK_HELD=1
  trap 'release_lock' EXIT INT TERM
}

release_lock() {
  if (( LOCK_HELD )); then
    rmdir "$LOCK_DIR" 2>/dev/null || true
    LOCK_HELD=0
  fi
  trap - EXIT INT TERM
}

write_json() {
  local tmp_json
  tmp_json=$(mktemp "${REMINDERS_JSON}.tmp.XXXXXX")
  if ! jq "$@" "$REMINDERS_JSON" > "$tmp_json"; then
    rm -f "$tmp_json"
    die "failed to update reminders store"
  fi
  mv "$tmp_json" "$REMINDERS_JSON"
}

# --- date helpers (BSD/GNU portable) ---
if date -j -f "%Y" "2000" "+%s" >/dev/null 2>&1; then _BSD=1; else _BSD=0; fi

_epoch_to_iso() {
  (( _BSD )) && date -r "$1" "+%Y-%m-%dT%H:%M:%S%z" || date -d "@$1" "+%Y-%m-%dT%H:%M:%S%z"
}

_parse_abs_to_epoch() {
  local str="${1/ /T}" tz="$2" has_tz=0 epoch

  # Normalize timezone markers
  if [[ "$str" =~ ^(.+[0-9])([+-])([0-9]{2}):([0-9]{2})$ ]]; then
    has_tz=1
    (( _BSD )) && str="${BASH_REMATCH[1]}${BASH_REMATCH[2]}${BASH_REMATCH[3]}${BASH_REMATCH[4]}"
  elif [[ "$str" =~ [+-][0-9]{4}$ ]]; then
    has_tz=1
  elif [[ "$str" =~ Z$ ]]; then
    has_tz=1
    (( _BSD )) && str="${str%Z}+0000"
  fi

  local use_tz=""
  [[ -n "$tz" && $has_tz -eq 0 ]] && use_tz="$tz"

  if (( _BSD )); then
    local fmts
    (( has_tz )) && fmts=("%Y-%m-%dT%H:%M:%S%z" "%Y-%m-%dT%H:%M%z") \
                 || fmts=("%Y-%m-%dT%H:%M:%S" "%Y-%m-%dT%H:%M")
    for fmt in "${fmts[@]}"; do
      if [[ -n "$use_tz" ]]; then
        epoch=$(TZ="$use_tz" date -j -f "$fmt" "$str" "+%s" 2>/dev/null) && { echo "$epoch"; return 0; }
      else
        epoch=$(date -j -f "$fmt" "$str" "+%s" 2>/dev/null) && { echo "$epoch"; return 0; }
      fi
    done
  else
    if [[ -n "$use_tz" ]]; then
      epoch=$(TZ="$use_tz" date -d "$str" "+%s" 2>/dev/null) && { echo "$epoch"; return 0; }
    else
      epoch=$(date -d "$str" "+%s" 2>/dev/null) && { echo "$epoch"; return 0; }
    fi
  fi
  return 1
}

# --- time parsing (sets DELAY_SECS, FIRES_AT) ---
parse_time() {
  local input="$1" tz="${2:-}" now
  now=$(date +%s)

  # Relative: 30s, 20m, 2h, 1d, 1h30m, 2d12h
  if [[ "$input" =~ ^[0-9] && "$input" =~ [smhd]$ && ! "$input" =~ [^0-9smhd] ]]; then
    local total=0 tmp="$input"
    while [[ "$tmp" =~ ^([0-9]+)([smhd])(.*)$ ]]; do
      local n="${BASH_REMATCH[1]}" u="${BASH_REMATCH[2]}"
      tmp="${BASH_REMATCH[3]}"
      case "$u" in
        s) total=$((total + n)) ;; m) total=$((total + n * 60)) ;;
        h) total=$((total + n * 3600)) ;; d) total=$((total + n * 86400)) ;;
      esac
    done
    [[ $total -gt 0 ]] || die "duration must be positive"
    DELAY_SECS=$total
    FIRES_AT=$(_epoch_to_iso $((now + total)))
    return 0
  fi

  # Absolute ISO-8601
  local target_epoch
  target_epoch=$(_parse_abs_to_epoch "$input" "$tz") \
    || die "unrecognized time format (use relative like 2h or ISO-8601)"
  local delta=$((target_epoch - now))
  [[ $delta -gt 0 ]] || die "time is in the past"
  DELAY_SECS=$delta
  FIRES_AT=$(_epoch_to_iso "$target_epoch")
}

prune() {
  local now_epoch
  now_epoch=$(date +%s)
  write_json --argjson now "$now_epoch" '[.[] | select((.fires_epoch // 0) > $now)]'
}

# --- usage ---
usage() {
  cat <<'EOF'
nohup-reminder — one-shot reminders via nohup sleep + openclaw message send

Env:
  REMINDERS_JSON   tracking file      (default: ./reminders.json)

Commands:
  add "text" --target ID -t TIME [--channel CH] [-z TZ]    set a reminder
  list                                       show active reminders
  remove ID [ID ...]                         cancel reminders
  remove --all                               cancel all reminders
  help                                       this message

TIME formats:
  Relative:  30s  20m  2h  1d  1h30m  2d12h
  Absolute:  2026-02-07T16:00:00+03:00
             2026-02-07T16:00:00         (uses -z or local tz)
             2026-02-07 16:00
EOF
}

usage_add() {
  cat <<'EOF'
nohup-reminder add — set a one-shot reminder

Usage:  add "Reminder text" --target ID -t TIME [--channel CH] [-z TIMEZONE]

  "text"         exact message delivered to user (first positional arg, required)
  --target ID    delivery target, e.g. Telegram chat ID (required)
  -t TIME        when to fire: relative (20m, 2h) or ISO-8601 (required)
  --channel CH   delivery channel (default: telegram)
  -z TZ          IANA timezone for naive absolute times (default: system local)

Examples:
  add "Call John back!" -t 2h
  add "Doctor appointment now" -t "2026-02-07T15:00:00" -z "Europe/Minsk"
  add "Take a break!" -t 1h30m
EOF
}

usage_remove() {
  cat <<'EOF'
nohup-reminder remove — cancel pending reminders

Usage:
  remove ID [ID ...]     cancel one or more reminders by ID
  remove --all           cancel all active reminders

ID is the numeric identifier shown by `list`.
EOF
}

# --- commands ---
cmd_add() {
  for arg in "$@"; do [[ "$arg" == "--help" || "$arg" == "-h" ]] && { usage_add; exit 0; }; done

  local text="" time_str="" tz_str="" channel="telegram"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --target) shift; REMINDER_TARGET="${1:-}"; [[ -n "$REMINDER_TARGET" ]] || die "--target requires a value" ;;
      --channel) shift; channel="${1:-}"; [[ -n "$channel" ]] || die "--channel requires a value" ;;
      -t) shift; time_str="${1:-}"; [[ -n "$time_str" ]] || die "-t requires a value" ;;
      -z) shift; tz_str="${1:-}"; [[ -n "$tz_str" ]] || die "-z requires a value" ;;
      -*) die "unknown flag: $1" ;;
      *)  [[ -z "$text" ]] && text="$1" || die "unexpected arg: $1" ;;
    esac
    shift
  done

  [[ -n "$text" ]] || die "reminder text required (first positional arg)"
  [[ -n "$REMINDER_TARGET" ]] || die "--target required (Telegram chat ID); see TOOLS.md § Reminders"
  [[ -n "$time_str" ]] || die "-t TIME required"

  parse_time "$time_str" "$tz_str"
  prune

  local id fires_epoch msg_file
  id=$(( $(jq -r 'map(.id) | max // 0' "$REMINDERS_JSON") + 1 ))
  fires_epoch=$(( $(date +%s) + DELAY_SECS ))
  msg_file="/tmp/oclaw-rem-${WORKSPACE_KEY}-${id}.msg"

  (umask 077; printf '%s' "$text" > "$msg_file")

  # Launch detached worker; message text is read from file at fire time.
  nohup bash -c '
    delay="$1"
    channel="$2"
    target="$3"
    msg_file="$4"
    script_path="$5"
    reminder_id="$6"
    reminders_json="$7"

    sleep "$delay"
    openclaw message send --channel "$channel" --target "$target" --message "$(cat "$msg_file")" || true
    REMINDERS_JSON="$reminders_json" "$script_path" remove "$reminder_id" 2>/dev/null || true
  ' _ "$DELAY_SECS" "$channel" "$REMINDER_TARGET" "$msg_file" "$SCRIPT_PATH" "$id" "$REMINDERS_JSON" > /dev/null 2>&1 &
  local pid=$!
  disown "$pid" 2>/dev/null || true

  write_json --argjson id "$id" --argjson pid "$pid" --arg text "$text" \
    --arg fires_at "$FIRES_AT" --argjson fires_epoch "$fires_epoch" \
    --arg created_at "$(date +%Y-%m-%dT%H:%M:%S%z)" --arg msg_file "$msg_file" \
    '. + [{id: $id, pid: $pid, text: $text, fires_at: $fires_at, fires_epoch: $fires_epoch, created_at: $created_at, msg_file: $msg_file}]'

  echo "ok: reminder #${id} set for ${FIRES_AT}"
}

cmd_list() {
  prune
  if [[ $(jq 'length' "$REMINDERS_JSON") -eq 0 ]]; then
    echo "No active reminders."
  else
    jq -r '.[] | "#\(.id) | \(.fires_at) | \(.text)"' "$REMINDERS_JSON"
  fi
}

_kill_one() {
  local id="$1" pid msg_file
  pid=$(jq -r --argjson id "$id" '.[] | select(.id == $id) | (.pid // empty)' "$REMINDERS_JSON")
  msg_file=$(jq -r --argjson id "$id" '.[] | select(.id == $id) | (.msg_file // empty)' "$REMINDERS_JSON")
  [[ -n "$pid" ]] || { echo "warning: reminder #${id} not found" >&2; return 1; }
  [[ "$pid" =~ ^[0-9]+$ ]] && kill "$pid" 2>/dev/null || true
  if [[ -n "$msg_file" ]]; then
    rm -f "$msg_file"
  else
    rm -f "/tmp/oclaw-rem-${WORKSPACE_KEY}-${id}.msg" "/tmp/oclaw-rem-${id}.msg"
  fi
  write_json --argjson id "$id" '[.[] | select(.id != $id)]'
  echo "ok: reminder #${id} canceled"
}

cmd_remove() {
  [[ $# -ge 1 ]] || die "usage: remove ID [ID ...] | --all"
  [[ "$1" == "--help" || "$1" == "-h" ]] && { usage_remove; exit 0; }

  if [[ "$1" == "--all" ]]; then
    prune
    local ids
    ids=$(jq -r '.[].id' "$REMINDERS_JSON")
    [[ -n "$ids" ]] || { echo "No active reminders."; return; }
    for id in $ids; do _kill_one "$id"; done
    return
  fi

  for id in "$@"; do
    [[ "$id" =~ ^[0-9]+$ ]] || die "ID must be an integer: $id"
    _kill_one "$id"
  done
}

# --- main ---
main() {
  check_deps
  ensure_json

  if [[ $# -eq 0 || "$1" == "help" || "$1" == "-h" || "$1" == "--help" ]]; then
    usage; exit 0
  fi

  local cmd="$1"; shift
  case "$cmd" in
    add)    acquire_lock; cmd_add "$@"; release_lock ;;
    list)   acquire_lock; cmd_list "$@"; release_lock ;;
    remove) acquire_lock; cmd_remove "$@"; release_lock ;;
    *)      die "unknown command: $cmd (try: help)" ;;
  esac
}

main "$@"
