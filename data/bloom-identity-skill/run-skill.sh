#!/bin/bash
# Bloom Identity Skill - Simple Wrapper
# Calls the working agent code

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse user ID
USER_ID=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --user-id)
      USER_ID="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# Check if agent directory exists
AGENT_DIR="/Users/andrea.unicorn/bloom-identity-card/agent"
if [ ! -d "$AGENT_DIR" ]; then
  echo "❌ Error: Agent directory not found at $AGENT_DIR"
  echo "Please clone the full repository first"
  exit 1
fi

# Generate token using the working agent code
cd "$AGENT_DIR"

# Load environment if exists
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Run token generator
npx tsx generate-fresh-token.ts 2>&1 | grep -A 1 "Dashboard URL"
