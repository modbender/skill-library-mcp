#!/usr/bin/env bash
# ShellMail CLI — lightweight wrapper around the ShellMail REST API
set -euo pipefail

# Config: set via env or openclaw skill config
API_URL="${SHELLMAIL_API_URL:-https://shellmail.ai}"
TOKEN="${SHELLMAIL_TOKEN:-}"

usage() {
  cat <<EOF
Usage: shellmail <command> [options]

Commands:
  inbox                     List emails (--unread for unread only)
  read <id>                 Read a specific email
  otp                       Get latest OTP code (--wait 30 to wait, --from domain)
  search                    Search emails (--query text, --from domain, --otp)
  send <to>                 Send email (--subject, --body, --html)
  reply <id>                Reply to email (--body, --html)
  sent                      List sent emails
  mark-read <id>            Mark email as read
  mark-unread <id>          Mark email as unread
  archive <id>              Archive an email
  delete <id>               Delete an email
  addresses                 Show current address info
  create <local> <email>    Create a new address (local@shellmail.ai)
  recover <address> <email> Recover token for an address
  delete-address            Delete address and all mail
  health                    Check API health

Environment:
  SHELLMAIL_TOKEN           Bearer token (required for most commands)
  SHELLMAIL_API_URL         API base URL (default: https://shellmail.ai)
EOF
  exit 1
}

auth_header() {
  if [ -z "$TOKEN" ]; then
    echo "Error: SHELLMAIL_TOKEN not set" >&2
    exit 1
  fi
  echo "Authorization: Bearer $TOKEN"
}

# URL-encode a string for safe use in query parameters (python only, no fallback)
urlencode() {
  printf '%s' "$1" | python3 -c "import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read(), safe=''))"
}

cmd="${1:-}"
shift || true

case "$cmd" in
  inbox)
    UNREAD=""
    LIMIT="50"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --unread) UNREAD="?unread=true"; shift ;;
        --limit) LIMIT="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    curl -sf "$API_URL/api/mail${UNREAD}&limit=${LIMIT}" \
      -H "$(auth_header)" 2>/dev/null || \
    curl -sf "$API_URL/api/mail${UNREAD}${UNREAD:+&}${UNREAD:-?}limit=${LIMIT}" \
      -H "$(auth_header)"
    ;;

  read)
    [ -z "${1:-}" ] && { echo "Usage: shellmail read <id>" >&2; exit 1; }
    curl -sf "$API_URL/api/mail/$(urlencode "$1")" -H "$(auth_header)"
    ;;

  otp)
    PARAMS=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --wait) PARAMS="${PARAMS}&timeout=$((${2}*1000))"; shift 2 ;;
        --from) PARAMS="${PARAMS}&from=$(urlencode "$2")"; shift 2 ;;
        *) shift ;;
      esac
    done
    PARAMS="${PARAMS#&}"
    curl -sf "$API_URL/api/mail/otp${PARAMS:+?$PARAMS}" -H "$(auth_header)"
    ;;

  search)
    PARAMS=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --query|-q) PARAMS="${PARAMS}&q=$(urlencode "$2")"; shift 2 ;;
        --from|-f) PARAMS="${PARAMS}&from=$(urlencode "$2")"; shift 2 ;;
        --otp) PARAMS="${PARAMS}&has_otp=true"; shift ;;
        --limit|-n) PARAMS="${PARAMS}&limit=$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    PARAMS="${PARAMS#&}"
    curl -sf "$API_URL/api/mail/search${PARAMS:+?$PARAMS}" -H "$(auth_header)"
    ;;

  mark-read)
    [ -z "${1:-}" ] && { echo "Usage: shellmail mark-read <id>" >&2; exit 1; }
    curl -sf -X PATCH "$API_URL/api/mail/$(urlencode "$1")" \
      -H "$(auth_header)" \
      -H "Content-Type: application/json" \
      -d '{"is_read": true}'
    ;;

  mark-unread)
    [ -z "${1:-}" ] && { echo "Usage: shellmail mark-unread <id>" >&2; exit 1; }
    curl -sf -X PATCH "$API_URL/api/mail/$(urlencode "$1")" \
      -H "$(auth_header)" \
      -H "Content-Type: application/json" \
      -d '{"is_read": false}'
    ;;

  archive)
    [ -z "${1:-}" ] && { echo "Usage: shellmail archive <id>" >&2; exit 1; }
    curl -sf -X PATCH "$API_URL/api/mail/$(urlencode "$1")" \
      -H "$(auth_header)" \
      -H "Content-Type: application/json" \
      -d '{"is_archived": true}'
    ;;

  delete)
    [ -z "${1:-}" ] && { echo "Usage: shellmail delete <id>" >&2; exit 1; }
    curl -sf -X DELETE "$API_URL/api/mail/$(urlencode "$1")" -H "$(auth_header)"
    ;;

  addresses)
    # Show the address associated with the current token by checking inbox
    curl -sf "$API_URL/api/mail?limit=0" -H "$(auth_header)"
    ;;

  create)
    [ -z "${1:-}" ] || [ -z "${2:-}" ] && { echo "Usage: shellmail create <local> <recovery_email>" >&2; exit 1; }
    # Build JSON safely using jq if available, otherwise python
    if command -v jq >/dev/null 2>&1; then
      json=$(jq -n --arg local "$1" --arg email "$2" '{local: $local, recovery_email: $email}')
    else
      json=$(python3 -c "import sys, json; print(json.dumps({'local': sys.argv[1], 'recovery_email': sys.argv[2]}))" "$1" "$2")
    fi
    printf '%s' "$json" | curl -sf -X POST "$API_URL/api/addresses" \
      -H "Content-Type: application/json" \
      -d @-
    ;;

  recover)
    [ -z "${1:-}" ] || [ -z "${2:-}" ] && { echo "Usage: shellmail recover <address> <recovery_email>" >&2; exit 1; }
    # Build JSON safely using jq if available, otherwise python
    if command -v jq >/dev/null 2>&1; then
      json=$(jq -n --arg addr "$1" --arg email "$2" '{address: $addr, recovery_email: $email}')
    else
      json=$(python3 -c "import sys, json; print(json.dumps({'address': sys.argv[1], 'recovery_email': sys.argv[2]}))" "$1" "$2")
    fi
    printf '%s' "$json" | curl -sf -X POST "$API_URL/api/recover" \
      -H "Content-Type: application/json" \
      -d @-
    ;;

  delete-address)
    curl -sf -X DELETE "$API_URL/api/addresses/me" -H "$(auth_header)"
    ;;

  send)
    [ -z "${1:-}" ] && { echo "Usage: shellmail send <to> --subject 'Subject' --body 'Body'" >&2; exit 1; }
    TO="$1"; shift
    SUBJECT=""
    BODY=""
    HTML=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --subject|-s) SUBJECT="$2"; shift 2 ;;
        --body|-b) BODY="$2"; shift 2 ;;
        --html) HTML="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    [ -z "$SUBJECT" ] && { echo "Error: --subject required" >&2; exit 1; }
    [ -z "$BODY" ] && { echo "Error: --body required" >&2; exit 1; }
    if command -v jq >/dev/null 2>&1; then
      json=$(jq -n --arg to "$TO" --arg subject "$SUBJECT" --arg body "$BODY" --arg html "$HTML" \
        '{to: $to, subject: $subject, body_text: $body} + (if $html != "" then {body_html: $html} else {} end)')
    else
      json=$(python3 -c "import sys, json; d={'to': sys.argv[1], 'subject': sys.argv[2], 'body_text': sys.argv[3]}; sys.argv[4] and d.update({'body_html': sys.argv[4]}); print(json.dumps(d))" "$TO" "$SUBJECT" "$BODY" "$HTML")
    fi
    printf '%s' "$json" | curl -sf -X POST "$API_URL/api/mail/send" \
      -H "$(auth_header)" \
      -H "Content-Type: application/json" \
      -d @-
    ;;

  reply)
    [ -z "${1:-}" ] && { echo "Usage: shellmail reply <email-id> --body 'Reply text'" >&2; exit 1; }
    REPLY_ID="$1"; shift
    BODY=""
    HTML=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --body|-b) BODY="$2"; shift 2 ;;
        --html) HTML="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    [ -z "$BODY" ] && { echo "Error: --body required" >&2; exit 1; }
    # Fetch original email to get recipient and subject
    ORIGINAL=$(curl -sf "$API_URL/api/mail/$(urlencode "$REPLY_ID")" -H "$(auth_header)")
    TO=$(echo "$ORIGINAL" | python3 -c "import sys, json; print(json.loads(sys.stdin.read())['from_addr'])")
    SUBJECT=$(echo "$ORIGINAL" | python3 -c "import sys, json; s=json.loads(sys.stdin.read())['subject']; print(s if s.startswith('Re:') else 'Re: '+s)")
    if command -v jq >/dev/null 2>&1; then
      json=$(jq -n --arg to "$TO" --arg subject "$SUBJECT" --arg body "$BODY" --arg html "$HTML" --arg reply "$REPLY_ID" \
        '{to: $to, subject: $subject, body_text: $body, reply_to_id: $reply} + (if $html != "" then {body_html: $html} else {} end)')
    else
      json=$(python3 -c "import sys, json; d={'to': sys.argv[1], 'subject': sys.argv[2], 'body_text': sys.argv[3], 'reply_to_id': sys.argv[5]}; sys.argv[4] and d.update({'body_html': sys.argv[4]}); print(json.dumps(d))" "$TO" "$SUBJECT" "$BODY" "$HTML" "$REPLY_ID")
    fi
    printf '%s' "$json" | curl -sf -X POST "$API_URL/api/mail/send" \
      -H "$(auth_header)" \
      -H "Content-Type: application/json" \
      -d @-
    ;;

  sent)
    LIMIT="50"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --limit) LIMIT="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    curl -sf "$API_URL/api/mail/sent?limit=${LIMIT}" -H "$(auth_header)"
    ;;

  health)
    curl -sf "$API_URL/health"
    ;;

  *)
    usage
    ;;
esac
