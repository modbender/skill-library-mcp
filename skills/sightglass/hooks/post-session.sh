#!/usr/bin/env bash
set -euo pipefail

# Called after a coding agent session ends.
# Analyzes what happened and outputs a summary.

SESSION_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/sightglass/sessions"
SESSION_FILE="$SESSION_DIR/current"

if [[ ! -f "$SESSION_FILE" ]]; then
  echo "⚠️  No active sightglass session found"
  exit 0
fi

START_EPOCH=$(grep -o '"start_epoch": [0-9]*' "$SESSION_FILE" | grep -o '[0-9]*')
START_TIME=$(grep -o '"start": "[^"]*"' "$SESSION_FILE" | cut -d'"' -f4)

if ! command -v sightglass &>/dev/null; then
  echo "❌ sightglass CLI not found" >&2
  exit 1
fi

echo "🔍 Sightglass: analyzing session since $START_TIME..."
echo ""

# Run analysis
RESULT=$(sightglass analyze --since "$START_TIME" --format json 2>/dev/null) || {
  echo "⚠️  Analysis returned no data (short session or no agent activity detected)"
  rm -f "$SESSION_FILE"
  exit 0
}

# Extract key findings
RISKS=$(echo "$RESULT" | grep -o '"risk_count": [0-9]*' | grep -o '[0-9]*' || echo "0")
TRAINING_RECALL=$(echo "$RESULT" | grep -o '"training_recall_pct": [0-9.]*' | grep -o '[0-9.]*' || echo "?")
ALTERNATIVES=$(echo "$RESULT" | grep -o '"alternatives_missed": [0-9]*' | grep -o '[0-9]*' || echo "0")
TOTAL_DEPS=$(echo "$RESULT" | grep -o '"total_dependencies": [0-9]*' | grep -o '[0-9]*' || echo "0")

echo "📊 Session Summary"
echo "  Dependencies added: $TOTAL_DEPS"
echo "  Risks found: $RISKS"
echo "  Training recall: ${TRAINING_RECALL}%"
echo "  Alternatives missed: $ALTERNATIVES"

if [[ "$RISKS" -gt 0 ]] 2>/dev/null; then
  echo ""
  echo "  ⚠️  Run 'sightglass analyze --since $START_TIME' for details"
fi

# Archive session
mv "$SESSION_FILE" "$SESSION_DIR/session-$(date +%s).json" 2>/dev/null || true
