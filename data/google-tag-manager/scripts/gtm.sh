#!/usr/bin/env bash
# Google Tag Manager API v2 CLI wrapper
# Requires: GOOGLE_APPLICATION_CREDENTIALS, GTM_ACCOUNT_ID, GTM_CONTAINER_ID
set -euo pipefail

BASE="https://tagmanager.googleapis.com/tagmanager/v2"

# --- Auth ---
get_access_token() {
  # Use gcloud if available, otherwise use service account JWT flow
  if command -v gcloud &>/dev/null; then
    gcloud auth print-access-token 2>/dev/null && return
  fi
  
  if [[ -z "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]]; then
    echo "ERROR: Set GOOGLE_APPLICATION_CREDENTIALS or configure gcloud auth" >&2
    exit 1
  fi
  
  # Python JWT-based token generation for service accounts
  python3 - "$GOOGLE_APPLICATION_CREDENTIALS" <<'PYEOF'
import json, sys, time, urllib.request, urllib.parse
try:
    import jwt
except ImportError:
    print("ERROR: pip3 install PyJWT cryptography", file=sys.stderr)
    sys.exit(1)

with open(sys.argv[1]) as f:
    sa = json.load(f)

now = int(time.time())
payload = {
    "iss": sa["client_email"],
    "scope": "https://www.googleapis.com/auth/tagmanager.edit.containers https://www.googleapis.com/auth/tagmanager.publish https://www.googleapis.com/auth/tagmanager.readonly",
    "aud": "https://oauth2.googleapis.com/token",
    "iat": now,
    "exp": now + 3600
}
signed = jwt.encode(payload, sa["private_key"], algorithm="RS256")
data = urllib.parse.urlencode({
    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "assertion": signed
}).encode()
req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
resp = json.loads(urllib.request.urlopen(req).read())
print(resp["access_token"])
PYEOF
}

TOKEN=""
auth_header() {
  [[ -z "$TOKEN" ]] && TOKEN=$(get_access_token)
  echo "Authorization: Bearer $TOKEN"
}

# --- Helpers ---
ACCOUNT="${GTM_ACCOUNT_ID:?Set GTM_ACCOUNT_ID}"
CONTAINER="${GTM_CONTAINER_ID:?Set GTM_CONTAINER_ID}"
CONTAINER_PATH="accounts/$ACCOUNT/containers/$CONTAINER"

api_get() {
  curl -sf -H "$(auth_header)" "$BASE/$1"
}

api_post() {
  curl -sf -X POST -H "$(auth_header)" -H "Content-Type: application/json" ${2:+-d "$2"} "$BASE/$1"
}

api_put() {
  curl -sf -X PUT -H "$(auth_header)" -H "Content-Type: application/json" -d "$2" "$BASE/$1"
}

api_delete() {
  curl -sf -X DELETE -H "$(auth_header)" "$BASE/$1"
}

resolve_workspace() {
  local ws="${1:-}"
  if [[ -n "$ws" ]]; then
    echo "$ws"
  else
    # Auto-resolve: pick first workspace
    api_get "$CONTAINER_PATH/workspaces" | python3 -c "import json,sys; ws=json.load(sys.stdin).get('workspace',[]); print(ws[0]['workspaceId'] if ws else '')"
  fi
}

ws_path() {
  local ws
  ws=$(resolve_workspace "${1:-}")
  echo "$CONTAINER_PATH/workspaces/$ws"
}

usage() {
  cat <<EOF
Google Tag Manager API v2 CLI

Usage: $(basename "$0") <command> [args...]

Account & Container:
  accounts                          List GTM accounts
  containers [accountId]            List containers
  workspaces                        List workspaces

Tags:
  tags [workspaceId]                List all tags
  tag <tagId> [workspaceId]         Get a tag
  create-tag <json> [workspaceId]   Create a tag (json file or -)
  update-tag <tagId> <json> [wsId]  Update a tag
  delete-tag <tagId> [workspaceId]  Delete a tag

Triggers:
  triggers [workspaceId]            List all triggers
  trigger <id> [workspaceId]        Get a trigger
  create-trigger <json> [wsId]      Create a trigger
  update-trigger <id> <json> [wsId] Update a trigger
  delete-trigger <id> [wsId]        Delete a trigger

Variables:
  variables [workspaceId]           List all variables
  variable <id> [workspaceId]       Get a variable
  create-variable <json> [wsId]     Create a variable
  update-variable <id> <json> [ws]  Update a variable
  delete-variable <id> [wsId]       Delete a variable
  built-in-vars [workspaceId]       List enabled built-in variables
  enable-built-in <types> [wsId]    Enable built-in variable(s), comma-separated

Versions:
  versions                          List version headers
  version <versionId>               Get a version
  version-live                      Get live (published) version
  create-version [wsId] [name] [notes]  Create version from workspace
  publish <versionId>               Publish a version

Environment:
  GTM_ACCOUNT_ID     - GTM account ID (required)
  GTM_CONTAINER_ID   - GTM container ID (required)
  GOOGLE_APPLICATION_CREDENTIALS - Service account JSON (or use gcloud auth)
EOF
  exit 0
}

read_json() {
  # Read JSON from file path or stdin (-)
  local src="$1"
  if [[ "$src" == "-" ]]; then
    cat
  elif [[ -f "$src" ]]; then
    cat "$src"
  else
    echo "ERROR: File not found: $src" >&2
    exit 1
  fi
}

# --- Commands ---
CMD="${1:-help}"
shift || true

case "$CMD" in
  help|--help|-h) usage ;;

  # Account & Container
  accounts)
    api_get "accounts" ;;
  containers)
    local_account="${1:-$ACCOUNT}"
    api_get "accounts/$local_account/containers" ;;
  workspaces)
    api_get "$CONTAINER_PATH/workspaces" ;;

  # Tags
  tags)
    api_get "$(ws_path "${1:-}")/tags" ;;
  tag)
    api_get "$(ws_path "${2:-}")/tags/${1:?tagId required}" ;;
  create-tag)
    json=$(read_json "${1:?json file required}")
    api_post "$(ws_path "${2:-}")/tags" "$json" ;;
  update-tag)
    tag_id="${1:?tagId required}"; json=$(read_json "${2:?json file required}")
    api_put "$(ws_path "${3:-}")/tags/$tag_id" "$json" ;;
  delete-tag)
    api_delete "$(ws_path "${2:-}")/tags/${1:?tagId required}" ;;

  # Triggers
  triggers)
    api_get "$(ws_path "${1:-}")/triggers" ;;
  trigger)
    api_get "$(ws_path "${2:-}")/triggers/${1:?triggerId required}" ;;
  create-trigger)
    json=$(read_json "${1:?json file required}")
    api_post "$(ws_path "${2:-}")/triggers" "$json" ;;
  update-trigger)
    tid="${1:?triggerId required}"; json=$(read_json "${2:?json file required}")
    api_put "$(ws_path "${3:-}")/triggers/$tid" "$json" ;;
  delete-trigger)
    api_delete "$(ws_path "${2:-}")/triggers/${1:?triggerId required}" ;;

  # Variables
  variables)
    api_get "$(ws_path "${1:-}")/variables" ;;
  variable)
    api_get "$(ws_path "${2:-}")/variables/${1:?variableId required}" ;;
  create-variable)
    json=$(read_json "${1:?json file required}")
    api_post "$(ws_path "${2:-}")/variables" "$json" ;;
  update-variable)
    vid="${1:?variableId required}"; json=$(read_json "${2:?json file required}")
    api_put "$(ws_path "${3:-}")/variables/$vid" "$json" ;;
  delete-variable)
    api_delete "$(ws_path "${2:-}")/variables/${1:?variableId required}" ;;
  built-in-vars)
    api_get "$(ws_path "${1:-}")/built_in_variables" ;;
  enable-built-in)
    types="${1:?types required (comma-separated)}"
    ws=$(ws_path "${2:-}")
    # Build query params: type=X&type=Y
    params=""
    IFS=',' read -ra TYPE_ARR <<< "$types"
    for t in "${TYPE_ARR[@]}"; do
      params+="type=$t&"
    done
    api_post "$ws/built_in_variables?${params%&}" ;;

  # Versions
  versions)
    api_get "$CONTAINER_PATH/version_headers" ;;
  version)
    api_get "$CONTAINER_PATH/versions/${1:?versionId required}" ;;
  version-live)
    api_get "$CONTAINER_PATH/versions:live" ;;
  create-version)
    ws=$(ws_path "${1:-}")
    name="${2:-}"
    notes="${3:-}"
    body="{}"
    if [[ -n "$name" || -n "$notes" ]]; then
      body=$(python3 -c "import json; print(json.dumps({k:v for k,v in {'name':'$name','notes':'$notes'}.items() if v}))")
    fi
    api_post "$ws:create_version" "$body" ;;
  publish)
    api_post "$CONTAINER_PATH/versions/${1:?versionId required}:publish" ;;

  *)
    echo "Unknown command: $CMD" >&2
    echo "Run '$(basename "$0") help' for usage." >&2
    exit 1 ;;
esac
