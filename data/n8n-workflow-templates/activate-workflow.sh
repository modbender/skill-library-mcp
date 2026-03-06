#!/bin/bash
# activate-workflow.sh - Activate a workflow by ID
# Usage: activate-workflow.sh <n8n-url> <api-key> <workflow-id>

set -euo pipefail

N8N_URL="${1:-}"
API_KEY="${2:-}"
WORKFLOW_ID="${3:-}"

if [[ -z "$N8N_URL" || -z "$API_KEY" || -z "$WORKFLOW_ID" ]]; then
    echo "Usage: activate-workflow.sh <n8n-url> <api-key> <workflow-id>"
    exit 1
fi

echo "Activating workflow $WORKFLOW_ID..."

RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "X-N8N-API-KEY: $API_KEY" \
    "$N8N_URL/api/v1/workflows/$WORKFLOW_ID/activate")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" == "200" || "$HTTP_CODE" == "201" ]]; then
    echo "✓ Workflow activated successfully"
else
    echo "✗ Failed to activate workflow (HTTP $HTTP_CODE)"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    exit 1
fi
