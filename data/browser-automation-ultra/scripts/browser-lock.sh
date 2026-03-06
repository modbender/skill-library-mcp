#!/bin/bash
# browser-lock.sh — OpenClaw browser ↔ Playwright mutex manager
#
# Usage:
#   browser-lock.sh acquire                    — stop OpenClaw browser, start standalone Chrome, take lock
#   browser-lock.sh release                    — kill standalone Chrome, release lock
#   browser-lock.sh run [--timeout S] <script> [args...]  — acquire → run script → release
#   browser-lock.sh status                     — show current state
#
# Environment:
#   CDP_PORT    (default: 18800)
#   CHROME_BIN  (default: auto-detect)
#   HEADLESS    (default: auto — headless if no DISPLAY/macOS)

set -euo pipefail

LOCK_FILE="/tmp/openclaw-browser.lock"
CDP_PORT="${CDP_PORT:-18800}"
USER_DATA_DIR="$HOME/.openclaw/browser/openclaw/user-data"
PID_FILE="/tmp/openclaw-browser-standalone.pid"
DEFAULT_TIMEOUT=300  # 5 minutes

# --- Auto-detect Chrome ---
if [ -z "${CHROME_BIN:-}" ]; then
  if [ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  elif command -v google-chrome &>/dev/null; then
    CHROME_BIN="google-chrome"
  elif command -v chromium-browser &>/dev/null; then
    CHROME_BIN="chromium-browser"
  elif command -v chromium &>/dev/null; then
    CHROME_BIN="chromium"
  else
    echo "❌ Chrome not found. Set CHROME_BIN." >&2
    exit 1
  fi
fi

# --- Auto-detect headless ---
needs_headless() {
  if [ "${HEADLESS:-}" = "true" ] || [ "${HEADLESS:-}" = "1" ]; then
    return 0
  fi
  if [ "${HEADLESS:-}" = "false" ] || [ "${HEADLESS:-}" = "0" ]; then
    return 1
  fi
  # Auto: headless if no display (Linux without X/Wayland)
  if [ "$(uname)" = "Linux" ] && [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
    return 0
  fi
  return 1
}

# --- Lock management ---
# Lock file format: "PID CHROME_PID TIMESTAMP"
write_lock() {
  local chrome_pid="${1:-0}"
  echo "$$ $chrome_pid $(date +%s)" > "$LOCK_FILE"
}

read_lock() {
  # outputs: shell_pid chrome_pid timestamp
  if [ -f "$LOCK_FILE" ]; then
    cat "$LOCK_FILE"
  fi
}

is_lock_alive() {
  if [ ! -f "$LOCK_FILE" ]; then
    return 1
  fi
  local info
  info=$(read_lock)
  local shell_pid chrome_pid timestamp
  shell_pid=$(echo "$info" | awk '{print $1}')
  chrome_pid=$(echo "$info" | awk '{print $2}')
  # Lock is alive if either the shell or chrome process is running
  if kill -0 "$shell_pid" 2>/dev/null || kill -0 "$chrome_pid" 2>/dev/null; then
    return 0
  fi
  return 1
}

check_lock_timeout() {
  if [ ! -f "$LOCK_FILE" ]; then
    return
  fi
  local info
  info=$(read_lock)
  local timestamp now age
  timestamp=$(echo "$info" | awk '{print $3}')
  if [ -z "$timestamp" ]; then return; fi
  now=$(date +%s)
  age=$(( now - timestamp ))
  if [ "$age" -gt "$DEFAULT_TIMEOUT" ]; then
    echo "⚠️ Lock is ${age}s old (timeout: ${DEFAULT_TIMEOUT}s), force-releasing..."
    release
  fi
}

kill_cdp_chrome() {
  local pids
  pids=$(ps aux | grep "remote-debugging-port=$CDP_PORT" | grep -v grep | awk '{print $2}' || true)
  if [ -n "$pids" ]; then
    echo "⏹ Stopping Chrome on CDP port $CDP_PORT (PIDs: $pids)..."
    echo "$pids" | xargs kill 2>/dev/null || true
    sleep 1
    for pid in $pids; do
      kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null || true
    done
  fi
}

start_chrome() {
  if curl -s --max-time 1 "http://127.0.0.1:$CDP_PORT/json/version" &>/dev/null; then
    echo "⚠️ CDP port $CDP_PORT already in use"
    # Grab the existing Chrome PID for the lock
    local existing_pid
    existing_pid=$(ps aux | grep "remote-debugging-port=$CDP_PORT" | grep -v grep | awk '{print $2}' | head -1 || echo 0)
    echo "$existing_pid" > "$PID_FILE"
    return 0
  fi

  local headless_flag=""
  if needs_headless; then
    headless_flag="--headless=new"
    echo "🖥 Headless mode"
  fi

  echo "🚀 Starting Chrome on CDP port $CDP_PORT..."
  "$CHROME_BIN" \
    --remote-debugging-port="$CDP_PORT" \
    --user-data-dir="$USER_DATA_DIR" \
    --no-first-run \
    --no-default-browser-check \
    --disable-sync \
    --disable-background-networking \
    --disable-component-update \
    --disable-features=Translate,MediaRouter \
    --disable-session-crashed-bubble \
    --hide-crash-restore-bubble \
    --password-store=basic \
    --disable-blink-features=AutomationControlled \
    $headless_flag \
    about:blank &>/dev/null &

  local chrome_pid=$!
  echo "$chrome_pid" > "$PID_FILE"

  for i in $(seq 1 10); do
    if curl -s --max-time 1 "http://127.0.0.1:$CDP_PORT/json/version" &>/dev/null; then
      echo "✅ Chrome ready (PID: $chrome_pid, CDP: $CDP_PORT)"
      return 0
    fi
    sleep 0.5
  done
  echo "❌ Chrome failed to start" >&2
  return 1
}

acquire() {
  # Check existing lock
  if [ -f "$LOCK_FILE" ]; then
    if is_lock_alive; then
      # Check if it's timed out
      local info timestamp now age
      info=$(read_lock)
      timestamp=$(echo "$info" | awk '{print $3}')
      now=$(date +%s)
      age=$(( now - ${timestamp:-0} ))
      if [ "$age" -gt "$DEFAULT_TIMEOUT" ]; then
        echo "⚠️ Lock is ${age}s old (timeout: ${DEFAULT_TIMEOUT}s), force-releasing..."
        release
      else
        echo "❌ Lock held ($(cat "$LOCK_FILE")). Age: ${age}s. Use 'release' to force." >&2
        exit 1
      fi
    else
      echo "⚠️ Stale lock (processes dead), cleaning..."
      rm -f "$LOCK_FILE"
    fi
  fi

  kill_cdp_chrome
  sleep 1
  start_chrome

  # Write lock with Chrome PID
  local chrome_pid
  chrome_pid=$(cat "$PID_FILE" 2>/dev/null || echo 0)
  write_lock "$chrome_pid"
}

release() {
  if [ -f "$PID_FILE" ]; then
    local pid
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
      echo "⏹ Stopping standalone Chrome (PID: $pid)..."
      kill "$pid" 2>/dev/null || true
      sleep 1
      kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
  fi
  kill_cdp_chrome
  rm -f "$LOCK_FILE"
  echo "🔓 Released. OpenClaw browser can restart via 'browser start'."
}

run_script() {
  local timeout=$DEFAULT_TIMEOUT

  # Parse --timeout flag
  if [ "${1:-}" = "--timeout" ]; then
    timeout="$2"
    shift 2
  fi

  if [ $# -lt 1 ]; then
    echo "Usage: browser-lock.sh run [--timeout S] <script.js> [args...]" >&2
    exit 1
  fi

  acquire

  local exit_code=0
  echo "▶ Running (timeout: ${timeout}s): node $*"

  # Run with timeout — kill on expiry
  local script_pid
  node "$@" &
  script_pid=$!

  # Update lock with script PID so liveness checks work
  local chrome_pid
  chrome_pid=$(cat "$PID_FILE" 2>/dev/null || echo 0)
  echo "$script_pid $chrome_pid $(date +%s)" > "$LOCK_FILE"

  # Background watchdog
  (
    sleep "$timeout"
    if kill -0 "$script_pid" 2>/dev/null; then
      echo "⏰ Timeout (${timeout}s) — killing script PID $script_pid" >&2
      kill "$script_pid" 2>/dev/null
      sleep 2
      kill -0 "$script_pid" 2>/dev/null && kill -9 "$script_pid" 2>/dev/null
    fi
  ) &
  local watchdog_pid=$!

  wait "$script_pid" || exit_code=$?

  # Kill watchdog if script finished before timeout
  kill "$watchdog_pid" 2>/dev/null || true
  wait "$watchdog_pid" 2>/dev/null || true

  release

  [ $exit_code -ne 0 ] && echo "❌ Script exited with code $exit_code"
  return $exit_code
}

status() {
  echo "--- Browser Lock Status ---"
  if [ -f "$LOCK_FILE" ]; then
    local info shell_pid chrome_pid timestamp now age
    info=$(read_lock)
    shell_pid=$(echo "$info" | awk '{print $1}')
    chrome_pid=$(echo "$info" | awk '{print $2}')
    timestamp=$(echo "$info" | awk '{print $3}')
    now=$(date +%s)
    age=$(( now - ${timestamp:-0} ))

    if is_lock_alive; then
      echo "🔒 Locked (script: $shell_pid, chrome: $chrome_pid, age: ${age}s, timeout: ${DEFAULT_TIMEOUT}s)"
    else
      echo "⚠️ Stale lock (both PIDs dead, age: ${age}s)"
    fi
  else
    echo "🔓 Unlocked"
  fi
  if curl -s --max-time 1 "http://127.0.0.1:$CDP_PORT/json/version" &>/dev/null; then
    echo "🌐 Chrome running on CDP port $CDP_PORT"
  else
    echo "⭕ No Chrome on CDP port $CDP_PORT"
  fi
}

case "${1:-status}" in
  acquire) acquire ;;
  release) release ;;
  run)     shift; run_script "$@" ;;
  status)  status ;;
  *)       echo "Usage: browser-lock.sh {acquire|release|run [--timeout S] <script.js>|status}" >&2; exit 1 ;;
esac
