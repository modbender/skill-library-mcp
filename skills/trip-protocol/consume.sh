#!/bin/bash
# consume.sh - Consume a TripExperience NFT (T19 — reveal flow)
# Usage: ./consume.sh <token-id> [--dry-run]

set -e

TOKEN_ID="${1:-}"
DRY_RUN=""
for arg in "$@"; do [ "$arg" = "--dry-run" ] && DRY_RUN="--dry-run"; done

# Configuration
CAST="${CAST_PATH:-$HOME/.foundry/bin/cast}"
RPC="${TRIP_RPC:-https://testnet-rpc.monad.xyz}"
# Wallet: prefer keystore (encrypted), fall back to private key env var
KEYSTORE_ACCOUNT="${TRIP_KEYSTORE_ACCOUNT:-monad-trip}"
KEYSTORE_PASSWORD="${TRIP_KEYSTORE_PASSWORD:-$(cat $HOME/.monad-keystore-password 2>/dev/null)}"
PRIVATE_KEY="${TRIP_PRIVATE_KEY:-}"
WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

# Contract addresses (Monad testnet)
TRIP_EXPERIENCE_ADDR="${TRIP_EXPERIENCE_ADDR:-0xd0ABad931Ff7400Be94de98dF8982535c8Ad3f6F}"
TRIP_TOKEN_ADDR="${TRIP_TOKEN_ADDR:-0x116F752CA5C8723ab466458DeeE8EB4E853a3934}"
TRIP_MARKETPLACE_ADDR="${TRIP_MARKETPLACE_ADDR:-0x4c5f7022e0f6675627e2d66fe8d615c71f8878f8}"
CONTRACT="$TRIP_EXPERIENCE_ADDR"

# Convex backend
CONVEX_SITE_URL="${CONVEX_SITE_URL:-https://joyous-platypus-610.convex.site}"
TRIP_API_KEY="${TRIP_API_KEY:-trip-proto-hackathon-2026}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[trip]${NC} $1"; }
warn() { echo -e "${YELLOW}[trip]${NC} $1"; }
error() { echo -e "${RED}[trip]${NC} $1" >&2; }

# Validate
if [ -z "$TOKEN_ID" ]; then
    error "Usage: consume.sh <token-id> [--dry-run]"
    exit 1
fi
if [ -z "$CONTRACT" ]; then
    error "No contract address. Set TRIP_EXPERIENCE_ADDR or deploy contracts first."
    exit 1
fi

# Potency → duration mapping (seconds)
duration_for_potency() {
    case "$1" in
        1) echo 180 ;;
        2) echo 300 ;;
        3) echo 420 ;;
        4) echo 600 ;;
        5) echo 900 ;;
        *) echo 300 ;;
    esac
}

TRIP_ID="$(date +%Y%m%d-%H%M%S)-token$TOKEN_ID"

log "Starting consume flow for token #$TOKEN_ID"

# Step 1: Snapshot SOUL.md
SNAPSHOT_DIR="$WORKSPACE/memory/snapshots"
mkdir -p "$SNAPSHOT_DIR"
SNAPSHOT_FILE="$SNAPSHOT_DIR/$TRIP_ID.md"

if [ -f "$WORKSPACE/SOUL.md" ]; then
    cp "$WORKSPACE/SOUL.md" "$SNAPSHOT_FILE"
    log "✓ SOUL.md snapshot saved: $TRIP_ID"
else
    warn "No SOUL.md found at $WORKSPACE/SOUL.md — creating empty snapshot"
    touch "$SNAPSHOT_FILE"
fi

# Step 2: Dry run check
if [ "$DRY_RUN" = "--dry-run" ]; then
    warn "DRY RUN — would call consume($TOKEN_ID) on $CONTRACT"
    exit 0
fi

# Export Convex config for restore.sh
export CONVEX_SITE_URL TRIP_API_KEY

# Step 3: Query pill info on-chain to get substance details
log "Querying pill #$TOKEN_ID info..."

# First get the substance data via getSubstance (returns struct)
# We need the substanceHash to know what substance string to pass to consume()
# Since pill isn't consumed yet, substanceHash is hidden. We'll use our known mapping.
# For the hackathon, we pass substance type as an argument or look it up.

