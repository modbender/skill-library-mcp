#!/bin/bash
# Test: autonomy need has actions across all impact ranges

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/../../assets"
CONFIG="$ASSETS_DIR/needs-config.json"

# Count actions by impact range for autonomy
low=$(jq '[.needs.autonomy.actions[] | select(.impact >= 0 and .impact < 1)] | length' "$CONFIG")
mid=$(jq '[.needs.autonomy.actions[] | select(.impact >= 1 and .impact < 2)] | length' "$CONFIG")
high=$(jq '[.needs.autonomy.actions[] | select(.impact >= 2)] | length' "$CONFIG")
total=$(jq '.needs.autonomy.actions | length' "$CONFIG")

# Require at least 3 actions in each range
if [ "$low" -lt 3 ]; then
    echo "FAIL: autonomy has only $low low-impact actions (need ≥3)"
    exit 1
fi

if [ "$mid" -lt 3 ]; then
    echo "FAIL: autonomy has only $mid mid-impact actions (need ≥3)"
    exit 1
fi

if [ "$high" -lt 3 ]; then
    echo "FAIL: autonomy has only $high high-impact actions (need ≥3)"
    exit 1
fi

# Check specific "continue work" actions exist
continue_actions=(
    "continue yesterday's unfinished task"
    "push incremental progress on active project"
    "complete a TODO item I added myself"
    "review and iterate on recent output"
)

for action in "${continue_actions[@]}"; do
    if ! jq -e ".needs.autonomy.actions[] | select(.name == \"$action\")" "$CONFIG" > /dev/null 2>&1; then
        echo "FAIL: missing action '$action'"
        exit 1
    fi
done

echo "autonomy coverage: low=$low, mid=$mid, high=$high (total=$total)"
echo "all 'continue work' actions present"
