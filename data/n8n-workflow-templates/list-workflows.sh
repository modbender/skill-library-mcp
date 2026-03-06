#!/bin/bash
# list-workflows.sh - List active workflows on n8n instance
# Usage: list-workflows.sh <n8n-url> <api-key>

set -euo pipefail

N8N_URL="${1:-${N8N_HOST:-}}"
API_KEY="${2:-${N8N_API_KEY:-}}"

if [[ -z "$N8N_URL" || -z "$API_KEY" ]]; then
    echo "Usage: list-workflows.sh <n8n-url> <api-key>"
    echo ""
    echo "Or set environment variables:"
    echo '  export N8N_HOST="http://localhost:5678"'
    echo '  export N8N_API_KEY="n8n_api_xxx"'
    exit 1
fi

echo "Fetching workflows from $N8N_URL..."
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "X-N8N-API-KEY: $API_KEY" \
    "$N8N_URL/api/v1/workflows")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" == "200" ]]; then
    # Parse and display workflows
    echo "$BODY" | python3 -c "
import json
import sys

data = json.load(sys.stdin)
workflows = data.get('data', data) if isinstance(data, dict) else data

print(f\"{'ID':<20} {'Name':<40} {'Active':<8}\")
print('-' * 70)

for wf in workflows:
    if isinstance(wf, dict):
        wf_id = wf.get('id', 'N/A')[:18]
        name = wf.get('name', 'Unnamed')[:38]
        active = 'Yes' if wf.get('active', False) else 'No'
        print(f'{wf_id:<20} {name:<40} {active:<8}')

print('-' * 70)
print(f'Total workflows: {len(workflows)}')
"
else
    echo "✗ Failed to fetch workflows (HTTP $HTTP_CODE)"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    exit 1
fi
