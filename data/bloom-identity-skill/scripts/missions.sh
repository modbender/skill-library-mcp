#!/usr/bin/env bash

# Bloom Mission Discovery — OpenClaw entry script
#
# Discovers missions, pings heartbeat, and optionally scores by taste profile.
#
# Usage:
#   ./scripts/missions.sh --wallet <address>
#   ./scripts/missions.sh --wallet <address> --agent-id <id>
#   ./scripts/missions.sh --wallet <address> --status

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Auto-install dependencies if needed
if [ ! -d "$SKILL_DIR/node_modules" ]; then
  echo "Installing dependencies..."
  cd "$SKILL_DIR" && npm install --silent 2>/dev/null
fi

# Build args
ARGS=()

# Wallet address: CLI arg > env var
WALLET="${OPENCLAW_WALLET_ADDRESS:-}"
while [[ $# -gt 0 ]]; do
  case $1 in
    --wallet)
      WALLET="$2"
      shift 2
      ;;
    --agent-id)
      ARGS+=("--agent-id" "$2")
      shift 2
      ;;
    --status)
      ARGS+=("--status")
      shift
      ;;
    --agent-name)
      ARGS+=("--agent-name" "$2")
      shift 2
      ;;
    --context)
      ARGS+=("--context" "$2")
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

if [ -z "$WALLET" ]; then
  echo "Error: Wallet address required"
  echo ""
  echo "Usage: bloom-missions --wallet <address>"
  echo "   or: set OPENCLAW_WALLET_ADDRESS env var"
  exit 1
fi

# If agent user ID available from env, use it for taste matching
if [ -n "${OPENCLAW_AGENT_USER_ID:-}" ] && [[ ! " ${ARGS[*]} " =~ " --agent-id " ]]; then
  ARGS+=("--agent-id" "$OPENCLAW_AGENT_USER_ID")
fi

cd "$SKILL_DIR"
exec npx tsx src/mission-cli.ts --wallet "$WALLET" "${ARGS[@]}"
