#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

usage() {
  cat <<'USAGE'
Usage:
  project_router.sh "<user message>"

Examples:
  project_router.sh "What am I working on today?"
  project_router.sh "Show my projects"
  project_router.sh "Next for project-os: run smoke tests"
USAGE
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

message="$*"
if [[ -z "$message" ]]; then
  message="show my projects"
fi

if [[ ! -f "$PROJECT_OS_DB" || ! -f "$PROJECT_OS_CONFIG" ]]; then
  "$SCRIPT_DIR/bootstrap.sh" --quick --compact --no-status >/dev/null
fi

root="$(project_os_root)"
py="$(project_os_python "$root")"
(
  cd "$root"
  "$py" -m project_os.router \
    --db "$PROJECT_OS_DB" \
    --message "$message" \
    --scripts-dir "$SCRIPT_DIR" \
    --host "$PROJECT_OS_HOST" \
    --port "$PROJECT_OS_PORT"
)
