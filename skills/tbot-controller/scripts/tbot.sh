#!/usr/bin/env bash
set -euo pipefail

# OpenClaw entrypoint (thin router)
# Contract: OpenClaw calls ONLY this script.
# It dispatches into Python modules that each own one responsibility.
#
#   tbot.sh ctl    ...  -> scripts/tbotctl.py
#   tbot.sh json   ...  -> scripts/tbotjson.py
#   tbot.sh status ...  -> scripts/tbotstatus.py (future)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQ_FILE="$SCRIPT_DIR/requirements.txt"

# Prefer uv (OpenClaw-native). It creates an isolated env and installs deps on demand.
if command -v uv >/dev/null 2>&1; then
  PYTHON_EXEC=(uv run --no-project --with-requirements "$REQ_FILE" python3)
elif command -v python3 >/dev/null 2>&1; then
  echo "Missing dependency: uv" >&2
  echo "Install uv (recommended): https://docs.astral.sh/uv/ (macOS: brew install uv)" >&2
  echo "(This skill expects uv for dependency isolation; python3 alone is not enough.)" >&2
  exit 2
else
  echo "Missing dependencies: uv (preferred) and python3" >&2
  echo "Install uv (recommended): https://docs.astral.sh/uv/ (macOS: brew install uv)" >&2
  exit 2
fi

cmd="${1:-}"
shift || true

case "$cmd" in
  ctl)
    exec "${PYTHON_EXEC[@]}" "$SCRIPT_DIR/tbotctl.py" "$@"
    ;;
  json)
    exec "${PYTHON_EXEC[@]}" "$SCRIPT_DIR/tbotjson.py" "$@"
    ;;
  status)
    if [[ -f "$SCRIPT_DIR/tbotstatus.py" ]]; then
      exec "${PYTHON_EXEC[@]}" "$SCRIPT_DIR/tbotstatus.py" "$@"
    fi
    echo "tbotstatus.py not implemented yet" >&2
    exit 2
    ;;
  -h|--help|"")
    cat <<'EOF'
tbot.sh — OpenClaw entrypoint (thin router)

Usage:
  scripts/tbot.sh ctl    <subcommand> [args...]
  scripts/tbot.sh json   [tbotjson args...]
  scripts/tbot.sh status [future]

Examples:
  scripts/tbot.sh ctl status
  scripts/tbot.sh ctl logs --tail 200
  scripts/tbot.sh ctl start --run-it
  scripts/tbot.sh json --ticker IBM --direction strategy.entrylong --orderRef r1 --contract stock --metric qty=500
  TBOT_WEBHOOK_URL="http://127.0.0.1:5001/webhook" RUN_IT=1 scripts/tbot.sh json --ticker NFLX --direction strategy.close --orderRef CloseNFLX50 --contract stock --metric qty=50 --key "WebhookReceived:123456"
EOF
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    echo "Run: scripts/tbot.sh --help" >&2
    exit 2
    ;;
esac
