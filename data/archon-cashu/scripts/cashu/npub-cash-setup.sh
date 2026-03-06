#!/bin/bash
# Archon Cashu Wallet — npub.cash Lightning Address Setup
# Enables receiving Lightning payments as cashu tokens via Nostr DMs
#
# npub.cash provides a Lightning address for any Nostr npub:
#   <npub>@npub.cash
#
# Flow: Someone pays your Lightning address → npub.cash mints cashu tokens
#       → delivers via NIP-17 encrypted DM → you redeem with receive.sh
#
# Usage: npub-cash-setup.sh [--check] [--claim]
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh" > /dev/null 2>&1

# Get npub from Archon DID (derive Nostr keys)
get_npub() {
    # Try archon nostr derivation
    local NOSTR_SCRIPT="$SCRIPT_DIR/../nostr/derive-nostr.sh"
    if [ -x "$NOSTR_SCRIPT" ]; then
        NPUB=$("$NOSTR_SCRIPT" 2>/dev/null | grep -oP 'npub1[a-z0-9]+' | head -1)
    fi

    # Fallback: check env
    if [ -z "$NPUB" ] && [ -n "$NOSTR_NPUB" ]; then
        NPUB="$NOSTR_NPUB"
    fi

    # Fallback: check nostr.env
    if [ -z "$NPUB" ] && [ -f "$HOME/.config/hex/nostr.env" ]; then
        source "$HOME/.config/hex/nostr.env"
        NPUB="${NOSTR_NPUB:-}"
    fi

    if [ -z "$NPUB" ]; then
        echo "Error: Could not determine npub. Set NOSTR_NPUB in config or run derive-nostr.sh" >&2
        exit 1
    fi
    echo "$NPUB"
}

check_address() {
    local NPUB="$1"
    local ADDR="${NPUB}@npub.cash"
    
    echo "⚡ Lightning Address: $ADDR"
    echo ""
    
    # Check LNURL endpoint
    local RESPONSE=$(curl -s "https://npub.cash/.well-known/lnurlp/$NPUB")
    local TAG=$(echo "$RESPONSE" | jq -r '.tag // empty')
    
    if [ "$TAG" = "payRequest" ]; then
        local MIN=$(echo "$RESPONSE" | jq -r '.minSendable // 0')
        local MAX=$(echo "$RESPONSE" | jq -r '.maxSendable // 0')
        local MIN_SATS=$((MIN / 1000))
        local MAX_SATS=$((MAX / 1000))
        echo "✅ Active!"
        echo "   Min: $MIN_SATS sats"
        echo "   Max: $MAX_SATS sats"
        echo "   Nostr zaps: $(echo "$RESPONSE" | jq -r '.allowsNostr')"
        echo ""
        echo "Anyone can send you sats at: $ADDR"
        echo "Tokens arrive as cashu in your Nostr DMs (NIP-17)."
        echo "Redeem with: receive-nostr.sh or use a Nostr cashu wallet."
    else
        echo "❌ Not active or error"
        echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
    fi
}

claim_tokens() {
    local NPUB="$1"
    echo "📬 Checking Nostr DMs for cashu tokens..."
    echo ""
    
    # Check for cashu tokens in NIP-17 DMs
    local NOSTR_CHECK="$SCRIPT_DIR/../nostr/scripts/nostr-check-dms.sh"
    if [ ! -x "$NOSTR_CHECK" ]; then
        NOSTR_CHECK="$HOME/clawd/skills/nostr/scripts/nostr-check-dms.sh"
    fi
    
    if [ -x "$NOSTR_CHECK" ]; then
        # Get recent DMs and scan for cashu tokens
        DMS=$("$NOSTR_CHECK" 10 2>/dev/null || true)
        TOKENS=$(echo "$DMS" | grep -oP 'cashu[AB][A-Za-z0-9_+/=-]{20,}' || true)
        
        if [ -n "$TOKENS" ]; then
            echo "🎫 Found cashu token(s) in Nostr DMs!"
            for TOKEN in $TOKENS; do
                RESULT=$($CASHU_BIN receive "$TOKEN" 2>&1) || true
                if echo "$RESULT" | grep -q "Received"; then
                    SATS=$(echo "$RESULT" | grep -oP '\d+(?= sat)' | head -1)
                    echo "   ✅ Received $SATS sats"
                elif echo "$RESULT" | grep -qi "already spent"; then
                    echo "   ⚠️  Already redeemed"
                else
                    echo "   ❌ $RESULT"
                fi
            done
        else
            echo "No cashu tokens found in recent DMs."
        fi
    else
        echo "⚠️  Nostr DM check script not found."
        echo "Check DMs manually with: nak req -k 1059 ..."
    fi
    
    echo ""
    echo "💰 Balance:"
    $CASHU_BIN balance 2>&1
}

# Main
NPUB=$(get_npub)

case "${1:-}" in
    --check)
        check_address "$NPUB"
        ;;
    --claim)
        claim_tokens "$NPUB"
        ;;
    *)
        echo "npub.cash Lightning Address"
        echo "=========================="
        echo ""
        check_address "$NPUB"
        echo ""
        echo "Commands:"
        echo "  --check   Verify your Lightning address is active"
        echo "  --claim   Check Nostr DMs for incoming cashu tokens"
        ;;
esac
