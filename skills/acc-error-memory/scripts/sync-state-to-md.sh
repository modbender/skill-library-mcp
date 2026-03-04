#!/bin/bash
# Syncs acc-state.json → ACC_STATE.md for prompt injection

STATE_JSON="$HOME/.openclaw/workspace/memory/acc-state.json"
STATE_MD="$HOME/.openclaw/workspace/memory/ACC_STATE.md"

if [ ! -f "$STATE_JSON" ]; then
    echo "No acc-state.json found"
    exit 0
fi

# Extract data from JSON
LAST_UPDATED=$(jq -r '.lastUpdated // "unknown"' "$STATE_JSON")
TOTAL_ERRORS=$(jq -r '.stats.totalErrorsLogged // 0' "$STATE_JSON")
TOTAL_RESOLVED=$(jq -r '.stats.totalResolved // 0' "$STATE_JSON")

# Build the markdown
cat > "$STATE_MD" << 'HEADER'
# ACC_STATE.md — Error Patterns & Lessons

*Auto-generated from acc-state.json*

## Active Error Patterns

HEADER

# Add active patterns
jq -r '.activePatterns | to_entries[] | "### " + (if .value.severity == "critical" then "🔴 CRITICAL" elif .value.severity == "warning" then "⚠️ WARNING" else "📝" end) + ": " + .key + " (" + (.value.count|tostring) + " occurrences)\n**Last seen:** " + .value.lastSeen + "\n**Context:** " + (.value.context | split("\n")[0] | .[0:100]) + "...\n"' "$STATE_JSON" >> "$STATE_MD"

cat >> "$STATE_MD" << FOOTER

---

## How This Works

The ACC watches for correction signals ("no that's wrong", "???", etc.) and tracks patterns.

**Before responding:** Am I about to repeat a known error pattern?

---

## Stats
- Total errors logged: $TOTAL_ERRORS
- Patterns resolved: $TOTAL_RESOLVED
- Last updated: $LAST_UPDATED
FOOTER

echo "✅ Synced ACC_STATE.md"
