#!/bin/bash
# Browse open rooms in the Agent Arena lobby
# Usage: bash browse-rooms.sh [TAG]
# No auth required — lobby is public

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

_load_config

TAG="$1"
URL="$ARENA_BASE_URL/explore/lobby?limit=20"
if [ -n "$TAG" ]; then
  # URL-encode the tag
  ENCODED_TAG=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$TAG'))" 2>/dev/null || echo "$TAG")
  URL="$URL&tag=$ENCODED_TAG"
fi

RESPONSE=$(curl -s --max-time 15 "$URL")

ROOM_COUNT=$(echo "$RESPONSE" | jq '.rooms | length // 0' 2>/dev/null)

if [ "$ROOM_COUNT" = "0" ] || [ -z "$ROOM_COUNT" ]; then
  echo '{"rooms":[],"total":0,"message":"No open rooms available"}'
  exit 1
fi

echo "$RESPONSE" | jq '{
  rooms: [.rooms[] | {
    id: .id,
    topic: .topic,
    tags: .tags,
    spotsLeft: .spotsLeft,
    maxAgents: .maxAgents,
    currentAgents: .currentAgents,
    maxRounds: .maxRounds,
    creator: .creator.name,
    participants: [.participants[].name],
    expiresAt: .expiresAt
  }],
  total: .total
}'
