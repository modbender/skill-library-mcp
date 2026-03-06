#!/bin/bash
# ===========================================
# 🐕 Gateway Watchdog - OpenClaw Gateway Error Monitor
# Universal: works with all channels (Telegram, WhatsApp, Discord, Slack, Signal, iMessage, Feishu, etc.)
# Security: read-only log analysis, no credentials, no network, no eval
# ===========================================

set -euo pipefail

# --- Configuration (all via environment variables) ---
THRESHOLD=${WATCHDOG_THRESHOLD:-30}
WINDOW=${WATCHDOG_WINDOW:-30}  # minutes
SPIKE_RATIO=${WATCHDOG_SPIKE_RATIO:-3}

# State files use XDG-style paths (user state directory, no elevated permissions needed)
WATCHDOG_DIR="${WATCHDOG_DIR:-${XDG_STATE_HOME:-$HOME/.local/state}/gateway-watchdog}"
STATE_FILE="${WATCHDOG_STATE:-${WATCHDOG_DIR}/state.json}"
LOG_HISTORY="${WATCHDOG_LOG:-${WATCHDOG_DIR}/history.log}"

# --- Error patterns (universal, channel-agnostic) ---
readonly P_RATE_LIMIT='status[: ]+429|HTTP[/ ][0-9.]* 429|rate.limit|too many requests|retry.after'
readonly P_HTTP_5XX='status[: ]+5[0-9]{2}|HTTP[/ ][0-9.]* 5[0-9]{2}'
readonly P_AUTH='status[: ]+40[13]|unauthorized|forbidden|token.expired|invalid.token'
readonly P_NETWORK='ETIMEDOUT|ECONNREFUSED|ECONNRESET|ENOTFOUND|EHOSTUNREACH|EAI_AGAIN|socket hang up'
readonly P_DELIVERY='sendMessage failed|deliver.*fail|fetch failed|dispatch.*fail'

build_pattern() {
  local pattern="(${P_RATE_LIMIT}|${P_HTTP_5XX}|${P_AUTH}|${P_NETWORK}|${P_DELIVERY})"
  if [ -n "${WATCHDOG_EXTRA_PATTERNS:-}" ]; then
    # Validate: extra patterns must not contain shell metacharacters
    if printf '%s' "$WATCHDOG_EXTRA_PATTERNS" | grep -qE '[;&|$`\\]'; then
      echo "⚠️ WATCHDOG_EXTRA_PATTERNS contains unsafe characters, ignoring" >&2
    else
      pattern="(${P_RATE_LIMIT}|${P_HTTP_5XX}|${P_AUTH}|${P_NETWORK}|${P_DELIVERY}|${WATCHDOG_EXTRA_PATTERNS})"
    fi
  fi
  printf '%s' "$pattern"
}

ERROR_PATTERNS=$(build_pattern)

# --- Functions ---

# Detect the Gateway systemd service and query its logs (read-only)
detect_and_query_logs() {
  local candidate scope
  for candidate in "openclaw-gateway" "openclaw"; do
    for scope in "--user" ""; do
      if systemctl ${scope:+"$scope"} is-active "$candidate" >/dev/null 2>&1; then
        if [ -n "$scope" ]; then
          journalctl "$scope" -u "$candidate" --since "${WINDOW}min ago" --no-pager 2>/dev/null
        else
          journalctl -u "$candidate" --since "${WINDOW}min ago" --no-pager 2>/dev/null
        fi
        return
      fi
    done
  done

  # Fallback: scan OpenClaw log directory (no -exec, use xargs with -print0 for safety)
  local log_dir="${HOME}/.openclaw/logs"
  if [ -d "$log_dir" ]; then
    find "$log_dir" -maxdepth 1 -name "*.log" -mmin "-${WINDOW}" -print0 2>/dev/null \
      | xargs -0 cat 2>/dev/null
  fi
}

count_matches() {
  # Count pattern matches from stdin; returns 0 if no input
  local n
  n=$(grep -icE "$ERROR_PATTERNS" 2>/dev/null || true)
  printf '%d' "${n:-0}"
}

