#!/bin/bash
# log-event.sh — Log ACC events to brain-events.jsonl
# Part of the anterior-cingulate-memory skill (ClawHub: @ImpKind/anterior-cingulate-memory)
#
# Usage: log-event.sh <event> [key=value ...]
# Events: analysis, error_logged, pattern_resolved
#
# Examples:
#   log-event.sh analysis errors_found=1 patterns_active=3 patterns_resolved=0
#   log-event.sh error_logged pattern=tone_mismatch count=2
#   log-event.sh pattern_resolved pattern=version_numbers days_clear=30

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
JSON="{\"ts\":\"$TS\",\"type\":\"acc\",\"event\":\"$EVENT\""

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
