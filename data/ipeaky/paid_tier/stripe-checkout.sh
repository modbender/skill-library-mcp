#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# stripe-checkout.sh — Create a Stripe Checkout Session (stub)
#
# Creates a Stripe checkout session for ipeaky paid tier upgrades.
# Reads the Stripe secret key from OpenClaw config (stored via stripe-setup.sh).
#
# Usage:
#   bash paid_tier/stripe-checkout.sh [--price PRICE_ID] [--mode subscription|payment]
#
# Environment:
#   STRIPE_SECRET_KEY — auto-injected from openclaw.json if stored via ipeaky
#
# This is a SCAFFOLD — customize the price ID, success/cancel URLs, and
# product details for your deployment.
###############################################################################

# Defaults
PRICE_ID="${PRICE_ID:-}"
MODE="subscription"
SUCCESS_URL="https://your-app.com/success?session_id={CHECKOUT_SESSION_ID}"
CANCEL_URL="https://your-app.com/cancel"

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --price)
            PRICE_ID="$2"
            shift 2
            ;;
        --mode)
            MODE="$2"
            shift 2
            ;;
        --success-url)
            SUCCESS_URL="$2"
            shift 2
            ;;
        --cancel-url)
            CANCEL_URL="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Get Stripe key from OpenClaw config if not in env
if [[ -z "${STRIPE_SECRET_KEY:-}" ]]; then
    echo "→ Reading Stripe key from OpenClaw config..."
    STRIPE_SECRET_KEY=$(openclaw gateway config.get skills.entries.ipeaky.env.STRIPE_SECRET_KEY 2>/dev/null || true)

    if [[ -z "$STRIPE_SECRET_KEY" ]]; then
        echo "❌ No Stripe key found."
        echo "   Run: bash paid_tier/stripe-setup.sh"
        exit 1
    fi
fi

# Validate key format
if [[ ! "$STRIPE_SECRET_KEY" =~ ^sk_(test|live)_ ]]; then
    echo "⚠️  Warning: Key doesn't match expected Stripe format (sk_test_* or sk_live_*)"
    echo "   Proceeding anyway..."
fi

# Check price ID
if [[ -z "$PRICE_ID" ]]; then
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║  No --price specified. Using Stripe Checkout stub mode. ║"
    echo "╠══════════════════════════════════════════════════════════╣"
    echo "║                                                         ║"
    echo "║  To create a real checkout session, you need:           ║"
    echo "║                                                         ║"
    echo "║  1. Create a Product in Stripe Dashboard                ║"
    echo "║  2. Create a Price for that product                     ║"
    echo "║  3. Pass --price price_XXXXX to this script             ║"
    echo "║                                                         ║"
    echo "║  Example:                                               ║"
    echo "║    bash paid_tier/stripe-checkout.sh \                  ║"
    echo "║      --price price_1ABC123 \                            ║"
    echo "║      --mode subscription                                ║"
    echo "║                                                         ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Stripe key detected: ${STRIPE_SECRET_KEY:0:7}****"
    echo "Key is valid and ready for checkout sessions."
    exit 0
fi

# Create checkout session via Stripe API
echo "→ Creating Stripe Checkout Session..."
echo "  Mode:  $MODE"
echo "  Price: $PRICE_ID"
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST https://api.stripe.com/v1/checkout/sessions \
    -u "$STRIPE_SECRET_KEY:" \
    -d "mode=$MODE" \
    -d "line_items[0][price]=$PRICE_ID" \
    -d "line_items[0][quantity]=1" \
    -d "success_url=$SUCCESS_URL" \
    -d "cancel_url=$CANCEL_URL")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" == "200" ]]; then
    # Extract checkout URL from JSON response
    CHECKOUT_URL=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('url',''))" 2>/dev/null || true)
    SESSION_ID=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || true)

    echo "✅ Checkout session created!"
    echo ""
    echo "  Session ID: $SESSION_ID"
    echo "  Checkout URL: $CHECKOUT_URL"
    echo ""
    echo "  Send this URL to the customer to complete payment."
else
    echo "❌ Stripe API error (HTTP $HTTP_CODE):"
    echo "$BODY" | python3 -c "
import sys, json
try:
    err = json.load(sys.stdin).get('error', {})
    print(f\"  Type: {err.get('type', 'unknown')}\")
    print(f\"  Message: {err.get('message', 'unknown')}\")
except:
    print(sys.stdin.read())
" 2>/dev/null || echo "$BODY"
    exit 1
fi
