#!/usr/bin/env bash
# rollbar.sh — Rollbar API helper for OpenClaw
# Supports both account-level and project-level tokens.
# Usage: rollbar.sh <command> [options]

set -euo pipefail

# --- Config ---
TOKEN="${ROLLBAR_ACCESS_TOKEN:-}"
BASE_URL="https://api.rollbar.com/api/1"

if [[ -z "$TOKEN" ]]; then
  echo "Error: ROLLBAR_ACCESS_TOKEN is not set." >&2
  echo "Set it via environment variable or add it to TOOLS.md." >&2
  exit 1
fi

# --- Helpers ---
api_get() {
  local endpoint="$1"
  shift
  curl -sf -H "X-Rollbar-Access-Token: $TOKEN" "$BASE_URL/$endpoint" "$@"
}

api_patch() {
  local endpoint="$1"
  local data="$2"
  curl -sf -X PATCH \
    -H "X-Rollbar-Access-Token: $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$data" \
    "$BASE_URL/$endpoint"
}

usage() {
  cat <<EOF
Usage: rollbar.sh <command> [options]

Commands:
  projects              List all projects (account token)
  items                 List recent items
  item <id>             Get item details
  occurrences <id>      Get occurrences for an item
  resolve <id>          Resolve an item
  mute <id>             Mute an item
  activate <id>         Reopen an item
  deploys               List recent deploys
  project               Get project info
  top                   Top active items by occurrence count

Options:
  --project-id <id>     Target a specific project (for account tokens)
  --status <active|resolved|muted>   Filter by status (items)
  --level <critical|error|warning|info>  Filter by level (items)
  --limit <n>           Max results (default: 20)
  --hours <n>           Time window for 'top' (default: 24)

Environment:
  ROLLBAR_ACCESS_TOKEN  Required. Account or project access token.
EOF
  exit 0
}

# Helper: get project tokens from account token
get_project_token() {
  local project_id="$1"
  local tmpfile
  tmpfile=$(mktemp)
  api_get "project/$project_id/access_tokens" > "$tmpfile" 2>/dev/null
  local result
  result=$(python3 -c "
import json
with open('$tmpfile') as f:
    tokens = json.load(f).get('result', [])
for t in tokens:
    if 'read' in t.get('scopes', []):
        print(t['access_token']); break
" 2>/dev/null)
  rm -f "$tmpfile"
  echo "$result"
}

# --- Parse command ---
COMMAND="${1:-}"
[[ -z "$COMMAND" || "$COMMAND" == "--help" || "$COMMAND" == "-h" ]] && usage
shift

# --- Parse options ---
STATUS=""
LEVEL=""
LIMIT="20"
HOURS="24"
ITEM_ID=""
PROJECT_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --status)      STATUS="$2"; shift 2 ;;
    --level)       LEVEL="$2"; shift 2 ;;
    --limit)       LIMIT="$2"; shift 2 ;;
    --hours)       HOURS="$2"; shift 2 ;;
    --project-id)  PROJECT_ID="$2"; shift 2 ;;
    *)
      if [[ -z "$ITEM_ID" ]]; then
        ITEM_ID="$1"; shift
      else
        echo "Unknown option: $1" >&2; exit 1
      fi
      ;;
  esac
done

# --- Input validation ---
# ITEM_ID: must be alphanumeric (Rollbar item IDs are numeric)
if [[ -n "$ITEM_ID" && ! "$ITEM_ID" =~ ^[a-zA-Z0-9_-]+$ ]]; then
  echo "Error: Invalid item ID: $ITEM_ID" >&2; exit 1
fi
# PROJECT_ID: must be numeric
if [[ -n "$PROJECT_ID" && ! "$PROJECT_ID" =~ ^[0-9]+$ ]]; then
  echo "Error: Invalid project ID: $PROJECT_ID" >&2; exit 1
fi
# LIMIT: must be numeric
if [[ ! "$LIMIT" =~ ^[0-9]+$ ]]; then
  echo "Error: Invalid limit: $LIMIT" >&2; exit 1
fi
# HOURS: must be numeric
if [[ ! "$HOURS" =~ ^[0-9]+$ ]]; then
  echo "Error: Invalid hours: $HOURS" >&2; exit 1
fi

# If project-id is given and we have an account token, resolve a project-level token
if [[ -n "$PROJECT_ID" && "$COMMAND" != "projects" ]]; then
  PROJECT_TOKEN=$(get_project_token "$PROJECT_ID")
  if [[ -n "$PROJECT_TOKEN" ]]; then
    TOKEN="$PROJECT_TOKEN"
  fi
fi

# --- Commands ---
case "$COMMAND" in
  projects)
    api_get "projects" | python3 -c "