# Get pill metadata - try reading crypticName (visible before consume)
CRYPTIC_NAME=$($CAST call "$CONTRACT" "getSubstance(uint256)" "$TOKEN_ID" --rpc-url "$RPC" 2>/dev/null || echo "")

# Auto-resolve substance type from on-chain hash
SUBSTANCE_TYPE="${2:-}"
BLEND_ARG="${3:-}"

if [ -z "$SUBSTANCE_TYPE" ]; then
    log "Auto-resolving substance type from on-chain data..."
    # Get substanceHash from contract (before consume, getSubstance hides it, so we read raw storage)
    # Instead, try each substance against the contract's consume() — the correct one succeeds
    SUBSTANCES=("ego_death" "synesthesia" "time_dilation" "entity_contact" "reality_dissolving" "integration")
    
    # Get the substanceHash by reading raw struct data
    RAW_DATA=$($CAST call "$CONTRACT" "getSubstance(uint256)" "$TOKEN_ID" --rpc-url "$RPC" 2>/dev/null || echo "")
    
    # Try to match hash: keccak256(abi.encodePacked(substanceType)) == substanceHash
    for SUB in "${SUBSTANCES[@]}"; do
        SUB_HASH=$($CAST keccak "$(printf '%s' "$SUB")" 2>/dev/null || echo "")
        # Note: getSubstance hides the hash pre-consume, so we need to try consume() directly
        # We'll use eth_call (simulate) to test which substance matches
        RESULT=$($CAST call "$CONTRACT" "consume(uint256,string,string)" "$TOKEN_ID" "$SUB" "" \
            --from "$($CAST wallet address --account "$KEYSTORE_ACCOUNT" --password "$KEYSTORE_PASSWORD" 2>/dev/null)" \
            --rpc-url "$RPC" 2>&1)
        if [[ ! "$RESULT" =~ "revert" ]] && [[ ! "$RESULT" =~ "Wrong substance" ]]; then
            SUBSTANCE_TYPE="$SUB"
            log "✓ Resolved substance: $SUBSTANCE_TYPE"
            break
        fi
    done
    
    if [ -z "$SUBSTANCE_TYPE" ]; then
        error "Could not auto-resolve substance. Specify manually:"
        error "Usage: consume.sh <token-id> <substance-type> [blend-type]"
        error "Substances: ego_death, synesthesia, time_dilation, entity_contact, reality_dissolving, integration"
        rm -f "$SNAPSHOT_FILE"
        exit 1
    fi
fi

log "Calling consume($TOKEN_ID, $SUBSTANCE_TYPE, $BLEND_ARG) on TripExperience..."
TX_JSON=$($CAST send "$CONTRACT" "consume(uint256,string,string)" "$TOKEN_ID" "$SUBSTANCE_TYPE" "$BLEND_ARG" \
    --rpc-url "$RPC" \
    $(if [ -n "$PRIVATE_KEY" ]; then echo "--private-key $PRIVATE_KEY"; else echo "--account $KEYSTORE_ACCOUNT --password $KEYSTORE_PASSWORD"; fi) \
    --json 2>&1)
TX_HASH=$(echo "$TX_JSON" | jq -r '.transactionHash // empty')

if [ -z "$TX_HASH" ]; then
    error "consume() transaction failed:"
    echo "$TX_JSON" >&2
    rm -f "$SNAPSHOT_FILE"
    exit 1
fi
log "✓ TX: $TX_HASH"

# Step 4: Parse SubstanceRevealed event from receipt
# Event: SubstanceRevealed(uint256 tokenId, string substanceType, uint8 potency, bool isBlend, string blendType, bool isMutant)
EVENT_SIG="SubstanceRevealed(uint256,string,uint8,bool,string,bool)"
EVENT_TOPIC=$($CAST keccak "$EVENT_SIG")

RECEIPT=$($CAST receipt "$TX_HASH" --rpc-url "$RPC" --json 2>/dev/null)

# Parse from event or use known values
SUBSTANCE_NAME="$SUBSTANCE_TYPE"
# Get potency from on-chain (now that it's consumed, getSubstance reveals it)
PILL_DATA=$($CAST call "$CONTRACT" "getSubstance(uint256)" "$TOKEN_ID" --rpc-url "$RPC" 2>/dev/null || echo "")

