#!/bin/bash
# pr-review-loop.sh — Fetch Greptile review, parse score, output structured JSON
# Usage: pr-review-loop.sh <owner/repo> <pr-number>
# Output: JSON with review data for the agent to process

set -euo pipefail

REPO="${1:?Usage: pr-review-loop.sh <owner/repo> <pr-number>}"
PR="${2:?Usage: pr-review-loop.sh <owner/repo> <pr-number>}"
STATE_FILE="${3:-review-state.json}"

# Initialize state file if missing
if [ ! -f "$STATE_FILE" ]; then
  echo '{}' > "$STATE_FILE"
fi

KEY="${REPO}#${PR}"

# Fetch latest Greptile review
REVIEW=$(gh api "/repos/${REPO}/pulls/${PR}/reviews" \
  --jq '[.[] | select(.user.login == "greptile-apps[bot]")] | last // empty' 2>/dev/null || echo "")

if [ -z "$REVIEW" ]; then
  echo '{"status":"no_review","message":"No Greptile review found"}'
  exit 0
fi

REVIEW_BODY=$(echo "$REVIEW" | jq -r '.body // ""')
REVIEW_STATE=$(echo "$REVIEW" | jq -r '.state // ""')

# Fetch inline comments
COMMENTS=$(gh api "/repos/${REPO}/pulls/${PR}/comments" \
  --jq '[.[] | select(.user.login == "greptile-apps[bot]") | {path: .path, line: .line, body: .body}]' 2>/dev/null || echo "[]")

COMMENT_COUNT=$(echo "$COMMENTS" | jq 'length')

# Parse score from review body (look for patterns like "Score: 4/5", "4/5", "Confidence: 3/5")
SCORE=$(echo "$REVIEW_BODY" | grep -oP '(?:Score|Confidence|Rating|Quality)?\s*:?\s*(\d)\s*/\s*5' | head -1 | grep -oP '\d(?=\s*/\s*5)' || echo "")

# Get current state
CURRENT=$(jq -r ".\"${KEY}\" // empty" "$STATE_FILE")
if [ -z "$CURRENT" ]; then
  ROUNDS=0
  LAST_SCORE=""
  SAME_COUNT=0
else
  ROUNDS=$(echo "$CURRENT" | jq -r '.rounds // 0')
  LAST_SCORE=$(echo "$CURRENT" | jq -r '.lastScore // ""')
  SAME_COUNT=$(echo "$CURRENT" | jq -r '.sameScoreCount // 0')
fi

# Update round count
ROUNDS=$((ROUNDS + 1))

# Check if score is same as last (guard against empty strings)
if [ -n "$SCORE" ] && [ -n "$LAST_SCORE" ] && [ "$SCORE" = "$LAST_SCORE" ]; then
  SAME_COUNT=$((SAME_COUNT + 1))
else
  SAME_COUNT=0
fi

# Determine action
ACTION="fix"
if [ -n "$SCORE" ] && [ "$SCORE" -ge 4 ]; then
  ACTION="merge"
elif [ "$ROUNDS" -ge 5 ]; then
  ACTION="force_merge"
elif [ "$SAME_COUNT" -ge 2 ]; then
  ACTION="force_merge"
elif [ "$COMMENT_COUNT" -eq 0 ] && [ "$REVIEW_STATE" = "APPROVED" ]; then
  ACTION="merge"
fi

# Update state (use lockfile to prevent concurrent write races)
LOCK="${STATE_FILE}.lock"
(
  flock -w 5 200 || { echo '{"error":"Could not acquire state lock"}' >&2; exit 1; }
  jq ".\"${KEY}\" = {rounds: ${ROUNDS}, maxRounds: 5, lastScore: $([ -n "$SCORE" ] && echo "$SCORE" || echo "null"), sameScoreCount: ${SAME_COUNT}}" \
    "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
) 200>"$LOCK"

# Output structured result
jq -n \
  --arg repo "$REPO" \
  --argjson pr "$PR" \
  --arg action "$ACTION" \
  --argjson score "$([ -n "$SCORE" ] && echo "$SCORE" || echo "null")" \
  --argjson rounds "$ROUNDS" \
  --argjson sameScoreCount "$SAME_COUNT" \
  --argjson commentCount "$COMMENT_COUNT" \
  --arg reviewBody "$REVIEW_BODY" \
  --argjson comments "$COMMENTS" \
  '{repo: $repo, pr: $pr, action: $action, score: $score, rounds: $rounds, sameScoreCount: $sameScoreCount, commentCount: $commentCount, reviewBody: $reviewBody, comments: $comments}'
