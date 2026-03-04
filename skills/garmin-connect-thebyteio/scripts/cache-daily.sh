#!/bin/bash
# Cache today's Garmin metrics to local JSON file
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TODAY=$(date +%Y-%m-%d)
CACHE_DIR="${GARMIN_CACHE_DIR:-/root/clawd/data/fitness/garmin}"
CACHE_FILE="$CACHE_DIR/$TODAY.json"

mkdir -p "$CACHE_DIR"

STATS=$("$SCRIPT_DIR/get-stats.sh" 2>/dev/null)

if [ -z "$STATS" ] || echo "$STATS" | grep -q '"error"'; then
  echo "⚠️ Could not fetch Garmin data"
  exit 1
fi

CACHED=$(echo "$STATS" | jq ". + {cached_at: \"$(date -Iseconds)\", date: \"$TODAY\"}")
echo "$CACHED" > "$CACHE_FILE"

echo "✅ Cached Garmin data for $TODAY"
echo "$CACHED" | jq .
