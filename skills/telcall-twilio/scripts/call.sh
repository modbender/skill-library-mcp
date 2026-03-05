#!/bin/bash
# Twilio Emergency Call Script
# Author: Micheal Sun
# Usage: call.sh "Your message"

CONFIG_FILE="$HOME/.openclaw/workspace/telcall-twilio/config/twilio.json"

# Check for message argument
if [ -z "$1" ]; then
    echo "Usage: call.sh \"Your message\""
    echo "Example: call.sh \"Server is down, please check!\""
    exit 1
fi

MESSAGE="$1"

# Check if config exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration not found!"
    echo "Please run setup first:"
    echo "   bash ~/.openclaw/workspace/telcall-twilio/scripts/setup.sh"
    exit 1
fi

# Load configuration
ACCOUNT_SID=$(jq -r '.account_sid' "$CONFIG_FILE")
AUTH_TOKEN=$(jq -r '.auth_token' "$CONFIG_FILE")
FROM_NUMBER=$(jq -r '.from_number' "$CONFIG_FILE")
TO_NUMBER=$(jq -r '.to_number' "$CONFIG_FILE")

# Validate configuration
if [ -z "$ACCOUNT_SID" ] || [ -z "$AUTH_TOKEN" ] || [ -z "$FROM_NUMBER" ] || [ -z "$TO_NUMBER" ]; then
    echo "❌ Invalid configuration. Please run setup again."
    exit 1
fi

# Create TwiML with the message
# Language options: en-US, zh-CN, ja-JP, etc.
TWIML="<Response><Say language=\"en-US\" voice=\"alice\">Emergency notification: ${MESSAGE}</Say></Response>"

# URL encode the TwiML
ENCODED_TWIML=$(echo "$TWIML" | jq -sRr @uri)

# Make the call
echo "📞 Initiating phone call..."
echo "   From: $FROM_NUMBER"
echo "   To:   $TO_NUMBER"
echo "   Message: $MESSAGE"
echo ""

RESPONSE=$(curl -s -X POST "https://api.twilio.com/2010-04-01/Accounts/${ACCOUNT_SID}/Calls.json" \
    -u "${ACCOUNT_SID}:${AUTH_TOKEN}" \
    -d "To=${TO_NUMBER}" \
    -d "From=${FROM_NUMBER}" \
    -d "Twiml=${ENCODED_TWIML}")

# Check result
if echo "$RESPONSE" | jq -e '.sid' > /dev/null 2>&1; then
    CALL_SID=$(echo "$RESPONSE" | jq -r '.sid')
    echo "✅ Call initiated successfully!"
    echo "   Call SID: $CALL_SID"
else
    echo "❌ Call failed!"
    ERROR_CODE=$(echo "$RESPONSE" | jq -r '.code // "unknown"')
    ERROR_MSG=$(echo "$RESPONSE" | jq -r '.message // "Unknown error"')
    echo "   Error Code: $ERROR_CODE"
    echo "   Message: $ERROR_MSG"
    
    # Provide helpful hints for common errors
    case "$ERROR_CODE" in
        "21219")
            echo ""
            echo "💡 Hint: Trial accounts can only call verified numbers."
            echo "   Either verify this number in Twilio Console, or upgrade your account."
            ;;
        "21214")
            echo ""
            echo "💡 Hint: The 'From' number may not have Voice capability."
            echo "   Check your Twilio number settings."
            ;;
    esac
    exit 1
fi
