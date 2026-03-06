#!/usr/bin/env bash
# Example: Safe message sending with arc-shield
# Usage: ./send-safe-message.sh "channel-id" "message text"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARC_SHIELD="${SCRIPT_DIR}/../scripts/arc-shield.sh"
OUTPUT_GUARD="${SCRIPT_DIR}/../scripts/output-guard.py"

CHANNEL="${1:-}"
MESSAGE="${2:-}"

if [[ -z "$CHANNEL" ]] || [[ -z "$MESSAGE" ]]; then
    echo "Usage: $0 <channel> <message>" >&2
    echo "Example: $0 discord 'Hello world'" >&2
    exit 1
fi

echo "🔍 Scanning message for secrets..." >&2

# First pass: regex-based detection (fast)
if ! echo "$MESSAGE" | "$ARC_SHIELD" --strict > /dev/null 2>&1; then
    echo "❌ BLOCKED: Message contains critical secrets (regex detection)" >&2
    echo "$MESSAGE" | "$ARC_SHIELD" --report >&2
    exit 1
fi

# Second pass: entropy-based detection (catches novel patterns)
if ! echo "$MESSAGE" | python3 "$OUTPUT_GUARD" --strict > /dev/null 2>&1; then
    echo "❌ BLOCKED: High-entropy secret detected" >&2
    echo "$MESSAGE" | python3 "$OUTPUT_GUARD" --report >&2
    exit 1
fi

echo "✅ Message sanitized, safe to send" >&2

# Send the message (replace with your actual send command)
# openclaw message send --channel "$CHANNEL" "$MESSAGE"
echo "Would send to $CHANNEL: $MESSAGE"
