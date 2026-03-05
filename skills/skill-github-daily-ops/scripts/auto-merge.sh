#!/usr/bin/env bash
# auto-merge.sh — Find open Dependabot PRs and merge if CI is green
# Usage: bash auto-merge.sh [repo1 repo2 ...]

set -euo pipefail

export GH_TOKEN="${GH_TOKEN:-$(cat ~/.github_token 2>/dev/null || echo '')}"
if [[ -z "$GH_TOKEN" ]]; then
  echo "❌ GH_TOKEN not set and ~/.github_token not found" >&2
  exit 1
fi

REPOS=("${@:-Zero2Ai-hub/Jarvis-Ops Zero2Ai-hub/Zeerotoai.com Zero2Ai-hub/openclaw-skills}")
if [[ $# -eq 0 ]]; then
  REPOS=(
    "Zero2Ai-hub/Jarvis-Ops"
    "Zero2Ai-hub/Zeerotoai.com"
    "Zero2Ai-hub/openclaw-skills"
  )
fi

MERGED=()
SKIPPED=()
FAILED=()

check_and_merge() {
  local repo="$1"
  local pr_number="$2"
  local pr_title="$3"
  local head_sha="$4"

  echo "  🔍 Checking CI for PR #${pr_number}: ${pr_title}"

  # Get check runs for the head SHA
  local checks
  checks=$(gh api "repos/${repo}/commits/${head_sha}/check-runs" \
    --jq '.check_runs[] | {name: .name, status: .status, conclusion: .conclusion}' 2>/dev/null || echo "")

  if [[ -z "$checks" ]]; then
    echo "  ⚠️  No CI checks found for PR #${pr_number} — skipping"
    SKIPPED+=("${repo}#${pr_number} (no CI checks)")
    return
  fi

  # Check if all completed checks have passed
  local total incomplete failed_count
  total=$(echo "$checks" | grep -c '"status"' || true)
  incomplete=$(echo "$checks" | grep '"status": "in_progress"\|"status": "queued"' | wc -l || echo 0)
  failed_count=$(echo "$checks" | grep '"conclusion": "failure"\|"conclusion": "cancelled"\|"conclusion": "timed_out"' | wc -l || echo 0)

  if [[ "$incomplete" -gt 0 ]]; then
    echo "  ⏳ PR #${pr_number} — CI still running (${incomplete} pending) — skipping"
    SKIPPED+=("${repo}#${pr_number} (CI pending)")
    return
  fi

  if [[ "$failed_count" -gt 0 ]]; then
    echo "  ❌ PR #${pr_number} — CI failed (${failed_count} failure(s)) — skipping"
    SKIPPED+=("${repo}#${pr_number} (CI failed)")
    return
  fi

  # All checks passed — merge
  echo "  ✅ CI green — merging PR #${pr_number}..."
  if gh pr merge "${pr_number}" --repo "${repo}" --squash --auto 2>/dev/null || \
     gh pr merge "${pr_number}" --repo "${repo}" --merge 2>/dev/null; then
    echo "  🎉 Merged PR #${pr_number}: ${pr_title}"
    MERGED+=("${repo}#${pr_number}: ${pr_title}")
  else
    echo "  ⚠️  Could not merge PR #${pr_number} (may need approval or branch protection)"
    FAILED+=("${repo}#${pr_number}: ${pr_title}")
  fi
}

for REPO in "${REPOS[@]}"; do
  echo ""
  echo "🔎 Checking Dependabot PRs in ${REPO}..."

  # Fetch open Dependabot PRs
  prs_json=$(gh pr list \
    --repo "${REPO}" \
    --author "app/dependabot" \
    --state open \
    --json number,title,headRefOid,headRefName \
    2>/dev/null || echo "[]")

  pr_count=$(echo "$prs_json" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 0)

  if [[ "$pr_count" -eq 0 ]]; then
    echo "  ✓ No open Dependabot PRs"
    continue
  fi

  echo "  Found ${pr_count} Dependabot PR(s)"

  # Process each PR
  echo "$prs_json" | python3 -c "
import sys, json
prs = json.load(sys.stdin)
for pr in prs:
    print(f\"{pr['number']}|{pr['title']}|{pr['headRefOid']}\")
" | while IFS='|' read -r number title sha; do
    check_and_merge "${REPO}" "${number}" "${title}" "${sha}"
  done
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Auto-merge Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Merged: ${#MERGED[@]}"
for m in "${MERGED[@]:-}"; do [[ -n "$m" ]] && echo "   • $m"; done
echo "⏭️  Skipped: ${#SKIPPED[@]}"
for s in "${SKIPPED[@]:-}"; do [[ -n "$s" ]] && echo "   • $s"; done
echo "⚠️  Could not merge: ${#FAILED[@]}"
for f in "${FAILED[@]:-}"; do [[ -n "$f" ]] && echo "   • $f"; done

# Export results for daily-ops.sh to consume
export AUTOMERGE_MERGED="${MERGED[*]:-}"
export AUTOMERGE_SKIPPED="${SKIPPED[*]:-}"
export AUTOMERGE_FAILED="${FAILED[*]:-}"
