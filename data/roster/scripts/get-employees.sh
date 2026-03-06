#!/bin/bash
# Fetch current employees.json from GitHub
# Usage: get-employees.sh
# Outputs the JSON content to stdout

set -e

REPO="${ROSTER_REPO}"

if [ -z "$REPO" ]; then
  echo "ERROR: ROSTER_REPO environment variable is not set."
  echo "Set it to your GitHub repository in 'owner/repo' format."
  exit 1
fi
FILE_PATH="employees.json"

RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO/contents/$FILE_PATH?ref=main" 2>/dev/null)

# Decode content from base64 via stdin (no shell interpolation)
printf '%s' "$RESPONSE" | python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
content = data.get('content', '')
decoded = base64.b64decode(content).decode('utf-8')
print(decoded)
"
