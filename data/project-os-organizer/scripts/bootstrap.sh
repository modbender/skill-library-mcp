#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

start_dashboard=0
compact=0
skip_status=0
detach_dashboard=0
quick_setup=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dashboard)
      start_dashboard=1
      shift
      ;;
    --dashboard-detach)
      start_dashboard=1
      detach_dashboard=1
      shift
      ;;
    --compact)
      compact=1
      shift
      ;;
    --no-status)
      skip_status=1
      shift
      ;;
    --noninteractive)
      compact=1
      skip_status=1
      detach_dashboard=1
      quick_setup=1
      shift
      ;;
    --noninteractive-full)
      compact=1
      skip_status=1
      detach_dashboard=1
      quick_setup=0
      shift
      ;;
    --quick)
      quick_setup=1
      shift
      ;;
    --help|-h)
      cat <<'USAGE'
Usage: bootstrap.sh [--dashboard] [--dashboard-detach] [--compact] [--no-status] [--quick] [--noninteractive] [--noninteractive-full]

Runs first-time OpenClaw setup for Project OS:
1) write/update test config
2) init db
3) refresh projects/sessions
4) write memory snapshot
5) print quick status

Options:
  --dashboard         Start dashboard in foreground
  --dashboard-detach  Start dashboard in background
  --compact           Reduce verbose output
  --no-status         Skip quick status listing
  --quick             Skip refresh; only ensure config/db + memory
  --noninteractive    Compact + no-status + detached dashboard + quick mode (timeout-safe)
  --noninteractive-full
                      Compact + no-status + detached dashboard with full refresh
USAGE
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n' "$1" >&2
      exit 1
      ;;
  esac
done

print_runtime_config
if [[ "$quick_setup" -eq 1 ]]; then
  "$SCRIPT_DIR/setup_test_config.py"
  project_os_cli init
else
  if [[ "$compact" -eq 1 ]]; then
    PROJECT_OS_COMPACT=1 "$SCRIPT_DIR/run_refresh.sh" --compact
  else
    "$SCRIPT_DIR/run_refresh.sh"
  fi
fi
"$SCRIPT_DIR/write_memory.sh"
if [[ "$skip_status" -eq 0 ]]; then
  "$SCRIPT_DIR/quick_status.sh"
fi

if [[ "$start_dashboard" -eq 1 ]]; then
  printf 'Starting dashboard at http://%s:%s\n' "$PROJECT_OS_HOST" "$PROJECT_OS_PORT"
  if [[ "$detach_dashboard" -eq 1 ]]; then
    "$SCRIPT_DIR/start_dashboard.sh" --detach --restart
  else
    exec "$SCRIPT_DIR/start_dashboard.sh"
  fi
fi

if [[ "$quick_setup" -eq 1 ]]; then
  printf 'OpenClaw quick setup complete. Run bootstrap.sh --noninteractive-full for full refresh.\n'
else
  printf 'OpenClaw setup complete. Run start_dashboard.sh when you want the UI.\n'
fi
