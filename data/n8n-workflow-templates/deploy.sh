#!/bin/bash
# deploy.sh - Deploy n8n workflow template
# Usage: deploy.sh <n8n-url> <api-key> <template-file> [workflow-name]

set -euo pipefail

N8N_URL="${1:-}"
API_KEY="${2:-}"
TEMPLATE_FILE="${3:-}"
WORKFLOW_NAME="${4:-}"

if [[ -z "$N8N_URL" || -z "$API_KEY" || -z "$TEMPLATE_FILE" ]]; then
    echo "Usage: deploy.sh <n8n-url> <api-key> <template-file> [workflow-name]"
    echo ""
    echo "Example:"
    echo '  deploy.sh "http://localhost:5678" "n8n_api_xxx" templates/health-check.json'
    exit 1
fi

if [[ ! -f "$TEMPLATE_FILE" ]]; then
    echo "Error: Template file not found: $TEMPLATE_FILE"
    exit 1
fi

# Validate JSON
if ! python3 -c "import json; json.load(open('$TEMPLATE_FILE'))" 2>/dev/null; then
    echo "Error: Invalid JSON in template file"
    exit 1
fi

# Read and optionally rename workflow
WORKFLOW_JSON=$(cat "$TEMPLATE_FILE")
if [[ -n "$WORKFLOW_NAME" ]]; then
    WORKFLOW_JSON=$(echo "$WORKFLOW_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); d['name']='$WORKFLOW_NAME'; print(json.dumps(d))")
fi

echo "Deploying workflow to $N8N_URL..."

# Deploy workflow
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-N8N-API-KEY: $API_KEY" \
    "$N8N_URL/api/v1/workflows" \
    -d "$WORKFLOW_JSON")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" == "200" || "$HTTP_CODE" == "201" ]]; then
    WORKFLOW_ID=$(echo "$BODY" | python3 -c "import json,sys; print(json.load(sys.stdin).get('id','unknown'))")
    WORKFLOW_NAME=$(echo "$BODY" | python3 -c "import json,sys; print(json.load(sys.stdin).get('name','unnamed'))")
    echo "✓ Successfully deployed workflow"
    echo "  Name: $WORKFLOW_NAME"
    echo "  ID: $WORKFLOW_ID"
    echo "  URL: $N8N_URL/workflow/$WORKFLOW_ID"
else
    echo "✗ Deployment failed (HTTP $HTTP_CODE)"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    exit 1
fi
