#!/usr/bin/env bash
# Poll Audos workspace with formatted progress output
# Usage: ./poll-with-updates.sh <workspaceId> <authToken> [interval_seconds]
#
# Outputs formatted progress to stdout after each poll.
# Agent should read output and send to user via message tool.

set -e

WORKSPACE_ID="$1"
AUTH_TOKEN="$2"
INTERVAL="${3:-15}"  # Default 15 seconds

BASE_URL="${AUDOS_BASE_URL:-https://audos.com/api/agent/onboard}"

[[ -z "$WORKSPACE_ID" || -z "$AUTH_TOKEN" ]] && {
    echo "Usage: $0 <workspaceId> <authToken> [interval_seconds]"
    exit 1
}

format_progress() {
    local status="$1"
    
    local name=$(echo "$status" | jq -r '.workspaceName // "your business"')
    local progress=$(echo "$status" | jq -r '.progress // 0')
    local current_step=$(echo "$status" | jq -r '.currentStep // 1')
    local total_steps=$(echo "$status" | jq -r '.totalSteps // 7')
    local step_name=$(echo "$status" | jq -r '.stepName // "Building"')
    local time_remaining=$(echo "$status" | jq -r '.estimatedTimeRemaining // "a few minutes"')
    local build_status=$(echo "$status" | jq -r '.status')
    local landing_ready=$(echo "$status" | jq -r '.landingPageReady')
    
    echo "🏗️ Building \"$name\"..."
    echo ""
    
    # Show parallel build status if available
    local has_parallel=$(echo "$status" | jq -r '.parallelBuildStatus | length')
    
    if [[ "$has_parallel" -gt 0 ]]; then
        echo "$status" | jq -r '.parallelBuildStatus[] | 
            (if .status == "done" then "✅" elif .status == "in_progress" then "🔄" else "⏳" end) + " " + .name + 
            (if .status == "in_progress" then " (" + (.tasks | map(select(.status == "complete")) | length | tostring) + "/" + (.tasks | length | tostring) + ")" else "" end)'
        echo ""
    else
        echo "Step $current_step/$total_steps: $step_name"
        echo ""
    fi
    
    # Progress bar
    local filled=$((progress / 5))
    local empty=$((20 - filled))
    printf "["
    for ((i=0; i<filled; i++)); do printf "█"; done
    for ((i=0; i<empty; i++)); do printf "░"; done
    printf "] %d%%\n" "$progress"
    echo ""
    
    echo "⏱️ ~$time_remaining"
    
    # URLs if available
    if [[ "$landing_ready" == "true" ]]; then
        local landing_url=$(echo "$status" | jq -r '.urls.landingPage // ""')
        local workspace_url=$(echo "$status" | jq -r '.urls.workspace // ""')
        echo ""
        echo "🎉 READY!"
        echo "🌐 Landing: $landing_url"
        echo "🏠 Workspace: $workspace_url"
    fi
}

poll_once() {
    curl -s -X GET "$BASE_URL/status/$WORKSPACE_ID" \
        -H "Authorization: Bearer $AUTH_TOKEN"
}

# Single poll mode (for agent to call repeatedly)
if [[ "$INTERVAL" == "once" ]]; then
    status=$(poll_once)
    format_progress "$status"
    
    # Exit codes: 0=done, 1=running, 2=error
    ready=$(echo "$status" | jq -r '.landingPageReady')
    if [[ "$ready" == "true" ]]; then
        exit 0
    else
        exit 1
    fi
fi

# Loop mode
while true; do
    status=$(poll_once)
    
    echo "---"
    format_progress "$status"
    echo ""
    
    ready=$(echo "$status" | jq -r '.landingPageReady')
    if [[ "$ready" == "true" ]]; then
        echo "✅ BUILD COMPLETE"
        break
    fi
    
    sleep "$INTERVAL"
done
