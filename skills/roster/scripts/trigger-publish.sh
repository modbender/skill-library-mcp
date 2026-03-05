#!/bin/bash
# Trigger the Publish Roster workflow (build PDF + send emails)
# Usage: trigger-publish.sh <KW> <YEAR>

set -e

KW="$1"
YEAR="$2"

if [ -z "$KW" ] || [ -z "$YEAR" ]; then
  echo "Usage: trigger-publish.sh <KW> <YEAR>"
  echo "  KW: Calendar week number (e.g. 08)"
  echo "  YEAR: Year (e.g. 2026)"
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

# Build dispatch payload safely via python3 json.dumps
BODY=$(python3 -c "
import json, sys
print(json.dumps({'ref': 'main', 'inputs': {'file': sys.argv[1]}}))
" "$FILE")

RESP=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO/actions/workflows/publish-roster.yml/dispatches" \
  -d "$BODY")

if [ "$RESP" = "204" ]; then
  echo "SUCCESS: Publish workflow gestartet für $FILE"
  echo "PDF wird gebaut und Emails an alle Mitarbeiter gesendet."
  echo "Status: https://github.com/$REPO/actions/workflows/publish-roster.yml"
else
  echo "ERROR: HTTP $RESP - Workflow konnte nicht gestartet werden."
  echo "Prüfe ob der GITHUB_TOKEN die Berechtigung actions:write hat."
  exit 1
fi
