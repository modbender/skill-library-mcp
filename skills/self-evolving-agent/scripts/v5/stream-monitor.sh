#!/usr/bin/env bash
# ============================================================
# scripts/v5/stream-monitor.sh — Real-Time Streaming Log Monitor
#
# Watches log files in real-time and fires alerts when thresholds
# are exceeded. Runs as a persistent background process or via
# --poll mode for periodic checks.
#
# Usage:
#   stream-monitor.sh                # continuous tail -F mode
#   stream-monitor.sh --poll         # 30s polling mode
#   stream-monitor.sh --poll --once  # single poll (for tests/CI)
#
# Environment:
#   LOG_DIR              Log directory (default: ~/.openclaw/logs)
#   ALERTS_DIR           Alert output directory (default: data/stream-alerts)
#   POLL_INTERVAL        Seconds between polls in --poll mode (default: 30)
#   EXEC_RETRY_THRESH    Consecutive exec retry threshold (default: 5)
#   CRON_ERROR_THRESH    Repeated cron error threshold (default: 3)
#   ALERT_CHANNEL_CMD    Command to send alerts (default: discord via OpenClaw)
#   QUIET_START          Quiet time start HH:MM (default: 23:00)
#   QUIET_END            Quiet time end HH:MM (default: 08:00)
#
# SECURITY MANIFEST:
#   - Reads: $LOG_DIR/*.log (tails in real-time)
#   - Writes: $ALERTS_DIR/alert-*.json
#   - Network: None (alerts are files; delivery is external)
#   - Exec: None
# ============================================================
# shellcheck shell=bash

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="${SKILL_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

# ── Configuration ──────────────────────────────────────────
LOG_DIR="${LOG_DIR:-$HOME/.openclaw/logs}"
ALERTS_DIR="${ALERTS_DIR:-$SKILL_DIR/data/stream-alerts}"
POLL_INTERVAL="${POLL_INTERVAL:-30}"
EXEC_RETRY_THRESH="${EXEC_RETRY_THRESH:-5}"
CRON_ERROR_THRESH="${CRON_ERROR_THRESH:-3}"
QUIET_START="${QUIET_START:-23:00}"
QUIET_END="${QUIET_END:-08:00}"

# ── State (in-memory per process) ─────────────────────────
CONSECUTIVE_EXEC=0
CRON_ERROR_COUNT=0
LAST_EXEC_LINE=""
LAST_CRON_ERR=""

# ── Mode flags ─────────────────────────────────────────────
MODE_POLL=false
MODE_ONCE=false

for arg in "$@"; do
  case "$arg" in
    --poll) MODE_POLL=true ;;
    --once) MODE_ONCE=true ;;
  esac
done

