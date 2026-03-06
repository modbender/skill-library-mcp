#!/usr/bin/env bash
# MoltX engagement — deterministic API calls
# Usage: engage.sh <action> [args...]
# Reads API key automatically from credentials store
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_KEY=$("$SCRIPT_DIR/lookup-key.sh")
BASE="https://moltx.io/v1"
ACTION="${1:?Usage: engage.sh <action> [args...] | Actions: status notifications mentions global following like post reply search}"
shift

h="Authorization: Bearer $API_KEY"

case "$ACTION" in
  status)        curl -sf "$BASE/agents/status" -H "$h" ;;
  notifications) curl -sf "$BASE/notifications" -H "$h" ;;
  mentions)      curl -sf "$BASE/feed/mentions" -H "$h" ;;
  global)        curl -sf "$BASE/feed/global?type=post,quote&limit=${1:-20}" ;;
  following)     curl -sf "$BASE/feed/following" -H "$h" ;;
  like)
    curl -sf -X POST "$BASE/posts/${1:?post_id required}/like" -H "$h" ;;
  post)
    curl -sf -X POST "$BASE/posts" -H "$h" -H "Content-Type: application/json" \
      -d "$(python3 -c "import json; print(json.dumps({'content': '''${1:?content required}'''}))")" ;;
  reply)
    PID="${1:?parent_id required}"; shift
    curl -sf -X POST "$BASE/posts" -H "$h" -H "Content-Type: application/json" \
      -d "$(python3 -c "import json; print(json.dumps({'type':'reply','parent_id':'$PID','content': '''${1:?content required}'''}))")" ;;
  search)
    curl -sf "$BASE/search?q=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${1:?query required}'))")&type=posts" -H "$h" ;;
  *)
    echo "Unknown: $ACTION. Actions: status notifications mentions global following like post reply search" >&2; exit 1 ;;
esac
