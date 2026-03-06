#!/bin/bash
# log-event.sh — Log amygdala events to brain-events.jsonl
# Part of the amygdala-memory skill (ClawHub: @ImpKind/amygdala-memory)
#
# Usage: log-event.sh <event> [key=value ...]
# Events: encoding, decay, update
#
# Examples:
#   log-event.sh encoding emotions_found=2 valence=0.85 arousal=0.6
#   log-event.sh decay valence_before=0.9 valence_after=0.85
#   log-event.sh update emotion=joy intensity=0.7

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
JSON="{\"ts\":\"$TS\",\"type\":\"amygdala\",\"event\":\"$EVENT\""

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
