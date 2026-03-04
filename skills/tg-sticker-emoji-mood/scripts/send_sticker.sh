#!/usr/bin/env bash
# send_sticker.sh — Send a Telegram sticker or emoji reaction via Bot API
#
# Usage:
#   send_sticker.sh --chat-id <CHAT_ID> --sticker <FILE_ID>
#   send_sticker.sh --chat-id <CHAT_ID> --sticker-set <SET_NAME> --emoji <EMOJI>
#   send_sticker.sh --list-set <SET_NAME>
#
# Requires: TELEGRAM_BOT_TOKEN environment variable

set -euo pipefail

if [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]]; then
  echo "Error: TELEGRAM_BOT_TOKEN is not set" >&2
  exit 1
fi

API="https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") --chat-id <ID> --sticker <FILE_ID>
      Send a sticker by file_id directly.

  $(basename "$0") --chat-id <ID> --sticker-set <SET_NAME> --emoji <EMOJI>
      Look up a sticker matching the emoji from the given set and send it.

  $(basename "$0") --list-set <SET_NAME>
      List all stickers in a set with their file_id and emoji.

Environment:
  TELEGRAM_BOT_TOKEN   Your bot token (required).
EOF
  exit 0
}

send_sticker_by_id() {
  local chat_id="$1" file_id="$2"
  curl -s -X POST "${API}/sendSticker" \
    -d chat_id="${chat_id}" \
    -d sticker="${file_id}"
}

get_sticker_set() {
  local set_name="$1"
  curl -s -X POST "${API}/getStickerSet" \
    -d name="${set_name}"
}

list_set() {
  local set_name="$1"
  local response
  response=$(get_sticker_set "${set_name}")
  echo "${response}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if not data.get('ok'):
    print('Error:', data.get('description', 'unknown'), file=sys.stderr)
    sys.exit(1)
for s in data['result']['stickers']:
    print(f\"{s['emoji']}  {s['file_id']}\")
"
}

send_sticker_by_emoji() {
  local chat_id="$1" set_name="$2" emoji="$3"
  local response
  response=$(get_sticker_set "${set_name}")
  local file_id
  file_id=$(echo "${response}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if not data.get('ok'):
    print('Error:', data.get('description', 'unknown'), file=sys.stderr)
    sys.exit(1)
emoji = '${emoji}'
matches = [s for s in data['result']['stickers'] if s.get('emoji') == emoji]
if matches:
    print(matches[0]['file_id'])
else:
    # Fallback: pick a random sticker from the set
    import random
    stickers = data['result']['stickers']
    print(random.choice(stickers)['file_id'])
")
  if [[ -n "${file_id}" ]]; then
    send_sticker_by_id "${chat_id}" "${file_id}"
  else
    echo "Error: Could not find a matching sticker" >&2
    exit 1
  fi
}

# --- Parse arguments ---
CHAT_ID="" FILE_ID="" SET_NAME="" EMOJI="" LIST_SET=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --chat-id)    CHAT_ID="$2";    shift 2 ;;
    --sticker)    FILE_ID="$2";    shift 2 ;;
    --sticker-set) SET_NAME="$2";  shift 2 ;;
    --emoji)      EMOJI="$2";      shift 2 ;;
    --list-set)   LIST_SET="$2";   shift 2 ;;
    -h|--help)    usage ;;
    *)            echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -n "${LIST_SET}" ]]; then
  list_set "${LIST_SET}"
elif [[ -n "${CHAT_ID}" && -n "${FILE_ID}" ]]; then
  send_sticker_by_id "${CHAT_ID}" "${FILE_ID}"
elif [[ -n "${CHAT_ID}" && -n "${SET_NAME}" && -n "${EMOJI}" ]]; then
  send_sticker_by_emoji "${CHAT_ID}" "${SET_NAME}" "${EMOJI}"
else
  echo "Error: insufficient arguments. Use --help for usage." >&2
  exit 1
fi
