#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

project_os_cli list-projects --limit 80
project_os_cli list-sessions --limit 25
project_os_cli list-items --status open --limit 40
