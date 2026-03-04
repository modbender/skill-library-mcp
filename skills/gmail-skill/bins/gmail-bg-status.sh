#!/usr/bin/env bash
#
# gmail-bg-status.sh — Show status of all background Gmail tasks
#
# Usage: gmail-bg-status.sh [options]
#   --running:    Show only running jobs
#   --completed:  Show only completed jobs
#   --failed:     Show only failed jobs
#   --all:        Show all jobs (default)
#   --json:       Output as JSON
#   --clean:      Remove completed/failed job records older than 24 hours
#
set -euo pipefail

REGISTRY_DIR="${HOME}/.gmail-skill/jobs"
FILTER="all"
OUTPUT_FORMAT="table"
CLEAN_OLD=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --running)   FILTER="running"; shift ;;
        --completed) FILTER="completed"; shift ;;
        --failed)    FILTER="failed"; shift ;;
        --all)       FILTER="all"; shift ;;
        --json)      OUTPUT_FORMAT="json"; shift ;;
        --clean)     CLEAN_OLD=true; shift ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: $0 [--running|--completed|--failed|--all] [--json] [--clean]" >&2
            exit 1
            ;;
    esac
done

# Create registry directory if needed
mkdir -p "$REGISTRY_DIR"

# Clean old jobs if requested
if [[ "$CLEAN_OLD" == "true" ]]; then
    CUTOFF=$(date -v-24H +%s 2>/dev/null || date -d '24 hours ago' +%s 2>/dev/null || echo 0)
    CLEANED=0

    for job_file in "$REGISTRY_DIR"/*.json; do
        [[ -f "$job_file" ]] || continue

        STATUS=$(jq -r '.status // "unknown"' "$job_file" 2>/dev/null || echo "unknown")
        END_TIME=$(jq -r '.end_time // 0' "$job_file" 2>/dev/null || echo 0)

        if [[ "$STATUS" != "running" ]] && [[ "$END_TIME" -lt "$CUTOFF" ]]; then
            rm -f "$job_file"
            ((CLEANED++)) || true
        fi
    done

    echo "Cleaned $CLEANED old job record(s)"
    exit 0
fi

# Collect jobs
JOBS=()
for job_file in "$REGISTRY_DIR"/*.json; do
    [[ -f "$job_file" ]] || continue

    STATUS=$(jq -r '.status // "unknown"' "$job_file" 2>/dev/null || echo "unknown")

    # Filter by status
    if [[ "$FILTER" != "all" ]] && [[ "$STATUS" != "$FILTER" ]]; then
        continue
    fi

    # Check if process is still running (update status if needed)
    PID=$(jq -r '.pid // 0' "$job_file" 2>/dev/null || echo 0)
    if [[ "$STATUS" == "running" ]] && [[ $PID -gt 0 ]]; then
        if ! kill -0 "$PID" 2>/dev/null; then
            # Process is dead but status file says running - update it
            jq '.status = "failed" | .exit_code = -1' "$job_file" > "${job_file}.tmp" && mv "${job_file}.tmp" "$job_file"
            STATUS="failed"
        fi
    fi

    JOBS+=("$job_file")
done

# Output results
if [[ "$OUTPUT_FORMAT" == "json" ]]; then
    # JSON output
    echo "["
    FIRST=true
    for job_file in "${JOBS[@]}"; do
        if [[ "$FIRST" == "true" ]]; then
            FIRST=false
        else
            echo ","
        fi
        cat "$job_file"
    done
    echo "]"
else
    # Table output
    if [[ ${#JOBS[@]} -eq 0 ]]; then
        echo "No background jobs found."
        echo ""
        echo "Tip: Jobs are tracked in $REGISTRY_DIR"
        exit 0
    fi

    echo "Gmail Background Jobs"
    echo "===================="
    echo ""

    for job_file in "${JOBS[@]}"; do
        JOB_ID=$(jq -r '.job_id // "unknown"' "$job_file")
        TASK_NAME=$(jq -r '.task_name // "unknown"' "$job_file")
        STATUS=$(jq -r '.status // "unknown"' "$job_file")
        ACCOUNT=$(jq -r '.account // "unknown"' "$job_file")
        START_TIME=$(jq -r '.start_time_human // "unknown"' "$job_file")
        DURATION=$(jq -r '.duration // "running"' "$job_file")
        LOG_FILE=$(jq -r '.log_file // "unknown"' "$job_file")
        EXIT_CODE=$(jq -r '.exit_code // ""' "$job_file")

        # Status icon
        case "$STATUS" in
            running)   STATUS_ICON="⏳" ;;
            completed) STATUS_ICON="✅" ;;
            failed)    STATUS_ICON="❌" ;;
            *)         STATUS_ICON="❓" ;;
        esac

        # Calculate current duration for running jobs
        if [[ "$STATUS" == "running" ]]; then
            START_EPOCH=$(jq -r '.start_time // 0' "$job_file")
            CURRENT_EPOCH=$(date +%s)
            ELAPSED=$((CURRENT_EPOCH - START_EPOCH))

            if [[ $ELAPSED -lt 60 ]]; then
                DURATION="${ELAPSED}s (running)"
            elif [[ $ELAPSED -lt 3600 ]]; then
                DURATION="$((ELAPSED / 60))m $((ELAPSED % 60))s (running)"
            else
                DURATION="$((ELAPSED / 3600))h $((ELAPSED % 3600 / 60))m (running)"
            fi
        fi

        echo "${STATUS_ICON} ${TASK_NAME}"
        echo "   Status:   $STATUS"
        [[ -n "$EXIT_CODE" ]] && echo "   Exit:     $EXIT_CODE"
        echo "   Account:  $ACCOUNT"
        echo "   Started:  $START_TIME"
        echo "   Duration: $DURATION"
        echo "   Log:      $LOG_FILE"
        echo ""
    done

    echo "Total: ${#JOBS[@]} job(s)"
    echo ""
    echo "Commands:"
    echo "  View log:    tail -f <log-file>"
    echo "  Clean old:   $0 --clean"
fi
