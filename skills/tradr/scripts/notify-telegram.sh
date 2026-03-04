#!/usr/bin/env bash
# notify-telegram.sh — Notification hook for tradr → Telegram
# Called by tradr-enter.py and exit-manager.py with: <level> <type> <text>
# Routes: buy → DM only, sell → DM + broadcast, error → DM only

set -u

LEVEL="${1:-info}"    # info, trade, warning, error
TYPE="${2:-info}"     # buy, sell, confluence, error, info
TEXT="${3:-}"

[ -z "$TEXT" ] && exit 0

# Load secrets
for _envf in "$HOME/.env.secrets" "$(dirname "$0")/../../.env.secrets"; do
    [ -f "$_envf" ] && { set -a; . "$_envf"; set +a; break; }
done

BOT1_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
CHAT_ID="${TELEGRAM_CHAT_ID:-}"
BOT2_TOKEN="${TELEGRAM_BOT2_TOKEN:-}"
CHANNEL_ID="${TELEGRAM_CHANNEL_ID:-}"

send_dm() {
    [ -z "$BOT1_TOKEN" ] || [ -z "$CHAT_ID" ] && return
    curl -sf -X POST "https://api.telegram.org/bot${BOT1_TOKEN}/sendMessage" \
        --data-urlencode "chat_id=${CHAT_ID}" \
        --data-urlencode "text=$1" \
        --data-urlencode "parse_mode=Markdown" >/dev/null 2>&1 || true
}

send_broadcast() {
    [ -z "$BOT2_TOKEN" ] || [ -z "$CHANNEL_ID" ] && return
    curl -sf -X POST "https://api.telegram.org/bot${BOT2_TOKEN}/sendMessage" \
        --data-urlencode "chat_id=${CHANNEL_ID}" \
        --data-urlencode "text=$1" \
        --data-urlencode "parse_mode=Markdown" >/dev/null 2>&1 || true
}

case "$TYPE" in
    buy)
        send_dm "$TEXT"
        send_broadcast "$TEXT"
        ;;
    sell)
        send_dm "$TEXT"
        send_broadcast "$TEXT"
        ;;
    error)
        send_dm "⚠️ $TEXT"
        ;;
    *)
        send_dm "$TEXT"
        ;;
esac
