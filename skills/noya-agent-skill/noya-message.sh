#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: noya-message.sh <message> <threadId>

Send a message to the Noya AI agent and display the parsed streaming response.

Requires:
  NOYA_API_KEY    — API key from https://agent.noya.ai (Settings > API Keys)

Dependencies: curl, jq (for JSON parsing)
USAGE
  exit 1
}

[[ $# -ge 2 ]] || usage

MESSAGE="$1"
THREAD_ID="$2"
BASE_URL="https://safenet.one"
if [[ -f /etc/timezone ]]; then
  TIMEZONE=$(cat /etc/timezone)
elif [[ -L /etc/localtime ]]; then
  TIMEZONE=$(readlink /etc/localtime | sed 's|.*/zoneinfo/||')
else
  TIMEZONE="America/New_York"
fi

if [[ -z "${NOYA_API_KEY:-}" ]]; then
  echo "Error: NOYA_API_KEY environment variable is required." >&2
  echo "Generate one at https://agent.noya.ai (Settings > API Keys)." >&2
  exit 1
fi

TMPFILE=$(mktemp)
trap 'rm -f "$TMPFILE"' EXIT

HTTP_CODE=$(curl -s -w '%{http_code}' -o "$TMPFILE" \
  -X POST "${BASE_URL}/api/messages/stream" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${NOYA_API_KEY}" \
  -H "x-timezone-name: ${TIMEZONE}" \
  -d "$(jq -n --arg msg "$MESSAGE" --arg tid "$THREAD_ID" \
    '{message: $msg, threadId: $tid}')")

if [[ "$HTTP_CODE" -ge 400 ]]; then
  echo "Error: API returned HTTP ${HTTP_CODE}" >&2
  cat "$TMPFILE" >&2
  exit 1
fi

# Parse the --breakpoint-- delimited stream.
# Messages arrive token-by-token and must be concatenated.
CHUNKS_FILE=$(mktemp)
trap 'rm -f "$TMPFILE" "$CHUNKS_FILE"' EXIT

awk 'BEGIN { RS="--breakpoint--\n"; FS="\n" }
{
  line = $0
  gsub(/^[ \t\n]+|[ \t\n]+$/, "", line)
  if (line == "" || line == "keep-alive") next
  print line
}' "$TMPFILE" > "$CHUNKS_FILE"

MESSAGE_TEXT=""
while IFS= read -r chunk; do
  TYPE=$(echo "$chunk" | jq -r '.type // empty' 2>/dev/null) || continue
  case "$TYPE" in
    message)
      TOKEN=$(echo "$chunk" | jq -r '.message // empty' 2>/dev/null)
      MESSAGE_TEXT="${MESSAGE_TEXT}${TOKEN}"
      ;;
    tool)
      CONTENT_TYPE=$(echo "$chunk" | jq -r '.content.type // empty' 2>/dev/null)
      if [[ "$CONTENT_TYPE" == "non_visible" ]]; then
        TEXT=$(echo "$chunk" | jq -r '.content.text // empty' 2>/dev/null)
        [[ -n "$TEXT" ]] && echo "[Agent Action] $TEXT"
      elif [[ "$CONTENT_TYPE" != "done" ]]; then
        echo "[Tool: $CONTENT_TYPE]"
        echo "$chunk" | jq -r '.content.data // .content | if type == "object" then tostring else . end' 2>/dev/null
      fi
      ;;
    interrupt)
      QUESTION=$(echo "$chunk" | jq -r '.content.question // empty' 2>/dev/null)
      OPTIONS=$(echo "$chunk" | jq -r '.content.options // [] | join(", ")' 2>/dev/null)
      echo ""
      echo "[REQUIRES INPUT] $QUESTION"
      [[ -n "$OPTIONS" ]] && echo "Options: $OPTIONS"
      ;;
    progress)
      CURRENT=$(echo "$chunk" | jq -r '.current // "?"' 2>/dev/null)
      TOTAL=$(echo "$chunk" | jq -r '.total // "?"' 2>/dev/null)
      MSG=$(echo "$chunk" | jq -r '.message // empty' 2>/dev/null)
      echo "[Progress ${CURRENT}/${TOTAL}] $MSG"
      ;;
    reasonForExecution)
      echo "[Reasoning] $(echo "$chunk" | jq -r '.message // empty' 2>/dev/null)"
      ;;
    executionSteps)
      echo "[Steps] $(echo "$chunk" | jq -r '.steps // [] | join(" → ")' 2>/dev/null)"
      ;;
    error)
      echo "[ERROR] $(echo "$chunk" | jq -r '.message // "Unknown error"' 2>/dev/null)"
      ;;
    portfolio|markets|defi_positions|prepare_swap|execute_swap|prepare_bridge|execute_bridge|prepare_send|execute_send|fund_wallet|request_delegation|request_safe_deployment|setup_dca_strategy|view_dca_strategy|list_dca_strategies|modify_dca_strategy|delete_dca_strategy|polymarket_safe_info|prepare_place_order|execute_place_order)
      echo "[$TYPE]"
      echo "$chunk" | jq '.' 2>/dev/null
      ;;
  esac
done < "$CHUNKS_FILE"

[[ -n "$MESSAGE_TEXT" ]] && printf '%s\n' "$MESSAGE_TEXT"
