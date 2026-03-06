#!/bin/bash
# Pet-Me-Master Auto-Reminder with 1h Fallback
# Checks if gotchis are ready, sends reminder, then auto-pets if no response

set -e

SKILL_DIR="$HOME/.openclaw/workspace/skills/pet-me-master"
REMINDER_FILE="$SKILL_DIR/.reminder-sent.txt"
CONTRACT="0xA99c4B08201F2913Db8D28e71d020c4298F29dBF"
RPC="https://mainnet.base.org"

echo "🔍 Checking gotchi petting status..."

# Get config
GOTCHIS=$(jq -r '.wallets[].gotchiIds[]' "$SKILL_DIR/config.json" | head -1)

if [ -z "$GOTCHIS" ]; then
  echo "❌ No gotchis configured"
  exit 1
fi

# Check first gotchi cooldown (representative)
GOTCHI_ID="$GOTCHIS"
LAST_PET=$(cast call "$CONTRACT" "getAavegotchi(uint256)" "$GOTCHI_ID" --rpc-url "$RPC" 2>/dev/null | \
  sed -n '78p' | xargs printf "%d")

if [ -z "$LAST_PET" ] || [ "$LAST_PET" = "0" ]; then
  echo "⚠️ Could not fetch last pet time"
  exit 1
fi

CURRENT=$(date +%s)
COOLDOWN=$((12 * 3600 + 300))  # 12h 5m
NEXT_PET=$((LAST_PET + COOLDOWN))
TIME_UNTIL=$((NEXT_PET - CURRENT))

echo "Last pet: $(date -d "@$LAST_PET" '+%Y-%m-%d %H:%M:%S %Z')"
echo "Next pet: $(date -d "@$NEXT_PET" '+%Y-%m-%d %H:%M:%S %Z')"
echo "Time until ready: $((TIME_UNTIL / 3600))h $(((TIME_UNTIL % 3600) / 60))m"
echo ""

# Check if reminder already sent
if [ -f "$REMINDER_FILE" ]; then
  REMINDER_TIME=$(cat "$REMINDER_FILE")
  TIME_SINCE_REMINDER=$((CURRENT - REMINDER_TIME))
  
  # If reminder was sent more than 1h ago, auto-pet!
  if [ $TIME_SINCE_REMINDER -gt 3600 ]; then
    echo "🤖 AUTO-PET FALLBACK: No response for 1h, petting now..."
    bash "$SKILL_DIR/scripts/pet-all-bankr.sh"
    rm -f "$REMINDER_FILE"
    exit 0
  else
    echo "⏳ Reminder sent $(($TIME_SINCE_REMINDER / 60))m ago, waiting for response..."
    exit 0
  fi
fi

# If ready to pet, send reminder
if [ $TIME_UNTIL -le 0 ]; then
  echo "✅ Gotchis ready! Sending reminder..."
  echo "$CURRENT" > "$REMINDER_FILE"
  
  # Send reminder via file (OpenClaw will pick it up)
  echo "🦞👻 GOTCHI PETTING REMINDER!

All 53 gotchis are ready to be petted!

Last pet: $(date -d "@$LAST_PET" '+%Y-%m-%d %H:%M %Z')

Reply within 1 hour or I'll auto-pet them as backup! 💜

To pet manually: Say 'pet gotchis' or 'pet all'
" > "$HOME/.openclaw/workspace/.gotchi-reminder.txt"
  
  echo "📬 Reminder file created!"
else
  echo "⏰ Not ready yet, checking again next cycle"
fi
