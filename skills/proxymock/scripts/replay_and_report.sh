#!/usr/bin/env bash
# Replay traffic and produce a summary report.
# Usage: replay_and_report.sh <test-against-url> [--in dir] [--for duration] [--vus N] [--fail-if ...]
#
# Example:
#   ./replay_and_report.sh localhost:3000 --for 30s --vus 5 --fail-if "requests.failed!=0"

set -euo pipefail

TARGET="${1:?Usage: replay_and_report.sh <target-url> [proxymock replay flags...]}"
shift

LOG_FILE=$(mktemp /tmp/proxymock-replay-XXXXXX.log)

echo "▶ Replaying traffic against ${TARGET}..."
proxymock replay --test-against "$TARGET" --log-to "$LOG_FILE" "$@" 2>&1

EXIT_CODE=$?

echo ""
echo "═══════════════════════════════════════"
echo "  Replay complete (exit code: ${EXIT_CODE})"
echo "  Log file: ${LOG_FILE}"
echo "═══════════════════════════════════════"

exit $EXIT_CODE
