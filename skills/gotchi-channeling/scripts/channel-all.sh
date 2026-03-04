#!/usr/bin/env bash
#
# Channel all configured gotchis
# Reads from config.json and channels each ready gotchi
#
# Usage: ./channel-all.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$(dirname "$SCRIPT_DIR")/config.json"

echo "🔮 Channeling All Gotchis"
echo "========================="
echo ""

# Check if config exists
if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ Config not found: $CONFIG_FILE"
  echo ""
  echo "Create config.json with your gotchis:"
  echo '{'
  echo '  "channeling": ['
  echo '    {"parcelId": "867", "gotchiId": "9638"}'
  echo '  ]'
  echo '}'
  exit 1
fi

# Read gotchis from config
GOTCHIS=$(jq -r '.channeling[] | "\(.gotchiId):\(.parcelId)"' "$CONFIG_FILE")

if [ -z "$GOTCHIS" ]; then
  echo "❌ No gotchis configured in $CONFIG_FILE"
  exit 1
fi

TOTAL=0
READY=0
WAITING=0
CHANNELED=0
FAILED=0

echo "📊 Checking gotchis..."
echo ""

# Check each gotchi
while IFS=: read -r GOTCHI_ID PARCEL_ID; do
  TOTAL=$((TOTAL + 1))
  
  echo "👻 Gotchi #$GOTCHI_ID (Parcel #$PARCEL_ID)"
  
  # Check cooldown
  COOLDOWN_RESULT=$("$SCRIPT_DIR/check-cooldown.sh" "$GOTCHI_ID" 2>/dev/null || echo "waiting:0")
  
  if [[ "$COOLDOWN_RESULT" =~ ^ready ]]; then
    echo "   ✅ Ready to channel!"
    READY=$((READY + 1))
    
    # Channel this gotchi
    if "$SCRIPT_DIR/channel.sh" "$GOTCHI_ID" "$PARCEL_ID" > /tmp/channel-${GOTCHI_ID}.log 2>&1; then
      echo "   ✅ Channeled successfully!"
      CHANNELED=$((CHANNELED + 1))
      
      # Extract rewards from log
      REWARDS=$(grep "Total:" /tmp/channel-${GOTCHI_ID}.log | tail -1 || echo "")
      if [ -n "$REWARDS" ]; then
        echo "   💎 $REWARDS"
      fi
    else
      echo "   ❌ Channeling failed (see /tmp/channel-${GOTCHI_ID}.log)"
      FAILED=$((FAILED + 1))
    fi
  else
    WAIT_TIME=$(echo "$COOLDOWN_RESULT" | cut -d: -f2)
    HOURS=$((WAIT_TIME / 3600))
    MINS=$(((WAIT_TIME % 3600) / 60))
    echo "   ⏰ Wait ${HOURS}h ${MINS}m"
    WAITING=$((WAITING + 1))
  fi
  
  echo ""
done <<< "$GOTCHIS"

# Summary
echo "============================================"
echo "📊 CHANNELING SUMMARY"
echo "============================================"
echo "Total gotchis: $TOTAL"
echo "Ready: $READY"
echo "Channeled: $CHANNELED ✅"
echo "Failed: $FAILED $([ $FAILED -gt 0 ] && echo '❌' || echo '')"
echo "Still waiting: $WAITING ⏰"
echo ""

if [ $CHANNELED -gt 0 ]; then
  echo "✅ Successfully channeled $CHANNELED gotchi(s)!"
  echo ""
  echo "LFGOTCHi! 🦞🔮💜"
elif [ $READY -eq 0 ]; then
  echo "⏰ No gotchis ready to channel yet."
  echo "Check back later! 👻"
else
  echo "⚠️  Some gotchis were ready but channeling failed."
  echo "Check logs in /tmp/channel-*.log"
fi

echo ""

exit 0
