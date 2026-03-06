#!/bin/bash
# Dynamically schedule next cooldown check after petting

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$HOME/.openclaw/workspace/skills/pet-me-master/config.json"

# Get last pet time from blockchain
GOTCHI_ID=$(jq -r '.gotchiIds[0]' "$CONFIG_FILE")
CONTRACT=$(jq -r '.contractAddress' "$CONFIG_FILE")
RPC_URL=$(jq -r '.rpcUrl' "$CONFIG_FILE")

DATA=$(cast call "$CONTRACT" "getAavegotchi(uint256)" "$GOTCHI_ID" --rpc-url "$RPC_URL" 2>/dev/null)

if [ -z "$DATA" ]; then
  echo "[$(date)] ❌ Failed to query blockchain for scheduling"
  exit 1
fi

# Extract last pet timestamp
LAST_PET_HEX=${DATA:2498:64}
LAST_PET_DEC=$((16#$LAST_PET_HEX))
NOW=$(date +%s)

# Calculate when to check (12h 5min after pet)
CHECK_AT=$(($LAST_PET_DEC + 43500))
SECONDS_UNTIL=$(($CHECK_AT - $NOW))

if [ $SECONDS_UNTIL -lt 60 ]; then
  echo "[$(date)] ⚠️ Check time already passed or too soon, running now"
  bash "$SCRIPT_DIR/check-and-remind.sh"
  exit 0
fi

# Schedule with 'at'
CHECK_TIME=$(date -d @$CHECK_AT +"%H:%M %Y-%m-%d")

echo "bash $SCRIPT_DIR/check-and-remind.sh" | at "$CHECK_TIME" 2>/dev/null && {
  echo "[$(date)] ✅ Scheduled check for $CHECK_TIME (12h 5min after pet)"
  exit 0
}

# Fallback: background sleep if 'at' unavailable
(sleep $SECONDS_UNTIL && bash "$SCRIPT_DIR/check-and-remind.sh" >> ~/.openclaw/logs/pet-me-master.log 2>&1) &
echo "[$(date)] ✅ Scheduled check via background process (in ${SECONDS_UNTIL}s)"

