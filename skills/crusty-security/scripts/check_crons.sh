#!/usr/bin/env bash
# check_crons.sh — Verify Crusty Security cron jobs exist
# Returns JSON with status of each expected job
# Agents should use this to self-check and create missing crons via the cron tool
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
HAS_API_KEY=false
[[ -n "${CRUSTY_API_KEY:-}" ]] && HAS_API_KEY=true

# Expected jobs
REQUIRED_JOBS=("crusty-daily-scan" "crusty-weekly-full" "crusty-monthly-deep")
DASHBOARD_JOBS=("crusty-heartbeat" "crusty-clawhub-sync")

# Try to list existing cron jobs via openclaw CLI
EXISTING_JOBS=""
if command -v openclaw &>/dev/null; then
    EXISTING_JOBS=$(openclaw cron list 2>/dev/null || true)
fi

check_job() {
    local name="$1"
    if echo "$EXISTING_JOBS" | grep -q "$name" 2>/dev/null; then
        echo "exists"
    else
        echo "missing"
    fi
}

MISSING=()
RESULTS="{"

for job in "${REQUIRED_JOBS[@]}"; do
    status=$(check_job "$job")
    RESULTS+="\"$job\":\"$status\","
    [[ "$status" == "missing" ]] && MISSING+=("$job")
done

if [[ "$HAS_API_KEY" == true ]]; then
    for job in "${DASHBOARD_JOBS[@]}"; do
        status=$(check_job "$job")
        RESULTS+="\"$job\":\"$status\","
        [[ "$status" == "missing" ]] && MISSING+=("$job")
    done
fi

RESULTS+="\"skill_dir\":\"$SKILL_DIR\","
RESULTS+="\"missing_count\":${#MISSING[@]},"
RESULTS+="\"all_configured\":$([[ ${#MISSING[@]} -eq 0 ]] && echo true || echo false)"
RESULTS+="}"

echo "$RESULTS"

if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo "" >&2
    echo "⚠️  Missing cron jobs: ${MISSING[*]}" >&2
    echo "Agent should create these using the OpenClaw cron tool. See SKILL.md." >&2
    echo "" >&2
    echo "⛔ IMPORTANT: All Crusty Security cron jobs MUST use:" >&2
    echo "   sessionTarget: \"isolated\"  +  payload.kind: \"agentTurn\"" >&2
    echo "   NEVER use systemEvent for jobs that execute commands." >&2
    echo "   systemEvent only injects text — it does NOT guarantee execution." >&2
fi