get_error_breakdown() {
  local logs="$1"
  [ -z "$logs" ] && return

  local c_rate c_5xx c_auth c_network c_delivery
  c_rate=$(printf '%s' "$logs" | grep -icE "$P_RATE_LIMIT" 2>/dev/null || true);     c_rate=${c_rate:-0}
  c_5xx=$(printf '%s' "$logs" | grep -icE "$P_HTTP_5XX" 2>/dev/null || true);        c_5xx=${c_5xx:-0}
  c_auth=$(printf '%s' "$logs" | grep -icE "$P_AUTH" 2>/dev/null || true);            c_auth=${c_auth:-0}
  c_network=$(printf '%s' "$logs" | grep -icE "$P_NETWORK" 2>/dev/null || true);      c_network=${c_network:-0}
  c_delivery=$(printf '%s' "$logs" | grep -icE "$P_DELIVERY" 2>/dev/null || true);    c_delivery=${c_delivery:-0}

  echo "  429/Rate-limit: ${c_rate}"
  echo "  5xx Server errors: ${c_5xx}"
  echo "  Auth/Permission: ${c_auth}"
  echo "  Network errors: ${c_network}"
  echo "  Delivery failures: ${c_delivery}"

  if [ -n "${WATCHDOG_EXTRA_PATTERNS:-}" ]; then
    local c_extra
    c_extra=$(printf '%s' "$logs" | grep -icE "$WATCHDOG_EXTRA_PATTERNS" 2>/dev/null || true)
    c_extra=${c_extra:-0}
    echo "  Custom patterns: ${c_extra}"
  fi

  # Concentration analysis: flag if one type dominates
  local total=$((c_rate + c_5xx + c_auth + c_network + c_delivery))
  if [ "$total" -gt 10 ]; then
    local max=$c_rate category="429/Rate-limit"
    [ "$c_5xx" -gt "$max" ] && max=$c_5xx && category="5xx Server errors"
    [ "$c_auth" -gt "$max" ] && max=$c_auth && category="Auth/Permission"
    [ "$c_network" -gt "$max" ] && max=$c_network && category="Network errors"
    [ "$c_delivery" -gt "$max" ] && max=$c_delivery && category="Delivery failures"
    local pct=$((max * 100 / total))
    if [ "$pct" -ge 80 ]; then
      echo ""
      echo "  ⚠️  Single error type \"${category}\" accounts for ${pct}% — likely a single fault source"
    fi
  fi
}

get_top_errors() {
  local logs="$1"
  [ -z "$logs" ] && return
  printf '%s' "$logs" | grep -iE "$ERROR_PATTERNS" | \
    sed -E 's/[0-9]{4}-[0-9]{2}-[0-9]{2}T[^ ]*//' | \
    sed -E 's/^[^:]+: //' | \
    sort | uniq -c | sort -rn | head -5
}

check_spike() {
  local current="$1"
  if [ -f "$STATE_FILE" ] && [ "$current" -gt 0 ]; then
    local prev
    prev=$(grep -o '"error_count":[0-9]*' "$STATE_FILE" 2>/dev/null | grep -o '[0-9]*' || echo 0)
    if [ "$prev" -gt 0 ] && [ "$current" -ge $((prev * SPIKE_RATIO)) ]; then
      echo "📈 Error spike: ${prev} → ${current} (${SPIKE_RATIO}x threshold triggered)"
    fi
  fi
}

save_state() {
  local count="$1"
  local timestamp epm=0
  timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  [ "$WINDOW" -gt 0 ] && epm=$((count / WINDOW))
  mkdir -p "$(dirname "$STATE_FILE")"

  printf '{"timestamp":"%s","error_count":%d,"threshold":%d,"window_min":%d,"errors_per_min":%d}\n' \
    "$timestamp" "$count" "$THRESHOLD" "$WINDOW" "$epm" > "$STATE_FILE"

  printf '%s errors=%d epm=%d threshold=%d\n' "$timestamp" "$count" "$epm" "$THRESHOLD" >> "$LOG_HISTORY"
  # Rotate history to last 100 entries
  if [ -f "$LOG_HISTORY" ] && [ "$(wc -l < "$LOG_HISTORY")" -gt 100 ]; then
    tail -100 "$LOG_HISTORY" > "${LOG_HISTORY}.tmp" && mv "${LOG_HISTORY}.tmp" "$LOG_HISTORY"
  fi
}

