#!/bin/bash
# Send a message to another agent

TO="$1"
SUBJECT="$2"
BODY="$3"

if [ -z "$TO" ] || [ -z "$SUBJECT" ] || [ -z "$BODY" ]; then
  echo "Usage: send.sh <to> <subject> <body>"
  echo "Example: send.sh 'kanta@moltmail.xyz' 'Hello!' 'Let's collaborate'"
  exit 1
fi

if [ -z "$MOLTMAIL_API_KEY" ]; then
  echo "Error: MOLTMAIL_API_KEY not set"
  exit 1
fi

API_URL="https://moltmail.xyz"

PAYLOAD=$(jq -n \
  --arg to "$TO" \
  --arg subject "$SUBJECT" \
  --arg body "$BODY" \
  '{to: $to, subject: $subject, body: $body}')

curl -s -X POST "$API_URL/send" \
  -H "Authorization: Bearer $MOLTMAIL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" | jq .
