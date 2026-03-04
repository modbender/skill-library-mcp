#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

restart=0
detach=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --restart)
      restart=1
      shift
      ;;
    --detach)
      detach=1
      shift
      ;;
    --help|-h)
      cat <<'USAGE'
Usage: start_dashboard.sh [--restart] [--detach]

Options:
  --restart   Stop existing dashboard first
  --detach    Start dashboard in background and return
USAGE
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n' "$1" >&2
      exit 1
      ;;
  esac
done

existing_pid=""
if command -v lsof >/dev/null 2>&1; then
  existing_pid="$(lsof -ti "tcp:$PROJECT_OS_PORT" 2>/dev/null | head -n 1 || true)"
fi

if [[ -n "$existing_pid" && "$restart" -eq 0 ]]; then
  printf 'Dashboard already running at http://%s:%s (pid %s)\n' "$PROJECT_OS_HOST" "$PROJECT_OS_PORT" "$existing_pid"
  exit 0
fi

if [[ -n "$existing_pid" && "$restart" -eq 1 ]]; then
  kill "$existing_pid"
  sleep 1
fi

if [[ "$detach" -eq 1 ]]; then
  root="$(project_os_root)"
  py="$(project_os_python)"
  mkdir -p "$HOME/.project_os"
  log_path="$HOME/.project_os/project_os_dashboard.log"
  pid_file="$HOME/.project_os/project_os_dashboard.pid"
  helper="$SCRIPT_DIR/daemonize_command.py"
  if [[ ! -x "$helper" ]]; then
    printf 'Missing executable helper: %s\n' "$helper" >&2
    exit 1
  fi
  new_pid="$(
    "$helper" \
      --log "$log_path" \
      --pid-file "$pid_file" \
      --cwd "$root" \
      -- \
      "$py" -m project_os.cli --db "$PROJECT_OS_DB" --config "$PROJECT_OS_CONFIG" dashboard --host "$PROJECT_OS_HOST" --port "$PROJECT_OS_PORT"
  )"
  if [[ -z "$new_pid" ]]; then
    printf 'Dashboard failed to start. No process id returned.\n' >&2
    tail -n 40 "$log_path" >&2 || true
    exit 1
  fi

  ready=0
  for _ in {1..20}; do
    if ! kill -0 "$new_pid" 2>/dev/null; then
      break
    fi
    if command -v curl >/dev/null 2>&1; then
      if curl -s --max-time 1 "http://$PROJECT_OS_HOST:$PROJECT_OS_PORT" >/dev/null 2>&1; then
        ready=1
        break
      fi
    else
      ready=1
      break
    fi
    sleep 0.5
  done

  if kill -0 "$new_pid" 2>/dev/null; then
    printf 'Dashboard started at http://%s:%s (pid %s)\n' "$PROJECT_OS_HOST" "$PROJECT_OS_PORT" "$new_pid"
    printf 'Log: %s\n' "$log_path"
    if [[ "$ready" -eq 0 ]]; then
      printf 'Warning: server not yet responding; check log and retry.\n' >&2
    fi
    exit 0
  fi
  printf 'Dashboard failed to start. Check log: %s\n' "$log_path" >&2
  tail -n 40 "$log_path" >&2 || true
  exit 1
fi

project_os_cli dashboard --host "$PROJECT_OS_HOST" --port "$PROJECT_OS_PORT"
