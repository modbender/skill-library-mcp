#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# stripe-setup.sh — Store your Stripe API key via ipeaky
#
# This script guides the user through adding their Stripe secret key using
# ipeaky's secure storage (v3 flow: macOS popup → config.patch → openclaw.json).
#
# Usage:
#   bash paid_tier/stripe-setup.sh
#
# Prerequisites:
#   - macOS (uses osascript for secure input)
#   - OpenClaw installed and running
#   - ipeaky skill installed
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         ipeaky — Stripe API Key Setup                   ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                         ║"
echo "║  This will securely store your Stripe secret key in     ║"
echo "║  OpenClaw's native config via ipeaky.                   ║"
echo "║                                                         ║"
echo "║  Your key will be used for:                             ║"
echo "║    • Creating checkout sessions (paid tier upgrades)    ║"
echo "║    • Managing subscriptions                             ║"
echo "║    • Verifying payment status                           ║"
echo "║                                                         ║"
echo "║  Get your key at: https://dashboard.stripe.com/apikeys  ║"
echo "║                                                         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Use ipeaky's store_key_v3.sh to securely store the Stripe key
# Config path: skills.entries.ipeaky.env.STRIPE_SECRET_KEY
echo "→ Launching secure input popup..."
echo "  (Paste your Stripe secret key — starts with sk_test_ or sk_live_)"
echo ""

if bash "$BASE_DIR/scripts/store_key_v3.sh" \
    "Stripe" \
    "skills.entries.ipeaky.env.STRIPE_SECRET_KEY"; then
    echo ""
    echo "✅ Stripe key stored successfully!"
    echo ""
    echo "Next steps:"
    echo "  • Your key is now in openclaw.json (encrypted at rest by OS keychain)"
    echo "  • Skills can access it via STRIPE_SECRET_KEY env var"
    echo "  • Run: bash paid_tier/stripe-checkout.sh  to test a checkout session"
    echo ""
else
    echo ""
    echo "❌ Failed to store Stripe key."
    echo "   Make sure OpenClaw gateway is running: openclaw gateway status"
    exit 1
fi
