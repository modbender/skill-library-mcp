#!/bin/bash
set -e
if [ ! -f /opt/moltbook-cli/notify.env ]; then
  echo "notify.env not found"
  exit 1
fi
source /opt/moltbook-cli/notify.env
if [ -z "$TELEGRAM_NOTIFY_TOKEN" ] || [ -z "$TELEGRAM_NOTIFY_CHAT_ID" ]; then
  echo "notify.env missing token/chat_id"
  exit 1
fi
MESSAGE="$1"
if [ -z "$MESSAGE" ]; then
  echo "Usage: notify.sh \"message\""
  exit 1
fi
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_NOTIFY_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_NOTIFY_CHAT_ID}" \
  -d "text=${MESSAGE}" \
  -d "disable_web_page_preview=true" >/dev/null
