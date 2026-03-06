#!/usr/bin/env bash
# n8n API helper — create, list, get, activate, deactivate, delete workflows
# Requires: N8N_URL and N8N_API_KEY environment variables
set -euo pipefail

N8N_URL="${N8N_URL:-http://localhost:5678}"
N8N_API_KEY="${N8N_API_KEY:-}"

if [ -z "$N8N_API_KEY" ]; then
  echo "ERROR: N8N_API_KEY not set" >&2; exit 1
fi

AUTH_HEADER="X-N8N-API-KEY: $N8N_API_KEY"
BASE="$N8N_URL/api/v1"

usage() {
  cat <<EOF
Usage: n8n-api.sh <command> [args]

Commands:
  list                          List all workflows
  get <workflow_id>             Get workflow by ID
  create <json_file>            Create workflow from JSON file
  create-stdin                  Create workflow from stdin JSON
  update <workflow_id> <json>   Update workflow from JSON file
  activate <workflow_id>        Activate workflow
  deactivate <workflow_id>      Deactivate workflow
  delete <workflow_id>          Delete workflow
  execute <workflow_id>         Execute workflow manually
  tags                          List all tags
  credentials                   List all credentials
EOF
}

case "${1:-}" in
  list)
    curl -s -H "$AUTH_HEADER" "$BASE/workflows" | jq .
    ;;
  get)
    curl -s -H "$AUTH_HEADER" "$BASE/workflows/$2" | jq .
    ;;
  create)
    curl -s -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
      -d @"$2" "$BASE/workflows" | jq .
    ;;
  create-stdin)
    curl -s -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
      -d @- "$BASE/workflows" | jq .
    ;;
  update)
    curl -s -X PUT -H "$AUTH_HEADER" -H "Content-Type: application/json" \
      -d @"$3" "$BASE/workflows/$2" | jq .
    ;;
  activate)
    curl -s -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
      -d '{"active": true}' "$BASE/workflows/$2/activate" | jq .
    ;;
  deactivate)
    curl -s -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
      -d '{"active": false}' "$BASE/workflows/$2/deactivate" | jq .
    ;;
  delete)
    curl -s -X DELETE -H "$AUTH_HEADER" "$BASE/workflows/$2" | jq .
    ;;
  execute)
    curl -s -X POST -H "$AUTH_HEADER" "$BASE/workflows/$2/run" | jq .
    ;;
  tags)
    curl -s -H "$AUTH_HEADER" "$BASE/tags" | jq .
    ;;
  credentials)
    curl -s -H "$AUTH_HEADER" "$BASE/credentials" | jq .
    ;;
  *)
    usage
    ;;
esac
