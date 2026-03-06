#!/usr/bin/env bash
#
# Wait for MR to be approved and pipeline to succeed.
# Exits 0 when merged, 1 on failure/timeout.
#
# Usage:
#   glab-mr-await.sh <mr-number> [--timeout SECONDS] [--require-approval]
#
# Examples:
#   glab-mr-await.sh 123                    # Wait for merge
#   glab-mr-await.sh 123 --timeout 600      # 10 min timeout
#   glab-mr-await.sh 123 --require-approval # Require at least one approval
#

set -euo pipefail

MR_NUMBER="${1:-}"
TIMEOUT="${TIMEOUT:-3600}"  # Default 1 hour
REQUIRE_APPROVAL=false
INTERVAL=10

usage() {
    echo "Usage: $0 <mr-number> [--timeout SECONDS] [--require-approval]"
    exit 1
}

# Parse args
shift || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --timeout|-t)
            TIMEOUT="$2"
            shift 2
            ;;
        --require-approval|-a)
            REQUIRE_APPROVAL=true
            shift
            ;;
        *)
            usage
            ;;
    esac
done

[[ -z "$MR_NUMBER" ]] && usage

# Check glab
command -v glab >/dev/null || { echo "Error: glab not installed"; exit 1; }

echo "⏳ Waiting for MR !${MR_NUMBER} (timeout: ${TIMEOUT}s)"

START_TIME=$(date +%s)

check_mr() {
    local mr_json
    mr_json=$(glab mr view "$MR_NUMBER" --output=json 2>/dev/null) || return 1
    
    local state merged approvals
    state=$(echo "$mr_json" | jq -r '.state')
    merged=$(echo "$mr_json" | jq -r '.merged_at // empty')
    approvals=$(echo "$mr_json" | jq -r '.user.can_merge')
    
    # Check if merged
    if [[ "$state" == "merged" ]] || [[ -n "$merged" ]]; then
        echo "✅ MR !${MR_NUMBER} has been merged!"
        return 0
    fi
    
    # Check if closed
    if [[ "$state" == "closed" ]]; then
        echo "❌ MR !${MR_NUMBER} was closed"
        return 1
    fi
    
    # Check approval if required
    if [[ "$REQUIRE_APPROVAL" == "true" ]]; then
        local approval_count
        approval_count=$(glab api "projects/:id/merge_requests/${MR_NUMBER}/approvals" 2>/dev/null | jq -r '.approved_by | length')
        if [[ "$approval_count" -eq 0 ]]; then
            echo "⏳ Waiting for approval... (state: $state)"
            return 2  # Continue waiting
        fi
    fi
    
    # Check pipeline status
    local pipeline_status
    pipeline_status=$(glab ci status --output=json 2>/dev/null | jq -r '.status // "unknown"')
    
    case "$pipeline_status" in
        success)
            echo "✅ Pipeline passed. Waiting for merge..."
            ;;
        failed|canceled)
            echo "❌ Pipeline $pipeline_status"
            return 1
            ;;
        running|pending)
            echo "⏳ Pipeline $pipeline_status..."
            ;;
    esac
    
    return 2  # Continue waiting
}

while true; do
    ELAPSED=$(($(date +%s) - START_TIME))
    
    if [[ $ELAPSED -ge $TIMEOUT ]]; then
        echo "⏰ Timeout after ${TIMEOUT}s"
        exit 1
    fi
    
    if check_mr; then
        exit 0
    elif [[ $? -eq 1 ]]; then
        exit 1
    fi
    
    sleep "$INTERVAL"
done
