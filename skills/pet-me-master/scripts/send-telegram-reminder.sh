#!/bin/bash
# Simple script to send Telegram reminder directly
# Called by check-and-remind.sh when gotchis are ready

GOTCHI_COUNT="${1:-3}"
GOTCHI_LIST="${2:-#9638, #10052, #21785}"

# Create the message
MESSAGE="🐾 **PET TIME!** 👻

All $GOTCHI_COUNT gotchis are ready for petting!

Gotchis: $GOTCHI_LIST

Reply with 'pet all my gotchis' or I'll auto-pet them in 1 hour if you're busy! 🦞

⏰ Next auto-pet: $(date -u -d "+1 hour" '+%H:%M UTC')"

# Send via simple curl to local OpenClaw instance
# This uses the internal message API
curl -s -X POST "http://localhost:3000/v1/message/send" \
  -H "Content-Type: application/json" \
  -d "{
    \"channel\": \"telegram\",
    \"chatId\": \"322059822\",
    \"message\": $(echo "$MESSAGE" | jq -Rs .)
  }" > /tmp/telegram-reminder-response.txt 2>&1

if [ $? -eq 0 ]; then
  echo "[$(date)] ✅ Telegram reminder sent successfully"
  cat /tmp/telegram-reminder-response.txt
else
  echo "[$(date)] ❌ Failed to send Telegram reminder"
  cat /tmp/telegram-reminder-response.txt
fi
