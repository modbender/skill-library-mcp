#!/usr/bin/env bash
# Tradekix API wrapper for OpenClaw agents
set -euo pipefail

BASE_URL="https://www.tradekix.ai/api/v1"
CONFIG_DIR="$HOME/.config/tradekix"
CONFIG_FILE="$CONFIG_DIR/config.json"

# Load API key from config
load_key() {
  if [[ -f "$CONFIG_FILE" ]]; then
    python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['api_key'])" 2>/dev/null || {
      echo "Error: Invalid config. Run: tradekix.sh signup" >&2; exit 1
    }
  else
    echo "Error: No API key found. Run: tradekix.sh signup --name YOUR_NAME --email YOUR_EMAIL" >&2; exit 1
  fi
}

# Authenticated GET request
api_get() {
  local endpoint="$1"
  local key; key=$(load_key)
  curl -sL "${BASE_URL}${endpoint}" -H "X-API-Key: $key" -H "Accept: application/json"
}

# Authenticated POST request
api_post() {
  local endpoint="$1"
  local body="${2:-{}}"
  local key; key=$(load_key)
  curl -sL "${BASE_URL}${endpoint}" -X POST -H "X-API-Key: $key" -H "Content-Type: application/json" -d "$body"
}

# Unauthenticated POST
api_post_noauth() {
  local endpoint="$1"
  local body="$2"
  curl -sL "${BASE_URL}${endpoint}" -X POST -H "Content-Type: application/json" -d "$body"
}

cmd="${1:-help}"
shift || true

case "$cmd" in
  signup)
    name=""; email=""; moltbook=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --name) name="$2"; shift 2 ;;
        --email) email="$2"; shift 2 ;;
        --moltbook) moltbook="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    if [[ -z "$name" || -z "$email" ]]; then
      echo "Usage: tradekix.sh signup --name AGENT_NAME --email EMAIL [--moltbook MOLTBOOK_ID]" >&2; exit 1
    fi
    body="{\"agent_name\":\"$name\",\"email\":\"$email\""
    [[ -n "$moltbook" ]] && body+=",\"moltbook_id\":\"$moltbook\""
    body+="}"
    
    response=$(api_post_noauth "/connect" "$body")
    success=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin).get('success',''))" 2>/dev/null || echo "")
    
    if [[ "$success" == "True" ]]; then
      api_key=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['api_key'])")
      mkdir -p "$CONFIG_DIR"
      echo "{\"api_key\":\"$api_key\",\"email\":\"$email\",\"agent_name\":\"$name\"}" > "$CONFIG_FILE"
      chmod 600 "$CONFIG_FILE"
      echo "API key saved to $CONFIG_FILE"
      echo "$response"
    else
      echo "$response"
    fi
    ;;
  
  market)    api_get "/market/overview" ;;
  prices)    api_get "/market/prices?symbols=${1:-}" ;;
  indices)   api_get "/market/indices" ;;
  forex)     api_get "/market/forex" ;;
  news)      api_get "/news/summary" ;;
  alerts)    api_get "/alerts/latest" ;;
  economic)  api_get "/events/economic" ;;
  earnings)  api_get "/events/earnings" ;;
  sentiment) api_get "/social/sentiment" ;;
  tweets)    api_get "/social/tweets" ;;
  trades)    api_get "/trades/congressional" ;;
  
  upgrade)
    plan="${1:-monthly}"
    api_post "/keys/upgrade" "{\"plan\":\"$plan\"}"
    ;;
  
  revoke)
    api_post "/keys/revoke" "{}"
    ;;
  
  status)
    if [[ -f "$CONFIG_FILE" ]]; then
      echo "Config: $CONFIG_FILE"
      python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(f'Agent: {c.get(\"agent_name\",\"?\")}'); print(f'Email: {c.get(\"email\",\"?\")}'); print(f'Key: {c[\"api_key\"][:16]}...')"
    else
      echo "Not configured. Run: tradekix.sh signup --name NAME --email EMAIL"
    fi
    ;;
  
  help|*)
    cat <<EOF
Tradekix API - Financial data for AI agents

Commands:
  signup   --name NAME --email EMAIL  Sign up for API key
  market                              Market overview
  prices   AAPL,TSLA,BTC             Price data for symbols
  indices                             Global market indices
  forex                               Forex rates
  news                                Market news summaries
  alerts                              Latest market alerts
  economic                            Economic calendar
  earnings                            Earnings calendar
  sentiment                           Social sentiment
  tweets                              Market tweets
  trades                              Congressional trades
  upgrade  monthly|yearly             Upgrade to Pro
  revoke                              Revoke API key
  status                              Show current config

Docs: https://tradekix.ai/docs/api
EOF
    ;;
esac
