#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

BACKEND_HOST="${RESEARCHVAULT_PORTAL_HOST:-127.0.0.1}"
BACKEND_PORT="${RESEARCHVAULT_PORTAL_PORT:-8000}"
FRONTEND_HOST="${RESEARCHVAULT_PORTAL_FRONTEND_HOST:-127.0.0.1}"
FRONTEND_PORT="${RESEARCHVAULT_PORTAL_FRONTEND_PORT:-5173}"

PID_DIR="${RESEARCHVAULT_PORTAL_PID_DIR:-$ROOT_DIR/.portal_pids}"
BACKEND_PID_FILE="$PID_DIR/backend.pid"
FRONTEND_PID_FILE="$PID_DIR/frontend.pid"

BACKEND_PATTERN="$ROOT_DIR/run_portal.py"
FRONTEND_PATTERN="$ROOT_DIR/portal/frontend/node_modules/.bin/vite --host $FRONTEND_HOST --port $FRONTEND_PORT"

BACKEND_PID=""
FRONTEND_PID=""

mkdir -p "$PID_DIR"

usage() {
  cat <<USAGE
Usage: ./start_portal.sh [start|--stop|--status]

Commands:
  start      Start backend + frontend (default)
  --stop     Stop portal processes from PID files (and stale matching processes)
  --status   Show process and endpoint status
USAGE
}

pid_from_file() {
  local file="$1"
  if [ -f "$file" ]; then
    tr -cd '0-9' < "$file"
  fi
}

