#!/bin/bash
# universal-notify — Send notifications through multiple channels
# Requires: curl

set -euo pipefail

error() { echo "❌ Error: $1" >&2; exit 1; }
success() { echo "✅ Sent via $CHANNEL"; exit 0; }

command -v curl >/dev/null 2>&1 || error "curl is required"

usage() {
  cat << 'EOF'
Usage: notify.sh --channel CHANNEL --message MESSAGE [OPTIONS]

Channels:
  ntfy        --topic TOPIC [--server URL]
  gotify      --url URL --token TOKEN [--title TITLE]
  webhook     --url URL [--title TITLE]
  email       --smtp URL --from ADDR --to ADDR --subject SUBJ
  telegram    --bot-token TOKEN --chat-id ID
  pushover    --app-token TOKEN --user-key KEY [--title TITLE]

Common:
  --message MSG       Notification text (required)
  --title TITLE       Notification title (optional)
  --priority LEVEL    low | normal | high | urgent (default: normal)

Examples:
  notify.sh --channel ntfy --topic myalerts --message "Disk full!"
  notify.sh --channel telegram --bot-token BOT:TOK --chat-id 123 --message "Hello"
  notify.sh --channel webhook --url https://hook.example.com --message '{"event":"deploy"}'
  notify.sh --channel pushover --app-token X --user-key Y --message "Alert" --priority urgent
EOF
  exit 1
}

# Defaults
CHANNEL="" MESSAGE="" TITLE="" PRIORITY="normal"
TOPIC="" URL="" TOKEN="" SMTP="" FROM="" TO="" SUBJECT=""
BOT_TOKEN="" CHAT_ID="" APP_TOKEN="" USER_KEY=""
NTFY_SERVER="https://ntfy.sh"

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --channel)    CHANNEL="$2"; shift 2 ;;
    --message)    MESSAGE="$2"; shift 2 ;;
    --title)      TITLE="$2"; shift 2 ;;
    --priority)   PRIORITY="$2"; shift 2 ;;
    --topic)      TOPIC="$2"; shift 2 ;;
    --url)        URL="$2"; shift 2 ;;
    --token)      TOKEN="$2"; shift 2 ;;
    --server)     NTFY_SERVER="$2"; shift 2 ;;
    --smtp)       SMTP="$2"; shift 2 ;;
    --from)       FROM="$2"; shift 2 ;;
    --to)         TO="$2"; shift 2 ;;
    --subject)    SUBJECT="$2"; shift 2 ;;
    --bot-token)  BOT_TOKEN="$2"; shift 2 ;;
    --chat-id)    CHAT_ID="$2"; shift 2 ;;
    --app-token)  APP_TOKEN="$2"; shift 2 ;;
    --user-key)   USER_KEY="$2"; shift 2 ;;
    -h|--help)    usage ;;
    *) error "Unknown option: $1" ;;
  esac
done

[[ -z "$CHANNEL" ]] && usage
[[ -z "$MESSAGE" ]] && error "--message is required"

# Priority mappings
ntfy_priority() {
  case "$1" in
    low) echo 2 ;; normal) echo 3 ;; high) echo 4 ;; urgent) echo 5 ;;
    *) echo 3 ;;
  esac
}

pushover_priority() {
  case "$1" in
    low) echo -1 ;; normal) echo 0 ;; high) echo 1 ;; urgent) echo 2 ;;
    *) echo 0 ;;
  esac
}

case "$CHANNEL" in
  ntfy)
    [[ -z "$TOPIC" ]] && error "--topic required for ntfy"
    HEADERS=(-H "Priority: $(ntfy_priority "$PRIORITY")")
    [[ -n "$TITLE" ]] && HEADERS+=(-H "Title: $TITLE")
    curl -sf "${HEADERS[@]}" -d "$MESSAGE" "${NTFY_SERVER}/${TOPIC}" >/dev/null || error "ntfy request failed"
    success
    ;;

  gotify)
    [[ -z "$URL" || -z "$TOKEN" ]] && error "--url and --token required for gotify"
    curl -sf -X POST "${URL}/message?token=${TOKEN}" \
      -F "title=${TITLE:-Notification}" \
      -F "message=${MESSAGE}" >/dev/null || error "gotify request failed"
    success
    ;;

  webhook)
    [[ -z "$URL" ]] && error "--url required for webhook"
    JSON=$(printf '{"title":"%s","message":"%s","priority":"%s"}' \
      "${TITLE:-Notification}" "$MESSAGE" "$PRIORITY")
    curl -sf -X POST -H "Content-Type: application/json" -d "$JSON" "$URL" >/dev/null || error "webhook request failed"
    success
    ;;

  email)
    [[ -z "$SMTP" || -z "$FROM" || -z "$TO" || -z "$SUBJECT" ]] && \
      error "--smtp, --from, --to, --subject required for email"
    printf "From: %s\nTo: %s\nSubject: %s\n\n%s" "$FROM" "$TO" "$SUBJECT" "$MESSAGE" | \
      curl -sf --url "$SMTP" --mail-from "$FROM" --mail-rcpt "$TO" -T - || error "email send failed"
    success
    ;;

  telegram)
    [[ -z "$BOT_TOKEN" || -z "$CHAT_ID" ]] && error "--bot-token and --chat-id required for telegram"
    curl -sf -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
      -d "chat_id=${CHAT_ID}" -d "text=${MESSAGE}" -d "parse_mode=HTML" >/dev/null || error "telegram request failed"
    success
    ;;

  pushover)
    [[ -z "$APP_TOKEN" || -z "$USER_KEY" ]] && error "--app-token and --user-key required for pushover"
    curl -sf \
      --form-string "token=${APP_TOKEN}" \
      --form-string "user=${USER_KEY}" \
      --form-string "message=${MESSAGE}" \
      --form-string "title=${TITLE:-Notification}" \
      --form-string "priority=$(pushover_priority "$PRIORITY")" \
      https://api.pushover.net/1/messages.json >/dev/null || error "pushover request failed"
    success
    ;;

  *)
    error "Unknown channel: $CHANNEL. Supported: ntfy, gotify, webhook, email, telegram, pushover"
    ;;
esac
