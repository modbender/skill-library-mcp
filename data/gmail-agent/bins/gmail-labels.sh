#!/usr/bin/env bash
#
# gmail-labels.sh — List Gmail labels with message counts in a tree structure
#
# Usage: gmail-labels.sh [account-email]
#   account-email: Gmail address (defaults to $GMAIL_ACCOUNT env var)
#
set -euo pipefail

ACCOUNT="${1:-${GMAIL_ACCOUNT:-}}"

if [[ -z "$ACCOUNT" ]]; then
    echo "Error: No Gmail account specified." >&2
    echo "Usage: $0 <account-email>  OR  set GMAIL_ACCOUNT env var" >&2
    exit 1
fi

# Get all label names (skip header line), sorted
labels=$(gog gmail labels list --account "$ACCOUNT" --plain \
    | tail -n +2 \
    | cut -f2 \
    | sort)

# For each label, get message counts
while IFS= read -r label; do
    [[ -z "$label" ]] && continue

    # Fetch counts for this label
    info=$(gog gmail labels get "$label" --account "$ACCOUNT" --plain 2>/dev/null || true)

    total=$(echo "$info" | grep '^messages_total' | cut -f2)
    unread=$(echo "$info" | grep '^messages_unread' | cut -f2)

    total="${total:-0}"
    unread="${unread:-0}"

    # Skip labels with 0 total messages to keep output clean
    if [[ "$total" -eq 0 ]] 2>/dev/null; then
        continue
    fi

    if [[ "$unread" -gt 0 ]]; then
        printf "%s\t%s total\t%s unread\n" "$label" "$total" "$unread"
    else
        printf "%s\t%s total\n" "$label" "$total"
    fi
done <<< "$labels"
