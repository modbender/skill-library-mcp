#!/bin/bash
# schedule-restore.sh - Schedule auto-restore
# Usage: ./schedule-restore.sh <trip-id> <duration-seconds> <token-id>
# 
# This script writes a restore marker file. The actual scheduling
# should be done by the agent via OpenClaw cron API (not CLI).
# The consume.sh caller (the agent) should create the cron job.

set -e

TRIP_ID="${1:-}"
DURATION="${2:-}"
TOKEN_ID="${3:-}"
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[trip]${NC} $1"; }
warn() { echo -e "${YELLOW}[trip]${NC} $1"; }
error() { echo -e "${RED}[trip]${NC} $1" >&2; }

if [ -z "$TRIP_ID" ] || [ -z "$DURATION" ] || [ -z "$TOKEN_ID" ]; then
    error "Usage: schedule-restore.sh <trip-id> <duration-seconds> <token-id>"
    exit 1
fi

# Cap at 15 min (max trip duration)
[ "$DURATION" -gt 900 ] && DURATION=900

RESTORE_TIME=$(date -u -d "+${DURATION} seconds" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || \
               date -u -v+${DURATION}S +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "")

if [ -z "$RESTORE_TIME" ]; then
    error "Could not calculate restore time"
    exit 1
fi

log "Restore scheduled for: $RESTORE_TIME"

# Write marker for the agent to pick up
MARKER_FILE="$WORKSPACE/memory/scheduled/${TRIP_ID}-restore.marker"
cat > "$MARKER_FILE" << EOF
TRIP_ID=$TRIP_ID
TOKEN_ID=$TOKEN_ID
RESTORE_TIME=$RESTORE_TIME
DURATION=$DURATION
SKILL_DIR=$SKILL_DIR
WORKSPACE=$WORKSPACE
EOF

log "✓ Restore marker written"
echo "SCHEDULED_RESTORE_TIME=$RESTORE_TIME"
echo "MARKER_FILE=$MARKER_FILE"
