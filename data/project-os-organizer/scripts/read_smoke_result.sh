#!/usr/bin/env bash
set -euo pipefail

result_file="${PROJECT_OS_SMOKE_RESULT_FILE:-$HOME/.project_os/openclaw_smoke_result.txt}"

if [[ ! -f "$result_file" ]]; then
  printf 'Smoke result file not found: %s\n' "$result_file" >&2
  printf 'Run scripts/openclaw_smoke.sh first.\n' >&2
  exit 1
fi

cat "$result_file"
