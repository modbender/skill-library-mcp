#!/bin/bash
# log-event.sh — Log hippocampus events to brain-events.jsonl
# Part of the hippocampus skill (ClawHub: @ImpKind/hippocampus)
#
# Usage: log-event.sh <event> [key=value ...]
# Events: encoding, decay, recall, reinforce
#
# Examples:
#   log-event.sh encoding new=3 reinforced=2 total=157
#   log-event.sh decay decayed=154 low_importance=5
#   log-event.sh recall query="user preferences" results=3

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
LOG_FILE="$WORKSPACE/memory/brain-events.jsonl"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Arguments
EVENT="${1:-unknown}"
shift 1 2>/dev/null || true

# Build JSON object
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
JSON="{\"ts\":\"$TS\",\"type\":\"hippocampus\",\"event\":\"$EVENT\""

# Add any key=value pairs
for arg in "$@"; do
    KEY="${arg%%=*}"
    VALUE="${arg#*=}"
    # Check if value is numeric
    if [[ "$VALUE" =~ ^-?[0-9]+\.?[0-9]*$ ]]; then
        JSON="$JSON,\"$KEY\":$VALUE"
    else
        VALUE="${VALUE//\"/\\\"}"
        JSON="$JSON,\"$KEY\":\"$VALUE\""
    fi
done

JSON="$JSON}"

# Append to log
echo "$JSON" >> "$LOG_FILE"
