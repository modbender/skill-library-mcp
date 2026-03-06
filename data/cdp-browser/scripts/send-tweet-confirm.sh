#!/bin/bash
# Send a Telegram message with "Confirm Post" inline button for tweet approval.
# Usage: send-tweet-confirm.sh <chat_id> <tweet_text>
# The agent should use the current session's reply target as chat_id.
set -euo pipefail
if [ $# -lt 2 ]; then
  echo "Usage: $0 <chat_id> <tweet_text>" >&2
  exit 1
fi
CHAT_ID="$1"
shift
TEXT="$*"
openclaw message send --channel telegram --target "$CHAT_ID" \
  --message "Draft ready: $TEXT

Review in browser, then click Confirm Post or say 'go ahead' to post." \
  --buttons '[[{"text":"Confirm Post","callback_data":"cdp:tweet:confirm"}]]'
