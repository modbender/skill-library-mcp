#!/data/data/com.termux/files/usr/bin/bash
set -e

if [ -z "$WEBHOOK_URL" ]; then
  echo "WEBHOOK_URL is empty. Please export WEBHOOK_URL first."
  exit 1
fi

MSG="${1:-hello from termux 👋}"

curl -sS -H "Content-Type: application/json" \
  -d "{\"content\":\"$MSG\"}" \
  "$WEBHOOK_URL" >/dev/null

echo "sent ✅"
