#!/bin/bash
# show-gotchi.sh - Display gotchi with image + stats in Telegram format
# This is the OFFICIAL way to show a gotchi: PNG image with caption

set -e

GOTCHI_ID="$1"

if [ -z "$GOTCHI_ID" ]; then
  echo "Usage: bash show-gotchi.sh <gotchi-id>"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Fetch gotchi data and generate PNG
cd "$SKILL_DIR"
bash scripts/find-gotchi.sh "$GOTCHI_ID"

# Read JSON data
JSON_FILE="./gotchi-$GOTCHI_ID.json"
PNG_FILE="./gotchi-$GOTCHI_ID.png"

if [ ! -f "$JSON_FILE" ] || [ ! -f "$PNG_FILE" ]; then
  echo "❌ Failed to generate gotchi files"
  exit 1
fi

# Parse JSON for display
NAME=$(jq -r '.name' "$JSON_FILE")
BRS=$(jq -r '.brs' "$JSON_FILE")
KINSHIP=$(jq -r '.kinship' "$JSON_FILE")
LEVEL=$(jq -r '.level' "$JSON_FILE")
XP=$(jq -r '.experience' "$JSON_FILE")
HAUNT=$(jq -r '.hauntId' "$JSON_FILE")
COLLATERAL=$(jq -r '.collateral' "$JSON_FILE")

# Get traits (modified with wearables)
NRG=$(jq -r '.modifiedTraits.energy' "$JSON_FILE")
AGG=$(jq -r '.modifiedTraits.aggression' "$JSON_FILE")
SPK=$(jq -r '.modifiedTraits.spookiness' "$JSON_FILE")
BRN=$(jq -r '.modifiedTraits.brainSize' "$JSON_FILE")

# Calculate rarity tier
TIER="COMMON"
if [ "$BRS" -ge 580 ]; then
  TIER="GODLIKE"
elif [ "$BRS" -ge 525 ]; then
  TIER="MYTHICAL"
elif [ "$BRS" -ge 475 ]; then
  TIER="UNCOMMON"
fi

# Check wearables
EQUIPPED_COUNT=$(jq -r '.equippedWearables | length' "$JSON_FILE" 2>/dev/null || echo "0")
if [ "$EQUIPPED_COUNT" = "0" ]; then
  WEARABLES="None equipped"
else
  WEARABLES="$EQUIPPED_COUNT equipped"
fi

# Map collateral address to name (Base mainnet)
case "$COLLATERAL" in
  "0x20D3922b4a1A8560E1aC99FBA4faDe0c849e2142")
    COLLATERAL="WETH"
    ;;
  "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
    COLLATERAL="USDC"
    ;;
  "0x4200000000000000000000000000000000000006")
    COLLATERAL="WETH"
    ;;
  *)
    # Keep address if unknown
    ;;
esac

# Output format for OpenClaw message tool
echo "PNG_PATH=$PNG_FILE"
echo "CAPTION<<EOF
👻 **Gotchi #$GOTCHI_ID - $NAME**

**📊 Stats:**
⭐ BRS: **$BRS** ($TIER tier)
💜 Kinship: **$KINSHIP**
🎮 Level: **$LEVEL** (XP: $XP)
👻 Haunt: **$HAUNT**
💎 Collateral: **$COLLATERAL**

**🎭 Traits:**
⚡ Energy: **$NRG**
👊 Aggression: **$AGG**
👻 Spookiness: **$SPK**
🧠 Brain Size: **$BRN**

**👔 Wearables:** $WEARABLES

LFGOTCHi! 🦞🚀
EOF"
