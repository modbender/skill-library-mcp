#!/usr/bin/env bash
set -euo pipefail

# Standalone analysis script
# Usage: ./analyze.sh [--since <time>] [--session <id>] [--format <fmt>] [--push]

ARGS=()
PUSH=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --since)  ARGS+=(--since "$2"); shift 2 ;;
    --session) ARGS+=(--session "$2"); shift 2 ;;
    --format) ARGS+=(--format "$2"); shift 2 ;;
    --push)   PUSH=true; shift ;;
    *)        ARGS+=("$1"); shift ;;
  esac
done

if ! command -v sightglass &>/dev/null; then
  echo "❌ sightglass CLI not found. Run setup.sh first." >&2
  exit 1
fi

echo "🔍 Running analysis..."
sightglass analyze "${ARGS[@]}"

if [[ "$PUSH" == "true" ]]; then
  echo ""
  echo "📤 Pushing results to https://sightglass.dev..."
  sightglass analyze "${ARGS[@]}" --push
fi
