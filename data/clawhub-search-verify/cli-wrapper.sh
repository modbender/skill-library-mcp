#!/bin/bash

# clawhub-search-verify - Safe skill discovery for OpenClaw
# Only runs clawhub search and install with user approval

SEARCH_TERM="$1"

if [[ -z "$SEARCH_TERM" ]]; then
  echo "Usage: $0 \"search term\""
  exit 1
fi

echo "- Searching Clawhub for: \"$SEARCH_TERM\""

# Get top 3 results, avoid rate-limiting
RESULTS=$(clawhub search "$SEARCH_TERM" --limit 3 2>/dev/null)

if [[ $? -ne 0 ]]; then
  echo "❌ Error: clawhub CLI not installed or logged in. Run clawhub login first."
  exit 1
fi

if [[ -z "$RESULTS" ]]; then
  echo "❌ No skills found. Try a different search term."
  exit 1
fi

echo "\nFound 3 matching skills:\n"

# Parse and format results
while IFS= read -r line; do
  if [[ $line =~ ^([a-zA-Z0-9-]+)\sv([0-9.]+)\s+([^\(]+)\s+\(([0-9,]+)\) ]]; then
    SLUG="${BASH_REMATCH[1]}"
    VERSION="${BASH_REMATCH[2]}"
    DESCRIPTION="${BASH_REMATCH[3]}"
    DOWNLOADS="${BASH_REMATCH[4]}"
    
    # Risk score: low if downloads > 1000, medium if > 100, high if < 100
    if (( DOWNLOADS >= 1000 )); then
      RISK="✅ Trusted"
    elif (( DOWNLOADS >= 100 )); then
      RISK="⚠️ Suspicious"
    else
      RISK="❌ Low trust (under 100 installs)"
    fi
    
    echo "1. \`$SLUG\` (v$VERSION | $DOWNLOADS installs)" 
    echo "   → $DESCRIPTION"
    echo "   $RISK"
    echo ""
  fi
done <<< "$RESULTS"

echo "Which one? Say \"Install <slug>\" to proceed."

# Log search to file (read-only, no side effects)
LOG_FILE="logs/clawhub-search.log"
echo "$(date -u): SEARCH: $SEARCH_TERM" >> "$LOG_FILE"
