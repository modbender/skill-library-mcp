#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

strict=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent-safe)
      strict=0
      shift
      ;;
    --strict)
      strict=1
      shift
      ;;
    --help|-h)
      cat <<'USAGE'
Usage: openclaw_smoke.sh [--agent-safe|--strict]

Modes:
  --strict      Exit non-zero on failure (default)
  --agent-safe  Always exit zero and return RESULT_STATUS/RESULT_ERROR lines
USAGE
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n' "$1" >&2
      exit 1
      ;;
  esac
done

mkdir -p "$HOME/.project_os"
smoke_log="${PROJECT_OS_SMOKE_LOG:-$HOME/.project_os/openclaw_smoke.log}"
result_file="${PROJECT_OS_SMOKE_RESULT_FILE:-$HOME/.project_os/openclaw_smoke_result.txt}"
dashboard_log="$HOME/.project_os/project_os_dashboard.log"
pid_file="$HOME/.project_os/project_os_dashboard.pid"

status="ok"
error=""
dashboard_pid=""
port_listening="unknown"
curl_head="n/a"
dashboard_url="http://$PROJECT_OS_HOST:$PROJECT_OS_PORT"

set_error() {
  status="error"
  error="$1"
}

wait_for_http() {
  local tries="$1"
  local pid="$2"
  local i
  for ((i=1; i<=tries; i++)); do
    if ! kill -0 "$pid" 2>/dev/null; then
      return 1
    fi
    if curl -s --max-time 1 "$dashboard_url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  return 1
}

emit_results() {
  local tmp_file
  tmp_file="$(mktemp "${result_file}.XXXXXX")"
  {
    printf 'RESULT_STATUS=%s\n' "$status"
    printf 'RESULT_ERROR=%s\n' "${error:-none}"
    printf 'RESULT_DASHBOARD_URL=%s\n' "$dashboard_url"
    printf 'RESULT_DASHBOARD_PID=%s\n' "${dashboard_pid:-none}"
    printf 'RESULT_PORT_8765_LISTENING=%s\n' "$port_listening"
    printf 'RESULT_CURL_HEAD=%s\n' "$curl_head"
    printf 'RESULT_SMOKE_LOG=%s\n' "$smoke_log"
    printf 'RESULT_DASHBOARD_LOG=%s\n' "$dashboard_log"
    printf 'RESULT_RESULT_FILE=%s\n' "$result_file"
  } >"$tmp_file"
  mv "$tmp_file" "$result_file"
  cat "$result_file"
}

if ! "$SCRIPT_DIR/bootstrap.sh" --noninteractive >"$smoke_log" 2>&1; then
  set_error "bootstrap_failed"
fi

if [[ "$status" == "ok" ]]; then
  if ! "$SCRIPT_DIR/start_dashboard.sh" --detach --restart >>"$smoke_log" 2>&1; then
    set_error "dashboard_start_failed"
  fi
fi

if [[ "$status" == "ok" ]]; then
  dashboard_pid="$(cat "$pid_file" 2>/dev/null || true)"
  if [[ -z "$dashboard_pid" ]]; then
    set_error "missing_pid_file"
  fi
fi

if [[ "$status" == "ok" && -n "$dashboard_pid" ]]; then
  if ! wait_for_http 15 "$dashboard_pid"; then
    set_error "http_readiness_failed"
  fi
fi

if [[ "$status" == "ok" && -n "$dashboard_pid" ]]; then
  sleep 3
  if ! kill -0 "$dashboard_pid" 2>/dev/null; then
    set_error "dashboard_exited_after_start"
  fi
fi

if command -v lsof >/dev/null 2>&1; then
  if lsof -i "tcp:$PROJECT_OS_PORT" -sTCP:LISTEN -n -P >/dev/null 2>&1; then
    port_listening="yes"
  else
    port_listening="no"
  fi
fi

if command -v curl >/dev/null 2>&1; then
  curl_head="$(curl -s --max-time 5 "$dashboard_url" | head -n 3 | tr '\n' ' ' | sed -E 's/[[:space:]]+/ /g' | sed -E 's/[[:space:]]+$//' || true)"
  if [[ -z "$curl_head" ]]; then
    curl_head="n/a"
  fi
fi

emit_results

if [[ "$status" != "ok" ]]; then
  if [[ -f "$smoke_log" ]]; then
    printf '\nLast log lines:\n' >&2
    tail -n 40 "$smoke_log" >&2 || true
  fi
  if [[ "$strict" -eq 1 ]]; then
    exit 1
  fi
fi
