#!/bin/bash
# delete-workflow.sh - Delete a workflow by ID
# Usage: delete-workflow.sh <n8n-url> <api-key> <workflow-id>

set -euo pipefail

N8N_URL="${1:-}"
API_KEY="${2:-}"
WORKFLOW_ID="${3:-}"

if [[ -z "$N8N_URL" || -z "$API_KEY" || -z "$WORKFLOW_ID" ]]; then
    echo "Usage: delete-workflow.sh <n8n-url> <api-key> <workflow-id>"
    exit 1
fi

read -p "Are you sure you want to delete workflow $WORKFLOW_ID? (yes/no): " CONFIRM
if [[ "$CONFIRM" != "yes" ]]; then
    echo "Cancelled"
    exit 0
fi

echo "Deleting workflow $WORKFLOW_ID..."

RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X DELETE \
    -H "X-N8N-API-KEY: $API_KEY" \
    "$N8N_URL/api/v1/workflows/$WORKFLOW_ID")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [[ "$HTTP_CODE" == "200" || "$HTTP_CODE" == "204" ]]; then
    echo "✓ Workflow deleted successfully"
else
    BODY=$(echo "$RESPONSE" | sed '$d')
    echo "✗ Failed to delete workflow (HTTP $HTTP_CODE)"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    exit 1
fi
