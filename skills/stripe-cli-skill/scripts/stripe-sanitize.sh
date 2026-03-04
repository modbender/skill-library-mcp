#!/usr/bin/env bash
set -euo pipefail

# Redact Stripe secrets from stdin or file
# Usage:
#   ./scripts/stripe-sanitize.sh logs.txt > logs.redacted.txt
#   cat logs.txt | ./scripts/stripe-sanitize.sh

if [[ "${1:-}" != "" && -f "$1" ]]; then
  INPUT=$(cat "$1")
else
  INPUT=$(cat)
fi

echo "$INPUT" \
  | sed -E 's/sk_(test|live)_[A-Za-z0-9]+/[REDACTED_STRIPE_SECRET_KEY]/g' \
  | sed -E 's/rk_(test|live)_[A-Za-z0-9]+/[REDACTED_STRIPE_RESTRICTED_KEY]/g' \
  | sed -E 's/whsec_[A-Za-z0-9]+/[REDACTED_WEBHOOK_SECRET]/g'