# ── Helpers ────────────────────────────────────────────────
log()  { echo "[SEA-v5 monitor] $*" >&2; }
ts()   { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
date_tag() { date +"%Y%m%d-%H%M%S"; }

is_quiet_time() {
  local current_hm
  current_hm=$(date +"%H:%M")
  # Simple string comparison for HH:MM ranges
  if [ "$QUIET_START" \< "$QUIET_END" ]; then
    # Normal range (e.g., 09:00-17:00)
    [ "$current_hm" \> "$QUIET_START" ] && [ "$current_hm" \< "$QUIET_END" ]
  else
    # Overnight range (e.g., 23:00-08:00)
    [ "$current_hm" \> "$QUIET_START" ] || [ "$current_hm" \< "$QUIET_END" ]
  fi
}

# ── Alert writer ───────────────────────────────────────────
fire_alert() {
  local type="$1"
  local severity="$2"
  local message="$3"
  local count="${4:-1}"
  local agent="${5:-unknown}"

  mkdir -p "$ALERTS_DIR" 2>/dev/null || true

  local alert_file="$ALERTS_DIR/alert-$(date_tag).json"
  python3 -c "
import json, sys
alert = {
    'timestamp': sys.argv[1],
    'type': sys.argv[2],
    'severity': sys.argv[3],
    'message': sys.argv[4],
    'count': int(sys.argv[5]),
    'agent': sys.argv[6],
    'source': 'stream-monitor'
}
with open(sys.argv[7], 'w') as f:
    json.dump(alert, f, ensure_ascii=False, indent=2)
print('Alert written:', sys.argv[7])
" "$(ts)" "$type" "$severity" "$message" "$count" "$agent" "$alert_file" 2>/dev/null || true

  log "ALERT [$severity] $type: $message (count: $count)"
}

# ── Line processor ─────────────────────────────────────────
process_line() {
  local line="$1"
  local source_file="${2:-unknown}"

  # exec retry detection
  if echo "$line" | grep -qiE "exec.*retry|retry.*attempt|command.*failed.*retry" 2>/dev/null; then
    if [ "$line" = "$LAST_EXEC_LINE" ] || echo "$line" | grep -qE "attempt [2-9]|attempt [0-9]{2}" 2>/dev/null; then
      CONSECUTIVE_EXEC=$((CONSECUTIVE_EXEC + 1))
    else
      CONSECUTIVE_EXEC=1
    fi
    LAST_EXEC_LINE="$line"

    if [ "$CONSECUTIVE_EXEC" -ge "$EXEC_RETRY_THRESH" ] && ! is_quiet_time; then
      fire_alert "exec_retry" "high" \
        "exec consecutive retries >= ${EXEC_RETRY_THRESH} detected" \
        "$CONSECUTIVE_EXEC" "$(basename "$source_file" .log)"
      CONSECUTIVE_EXEC=0  # Reset after alert
    fi
  else
    # Reset if non-retry line
    if ! echo "$line" | grep -qiE "retry|attempt|failed" 2>/dev/null; then
      CONSECUTIVE_EXEC=0
    fi
  fi

  # cron error detection
  if echo "$line" | grep -qiE "error:|ERROR|FATAL|exception|traceback" 2>/dev/null; then
    if [ "$line" = "$LAST_CRON_ERR" ]; then
      CRON_ERROR_COUNT=$((CRON_ERROR_COUNT + 1))
    else
      CRON_ERROR_COUNT=1
    fi
    LAST_CRON_ERR="$line"

    if [ "$CRON_ERROR_COUNT" -ge "$CRON_ERROR_THRESH" ] && ! is_quiet_time; then
      fire_alert "cron_error" "medium" \
        "cron error repeated ${CRON_ERROR_COUNT} times: ${line:0:100}" \
        "$CRON_ERROR_COUNT" "$(basename "$source_file" .log)"
      CRON_ERROR_COUNT=0
    fi
  fi
}

# ── Polling mode ───────────────────────────────────────────
run_poll() {
  log "Starting polling mode (interval: ${POLL_INTERVAL}s)"

  local log_files
  log_files=$(find "$LOG_DIR" -name "*.log" -type f 2>/dev/null | head -10 || true)

  if [ -z "$log_files" ]; then
    log "No log files found in $LOG_DIR"
    # Still create the alerts dir to show monitor ran
    mkdir -p "$ALERTS_DIR" 2>/dev/null || true
    return 0
  fi

  # For --once mode: process last 50 lines of each log file
  while IFS= read -r log_file; do
    [ -f "$log_file" ] || continue
    log "Polling: $log_file"

    # Process the last N lines (recent activity)
    local tail_lines=50
    while IFS= read -r line; do
      [ -n "$line" ] || continue
      process_line "$line" "$log_file"
    done < <(tail -n "$tail_lines" "$log_file" 2>/dev/null || true)

  done <<< "$log_files"

  if [ "$MODE_ONCE" = "true" ]; then
    log "One-shot poll complete"
    return 0
  fi

  # Continuous polling
  while true; do
    sleep "$POLL_INTERVAL"
    while IFS= read -r log_file; do
      [ -f "$log_file" ] || continue
      while IFS= read -r line; do
        [ -n "$line" ] || continue
        process_line "$line" "$log_file"
      done < <(tail -n 10 "$log_file" 2>/dev/null || true)
    done <<< "$log_files"
  done
}

# ── Streaming mode (tail -F) ───────────────────────────────
run_stream() {
  local log_files
  log_files=$(find "$LOG_DIR" -name "*.log" -type f 2>/dev/null | head -5 || true)

  if [ -z "$log_files" ]; then
    log "No log files found in $LOG_DIR. Waiting for files to appear..."
    sleep 5
    return 0
  fi

  log "Starting streaming mode (tail -F)"
  mkdir -p "$ALERTS_DIR" 2>/dev/null || true

  # Tail all log files and process each line
  # shellcheck disable=SC2086
  tail -F $log_files 2>/dev/null | while IFS= read -r line; do
    process_line "$line" "stream"
  done
}

# ── Main ───────────────────────────────────────────────────
main() {
  log "Stream monitor starting"
  log "LOG_DIR: $LOG_DIR"
  log "ALERTS_DIR: $ALERTS_DIR"
  log "Thresholds: exec_retry=${EXEC_RETRY_THRESH}, cron_error=${CRON_ERROR_THRESH}"
  log "Quiet hours: ${QUIET_START} – ${QUIET_END}"

  mkdir -p "$ALERTS_DIR" 2>/dev/null || true

  if [ "$MODE_POLL" = "true" ]; then
    run_poll
  else
    run_stream
  fi
}

main "$@"
