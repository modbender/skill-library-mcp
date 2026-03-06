#!/bin/bash
# Send email via Resend API
# Usage: send.sh --to "email" --subject "subject" --body "body" [--from "from"] [--html]

set -e

# Load credentials
CREDS_FILE="$HOME/.config/resend/credentials.json"
if [ ! -f "$CREDS_FILE" ]; then
    echo "Error: Credentials not found at $CREDS_FILE"
    exit 1
fi

API_KEY=$(cat "$CREDS_FILE" | grep -o '"api_key"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
DEFAULT_FROM=$(cat "$CREDS_FILE" | grep -o '"default_from"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)

# Parse arguments
TO=""
FROM="$DEFAULT_FROM"
SUBJECT=""
BODY=""
IS_HTML=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --to)
            TO="$2"
            shift 2
            ;;
        --from)
            FROM="$2"
            shift 2
            ;;
        --subject)
            SUBJECT="$2"
            shift 2
            ;;
        --body)
            BODY="$2"
            shift 2
            ;;
        --html)
            IS_HTML=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required fields
if [ -z "$TO" ] || [ -z "$SUBJECT" ] || [ -z "$BODY" ]; then
    echo "Usage: send.sh --to EMAIL --subject SUBJECT --body BODY [--from FROM] [--html]"
    exit 1
fi

# Build JSON payload
if [ "$IS_HTML" = true ]; then
    BODY_KEY="html"
else
    BODY_KEY="text"
fi

# Build JSON payload safely (preserve newlines)
PAYLOAD=$(FROM="$FROM" TO="$TO" SUBJECT="$SUBJECT" BODY="$BODY" BODY_KEY="$BODY_KEY" python3 - <<'PY'
import json, os
from_addr = os.environ['FROM']
to_addr = os.environ['TO']
subject = os.environ['SUBJECT']
body = os.environ['BODY']
body_key = os.environ['BODY_KEY']
payload = {
    "from": from_addr,
    "to": [to_addr],
    "subject": subject,
    body_key: body,
}
print(json.dumps(payload))
PY
)

# Send email
RESPONSE=$(curl -s -X POST 'https://api.resend.com/emails' \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

# Check response
if echo "$RESPONSE" | grep -q '"id"'; then
    EMAIL_ID=$(echo "$RESPONSE" | grep -o '"id"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
    echo "✅ Email sent successfully"
    echo "   ID: $EMAIL_ID"
    echo "   To: $TO"
    echo "   From: $FROM"
    echo "   Subject: $SUBJECT"
else
    echo "❌ Failed to send email"
    echo "$RESPONSE"
    exit 1
fi
