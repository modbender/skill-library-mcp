#!/usr/bin/env bash
# incremental-review.sh — Layer 2: Trigger incremental review
# Tracks commits since last review, triggers when threshold reached.
# Usage: incremental-review.sh <project_dir> [--check-only]

set -euo pipefail

PROJECT_DIR="${1:?Usage: incremental-review.sh <project_dir> [--check-only]}"
CHECK_ONLY="${2:-}"
STATE_DIR="$HOME/.autopilot/state/review"
COMMIT_THRESHOLD=15
TIME_THRESHOLD=7200  # 2 hours in seconds

mkdir -p "$STATE_DIR"

cd "$PROJECT_DIR" || exit 1
PROJECT_NAME=$(basename "$PROJECT_DIR")
SAFE_NAME=$(echo "$PROJECT_NAME" | tr -c 'a-zA-Z0-9_-' '_')

STATE_FILE="$STATE_DIR/${SAFE_NAME}.json"

# Get current state
CURRENT_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "none")
CURRENT_TIME=$(date +%s)

# Get last review state
if [ -f "$STATE_FILE" ]; then
    LAST_COMMIT=$(jq -r '.last_review_commit // "none"' "$STATE_FILE")
    LAST_TIME=$(jq -r '.last_review_time // 0' "$STATE_FILE")
else
    LAST_COMMIT="none"
    LAST_TIME=0
fi

# Count commits since last review
if [ "$LAST_COMMIT" = "none" ]; then
    COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")
else
    COMMIT_COUNT=$(git rev-list --count "${LAST_COMMIT}..HEAD" 2>/dev/null || echo "0")
fi

# Time since last review
if [ "$LAST_TIME" -gt 0 ]; then
    TIME_ELAPSED=$((CURRENT_TIME - LAST_TIME))
else
    TIME_ELAPSED=$((TIME_THRESHOLD + 1))
fi

# Determine if review needed
NEEDS_REVIEW=false
REASON=""

if [ "$COMMIT_COUNT" -ge "$COMMIT_THRESHOLD" ]; then
    NEEDS_REVIEW=true
    REASON="≥${COMMIT_THRESHOLD} commits since last review (${COMMIT_COUNT} commits)"
elif [ "$TIME_ELAPSED" -ge "$TIME_THRESHOLD" ] && [ "$COMMIT_COUNT" -gt 0 ]; then
    NEEDS_REVIEW=true
    HOURS=$((TIME_ELAPSED / 3600))
    REASON="≥2h since last review (${HOURS}h, ${COMMIT_COUNT} commits)"
fi

if [ "$CHECK_ONLY" = "--check-only" ]; then
    if [ "$NEEDS_REVIEW" = true ]; then
        echo "REVIEW_NEEDED: $REASON"
        echo "COMMITS: $COMMIT_COUNT"
        echo "LAST_COMMIT: $LAST_COMMIT"
        exit 0
    else
        echo "NO_REVIEW_NEEDED: ${COMMIT_COUNT} commits, ${TIME_ELAPSED}s elapsed"
        exit 1
    fi
fi

if [ "$NEEDS_REVIEW" = false ]; then
    echo "No review needed: ${COMMIT_COUNT} commits, ${TIME_ELAPSED}s elapsed"
    exit 0
fi

# Generate diff for review
echo "🔍 Incremental review triggered: $REASON"

if [ "$LAST_COMMIT" = "none" ]; then
    # First review: get recent changes (last 15 commits)
    DIFF_BASE=$(git rev-list --max-count=15 HEAD | tail -1)
else
    DIFF_BASE="$LAST_COMMIT"
fi

# Output changed files and stats
echo ""
echo "## Changed files:"
git diff --stat "${DIFF_BASE}..HEAD" 2>/dev/null
echo ""
echo "## Diff:"
git diff "${DIFF_BASE}..HEAD" --diff-filter=ACMR -- '*.ts' '*.tsx' '*.swift' '*.sol' '*.py' 2>/dev/null | head -2000

# Update state
TMP_STATE=$(mktemp)
jq -n \
    --arg commit "$CURRENT_COMMIT" \
    --argjson time "$CURRENT_TIME" \
    --argjson count "$COMMIT_COUNT" \
    '{last_review_commit: $commit, last_review_time: $time, commits_reviewed: $count}' \
    > "$TMP_STATE" && mv "$TMP_STATE" "$STATE_FILE"

echo ""
echo "✅ Review state updated: $STATE_FILE"
