#!/usr/bin/env bash
#
# Watch pipeline and exit with appropriate code.
# Exits 0 on success, 1 on failure, 2 on timeout.
#
# Usage:
#   glab-pipeline-watch.sh [--timeout SECONDS] [--interval SECONDS]
#
# Examples:
#   glab-pipeline-watch.sh                  # Watch current branch pipeline
#   glab-pipeline-watch.sh --timeout 300    # 5 min timeout
#

set -euo pipefail

TIMEOUT="${TIMEOUT:-1800}"  # Default 30 min
INTERVAL="${INTERVAL:-5}"

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --timeout|-t)
            TIMEOUT="$2"
            shift 2
            ;;
        --interval|-i)
            INTERVAL="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

command -v glab >/dev/null || { echo "Error: glab not installed"; exit 1; }
command -v jq >/dev/null || { echo "Error: jq not installed"; exit 1; }

START_TIME=$(date +%s)
PIPELINE_ID=""

echo "⏳ Watching pipeline (timeout: ${TIMEOUT}s)"

check_pipeline() {
    local status_json
    status_json=$(glab ci status --output=json 2>/dev/null) || return 3
    
    local status pipeline_id
    status=$(echo "$status_json" | jq -r '.status // "unknown"')
    pipeline_id=$(echo "$status_json" | jq -r '.id // empty')
    
    [[ -n "$pipeline_id" ]] && PIPELINE_ID="$pipeline_id"
    
    local elapsed=$(($(date +%s) - START_TIME))
    local spinner=("⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏")
    local spin_idx=$((elapsed % ${#spinner[@]}))
    local spin="${spinner[$spin_idx]}"
    
    case "$status" in
        success)
            echo -e "\r✅ Pipeline #${PIPELINE_ID} succeeded! (${elapsed}s)  "
            return 0
            ;;
        failed)
            echo -e "\r❌ Pipeline #${PIPELINE_ID} failed (${elapsed}s)  "
            echo "Run 'glab ci trace' to see logs"
            return 1
            ;;
        canceled)
            echo -e "\r🚫 Pipeline #${PIPELINE_ID} was canceled  "
            return 1
            ;;
        running|pending|created)
            printf "\r%s Pipeline #%s %s... (%ds)  " "$spin" "${PIPELINE_ID:-?}" "$status" "$elapsed"
            return 3
            ;;
        *)
            printf "\r%s Pipeline status: %s (%ds)  " "$spin" "$status" "$elapsed"
            return 3
            ;;
    esac
}

while true; do
    ELAPSED=$(($(date +%s) - START_TIME))
    
    if [[ $ELAPSED -ge $TIMEOUT ]]; then
        echo -e "\r⏰ Timeout after ${TIMEOUT}s  "
        exit 2
    fi
    
    if check_pipeline; then
        exit 0
    else
        local ret=$?
        [[ $ret -eq 1 ]] && exit 1
        [[ $ret -eq 3 ]] && sleep "$INTERVAL" && continue
        exit $ret
    fi
done
