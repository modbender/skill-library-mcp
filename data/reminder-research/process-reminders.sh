#!/bin/bash
# Reminder Intelligence v4 - Agent-based task executor
# 
# Evolution:
#   Gen 1: 🔍 emoji trigger (manual)
#   Gen 2: Empty notes = auto-process (list-based behavior)
#   Gen 3: Custom instructions in notes OR empty (💎 = already processed)
#   Gen 4: Agent spawning for ANY instruction (🤖 = AI processed) ← NOW
#
# Rules (universal, no exceptions):
#   1. No notes? → SKIP
#   2. Notes start with 🤖? → SKIP (already processed)
#   3. Notes exist without 🤖? → EXECUTE (spawn agent)
#
# Agent can do ANYTHING:
#   - Use skills (i-ching, librarian, weather, etc.)
#   - Edit files (ROADMAP, calendar, etc.)
#   - Call APIs (GitHub, Home Assistant, etc.)
#   - Research (web search, book search, etc.)

set -e

# Get all incomplete reminders with notes (no 🤖)
ALL_REMINDERS=$(remindctl all --json 2>/dev/null)

NEEDS_PROCESSING=$(echo "$ALL_REMINDERS" | jq -c '[
  .[] | 
  select(.isCompleted == false) |
  select(.notes != null and .notes != "") |
  select(.notes | startswith("🤖") | not)
]')

COUNT=$(echo "$NEEDS_PROCESSING" | jq 'length')

if [ "$COUNT" -eq 0 ]; then
  echo "NO_REMINDERS_TO_PROCESS"
  exit 0
fi

# Output items for agent processing
echo "$NEEDS_PROCESSING" | jq -c '.[]' | while read -r item; do
  ID=$(echo "$item" | jq -r '.id')
  TITLE=$(echo "$item" | jq -r '.title')
  NOTES=$(echo "$item" | jq -r '.notes')
  
  echo "EXECUTE|$ID|$TITLE|$NOTES"
done