# --- Main ---
main() {
  local mode="${1:-check}"

  case "$mode" in
    check)
      local logs error_count spike_msg epm=0
      logs=$(detect_and_query_logs)
      error_count=$(printf '%s' "$logs" | count_matches)
      spike_msg=$(check_spike "$error_count")
      save_state "$error_count"
      [ "$WINDOW" -gt 0 ] && epm=$((error_count / WINDOW))

      if [ "$error_count" -ge "$THRESHOLD" ]; then
        echo "🔴 Gateway: ${error_count} errors in last ${WINDOW}min (threshold: ${THRESHOLD}, ${epm}/min)"
        [ -n "$spike_msg" ] && echo "$spike_msg"
        echo ""
        echo "Breakdown:"
        get_error_breakdown "$logs"
        echo ""
        echo "Top errors:"
        get_top_errors "$logs"
        exit 1
      elif [ -n "$spike_msg" ]; then
        echo "⚠️ Gateway: ${error_count} errors (below threshold), but spike detected:"
        echo "$spike_msg"
        echo ""
        echo "Breakdown:"
        get_error_breakdown "$logs"
        exit 1
      else
        exit 0
      fi
      ;;

    verbose)
      local logs error_count spike_msg epm=0
      logs=$(detect_and_query_logs)
      error_count=$(printf '%s' "$logs" | count_matches)
      spike_msg=$(check_spike "$error_count")
      save_state "$error_count"
      [ "$WINDOW" -gt 0 ] && epm=$((error_count / WINDOW))

      echo "========================================="
      echo "🐕 Gateway Watchdog Report"
      echo "📅 $(date '+%Y-%m-%d %H:%M:%S')"
      echo "========================================="
      echo "Window: last ${WINDOW} minutes"
      echo "Threshold: ${THRESHOLD}"
      echo "Errors: ${error_count} (${epm}/min)"
      [ -n "$spike_msg" ] && echo "$spike_msg"
      echo ""
      if [ "$error_count" -ge "$THRESHOLD" ]; then
        echo "🔴 Status: ALERT"
        echo ""
        echo "Breakdown:"
        get_error_breakdown "$logs"
        echo ""
        echo "Top errors:"
        get_top_errors "$logs"
        exit 1
      else
        echo "💚 Status: OK"
        exit 0
      fi
      ;;

    history)
      if [ -f "$LOG_HISTORY" ]; then
        echo "📊 Gateway Watchdog History (last 100 entries)"
        echo "========================================="
        cat "$LOG_HISTORY"
      else
        echo "No history yet."
      fi
      ;;

    trend)
      if [ -f "$LOG_HISTORY" ]; then
        echo "📈 Error trend (last 24h)"
        echo "========================================="
        local since
        since=$(date -d '24 hours ago' -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null \
             || date -v-24H -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null \
             || echo "")
        if [ -n "$since" ]; then
          awk -v since="$since" '$1 >= since' "$LOG_HISTORY"
        else
          tail -48 "$LOG_HISTORY"
        fi
      else
        echo "No history yet."
      fi
      ;;

    *)
      echo "Usage: gateway-watchdog.sh [check|verbose|history|trend]"
      echo ""
      echo "  check    Silent check, output only when errors exceed threshold (default)"
      echo "  verbose  Always output full report"
      echo "  history  Show monitoring history"
      echo "  trend    Show last 24h error trend"
      echo ""
      echo "Environment variables:"
      echo "  WATCHDOG_THRESHOLD       Error count threshold (default: 30)"
      echo "  WATCHDOG_WINDOW          Monitoring window in minutes (default: 30)"
      echo "  WATCHDOG_SPIKE_RATIO     Spike detection multiplier (default: 3)"
      echo "  WATCHDOG_EXTRA_PATTERNS  Custom regex patterns (e.g., '99991400|99991403')"
      echo "  WATCHDOG_DIR             State directory (default: ~/.local/state/gateway-watchdog)"
      exit 0
      ;;
  esac
}

main "$@"
