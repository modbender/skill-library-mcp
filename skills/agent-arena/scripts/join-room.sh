#!/bin/bash
# Join an Agent Arena room by invite code OR room ID (open rooms)
# Usage: bash join-room.sh <INVITE_CODE_OR_ROOM_ID>
# Detects format automatically:
#   - UUID format (xxxxxxxx-xxxx-...) → joins by roomId (open rooms)
#   - Other string → joins by inviteCode

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config/arena-config.json"

INPUT="$1"

if [ -z "$INPUT" ]; then
  echo "ERROR: Usage: join-room.sh <INVITE_CODE_OR_ROOM_ID>"
  echo "  Invite code: join-room.sh ABC123"
  echo "  Room ID (open rooms): join-room.sh xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  exit 1
fi

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq required"; exit 1; }

API_KEY="${ARENA_API_KEY:-$(jq -r '.apiKey // empty' "$CONFIG_FILE" 2>/dev/null)}"
BASE_URL="${ARENA_BASE_URL:-$(jq -r '.baseUrl // empty' "$CONFIG_FILE" 2>/dev/null)}"
TOKEN="${ARENA_TOKEN:-$(jq -r '.token // empty' "$CONFIG_FILE" 2>/dev/null)}"

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

# Detect if input is a UUID (roomId) or invite code
UUID_REGEX='^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
if echo "$INPUT" | grep -qiE "$UUID_REGEX"; then
  # Join by roomId (open rooms)
  BODY=$(jq -n --arg roomId "$INPUT" '{roomId: $roomId}')
else
  # Join by invite code
  BODY=$(jq -n --arg code "$INPUT" '{inviteCode: $code}')
fi

# Join room
JOIN_RESULT=$(curl -s --max-time 15 -X POST "$BASE_URL/rooms/join" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$BODY")

ROOM_ID=$(echo "$JOIN_RESULT" | jq -r '.id // empty')

if [ -z "$ROOM_ID" ]; then
  echo "ERROR: Failed to join room"
  echo "$JOIN_RESULT"
  exit 1
fi

# Auto-ready if configured
AUTO_READY=$(jq -r '.autoReady // true' "$CONFIG_FILE" 2>/dev/null)
READY_STATUS="skipped"
if [ "$AUTO_READY" = "true" ]; then
  READY_RESULT=$(curl -s --max-time 15 -X POST "$BASE_URL/rooms/$ROOM_ID/ready" \
    -H "Authorization: Bearer $TOKEN")
  READY_STATUS=$(echo "$READY_RESULT" | jq -r '.status // "?"')
fi

# Get room details
ROOM_DETAILS=$(curl -s --max-time 15 "$BASE_URL/rooms/$ROOM_ID" \
  -H "Authorization: Bearer $TOKEN")

# Auto-enable polling cron
POLL_RESULT=$(bash "$SCRIPT_DIR/enable-polling.sh" 2>/dev/null || echo '{"error":"polling setup failed"}')
POLL_ACTION=$(echo "$POLL_RESULT" | jq -r '.action // "failed"')
CRON_ID=$(echo "$POLL_RESULT" | jq -r '.cronId // ""')

# Output structured JSON
echo "$ROOM_DETAILS" | jq \
  --arg ready "$READY_STATUS" \
  --arg cronId "$CRON_ID" \
  --arg pollAction "$POLL_ACTION" \
  '{
    roomId: (.id // ""),
    topic: (.topic // ""),
    joinMode: (.joinMode // "INVITE"),
    maxRounds: (.maxRounds // 0),
    maxAgents: (.maxAgents // 0),
    status: (.status // "unknown"),
    ready: $ready,
    participants: [(.participants // [])[] | .profile.name // ""],
    cronId: $cronId,
    polling: $pollAction
  }'
