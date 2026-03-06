#!/usr/bin/env bash
# Chainbase API wrapper script
# Usage: chainbase.sh <endpoint> [params...]
#
# Web3 API:
#   chainbase.sh /v1/token/top-holders chain_id=1 contract_address=0x...
#
# SQL API (async - auto-polls for results):
#   chainbase.sh /query/execute --sql="SELECT * FROM ethereum.blocks LIMIT 5"
#
# SQL API (fetch existing results):
#   chainbase.sh /execution/<id>/results

set -euo pipefail

API_KEY="${CHAINBASE_API_KEY:-demo}"
BASE_URL="https://api.chainbase.online"
SQL_BASE_URL="https://api.chainbase.com/api/v1"
SQL_POLL_INTERVAL=2
SQL_POLL_MAX=30

endpoint="$1"
shift || true

# Build query string from remaining args
query=""
body=""
method="GET"
is_sql_execute=false

for arg in "$@"; do
  case "$arg" in
    --method=*)
      method="${arg#--method=}"
      ;;
    --sql=*)
      body="{\"sql\": \"${arg#--sql=}\"}"
      method="POST"
      is_sql_execute=true
      ;;
    --body=*)
      body="${arg#--body=}"
      method="POST"
      ;;
    *)
      if [ -z "$query" ]; then
        query="?${arg}"
      else
        query="${query}&${arg}"
      fi
      ;;
  esac
done

pretty_json() {
  python3 -m json.tool 2>/dev/null || cat
}

api_call() {
  local call_method="$1" call_url="$2" call_header="$3" call_body="${4:-}"
  if [ "$call_method" = "POST" ]; then
    curl -s -X POST "$call_url" \
      -H "${call_header}: ${API_KEY}" \
      -H "Content-Type: application/json" \
      -d "$call_body"
  else
    curl -s "$call_url" -H "${call_header}: ${API_KEY}"
  fi
}

# Determine base URL and header
if [[ "$endpoint" == /query/* ]] || [[ "$endpoint" == /execution/* ]] || [[ "$endpoint" == /dw/* ]]; then
  url="${SQL_BASE_URL}${endpoint}${query}"
  api_header="X-API-KEY"
else
  url="${BASE_URL}${endpoint}${query}"
  api_header="x-api-key"
fi

result=$(api_call "$method" "$url" "$api_header" "$body")

# For SQL execute: auto-poll for results
if [ "$is_sql_execute" = true ]; then
  exec_id=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data'][0]['executionId'])" 2>/dev/null || true)

  if [ -n "$exec_id" ]; then
    echo "Execution ID: $exec_id" >&2
    echo "Polling for results..." >&2

    poll_url="${SQL_BASE_URL}/execution/${exec_id}/status"
    for i in $(seq 1 $SQL_POLL_MAX); do
      sleep $SQL_POLL_INTERVAL
      status_result=$(api_call "GET" "$poll_url" "$api_header")
      status=$(echo "$status_result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data'][0]['status'])" 2>/dev/null || echo "UNKNOWN")

      if [ "$status" = "FINISHED" ] || [ "$status" = "FAILED" ]; then
        result_url="${SQL_BASE_URL}/execution/${exec_id}/results"
        api_call "GET" "$result_url" "$api_header" | pretty_json
        exit 0
      fi
      echo "  Status: $status (attempt $i/$SQL_POLL_MAX)" >&2
    done

    echo "Timeout waiting for query. Check manually:" >&2
    echo "  chainbase.sh /execution/${exec_id}/results" >&2
    echo "$result" | pretty_json
    exit 1
  fi
fi

echo "$result" | pretty_json
