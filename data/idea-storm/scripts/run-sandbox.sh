#!/usr/bin/env bash
# run-sandbox.sh - Run Claude Code in Docker sandbox for idea-lab experiments
# Usage: ./run-sandbox.sh <experiment-id> "<prompt>"
# Or:    ./run-sandbox.sh <experiment-id> --file PROMPT.md
set -euo pipefail

EXPERIMENT_ID="${1:?Usage: $0 <experiment-id> \"<prompt>\" | --file <file>}"
shift

# Resolve experiment directory
WORKSPACE="${OPENCLAW_WORKSPACE:-/root/.openclaw/workspace}"
EXP_DIR="$WORKSPACE/experiments/$EXPERIMENT_ID"

if [[ ! -d "$EXP_DIR" ]]; then
  echo "❌ Experiment directory not found: $EXP_DIR"
  exit 1
fi

# Get prompt
if [[ "${1:-}" == "--file" ]]; then
  PROMPT_FILE="${2:?Missing file path after --file}"
  [[ "$PROMPT_FILE" != /* ]] && PROMPT_FILE="$EXP_DIR/$PROMPT_FILE"
  PROMPT="$(cat "$PROMPT_FILE")"
else
  PROMPT="$*"
fi

# Extract API config from openclaw.json
OC_CONFIG="${OPENCLAW_CONFIG:-/root/.openclaw/openclaw.json}"
API_KEY=$(python3 -c "import json; print(json.load(open('$OC_CONFIG'))['models']['providers']['cc']['apiKey'])")
BASE_URL=$(python3 -c "import json; print(json.load(open('$OC_CONFIG'))['models']['providers']['cc']['baseUrl'])")

# Ensure experiment dir is writable by container user (uid 1000)
chmod 777 "$EXP_DIR" 2>/dev/null || true

echo "🐳 Running Claude Code in sandbox..."
echo "   Experiment: $EXPERIMENT_ID"
echo "   Directory: $EXP_DIR"
echo ""

docker run --rm -t \
  -e ANTHROPIC_AUTH_TOKEN="$API_KEY" \
  -e ANTHROPIC_BASE_URL="$BASE_URL" \
  -v "$EXP_DIR":/workspace \
  idea-lab-sandbox \
  bash -c "cd /workspace && git init -q 2>/dev/null; claude --print --dangerously-skip-permissions \"$PROMPT\""