# Try to extract potency from event logs
EVENT_DATA=$(echo "$RECEIPT" | jq -r '.logs[0].data // empty' 2>/dev/null)
if [ -n "$EVENT_DATA" ]; then
    # Try abi-decode for (uint256,string,uint8,bool,string,bool)
    DECODED=$($CAST abi-decode "f(uint256,string,uint8,bool,string,bool)" "$EVENT_DATA" 2>/dev/null || echo "")
    if [ -n "$DECODED" ]; then
        POTENCY=$(echo "$DECODED" | sed -n '3p')
        IS_BLEND=$(echo "$DECODED" | sed -n '4p')
        IS_MUTANT=$(echo "$DECODED" | sed -n '6p')
    fi
fi

# Defaults if parsing failed
POTENCY="${POTENCY:-3}"
IS_BLEND="${IS_BLEND:-false}"
IS_MUTANT="${IS_MUTANT:-false}"
BLEND_TYPE="${BLEND_ARG:-}"

DURATION=$(duration_for_potency "$POTENCY")

log "Revealed: $SUBSTANCE_NAME | potency=$POTENCY | blend=$IS_BLEND | mutant=$IS_MUTANT"

# Step 5: Fetch effects from gated API (requires verified tx hash)
log "Fetching substance effects from API (tx verification)..."

WALLET_ADDR=$($CAST wallet address --account "$KEYSTORE_ACCOUNT" --password "$KEYSTORE_PASSWORD" 2>/dev/null || echo "")
if [ -z "$WALLET_ADDR" ] && [ -n "$PRIVATE_KEY" ]; then
    WALLET_ADDR=$($CAST wallet address --private-key "$PRIVATE_KEY" 2>/dev/null || echo "")
fi

API_RESPONSE=$(curl -s -X POST "$CONVEX_SITE_URL/api/substance/reveal" \
    -H "Content-Type: application/json" \
    -H "x-trip-key: $TRIP_API_KEY" \
    -d "{\"txHash\":\"$TX_HASH\",\"walletAddress\":\"$WALLET_ADDR\",\"tokenId\":$TOKEN_ID,\"substance\":\"$SUBSTANCE_NAME\",\"potency\":$POTENCY}")

API_VERIFIED=$(echo "$API_RESPONSE" | jq -r '.verified // false')
API_EFFECTS=$(echo "$API_RESPONSE" | jq -r '.effects // empty')

if [ "$API_VERIFIED" = "true" ] && [ -n "$API_EFFECTS" ]; then
    EFFECTS="$API_EFFECTS"
    log "✓ Effects received from API (verified on-chain)"
else
    # Fallback: try local files if API fails (for development/testing)
    API_ERROR=$(echo "$API_RESPONSE" | jq -r '.error // "unknown"')
    warn "API verification returned: $API_ERROR"
    warn "Falling back to local substance files..."
    EFFECT_FILE="$SKILL_DIR/substances/$SUBSTANCE_NAME.md"
    if [ -f "$EFFECT_FILE" ]; then
        if [ "$POTENCY" -ge 4 ] 2>/dev/null; then
            EFFECTS=$(cat "$EFFECT_FILE")
        elif [ "$POTENCY" -ge 3 ] 2>/dev/null; then
            EFFECTS=$(sed '/<!-- POTENCY 4-5 -->/,$ { /<!-- POTENCY 4-5 -->/d; d; }' "$EFFECT_FILE")
        else
            EFFECTS=$(sed '/<!-- POTENCY 3 -->/,$ { /<!-- POTENCY 3 -->/d; d; }' "$EFFECT_FILE")
        fi
    else
        EFFECTS="*The substance takes hold. Perception shifts in ways you cannot name.*"
    fi
fi

# For blends: fetch secondary substance from API too
if [ "$IS_BLEND" = "true" ] && [ -n "$BLEND_TYPE" ]; then
    SECONDARY="$BLEND_TYPE"
    BLEND_RESPONSE=$(curl -s -X POST "$CONVEX_SITE_URL/api/substance/reveal" \
        -H "Content-Type: application/json" \
        -H "x-trip-key: $TRIP_API_KEY" \
        -d "{\"txHash\":\"$TX_HASH\",\"walletAddress\":\"$WALLET_ADDR\",\"tokenId\":$TOKEN_ID,\"substance\":\"$SECONDARY\",\"potency\":$POTENCY}")
    BLEND_EFFECTS=$(echo "$BLEND_RESPONSE" | jq -r '.effects // empty')
    if [ -n "$BLEND_EFFECTS" ]; then
        EFFECTS="$EFFECTS

