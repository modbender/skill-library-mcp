#!/bin/bash
# Determine the next invoice number by scanning existing files on GitHub
# Usage: get-next-number.sh [PREFIX] [YEAR]
# Example: get-next-number.sh RE 2026
# Outputs the next sequential number (e.g. 6008 if RE-6007 is the last)

set -e

PREFIX="${1:-RE}"
YEAR="${2:-$(date +%Y)}"

REPO="${INVOICE_REPO}"

if [ -z "$REPO" ]; then
  echo "ERROR: INVOICE_REPO environment variable is not set."
  echo "Set it to your GitHub repository in 'owner/repo' format."
  exit 1
fi

DIR_PATH="${PREFIX}-${YEAR}"

# List files in the year directory
RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO/contents/$DIR_PATH?ref=main" 2>/dev/null)

# Extract the highest invoice number from filenames
NEXT_NUMBER=$(python3 -c "
import sys, json, re

try:
    files = json.loads(sys.stdin.read())
    if not isinstance(files, list):
        print('${PREFIX}' + '6001')
        sys.exit(0)
    numbers = []
    for f in files:
        name = f.get('name', '')
        m = re.match(r'${PREFIX}-(\d+)\.json$', name)
        if m:
            numbers.append(int(m.group(1)))
    if numbers:
        print(max(numbers) + 1)
    else:
        print(6001)
except Exception:
    print(6001)
" <<< "$RESPONSE")

echo "$NEXT_NUMBER"