pid_alive() {
  local pid="${1:-}"
  [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

wait_for_exit() {
  local pid="$1"
  local timeout_s="$2"
  local waited=0
  while pid_alive "$pid"; do
    if [ "$waited" -ge "$timeout_s" ]; then
      return 1
    fi
    sleep 1
    waited=$((waited + 1))
  done
  return 0
}

kill_pid_and_children() {
  local pid="$1"
  local signal="$2"

  if ! pid_alive "$pid"; then
    return 0
  fi

  if command -v pkill >/dev/null 2>&1; then
    pkill -"$signal" -P "$pid" 2>/dev/null || true
  fi

  kill -"$signal" "$pid" 2>/dev/null || true
}

kill_pattern_if_present() {
  local pattern="$1"
  local signal="$2"

  if ! command -v pgrep >/dev/null 2>&1; then
    return 0
  fi

  local pids
  pids="$(pgrep -f "$pattern" || true)"
  if [ -z "$pids" ]; then
    return 0
  fi

  for p in $pids; do
    kill -"$signal" "$p" 2>/dev/null || true
  done
}

cleanup_stale_pidfiles() {
  local bpid
  local fpid

  bpid="$(pid_from_file "$BACKEND_PID_FILE")"
  if [ -n "$bpid" ] && ! pid_alive "$bpid"; then
    rm -f "$BACKEND_PID_FILE"
  fi

  fpid="$(pid_from_file "$FRONTEND_PID_FILE")"
  if [ -n "$fpid" ] && ! pid_alive "$fpid"; then
    rm -f "$FRONTEND_PID_FILE"
  fi
}

port_open() {
  local host="$1"
  local port="$2"
  python3 - "$host" "$port" <<'PY'
import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(0.5)
try:
    rc = sock.connect_ex((host, port))
finally:
    sock.close()

raise SystemExit(0 if rc == 0 else 1)
PY
}

stop_one() {
  local name="$1"
  local pid_file="$2"
  local pattern="$3"

  local pid
  pid="$(pid_from_file "$pid_file")"

  if [ -n "$pid" ] && pid_alive "$pid"; then
    echo "Stopping $name (pid $pid)..."
    kill_pid_and_children "$pid" TERM
    if ! wait_for_exit "$pid" 8; then
      echo "$name did not stop in time; forcing kill..."
      kill_pid_and_children "$pid" KILL
      wait_for_exit "$pid" 2 || true
    fi
    rm -f "$pid_file"
  elif [ -f "$pid_file" ]; then
    echo "Removing stale $name pid file ($pid_file)."
    rm -f "$pid_file"
  fi

  # Safety net for stale processes without pid files.
  kill_pattern_if_present "$pattern" TERM
  sleep 1
  kill_pattern_if_present "$pattern" KILL
}

stop_services() {
  cleanup_stale_pidfiles

  local any=0
  if [ -f "$BACKEND_PID_FILE" ] || [ -f "$FRONTEND_PID_FILE" ]; then
    any=1
  fi

  stop_one "backend" "$BACKEND_PID_FILE" "$BACKEND_PATTERN"
  stop_one "frontend" "$FRONTEND_PID_FILE" "$FRONTEND_PATTERN"

  if [ "$any" -eq 0 ]; then
    echo "Portal is not running (no pid files found)."
  else
    echo "Portal stopped."
  fi
}

status_services() {
  cleanup_stale_pidfiles

  local bpid
  local fpid
  local bstate="stopped"
  local fstate="stopped"

  bpid="$(pid_from_file "$BACKEND_PID_FILE")"
  if [ -n "$bpid" ] && pid_alive "$bpid"; then
    bstate="running (pid $bpid)"
  fi

  fpid="$(pid_from_file "$FRONTEND_PID_FILE")"
  if [ -n "$fpid" ] && pid_alive "$fpid"; then
    fstate="running (pid $fpid)"
  fi

  echo "Backend:  $bstate"
  echo "Frontend: $fstate"

  if curl -fsS "http://${BACKEND_HOST}:${BACKEND_PORT}/health" >/dev/null 2>&1; then
    echo "Health:   ok (http://${BACKEND_HOST}:${BACKEND_PORT}/health)"
  else
    echo "Health:   down (http://${BACKEND_HOST}:${BACKEND_PORT}/health)"
  fi

  if curl -fsS "http://127.0.0.1:${FRONTEND_PORT}/" >/dev/null 2>&1; then
    echo "UI:       ok (http://127.0.0.1:${FRONTEND_PORT}/)"
  elif curl -fsS "http://localhost:${FRONTEND_PORT}/" >/dev/null 2>&1; then
    echo "UI:       ok (http://localhost:${FRONTEND_PORT}/)"
  else
    echo "UI:       down (port ${FRONTEND_PORT})"
  fi
}

start_cleanup() {
  echo ""
  echo "Shutting down Portal..."

  if [ -n "$BACKEND_PID" ] && pid_alive "$BACKEND_PID"; then
    kill_pid_and_children "$BACKEND_PID" TERM
  fi
  if [ -n "$FRONTEND_PID" ] && pid_alive "$FRONTEND_PID"; then
    kill_pid_and_children "$FRONTEND_PID" TERM
  fi

  if [ -n "$FRONTEND_PID" ]; then
    wait_for_exit "$FRONTEND_PID" 8 || true
  fi
  if [ -n "$BACKEND_PID" ]; then
    wait_for_exit "$BACKEND_PID" 8 || true
  fi

  rm -f "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE"
}

await_http_ok() {
  local url="$1"
  local timeout_s="$2"

  python3 - "$url" "$timeout_s" <<'PY'
import sys
import time
import urllib.request

url = sys.argv[1]
timeout_s = int(sys.argv[2])

deadline = time.time() + timeout_s
while time.time() < deadline:
    try:
        with urllib.request.urlopen(url, timeout=1) as response:
            if 200 <= response.status < 500:
                raise SystemExit(0)
    except Exception:
        time.sleep(0.25)

raise SystemExit(1)
PY
}

run_start() {
  cleanup_stale_pidfiles

  local existing_backend
  local existing_frontend
  existing_backend="$(pid_from_file "$BACKEND_PID_FILE")"
  existing_frontend="$(pid_from_file "$FRONTEND_PID_FILE")"

  if { [ -n "$existing_backend" ] && pid_alive "$existing_backend"; } || { [ -n "$existing_frontend" ] && pid_alive "$existing_frontend"; }; then
    echo "Portal already appears to be running."
    status_services
    echo "Use ./start_portal.sh --stop before starting again."
    exit 0
  fi

  # Cleanup orphaned processes from old runs.
  kill_pattern_if_present "$BACKEND_PATTERN" TERM
  kill_pattern_if_present "$FRONTEND_PATTERN" TERM
  sleep 1
  kill_pattern_if_present "$BACKEND_PATTERN" KILL
  kill_pattern_if_present "$FRONTEND_PATTERN" KILL

  if port_open "$BACKEND_HOST" "$BACKEND_PORT"; then
    echo "Error: backend port ${BACKEND_PORT} is already in use on ${BACKEND_HOST}."
    echo "Run ./start_portal.sh --stop and retry."
    exit 1
  fi

  if port_open "$FRONTEND_HOST" "$FRONTEND_PORT"; then
    echo "Error: frontend port ${FRONTEND_PORT} is already in use on ${FRONTEND_HOST}."
    echo "Run ./start_portal.sh --stop and retry."
    exit 1
  fi

  export RESEARCHVAULT_PORTAL_HOST="$BACKEND_HOST"
  export RESEARCHVAULT_PORTAL_PORT="$BACKEND_PORT"
  export RESEARCHVAULT_PORTAL_CORS_ORIGINS="${RESEARCHVAULT_PORTAL_CORS_ORIGINS:-http://localhost:${FRONTEND_PORT},http://127.0.0.1:${FRONTEND_PORT}}"

  # DB resolution:
  # - If RESEARCHVAULT_DB is already set, respect it.
  # - OpenClaw workspace DB scope requires explicit opt-in (RESEARCHVAULT_PORTAL_SCAN_OPENCLAW=1)
  #   and allowed DB roots (RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS).
  # - By default, pin to ~/.researchvault/research_vault.db.
  if [ -z "${RESEARCHVAULT_DB:-}" ]; then
    LEGACY_DB="$HOME/.openclaw/workspace/memory/research_vault.db"
    OPENCLAW_ROOT="$HOME/.openclaw/workspace"
    DEFAULT_DB="$HOME/.researchvault/research_vault.db"
    LEGACY_EXISTS="false"
    DEFAULT_EXISTS="false"
    OPENCLAW_SCAN="${RESEARCHVAULT_PORTAL_SCAN_OPENCLAW:-0}"
    export OPENCLAW_ROOT
    export RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS="${RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS:-$HOME/.researchvault,/tmp}"
    OPENCLAW_ALLOWED="$(
      python3 - <<'PY'
import os

target = os.path.realpath(os.path.expanduser(os.environ["OPENCLAW_ROOT"]))
raw = os.environ.get("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", "")
allowed = False
for part in raw.split(","):
    p = part.strip()
    if not p:
        continue
    p = os.path.realpath(os.path.expanduser(p))
    if target == p or target.startswith(p + os.sep):
        allowed = True
        break
print("1" if allowed else "0")
PY
    )"

    if [ -f "$LEGACY_DB" ]; then LEGACY_EXISTS="true"; fi
    if [ -f "$DEFAULT_DB" ]; then DEFAULT_EXISTS="true"; fi

    if [ "$DEFAULT_EXISTS" = "true" ] && [ "$LEGACY_EXISTS" = "false" ]; then
      echo "Using default database: $DEFAULT_DB"
      export RESEARCHVAULT_DB="$DEFAULT_DB"
    elif [ "$DEFAULT_EXISTS" = "false" ] && [ "$LEGACY_EXISTS" = "true" ]; then
      if [ "$OPENCLAW_SCAN" = "1" ] && [ "$OPENCLAW_ALLOWED" = "1" ]; then
        echo "Using OpenClaw legacy database (scan enabled): $LEGACY_DB"
        export RESEARCHVAULT_DB="$LEGACY_DB"
      else
        echo "Legacy OpenClaw DB detected, but OpenClaw scanning is not effective."
        echo "Require both: RESEARCHVAULT_PORTAL_SCAN_OPENCLAW=1 and an allowed root that contains $OPENCLAW_ROOT."
        echo "Using default path instead: $DEFAULT_DB"
        echo "Current allowed roots: $RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS"
        export RESEARCHVAULT_DB="$DEFAULT_DB"
      fi
    elif [ "$DEFAULT_EXISTS" = "true" ] && [ "$LEGACY_EXISTS" = "true" ]; then
      if [ "$OPENCLAW_SCAN" = "1" ] && [ "$OPENCLAW_ALLOWED" = "1" ]; then
        echo "Multiple vault DBs detected (default + OpenClaw scan enabled)."
      else
        echo "Multiple DBs detected; OpenClaw scan is not effective under current allowed roots. Using default DB: $DEFAULT_DB"
        export RESEARCHVAULT_DB="$DEFAULT_DB"
      fi
    else
      export RESEARCHVAULT_DB="$DEFAULT_DB"
    fi
  fi

  AUTH_FILE=".portal_auth"
  if [ -z "${RESEARCHVAULT_PORTAL_TOKEN:-}" ]; then
    if [ -f "$AUTH_FILE" ]; then
      echo "Loading token from $AUTH_FILE and exporting RESEARCHVAULT_PORTAL_TOKEN..."
      local loaded_token
      loaded_token="$(tr -d '\r\n' < "$AUTH_FILE")"
      if [ -n "$loaded_token" ]; then
        export RESEARCHVAULT_PORTAL_TOKEN="$loaded_token"
      else
        echo "Token file was empty; generating a new portal token..."
        local new_token
        new_token="$(python3 -c "import secrets; print(secrets.token_hex(24))")"
        echo "$new_token" > "$AUTH_FILE"
        chmod 600 "$AUTH_FILE"
        export RESEARCHVAULT_PORTAL_TOKEN="$new_token"
      fi
    else
      echo "Generating new portal token..."
      local new_token
      new_token="$(python3 -c "import secrets; print(secrets.token_hex(24))")"
      echo "$new_token" > "$AUTH_FILE"
      chmod 600 "$AUTH_FILE"
      export RESEARCHVAULT_PORTAL_TOKEN="$new_token"
    fi
  fi

  if [ -z "${RESEARCHVAULT_PORTAL_TOKEN:-}" ]; then
    echo "Error: missing RESEARCHVAULT_PORTAL_TOKEN after token initialization." >&2
    echo "Set RESEARCHVAULT_PORTAL_TOKEN explicitly or remove $AUTH_FILE and retry." >&2
    exit 1
  fi

  local token_url_127
  local token_url_localhost
  token_url_127="http://127.0.0.1:${FRONTEND_PORT}/#token=${RESEARCHVAULT_PORTAL_TOKEN}"
  token_url_localhost="http://localhost:${FRONTEND_PORT}/#token=${RESEARCHVAULT_PORTAL_TOKEN}"

  echo ""
  echo "=========================================================="
  echo "  Portal token is exported via RESEARCHVAULT_PORTAL_TOKEN."
  echo "  Token file: $AUTH_FILE (chmod 600)"
  echo "  Login pages:"
  echo "  http://127.0.0.1:${FRONTEND_PORT}/"
  echo "  http://localhost:${FRONTEND_PORT}/"
  if [ "${RESEARCHVAULT_PORTAL_SHOW_TOKEN:-0}" = "1" ]; then
    echo "  Tokenized URLs (explicitly requested):"
    echo "  $token_url_127"
    echo "  $token_url_localhost"
  else
    echo "  Tokenized URLs are hidden by default (set RESEARCHVAULT_PORTAL_SHOW_TOKEN=1 to print)."
  fi
  echo "=========================================================="
  echo ""

  export RESEARCHVAULT_WATCHDOG_INGEST_TOP="${RESEARCHVAULT_WATCHDOG_INGEST_TOP:-2}"
  export RESEARCHVAULT_VERIFY_INGEST_TOP="${RESEARCHVAULT_VERIFY_INGEST_TOP:-1}"

  echo "[1/4] Checking Python Dependencies..."
  UV_BIN="${UV_BIN:-$HOME/.local/bin/uv}"
  if [ ! -x "$UV_BIN" ]; then
    if command -v uv >/dev/null 2>&1; then
      UV_BIN="$(command -v uv)"
    else
      echo "Error: uv not found. Install uv or set UV_BIN." >&2
      exit 1
    fi
  fi
  echo "Using uv from $UV_BIN"
  "$UV_BIN" sync

  echo "[2/4] Checking Frontend Dependencies..."
  pushd portal/frontend >/dev/null
  if [ ! -d node_modules ]; then
    echo "Installing missing node_modules..."
    if [ -f package-lock.json ]; then
      npm ci
    else
      npm install
    fi
  fi

  local vite_bin
  vite_bin="$ROOT_DIR/portal/frontend/node_modules/.bin/vite"
  if [ ! -x "$vite_bin" ]; then
    echo "Error: vite binary not found at $vite_bin" >&2
    popd >/dev/null
    exit 1
  fi
  popd >/dev/null

  echo "[3/4] Launching Backend (FastAPI)..."
  "$UV_BIN" run "$ROOT_DIR/run_portal.py" &
  BACKEND_PID=$!
  echo "$BACKEND_PID" > "$BACKEND_PID_FILE"

  if ! await_http_ok "http://${BACKEND_HOST}:${BACKEND_PORT}/health" 20; then
    echo "Error: backend did not become ready within 20s." >&2
    start_cleanup
    exit 1
  fi

  echo "[4/4] Launching Frontend (Vite)..."
  pushd portal/frontend >/dev/null
  "$vite_bin" --host "$FRONTEND_HOST" --port "$FRONTEND_PORT" &
  FRONTEND_PID=$!
  echo "$FRONTEND_PID" > "$FRONTEND_PID_FILE"
  popd >/dev/null

  if ! await_http_ok "http://${FRONTEND_HOST}:${FRONTEND_PORT}/" 20; then
    echo "Warning: frontend did not become ready within 20s." >&2
  fi

  echo "Portal is running!"
  echo "Backend:      http://${BACKEND_HOST}:${BACKEND_PORT}/docs"
  echo "Frontend 127: http://127.0.0.1:${FRONTEND_PORT}"
  echo "Frontend loc: http://localhost:${FRONTEND_PORT}"
  if [ "${RESEARCHVAULT_PORTAL_SHOW_TOKEN:-0}" = "1" ]; then
    echo "Direct 127:   $token_url_127"
    echo "Direct loc:   $token_url_localhost"
  fi

  if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://127.0.0.1:${FRONTEND_PORT}" >/dev/null 2>&1 || true
  elif command -v xdg-open >/dev/null 2>&1 && { [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; }; then
    xdg-open "http://127.0.0.1:${FRONTEND_PORT}" >/dev/null 2>&1 || true
  fi

  trap 'start_cleanup; exit 0' INT TERM
  trap 'start_cleanup' EXIT

  set +e
  wait "$BACKEND_PID" "$FRONTEND_PID"
  local wait_status=$?
  set -e

  exit "$wait_status"
}

case "${1:-start}" in
  start)
    run_start
    ;;
  --stop|stop)
    stop_services
    ;;
  --status|status)
    status_services
    ;;
  --help|-h|help)
    usage
    ;;
  *)
    echo "Unknown command: $1" >&2
    usage >&2
    exit 1
    ;;
esac
