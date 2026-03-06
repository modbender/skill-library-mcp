#!/usr/bin/env bash
set -euo pipefail

# Safe local webhook listener wrapper for Stripe CLI
# Usage:
#   ./scripts/stripe-dev-listen.sh localhost:4242/webhook
#   EVENTS=checkout.session.completed,invoice.paid ./scripts/stripe-dev-listen.sh localhost:4242/webhook

FORWARD_TO="${1:-localhost:4242/webhook}"
EVENTS="${EVENTS:-checkout.session.completed,invoice.paid,invoice.payment_failed,customer.subscription.updated,customer.subscription.deleted}"

if ! command -v stripe >/dev/null 2>&1; then
  echo "[ERROR] stripe CLI not found in PATH"
  exit 1
fi

if [[ "$FORWARD_TO" != localhost* && "$FORWARD_TO" != 127.0.0.1* ]]; then
  echo "[WARN] forward target is not localhost: $FORWARD_TO"
  echo "[WARN] confirm this is intended (Ctrl+C to abort)"
  sleep 3
fi

echo "[INFO] Starting stripe listen"
echo "[INFO] events: $EVENTS"
echo "[INFO] forward-to: $FORWARD_TO"
stripe listen --events "$EVENTS" --forward-to "$FORWARD_TO"
