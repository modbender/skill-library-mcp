#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

project_os_cli write-memory --out "$PROJECT_OS_MEMORY" --limit 220
printf 'Memory file: %s\n' "$PROJECT_OS_MEMORY"
