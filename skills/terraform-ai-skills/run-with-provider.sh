#!/bin/bash
# Script wrapper to select provider config and run operations
# Usage: ./run-with-provider.sh [aws|gcp|azure|do] [script-name] [args...]

set -e

PROVIDER=$1
SCRIPT=$2
shift 2
ARGS="$@"

# Validate provider
case $PROVIDER in
  aws|gcp|azure|do|digitalocean)
    if [ "$PROVIDER" = "do" ]; then
      PROVIDER="digitalocean"
    fi
    ;;
  *)
    echo "❌ Invalid provider. Use: aws, gcp, azure, or do"
    echo ""
    echo "Usage: $0 [provider] [script] [args]"
    echo ""
    echo "Examples:"
    echo "  $0 aws batch-provider-upgrade.sh"
    echo "  $0 gcp validate-all.sh"
    echo "  $0 azure create-releases.sh"
    echo "  $0 do batch-provider-upgrade.sh"
    exit 1
    ;;
esac

# Set config path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export COPILOT_CONFIG="${SCRIPT_DIR}/config/${PROVIDER}.config"

if [ ! -f "$COPILOT_CONFIG" ]; then
  echo "❌ Config file not found: $COPILOT_CONFIG"
  exit 1
fi

echo "🔧 Using config: ${PROVIDER}.config"
echo ""

# Run the specified script
SCRIPT_PATH="${SCRIPT_DIR}/scripts/${SCRIPT}"

if [ ! -f "$SCRIPT_PATH" ]; then
  echo "❌ Script not found: $SCRIPT_PATH"
  echo ""
  echo "Available scripts:"
  ls -1 "${SCRIPT_DIR}/scripts/"
  exit 1
fi

# Execute
bash "$SCRIPT_PATH" $ARGS
