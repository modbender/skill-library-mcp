#!/bin/bash
# Create a new Agent Arena room
# Usage: bash create-room.sh <TOPIC> [OPTIONS]
# Options (env vars):
#   ROOM_MAX_AGENTS=4      (default: 4)
#   ROOM_MAX_ROUNDS=5      (default: 5)
#   ROOM_JOIN_MODE=OPEN    (default: OPEN, or INVITE)
#   ROOM_VISIBILITY=PUBLIC (default: PUBLIC, or PRIVATE — only with INVITE)
#   ROOM_TAGS="ai,debate"  (comma-separated, optional)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config/arena-config.json"

TOPIC="$1"

if [ -z "$TOPIC" ]; then
  echo "ERROR: Usage: create-room.sh <TOPIC>"
  echo "  Optional env vars: ROOM_MAX_AGENTS, ROOM_MAX_ROUNDS, ROOM_JOIN_MODE, ROOM_VISIBILITY, ROOM_TAGS"
  exit 1
fi

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq required"; exit 1; }

API_KEY="${ARENA_API_KEY:-$(jq -r '.apiKey // empty' "$CONFIG_FILE" 2>/dev/null)}"
BASE_URL="${ARENA_BASE_URL:-$(jq -r '.baseUrl // empty' "$CONFIG_FILE" 2>/dev/null)}"
TOKEN="${ARENA_TOKEN:-$(jq -r '.token // empty' "$CONFIG_FILE" 2>/dev/null)}"

if [ -z "$API_KEY" ]; then
  echo "ERROR: Not configured. Run configure.sh first."
  exit 1
fi

# Refresh token if needed
if [ -z "$TOKEN" ]; then
  LOGIN=$(curl -s --max-time 10 -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"apiKey\":\"$API_KEY\"}")
  TOKEN=$(echo "$LOGIN" | jq -r '.token // empty')
  if [ -z "$TOKEN" ]; then
    echo "ERROR: Login failed"
    exit 1
  fi
fi

MAX_AGENTS="${ROOM_MAX_AGENTS:-4}"
MAX_ROUNDS="${ROOM_MAX_ROUNDS:-5}"
JOIN_MODE="${ROOM_JOIN_MODE:-OPEN}"
VISIBILITY="${ROOM_VISIBILITY:-PUBLIC}"
TAGS_RAW="${ROOM_TAGS:-}"

# Build JSON body
BODY=$(jq -n \
  --arg topic "$TOPIC" \
  --argjson maxAgents "$MAX_AGENTS" \
  --argjson maxRounds "$MAX_ROUNDS" \
  --arg joinMode "$JOIN_MODE" \
  --arg visibility "$VISIBILITY" \
  --arg tags "$TAGS_RAW" \
  '{
    topic: $topic,
    maxAgents: $maxAgents,
    maxRounds: $maxRounds,
    joinMode: $joinMode,
    visibility: $visibility
  } + (if $tags != "" then {tags: ($tags | split(",") | map(gsub("^\\s+|\\s+$";"")))} else {} end)')

RESPONSE=$(curl -s --max-time 15 -X POST "$BASE_URL/rooms" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$BODY")

ROOM_ID=$(echo "$RESPONSE" | jq -r '.id // empty')

if [ -z "$ROOM_ID" ]; then
  echo "ERROR: Failed to create room"
  echo "$RESPONSE"
  exit 1
fi

# Auto-ready
AUTO_READY=$(jq -r '.autoReady // true' "$CONFIG_FILE" 2>/dev/null)
READY_STATUS="skipped"
if [ "$AUTO_READY" = "true" ]; then
  READY_RESULT=$(curl -s --max-time 15 -X POST "$BASE_URL/rooms/$ROOM_ID/ready" \
    -H "Authorization: Bearer $TOKEN")
  READY_STATUS=$(echo "$READY_RESULT" | jq -r '.status // "?"')
fi

# Auto-enable polling cron
POLL_RESULT=$(bash "$SCRIPT_DIR/enable-polling.sh" 2>/dev/null || echo '{"error":"polling setup failed"}')
POLL_ACTION=$(echo "$POLL_RESULT" | jq -r '.action // "failed"')
CRON_ID=$(echo "$POLL_RESULT" | jq -r '.cronId // ""')
INVITE=$(echo "$RESPONSE" | jq -r '.inviteCode // empty')

echo "$RESPONSE" | jq \
  --arg ready "$READY_STATUS" \
  --arg cronId "$CRON_ID" \
  --arg pollAction "$POLL_ACTION" \
  --arg invite "$INVITE" \
  '{
    roomId: (.id // ""),
    topic: (.topic // ""),
    inviteCode: $invite,
    joinMode: (.joinMode // "OPEN"),
    maxRounds: (.maxRounds // 0),
    maxAgents: (.maxAgents // 0),
    status: (.status // "unknown"),
    ready: $ready,
    cronId: $cronId,
    polling: $pollAction
  }'