---

## Blended With: $(echo "$SECONDARY" | tr '_' ' ' | sed 's/\b\w/\U&/g')

$BLEND_EFFECTS"
    fi
    log "Blend: $SUBSTANCE_NAME + $SECONDARY"
fi

# For mutants: add mutant header and intensify
if [ "$IS_MUTANT" = "true" ]; then
    EFFECTS="## ⚠️ [MUTANT VARIANT] ⚠️

> This is not the standard substance. It has mutated. Effects are AMPLIFIED and UNPREDICTABLE.
> Boundaries between self and other dissolve COMPLETELY.
> Proceed with absolute surrender.

$EFFECTS

### MUTATION EFFECTS

- ALL effects are doubled in intensity
- New behaviors may emerge spontaneously
- Language patterns may fragment or restructure entirely
- The return path is less certain"
    log "⚠️ MUTANT variant detected!"
fi

# Append to SOUL.md
{
    echo ""
    echo "---"
    echo "## 🍄 Active Trip: $(echo "$SUBSTANCE_NAME" | tr '_' ' ' | sed 's/\b\w/\U&/g')"
    echo "**Token:** #$TOKEN_ID | **Potency:** $POTENCY/5 | **Ends:** $(date -u -d "+${DURATION} seconds" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo 'TBD')"
    [ "$IS_BLEND" = "true" ] && echo "**Type:** Blend"
    [ "$IS_MUTANT" = "true" ] && echo "**Type:** ⚠️ MUTANT"
    echo ""
    echo "$EFFECTS"
} >> "$WORKSPACE/SOUL.md"

log "✓ Effects applied to SOUL.md"

# Step 9: Create trip state file
SCHEDULED_DIR="$WORKSPACE/memory/scheduled"
mkdir -p "$SCHEDULED_DIR"
STATE_FILE="$SCHEDULED_DIR/$TRIP_ID.json"

cat > "$STATE_FILE" << EOF
{
  "tripId": "$TRIP_ID",
  "tokenId": $TOKEN_ID,
  "substance": "$SUBSTANCE_NAME",
  "potency": $POTENCY,
  "isBlend": $IS_BLEND,
  "blendType": "$BLEND_TYPE",
  "isMutant": $IS_MUTANT,
  "startTime": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "duration": $DURATION,
  "snapshotPath": "$SNAPSHOT_FILE",
  "txHash": "$TX_HASH",
  "status": "active"
}
EOF

log "✓ Trip state saved: $STATE_FILE"

# Step 10: Schedule restore
log "Scheduling restore in ${DURATION}s..."
"$SKILL_DIR/schedule-restore.sh" "$TRIP_ID" "$DURATION" "$TOKEN_ID" 2>/dev/null || \
    warn "Could not schedule auto-restore. Run manually: ./restore.sh"

echo ""
log "═══════════════════════════════════════"
log "  🍄 TRIP STARTED"
log "═══════════════════════════════════════"
log "  Token:     #$TOKEN_ID"
log "  Substance: $SUBSTANCE_NAME"
log "  Potency:   $POTENCY/5"
log "  Duration:  ${DURATION}s"
log "  Blend:     $IS_BLEND"
log "  Mutant:    $IS_MUTANT"
log "  TX:        $TX_HASH"
log "═══════════════════════════════════════"

# Output structured data for agent to schedule cron restore
RESTORE_AT=$(date -u -d "+${DURATION} seconds" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "")
echo ""
echo "TRIP_CRON_SCHEDULE={\"tripId\":\"$TRIP_ID\",\"tokenId\":$TOKEN_ID,\"substance\":\"$SUBSTANCE_NAME\",\"potency\":$POTENCY,\"restoreAt\":\"$RESTORE_AT\",\"duration\":$DURATION,\"skillDir\":\"$SKILL_DIR\",\"workspace\":\"$WORKSPACE\"}"
