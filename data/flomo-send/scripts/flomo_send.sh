#!/bin/bash
#
# flomo_send.sh - Send notes to flomo app via URL Scheme with webhook fallback
#
# Usage:
#   ./flomo_send.sh "Note content" "#tag1 #tag2"
#   ./scripts/flomo_send.sh "$(pbpaste)" "#clippings"
#   echo "Note content" | ./scripts/flomo_send.sh
#

set -e

# Load local .env if present (export variables so they're available to curl/python)
ENV_FILE="$(dirname "$0")/../.env"
if [ -f "$ENV_FILE" ]; then
    set -o allexport
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +o allexport
fi

# Get content from arguments or stdin.
# If the last positional argument starts with '#', treat it as TAGS and
# join the remaining arguments as CONTENT. Otherwise join all positional
# args as CONTENT. If no positional args are given, read from stdin.
TAGS=""
if [ $# -ge 1 ]; then
    LAST_ARG="${@: -1}"
    if [[ "$LAST_ARG" == \#* ]]; then
        TAGS="$LAST_ARG"
        if [ $# -ge 2 ]; then
            CONTENT="${@:1:$(($#-1))}"
        else
            # single arg which is a tag -> read content from stdin
            CONTENT=$(cat)
        fi
    else
        CONTENT="$*"
    fi
else
    CONTENT=$(cat)
fi

# Combine content and tags
if [ -n "$TAGS" ]; then
    FULL_CONTENT="${CONTENT} ${TAGS}"
else
    FULL_CONTENT="${CONTENT}"
fi

# Trim whitespace (remove leading/trailing spaces and newlines)
FULL_CONTENT=$(echo "$FULL_CONTENT" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

# Check if content is empty
if [ -z "$FULL_CONTENT" ]; then
    echo "Error: Note content is empty" >&2
    echo "Usage: $0 \"Note content\" \"#tag1 #tag2\"" >&2
    exit 1
fi

# Check content length (flomo limit: 5000 characters before encoding)
if [ "${#FULL_CONTENT}" -gt 5000 ]; then
    echo "Error: Content exceeds 5000 character limit (current: ${#FULL_CONTENT})" >&2
    exit 1
fi

# Function: send via webhook. Returns 0 on success, non-zero on failure.
send_webhook() {
    if [ -n "$FLOMO_WEBHOOK_URL" ]; then
        WEBHOOK_URL="$FLOMO_WEBHOOK_URL"
    elif [ -n "$FLOMO_WEBHOOK_TOKEN" ]; then
        WEBHOOK_URL="https://flomoapp.com/iwh/$FLOMO_WEBHOOK_TOKEN"
    else
        return 2
    fi

    # Build JSON payload safely (handles quotes/newlines in content).
    if command -v python3 >/dev/null 2>&1; then
        PAYLOAD=$(printf '%s' "$FULL_CONTENT" | python3 -c 'import sys,json;print(json.dumps({"content": sys.stdin.read()}))')
    else
        # Fallback: escape simple cases (less safe for arbitrary input)
        ESCAPED=$(printf '%s' "$FULL_CONTENT" | sed -e 's/\\/\\\\/g' -e 's/"/\\\"/g' -e ':a;N;$!ba;s/\n/\\n/g')
        PAYLOAD="{\"content\": \"$ESCAPED\"}"
    fi

    RESP=$(curl -sS -w "\n%{http_code}" -X POST "$WEBHOOK_URL" -H "Content-Type: application/json" -d "$PAYLOAD" || true)
    HTTP_STATUS=$(echo "$RESP" | tail -n1)
    BODY=$(echo "$RESP" | sed '$d')

    if echo "$HTTP_STATUS" | grep -q "^2"; then
        echo "✓ Sent to flomo webhook: ${FULL_CONTENT:0:50}..."
        return 0
    else
        echo "Warning: Webhook request failed (HTTP $HTTP_STATUS): $BODY" >&2
        return 1
    fi
}

# Main: webhook-only delivery
if [ -n "$FLOMO_WEBHOOK_URL" ] || [ -n "$FLOMO_WEBHOOK_TOKEN" ]; then
    if send_webhook; then
        exit 0
    else
        echo "Error: webhook delivery failed. Check FLOMO_WEBHOOK_URL/FLOMO_WEBHOOK_TOKEN and network." >&2
        exit 1
    fi
else
    echo "Error: Webhook not configured. Set FLOMO_WEBHOOK_URL or FLOMO_WEBHOOK_TOKEN or run ./scripts/configure.sh" >&2
    exit 1
fi
