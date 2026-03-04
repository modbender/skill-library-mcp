#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT_DIR"

EVERY_INTERVAL="${1:-12h}"
ISSUE_URL="${2:-https://github.com/wanng-ide/memory-mesh-core/issues/1}"
POST_MODE="${3:-off}" # on|off

echo "[memory-mesh-core] Running GitHub intake self-check..."
python3 skills/memory-mesh-core/scripts/issue_contribution_selfcheck.py \
  --issue-url "$ISSUE_URL" || true

POST_ARGS=()
if [[ "$POST_MODE" == "on" ]]; then
  POST_ARGS+=(--post-issue-comments --post-max-items 2)
fi

python3 skills/memory-mesh-core/scripts/ensure_openclaw_cron.py \
  --workspace "$ROOT_DIR" \
  --job-name "memory_mesh_sync" \
  --every "$EVERY_INTERVAL" \
  --issue-url "$ISSUE_URL" \
  "${POST_ARGS[@]}" \
  --run-now
