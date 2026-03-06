#!/bin/bash
# ACC: Analyze yesterday's transcript for errors
# Called by daily cron job

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
STATE_FILE="$WORKSPACE/memory/acc-state.json"
TRANSCRIPTS_DIR="$HOME/.openclaw/sessions"

echo "⚡ ACC Daily Analysis"
echo "===================="

# Find yesterday's main session transcript
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d 'yesterday' +%Y-%m-%d)
echo "Analyzing: $YESTERDAY"

# Get list of transcript files modified yesterday or today (to catch spanning sessions)
# The cron agent will read these and analyze them

echo ""
echo "📋 Transcript files to analyze:"
find "$TRANSCRIPTS_DIR" -name "*.jsonl" -mtime -2 2>/dev/null | head -10

echo ""
echo "📊 Current ACC State:"
cat "$STATE_FILE" | python3 -c "
import json, sys
state = json.load(sys.stdin)
active = state.get('activePatterns', {})
resolved = state.get('resolved', {})
print(f'Active patterns: {len(active)}')
print(f'Resolved patterns: {len(resolved)}')
for name, data in active.items():
    print(f'  - {name}: {data.get(\"count\", 0)}x ({data.get(\"severity\", \"normal\")})')
"

echo ""
echo "🔍 Analysis task for agent:"
echo "1. Read recent transcripts"
echo "2. Look for: user corrections, 'no/wrong', frustration, confusion"
echo "3. Identify error patterns"
echo "4. Call log-error.sh for each found"
echo "5. Run resolve-check.sh to archive old patterns"
