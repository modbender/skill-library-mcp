#!/bin/bash
# List all invoices for a given year (or fetch a specific invoice)
# Usage: get-invoices.sh [PREFIX] [YEAR] [NUMBER]
# Example: get-invoices.sh RE 2026        -> lists all RE-2026 invoices
# Example: get-invoices.sh RE 2026 6007   -> fetches RE-6007.json content

set -e

PREFIX="${1:-RE}"
YEAR="${2:-$(date +%Y)}"
NUMBER="$3"

REPO="${INVOICE_REPO}"

if [ -z "$REPO" ]; then
  echo "ERROR: INVOICE_REPO environment variable is not set."
  echo "Set it to your GitHub repository in 'owner/repo' format."
  exit 1
fi

if [ -n "$NUMBER" ]; then
  # Fetch a specific invoice
  FILE_PATH="${PREFIX}-${YEAR}/${PREFIX}-${NUMBER}.json"
  RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$REPO/contents/$FILE_PATH?ref=main" 2>/dev/null)

  printf '%s' "$RESPONSE" | python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
content = data.get('content', '')
decoded = base64.b64decode(content).decode('utf-8')
print(decoded)
"
else
  # List all invoices in the year directory
  DIR_PATH="${PREFIX}-${YEAR}"
  RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$REPO/contents/$DIR_PATH?ref=main" 2>/dev/null)

  python3 -c "
import sys, json, re

data = json.loads(sys.stdin.read())
if not isinstance(data, list):
    print('No invoices found for ${PREFIX}-${YEAR}')
    sys.exit(0)

invoices = []
for f in data:
    name = f.get('name', '')
    m = re.match(r'${PREFIX}-(\d+)\.json$', name)
    if m:
        invoices.append({'number': int(m.group(1)), 'name': name})

invoices.sort(key=lambda x: x['number'])
print(f'Found {len(invoices)} invoice(s) in ${PREFIX}-${YEAR}:')
for inv in invoices:
    print(f'  - {inv[\"name\"]}')
" <<< "$RESPONSE"
fi
