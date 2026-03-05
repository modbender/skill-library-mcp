#!/usr/bin/env bash
set -euo pipefail

# Wrapper intended for cron/automation.
# Runs sync, but first scans the would-be sync repo for secrets.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=bootstrap.sh
source "$SCRIPT_DIR/bootstrap.sh"
openclaw_github_sync_load_env \
  WORKSPACE_DIR SYNC_REPO_DIR SYNC_REMOTE REPORT_PATH

WORKSPACE_DIR="${WORKSPACE_DIR:-$HOME/.openclaw/workspace}"
SYNC_REPO_DIR="${SYNC_REPO_DIR:-$WORKSPACE_DIR/openclaw-sync-repo}"
SYNC_REMOTE="${SYNC_REMOTE:-}"
REPORT_PATH="${REPORT_PATH:-$WORKSPACE_DIR/memory/secret-scan-alert.txt}"

if [[ -z "$SYNC_REMOTE" ]]; then
  echo "SYNC_REMOTE is required" >&2
  exit 2
fi

# Run the sync export up to staging point by executing sync.sh but stopping before commits is hard.
# Instead we run sync.sh normally into SYNC_REPO_DIR, then scan SYNC_REPO_DIR, then only commit if scan passes.
# To do that, we rely on sync.sh to export first, then we scan, then we commit/push.
#
# So sync.sh has been updated to call scan_secrets.py before committing.

set +e
OUTPUT=$(SYNC_REMOTE="$SYNC_REMOTE" WORKSPACE_DIR="$WORKSPACE_DIR" SYNC_REPO_DIR="$SYNC_REPO_DIR" "$SCRIPT_DIR/sync.sh" 2>&1)
CODE=$?
set -e

echo "$OUTPUT"

if [[ $CODE -eq 3 ]]; then
  # Secret scan failed (see sync.sh contract).
  printf "%s\n" "$OUTPUT" > "$REPORT_PATH"
  echo "SECRET_ALERT: potential secrets detected; see $REPORT_PATH"
  exit 3
fi

exit $CODE
