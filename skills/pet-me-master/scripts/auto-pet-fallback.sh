#!/bin/bash
set -e

# Auto-pet fallback - triggered 1 hour after reminder if user didn't respond
# This only runs if the user didn't manually pet after the reminder

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$HOME/.openclaw/workspace/skills/pet-me-master/config.json"
STATE_FILE="$HOME/.openclaw/workspace/skills/pet-me-master/reminder-state.json"
PET_SCRIPT="$SCRIPT_DIR/pet-via-bankr.sh"

echo "🤖 Auto-pet fallback triggered at $(date)"

# Load config
GOTCHI_IDS=($(jq -r '.gotchiIds[]' "$CONFIG_FILE"))
CONTRACT=$(jq -r '.contractAddress' "$CONFIG_FILE")
RPC_URL=$(jq -r '.rpcUrl' "$CONFIG_FILE")

# Cooldown requirement
REQUIRED_WAIT=43260
NOW=$(date +%s)

# Check if gotchis still need petting
NEED_PETTING=()

for GOTCHI_ID in "${GOTCHI_IDS[@]}"; do
  DATA=$(cast call "$CONTRACT" "getAavegotchi(uint256)" "$GOTCHI_ID" --rpc-url "$RPC_URL" 2>/dev/null)
  
  if [ -z "$DATA" ]; then
    echo "⚠️  Failed to query gotchi #$GOTCHI_ID"
    continue
  fi
  
  LAST_PET_HEX=${DATA:2498:64}
  LAST_PET_DEC=$((16#$LAST_PET_HEX))
  TIME_SINCE=$((NOW - LAST_PET_DEC))
  
  if [ $TIME_SINCE -ge $REQUIRED_WAIT ]; then
    NEED_PETTING+=("$GOTCHI_ID")
  fi
done

# If any gotchis still need petting, pet them
if [ ${#NEED_PETTING[@]} -gt 0 ]; then
  echo "🦞 User didn't respond - auto-petting ${#NEED_PETTING[@]} gotchi(s)..."
  
  PETTED=()
  FAILED=()
  
  for GOTCHI_ID in "${NEED_PETTING[@]}"; do
    echo "Petting gotchi #$GOTCHI_ID..."
    if bash "$PET_SCRIPT" "$GOTCHI_ID" >> /tmp/auto-pet.log 2>&1; then
      PETTED+=("$GOTCHI_ID")
      echo "✅ Gotchi #$GOTCHI_ID petted"
      sleep 2
    else
      FAILED+=("$GOTCHI_ID")
      echo "❌ Failed to pet gotchi #$GOTCHI_ID"
    fi
  done
  
  # Send notification about auto-petting
  if [ ${#PETTED[@]} -gt 0 ]; then
    PETTED_LIST=$(IFS=, ; echo "${PETTED[*]}")
    NOTIFY_MSG="🤖 Auto-pet fallback executed! Petted gotchi(s): #$PETTED_LIST since you were busy. Kinship +${#PETTED[@]}! 👻💜"
    echo "$NOTIFY_MSG"
    
    # Try to send notification (best effort)
    echo "$NOTIFY_MSG" > /tmp/autopet-notification.txt
  fi
  
  if [ ${#FAILED[@]} -gt 0 ]; then
    FAILED_LIST=$(IFS=, ; echo "${FAILED[*]}")
    echo "⚠️  Failed to pet: #$FAILED_LIST"
  fi
else
  echo "✅ All gotchis already petted! User must have done it manually. Great job fren! 👻"
fi

# Reset state
echo '{"lastReminder": 0, "fallbackScheduled": false}' > "$STATE_FILE"
echo "🔄 State reset, ready for next cycle"

# Schedule next check dynamically based on actual pet time
bash "$SCRIPT_DIR/schedule-dynamic-check.sh" &
echo "📅 Scheduling next check based on pet time..."

exit 0
