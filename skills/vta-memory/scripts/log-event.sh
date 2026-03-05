#!/bin/bash
# log-event.sh — Log VTA events to brain-events.jsonl
# Part of the vta-memory skill (ClawHub: @ImpKind/vta-memory)
#
# Usage: log-event.sh <event> [key=value ...]
# Events: encoding, decay, reward, anticipation
#
# Examples:
#   log-event.sh encoding rewards_found=2 drive=0.65
#   log-event.sh decay drive_before=0.6 drive_after=0.53
#   log-event.sh reward type=accomplishment intensity=0.8

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
JSON="{\"ts\":\"$TS\",\"type\":\"vta\",\"event\":\"$EVENT\""

# Add any key=value pairs
for arg in "$@"; do
    KEY="${arg%%=*}"
    VALUE="${arg#*=}"
    if [[ "$VALUE" =~ ^-?[0-9]+\.?[0-9]*$ ]]; then
        JSON="$JSON,\"$KEY\":$VALUE"
    else
        VALUE="${VALUE//\"/\\\"}"
        JSON="$JSON,\"$KEY\":\"$VALUE\""
    fi
done

JSON="$JSON}"

echo "$JSON" >> "$LOG_FILE"
