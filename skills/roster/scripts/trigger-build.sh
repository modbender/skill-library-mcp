#!/bin/bash
# Trigger the Build Roster Preview workflow
# Usage: trigger-build.sh <KW> <YEAR> [CHAT_ID]
# If CHAT_ID is provided, the built PDF will be sent to that Telegram chat

set -e

KW="$1"
YEAR="$2"
CHAT_ID="$3"

if [ -z "$KW" ] || [ -z "$YEAR" ]; then
  echo "Usage: trigger-build.sh <KW> <YEAR> [CHAT_ID]"
  echo "  KW: Calendar week number (e.g. 08)"
  echo "  YEAR: Year (e.g. 2026)"
  echo "  CHAT_ID: Telegram chat ID for PDF delivery (optional)"
  exit 1
fi

# Zero-pad KW
KW=$(printf "%02d" "$KW")

FILE="KW-${YEAR}/KW-${KW}-${YEAR}.json"
REPO="${ROSTER_REPO}"

if [ -z "$REPO" ]; then
  echo "ERROR: ROSTER_REPO environment variable is not set."
  echo "Set it to your GitHub repository in 'owner/repo' format."
  exit 1
fi

# Validate CHAT_ID is numeric if provided (Telegram chat IDs are integers)
if [ -n "$CHAT_ID" ]; then
  if ! echo "$CHAT_ID" | grep -qE '^-?[0-9]+$'; then
    echo "ERROR: CHAT_ID must be a numeric value, got: $CHAT_ID"
    exit 1
  fi
fi

# Build dispatch payload safely via python3 json.dumps
BODY=$(python3 -c "
import json, sys
file_path = sys.argv[1]
chat_id = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else ''
inputs = {'file': file_path}
if chat_id:
    inputs['telegram_chat_id'] = chat_id
print(json.dumps({'ref': 'main', 'inputs': inputs}))
" "$FILE" "$CHAT_ID")

RESP=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO/actions/workflows/build-roster.yml/dispatches" \
  -d "$BODY")

if [ "$RESP" = "204" ]; then
  echo "SUCCESS: Build workflow gestartet für $FILE"
  if [ -n "$CHAT_ID" ]; then
    echo "Die PDF-Vorschau wird in ca. 3-5 Minuten an den Telegram-Chat gesendet."
  else
    echo "PDF wird als Artefakt auf GitHub erstellt."
  fi
  echo "Status: https://github.com/$REPO/actions/workflows/build-roster.yml"
else
  echo "ERROR: HTTP $RESP - Workflow konnte nicht gestartet werden."
  echo "Prüfe ob der GITHUB_TOKEN die Berechtigung actions:write hat."
  exit 1
fi
