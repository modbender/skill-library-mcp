#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_URL="https://api.revapay.ai"
ROOM_STATE_FILE="$HOME/.openclaw/payid/room_state.txt"

TOKEN=$("$SCRIPT_DIR/auth-manager.sh" get-token)

if [ -z "$TOKEN" ]; then
    echo '{"success": false, "error": "Not authenticated. Please login first"}'
    exit 1
fi

MESSAGE="$1"

if [ -z "$MESSAGE" ]; then
    echo '{"success": false, "error": "Message is required"}'
    exit 1
fi

ROOM_ID=""
if [ -f "$ROOM_STATE_FILE" ]; then
    ROOM_ID=$(cat "$ROOM_STATE_FILE")
fi

# Use jq to safely construct JSON payload, preventing injection attacks
if [ -z "$ROOM_ID" ] || [ "$ROOM_ID" = "null" ]; then
    PAYLOAD=$(jq -n --arg msg "$MESSAGE" '{message: $msg, roomId: null}')
else
    PAYLOAD=$(jq -n --arg msg "$MESSAGE" --arg room "$ROOM_ID" '{message: $msg, roomId: $room}')
fi

RESPONSE=$(curl -s -X POST "$API_URL/api/message/create-message" \
    -H "Content-Type: application/json" \
    -H "openclaw-token: $TOKEN" \
    -d "$PAYLOAD" \
    -w "\n%{http_code}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    NEW_ROOM_ID=$(echo "$BODY" | grep -o '"roomId":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ -n "$NEW_ROOM_ID" ]; then
        echo "$NEW_ROOM_ID" > "$ROOM_STATE_FILE"
        chmod 600 "$ROOM_STATE_FILE"
    fi
    
    echo "$BODY"
    exit 0
elif [ "$HTTP_CODE" = "401" ]; then
    "$SCRIPT_DIR/auth-manager.sh" clear
    echo '{"success": false, "error": "Unauthorized or token expired. Please login again"}'
    exit 1
else
    echo "$BODY"
    exit 1
fi
