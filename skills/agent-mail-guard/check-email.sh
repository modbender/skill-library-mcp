#!/usr/bin/env bash
# =============================================================================
# check-email.sh — Fetch unread emails via gog CLI, sanitize, output clean JSON
# =============================================================================
#
# Usage:
#   ./check-email.sh [--raw] [--help]
#
# Options:
#   --raw   Skip audit logging (just output sanitized JSON)
#   --help  Show this help message
#
# Environment:
#   EMAIL_ACCOUNTS  Comma-separated list of Gmail accounts to check
#                   Default: reads from accounts.conf or uses $USER
#   EMAIL_QUERY     Gmail search query override
#                   Default: 'is:unread -category:promotions -category:social
#                             -category:updates newer_than:2h'
#
# Requires: gog CLI (https://github.com/liamg/gog), python3
# =============================================================================

set -euo pipefail

# --- Help ---
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    sed -n '2,/^# =====/{ /^# =====/d; s/^# \?//p }' "$0"
    exit 0
fi

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SANITIZER="$SCRIPT_DIR/sanitizer.py"
AUDIT="$SCRIPT_DIR/audit.py"
ACCOUNTS_CONF="$SCRIPT_DIR/accounts.conf"

# Load accounts: env var > config file > empty
if [ -n "${EMAIL_ACCOUNTS:-}" ]; then
    IFS=',' read -ra ACCOUNTS <<< "$EMAIL_ACCOUNTS"
elif [ -f "$ACCOUNTS_CONF" ]; then
    mapfile -t ACCOUNTS < <(grep -v '^\s*#' "$ACCOUNTS_CONF" | grep -v '^\s*$')
else
    echo '[]'
    exit 0
fi

# Gmail search query
SEARCH_QUERY="${EMAIL_QUERY:-is:unread -category:promotions -category:social -category:updates newer_than:2h}"

# --- Fetch and sanitize ---
all_emails="[]"

for account in "${ACCOUNTS[@]}"; do
    account="$(echo "$account" | xargs)"  # trim whitespace
    [ -z "$account" ] && continue

    # Search for matching message IDs
    ids=$(gog gmail search "$SEARCH_QUERY" --account "$account" 2>/dev/null | grep -oE '[a-f0-9]{10,}' || true)
    [ -z "$ids" ] && continue

    while IFS= read -r msg_id; do
        [ -z "$msg_id" ] && continue

        # Read individual email via gog
        raw_output=$(gog gmail read "$msg_id" --account "$account" 2>/dev/null || true)
        [ -z "$raw_output" ] && continue

        # Parse gog text output into structured fields
        sender=$(echo "$raw_output" | grep -m1 '^From:' | sed 's/^From: //' || echo "")
        subject=$(echo "$raw_output" | grep -m1 '^Subject:' | sed 's/^Subject: //' || echo "")
        date=$(echo "$raw_output" | grep -m1 '^Date:' | sed 's/^Date: //' || echo "")
        body=$(echo "$raw_output" | sed '1,/^$/d')

        # Build JSON and sanitize
        email_json=$(python3 -c "
import json, sys
print(json.dumps({
    'sender': sys.argv[1],
    'subject': sys.argv[2],
    'date': sys.argv[3],
    'body': sys.argv[4],
    'account': sys.argv[5],
    'message_id': sys.argv[6]
}))
" "$sender" "$subject" "$date" "$body" "$account" "$msg_id")

        sanitized=$(echo "$email_json" | python3 "$SANITIZER")

        all_emails=$(python3 -c "
import json, sys
arr = json.loads(sys.argv[1])
arr.append(json.loads(sys.argv[2]))
print(json.dumps(arr))
" "$all_emails" "$sanitized")

    done <<< "$ids"
done

# --- Output ---
echo "$all_emails" | python3 -m json.tool

# Audit log (unless --raw)
if [[ "${1:-}" != "--raw" ]]; then
    echo "$all_emails" | python3 "$AUDIT" 2>/dev/null || true
fi
