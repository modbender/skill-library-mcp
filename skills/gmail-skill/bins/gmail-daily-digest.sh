#!/usr/bin/env bash
#
# gmail-daily-digest.sh — Daily email summary + spam/trash cleanup
#
# Usage: gmail-daily-digest.sh [account-email]
#   account-email: Gmail address (defaults to $GMAIL_ACCOUNT env var)
#
# This script combines:
# 1. Summary of ALL unread emails (across all folders, excluding spam/trash)
# 2. Spam and trash folder cleanup
#
# Designed to be run via background task wrapper for WhatsApp delivery.
#
set -euo pipefail

ACCOUNT="${1:-${GMAIL_ACCOUNT:-}}"

if [[ -z "$ACCOUNT" ]]; then
    echo "Error: No Gmail account specified." >&2
    echo "Usage: $0 <account-email>  OR  set GMAIL_ACCOUNT env var" >&2
    exit 1
fi

echo "Gmail Daily Digest for $ACCOUNT"
echo "================================"
echo ""

# Part 1: Unread email summary
echo "UNREAD EMAILS"
echo "-------------"
gog gmail messages search "is:unread -in:spam -in:trash" \
    --account "$ACCOUNT" \
    --max 50 \
    --plain 2>&1 || echo "No unread messages found"

echo ""
echo ""

# Part 2: Spam & trash cleanup
echo "SPAM & TRASH CLEANUP"
echo "--------------------"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$SCRIPT_DIR/gmail-cleanup.sh" "$ACCOUNT"

echo ""
echo "================================"
echo "Daily digest complete"
