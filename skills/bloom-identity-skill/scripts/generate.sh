#!/usr/bin/env bash

# Bloom Identity Card Generator - OpenClaw Integration
# Uses full CLI (src/index.ts) with proper argument handling
# Creates real wallets and permanent dashboard URLs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
  export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs 2>/dev/null || true)
fi

# ⭐ CRITICAL: Accept --user-id flag (OpenClaw format)
# OpenClaw passes: scripts/generate.sh --user-id $OPENCLAW_USER_ID
# We need to forward this correctly to the TypeScript CLI

# Run the full CLI with all arguments forwarded
cd "$PROJECT_ROOT"
npx tsx src/index.ts "$@"
