#!/bin/bash
# Push a KW roster JSON file to GitHub
# Usage: push-to-github.sh <KW_NUMBER> <YEAR> '<JSON_CONTENT>'
# Example: push-to-github.sh 08 2026 '{"meta":...}'

set -e

KW=$(printf '%02d' "$1")
YEAR="$2"
JSON_CONTENT="$3"

if [ -z "$KW" ] || [ -z "$YEAR" ] || [ -z "$JSON_CONTENT" ]; then
  echo "Usage: push-to-github.sh <KW_NUMBER> <YEAR> '<JSON_CONTENT>'"
  exit 1
fi

REPO="${ROSTER_REPO}"

if [ -z "$REPO" ]; then
  echo "ERROR: ROSTER_REPO environment variable is not set."
  echo "Set it to your GitHub repository in 'owner/repo' format."
  exit 1
fi
FILE_PATH="KW-${YEAR}/KW-${KW}-${YEAR}.json"

# Base64 encode via stdin to avoid shell escaping issues
CONTENT_B64=$(printf '%s' "$JSON_CONTENT" | base64 -w 0)

# Check if file already exists (to get its SHA for updates)
EXISTING_SHA=""
RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO/contents/$FILE_PATH?ref=main" 2>/dev/null || echo "{}")

EXISTING_SHA=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('sha',''))" 2>/dev/null || echo "")

# Build the API payload safely via python3 with sys.argv (no shell interpolation)
PAYLOAD=$(python3 -c "
import json, sys
msg = sys.argv[1]
b64 = sys.argv[2]
sha = sys.argv[3] if len(sys.argv) > 3 else ''
payload = {
    'message': msg,
    'content': b64,
    'branch': 'main'
}
if sha:
    payload['sha'] = sha
print(json.dumps(payload))
" "feat: add Dienstplan KW-${KW}-${YEAR}" "$CONTENT_B64" "$EXISTING_SHA")

# Push to GitHub
RESULT=$(curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO/contents/$FILE_PATH" \
  -d "$PAYLOAD")

# Check result
if echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'content' in d" 2>/dev/null; then
  COMMIT_SHA=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('commit',{}).get('sha','unknown'))")
  echo "SUCCESS: Pushed $FILE_PATH to GitHub"
  echo "Commit: $COMMIT_SHA"
  echo "URL: https://github.com/$REPO/blob/main/$FILE_PATH"
  echo "The GitHub Action will now build the PDF and send emails automatically."
else
  echo "ERROR: Failed to push to GitHub"
  echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message','Unknown error'))" 2>/dev/null || echo "$RESULT"
  exit 1
fi
