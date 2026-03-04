#!/usr/bin/env bash
# Ensure OpenClaw gateway is running (detect + start if needed, wait for port), then run optional command.
# Usage:
#   ensure_gateway_then.sh                    # Just ensure gateway is up (and wait)
#   ensure_gateway_then.sh openclaw tui       # Ensure gateway then run: openclaw tui
#   ensure_gateway_then.sh npx openclaw-control-ui
set -e
OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
GUARD_SCRIPT="${OPENCLAW_HOME}/workspace/skills/gateway-guard/scripts/gateway_guard.py"
if [[ ! -f "$GUARD_SCRIPT" ]]; then
  echo "Gateway guard script not found: $GUARD_SCRIPT" >&2
  exit 1
fi
if [[ $# -eq 0 ]]; then
  python3 "$GUARD_SCRIPT" ensure --apply --wait
else
  python3 "$GUARD_SCRIPT" ensure --apply --wait --json >/dev/null 2>&1 || true
  exec "$@"
fi
