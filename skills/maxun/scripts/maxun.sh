#!/usr/bin/env bash
# maxun.sh — Maxun SDK API helper for OpenClaw
# All routes are under /api/sdk/ and require x-api-key header only.
#
# Commands:
#   list                        List all robots
#   get <robotId>               Get robot details
#   run <robotId>               Execute a robot (synchronous — waits for result)
#   result <robotId> <runId>    Get a specific run result
#   runs <robotId>              List all runs for a robot
#   abort <robotId> <runId>     Abort an in-progress run

set -euo pipefail

BASE_URL="${MAXUN_BASE_URL:-https://app.maxun.dev}"
API_KEY="${MAXUN_API_KEY:-}"

if [[ -z "$API_KEY" ]]; then
  echo '{"error": "MAXUN_API_KEY environment variable is not set"}' >&2
  exit 1
fi

AUTH_HEADER="x-api-key: $API_KEY"

_get() {
  curl -sf -H "$AUTH_HEADER" -H "Content-Type: application/json" "$BASE_URL$1"
}

_post() {
  local path="$1"
  local body="${2:-{}}"
  curl -sf -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
    -d "$body" "$BASE_URL$path"
}

cmd="${1:-}"

case "$cmd" in

  list)
    LIMIT="${2:-}"
    _get "/api/sdk/robots" | python3 -c "
import json, sys
raw = '${LIMIT}'
limit = int(raw) if raw.isdigit() else None
data = json.load(sys.stdin)
robots = data.get('data', [])
total = len(robots)
if limit:
    robots = robots[:limit]
if not robots:
    print('No robots found.')
else:
    shown = len(robots)
    print(f'Showing {shown} of {total} robot(s):\n' if limit else f'Found {total} robot(s):\n')
    for r in robots:
        meta = r.get('recording_meta', {})
        print(f'  ID:      {meta.get(\"id\", r.get(\"id\", \"\"))}')
        print(f'  Name:    {meta.get(\"name\", \"\")}')
        print(f'  Type:    {meta.get(\"type\", \"\")}')
        print(f'  URL:     {meta.get(\"url\", \"\")}')
        print()
"
    ;;

  get)
    ROBOT_ID="${2:?'Usage: maxun.sh get <robotId>'}"
    _get "/api/sdk/robots/$ROBOT_ID" | python3 -c "
import json, sys
data = json.load(sys.stdin)
robot = data.get('data', data)
print(json.dumps(robot, indent=2))
"
    ;;

  run)
    ROBOT_ID="${2:?'Usage: maxun.sh run <robotId>'}"
    echo "Executing robot $ROBOT_ID (waiting for completion)..." >&2
    _post "/api/sdk/robots/$ROBOT_ID/execute" | python3 -c "
import json, sys
data = json.load(sys.stdin)
result = data.get('data', data)
print(f'Run ID:  {result.get(\"runId\", \"\")}')
print(f'Status:  {result.get(\"status\", \"\")}')
print()
extracted = result.get('data', {})
text_data = extracted.get('textData', {})
list_data = extracted.get('listData', [])
crawl_data = extracted.get('crawlData', [])
search_data = extracted.get('searchData', {})
if text_data:
    print('Text Data:')
    print(json.dumps(text_data, indent=2))
if list_data:
    print(f'List Data ({len(list_data)} items):')
    print(json.dumps(list_data[:5], indent=2))
    if len(list_data) > 5:
        print(f'  ... and {len(list_data) - 5} more items')
if crawl_data:
    print(f'Crawl Data ({len(crawl_data)} pages):')
    print(json.dumps(crawl_data[:3], indent=2))
if search_data:
    print('Search Data:')
    print(json.dumps(search_data, indent=2))
if not any([text_data, list_data, crawl_data, search_data]):
    print('No data extracted.')
    print(json.dumps(result, indent=2))
"
    ;;

  result)
    ROBOT_ID="${2:?'Usage: maxun.sh result <robotId> <runId>'}"
    RUN_ID="${3:?'Usage: maxun.sh result <robotId> <runId>'}"
    _get "/api/sdk/robots/$ROBOT_ID/runs/$RUN_ID" | python3 -c "
import json, sys
data = json.load(sys.stdin)
run = data.get('data', data)
print(f'Run ID:  {run.get(\"runId\", run.get(\"id\", \"\"))}')
print(f'Status:  {run.get(\"status\", \"\")}')
print(f'Started: {run.get(\"startedAt\", \"\")}')
print(f'Ended:   {run.get(\"finishedAt\", \"\")}')
print()
output = run.get('serializableOutput', {})
if output:
    print('Output:')
    print(json.dumps(output, indent=2))
else:
    print('No output yet.')
"
    ;;

  runs)
    ROBOT_ID="${2:?'Usage: maxun.sh runs <robotId>'}"
    _get "/api/sdk/robots/$ROBOT_ID/runs" | python3 -c "
import json, sys
data = json.load(sys.stdin)
runs = data.get('data', [])
print(f'Total runs: {len(runs)}\n')
for r in runs:
    print(f'  Run ID: {r.get(\"runId\",\"\")}  |  Status: {r.get(\"status\",\"?\")}  |  Started: {r.get(\"startedAt\",\"\")}')
"
    ;;

  abort)
    ROBOT_ID="${2:?'Usage: maxun.sh abort <robotId> <runId>'}"
    RUN_ID="${3:?'Usage: maxun.sh abort <robotId> <runId>'}"
    _post "/api/sdk/robots/$ROBOT_ID/runs/$RUN_ID/abort" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(json.dumps(data, indent=2))
"
    ;;

  *)
    echo "Maxun SDK API helper"
    echo ""
    echo "Usage: maxun.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  list                         List all robots"
    echo "  get <robotId>                Get robot details"
    echo "  run <robotId>                Execute a robot (synchronous)"
    echo "  result <robotId> <runId>     Get a specific run result"
    echo "  runs <robotId>               List all runs for a robot"
    echo "  abort <robotId> <runId>      Abort a running execution"
    echo ""
    echo "Environment:"
    echo "  MAXUN_API_KEY    Required. Your Maxun API key."
    echo "  MAXUN_BASE_URL   Optional. Default: https://app.maxun.dev"
    exit 1
    ;;
esac
