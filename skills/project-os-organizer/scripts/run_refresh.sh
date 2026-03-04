#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

compact="${PROJECT_OS_COMPACT:-0}"
if [[ "${1:-}" == "--compact" ]]; then
  compact=1
fi

"$SCRIPT_DIR/setup_test_config.py"
project_os_cli init
project_os_cli refresh
if [[ "$compact" -eq 0 ]]; then
  project_os_cli list-projects --limit 140
fi