import json, sys
data = json.load(sys.stdin)
projects = data.get('result', [])
result = []
for p in projects:
    result.append({
        'id': p['id'],
        'name': p['name'],
        'status': p.get('status', '?'),
        'date_created': p.get('date_created'),
    })
print(json.dumps(result, indent=2))
"
    ;;

  items)
    PARAMS="?page=1&sort=last_occurrence"
    [[ -n "$STATUS" ]] && PARAMS="$PARAMS&status=$STATUS"
    [[ -n "$LEVEL" ]] && PARAMS="$PARAMS&level=$LEVEL"
    api_get "items$PARAMS" | _LIMIT="$LIMIT" python3 -c "
import json, sys, os
data = json.load(sys.stdin)
items = data.get('result', {}).get('items', data.get('result', []))
limit = int(os.environ['_LIMIT'])
if isinstance(items, list):
    items = items[:limit]
result = []
for i in items:
    result.append({
        'id': i['id'],
        'counter': i.get('counter'),
        'title': i.get('title', '')[:150],
        'level': i.get('level_string', i.get('level', '')),
        'status': i.get('status', ''),
        'total_occurrences': i.get('total_occurrences', 0),
        'last_occurrence': i.get('last_occurrence_timestamp'),
        'environment': i.get('environment', ''),
        'framework': i.get('framework', ''),
    })
print(json.dumps(result, indent=2))
"
    ;;

  item)
    [[ -z "$ITEM_ID" ]] && { echo "Usage: rollbar.sh item <item_id>" >&2; exit 1; }
    api_get "item/$ITEM_ID" | python3 -m json.tool 2>/dev/null || api_get "item/$ITEM_ID"
    ;;

  occurrences)
    [[ -z "$ITEM_ID" ]] && { echo "Usage: rollbar.sh occurrences <item_id>" >&2; exit 1; }
    api_get "item/$ITEM_ID/instances/?page=1" | python3 -m json.tool 2>/dev/null || api_get "item/$ITEM_ID/instances/?page=1"
    ;;

  resolve)
    [[ -z "$ITEM_ID" ]] && { echo "Usage: rollbar.sh resolve <item_id>" >&2; exit 1; }
    api_patch "item/$ITEM_ID" '{"status":"resolved"}' | python3 -m json.tool 2>/dev/null || api_patch "item/$ITEM_ID" '{"status":"resolved"}'
    ;;

  mute)
    [[ -z "$ITEM_ID" ]] && { echo "Usage: rollbar.sh mute <item_id>" >&2; exit 1; }
    api_patch "item/$ITEM_ID" '{"status":"muted"}' | python3 -m json.tool 2>/dev/null || api_patch "item/$ITEM_ID" '{"status":"muted"}'
    ;;

  activate)
    [[ -z "$ITEM_ID" ]] && { echo "Usage: rollbar.sh activate <item_id>" >&2; exit 1; }
    api_patch "item/$ITEM_ID" '{"status":"active"}' | python3 -m json.tool 2>/dev/null || api_patch "item/$ITEM_ID" '{"status":"active"}'
    ;;

  deploys)
    api_get "deploys/?page=1" | python3 -m json.tool 2>/dev/null || api_get "deploys/?page=1"
    ;;

  project)
    api_get "project" | python3 -m json.tool 2>/dev/null || api_get "project"
    ;;

  top)
    PARAMS="?status=active&sort=total_occurrences&direction=desc&page=1"
    [[ -n "$LEVEL" ]] && PARAMS="$PARAMS&level=$LEVEL"
    api_get "items$PARAMS" | _HOURS="$HOURS" _LIMIT="$LIMIT" python3 -c "
import json, sys, os
from datetime import datetime, timedelta, timezone

data = json.load(sys.stdin)
items = data.get('result', {}).get('items', data.get('result', []))
hours = int(os.environ['_HOURS'])
limit = int(os.environ['_LIMIT'])
cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

print(json.dumps({
    'window_hours': hours,
    'items': [{
        'id': i['id'],
        'counter': i.get('counter'),
        'title': i.get('title', '')[:120],
        'level': i.get('level_string', i.get('level', '')),
        'total_occurrences': i.get('total_occurrences', 0),
        'last_occurrence': i.get('last_occurrence_timestamp'),
        'environment': i.get('environment', ''),
    } for i in (items if isinstance(items, list) else [])
      if i.get('last_occurrence_timestamp', 0) >= cutoff.timestamp()
    ][:limit]
}, indent=2))
" 2>/dev/null || api_get "items$PARAMS"
    ;;

  *)
    echo "Unknown command: $COMMAND" >&2
    usage
    ;;
esac
