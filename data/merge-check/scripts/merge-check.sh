#!/usr/bin/env bash
# merge-check.sh — Gather PR data for mergeability analysis
# Usage: merge-check.sh owner/repo#123
#        merge-check.sh https://github.com/owner/repo/pull/123
set -euo pipefail

if [ $# -lt 1 ]; then
  echo '{"error":"Usage: merge-check.sh owner/repo#123 or GitHub PR URL"}' >&2
  exit 1
fi

INPUT="$1"

# Parse input — support URL or owner/repo#number
if [[ "$INPUT" =~ ^https?://github\.com/([^/]+)/([^/]+)/pull/([0-9]+) ]]; then
  OWNER="${BASH_REMATCH[1]}"
  REPO="${BASH_REMATCH[2]}"
  NUMBER="${BASH_REMATCH[3]}"
elif [[ "$INPUT" =~ ^([^/]+)/([^#]+)#([0-9]+)$ ]]; then
  OWNER="${BASH_REMATCH[1]}"
  REPO="${BASH_REMATCH[2]}"
  NUMBER="${BASH_REMATCH[3]}"
else
  echo '{"error":"Cannot parse PR reference. Use owner/repo#123 or GitHub PR URL"}' >&2
  exit 1
fi

API="repos/${OWNER}/${REPO}"

safe_gh() {
  local result
  if result=$(gh api "$@" 2>/dev/null); then
    echo "$result"
  else
    echo "null"
  fi
}

# 1. PR metadata
PR=$(safe_gh "${API}/pulls/${NUMBER}")
if [ "$PR" = "null" ]; then
  echo "{\"error\":\"PR not found: ${OWNER}/${REPO}#${NUMBER}\"}"
  exit 1
fi

HEAD_SHA=$(echo "$PR" | jq -r '.head.sha // empty')
AUTHOR=$(echo "$PR" | jq -r '.user.login // empty')

# 2. PR files (paginated up to 300)
FILES=$(safe_gh "${API}/pulls/${NUMBER}/files?per_page=100")

# 3. Diff stats
DIFF_STATS=$(echo "$FILES" | jq '{
  files_changed: length,
  additions: [.[].additions] | add,
  deletions: [.[].deletions] | add,
  total_changes: ([.[].additions] | add) + ([.[].deletions] | add),
  directories: [.[].filename | split("/")[:-1] | join("/")] | unique | length
}' 2>/dev/null || echo 'null')

# 4. Check runs
CHECKS="null"
if [ -n "$HEAD_SHA" ]; then
  CHECKS=$(safe_gh "${API}/commits/${HEAD_SHA}/check-runs")
fi

# 5. Reviews
REVIEWS=$(safe_gh "${API}/pulls/${NUMBER}/reviews?per_page=100")

# 6. Review comments
REVIEW_COMMENTS=$(safe_gh "${API}/pulls/${NUMBER}/comments?per_page=100")

# 7. Issue comments
ISSUE_COMMENTS=$(safe_gh "${API}/issues/${NUMBER}/comments?per_page=100")

# 8. Commits
COMMITS=$(safe_gh "${API}/pulls/${NUMBER}/commits?per_page=100")

# 9. Repo info
REPO_INFO=$(safe_gh "${API}")

# 10. Author history — recent closed PRs
AUTHOR_PRS="null"
if [ -n "$AUTHOR" ]; then
  CLOSED_PRS=$(safe_gh "${API}/pulls?state=closed&per_page=30")
  if [ "$CLOSED_PRS" != "null" ]; then
    AUTHOR_PRS=$(echo "$CLOSED_PRS" | jq --arg author "$AUTHOR" '{
      recent_closed: [.[] | select(.user.login == $author)] | length,
      recent_merged: [.[] | select(.user.login == $author and .merged_at != null)] | length
    }' 2>/dev/null || echo 'null')
  fi
fi

# 11. CODEOWNERS
HAS_CODEOWNERS=false
if gh api "${API}/contents/.github/CODEOWNERS" --silent 2>/dev/null; then
  HAS_CODEOWNERS=true
elif gh api "${API}/contents/CODEOWNERS" --silent 2>/dev/null; then
  HAS_CODEOWNERS=true
fi

# 12. CONTRIBUTING.md
HAS_CONTRIBUTING=false
if gh api "${API}/contents/CONTRIBUTING.md" --silent 2>/dev/null; then
  HAS_CONTRIBUTING=true
fi

# Compact PR metadata
PR_COMPACT=$(echo "$PR" | jq '{
  title: .title,
  body: (.body // "" | if length > 2000 then .[:2000] + "..." else . end),
  state: .state,
  draft: .draft,
  author: .user.login,
  author_association: .author_association,
  created_at: .created_at,
  updated_at: .updated_at,
  merged_at: .merged_at,
  labels: [.labels[].name],
  requested_reviewers: [.requested_reviewers[].login],
  requested_teams: [.requested_teams[].slug],
  milestone: (.milestone.title // null),
  head_ref: .head.ref,
  base_ref: .base.ref,
  head_sha: .head.sha
}')

# Compact checks
CHECKS_COMPACT=$(echo "$CHECKS" | jq '{
  total: .total_count,
  runs: [.check_runs[] | {name: .name, status: .status, conclusion: .conclusion}]
}' 2>/dev/null || echo 'null')

# Compact reviews
REVIEWS_COMPACT=$(echo "$REVIEWS" | jq '[.[] | {user: .user.login, state: .state, submitted_at: .submitted_at, body: (.body // "" | if length > 500 then .[:500] + "..." else . end)}]' 2>/dev/null || echo 'null')

# Compact review comments
REVIEW_COMMENTS_COMPACT=$(echo "$REVIEW_COMMENTS" | jq '[.[] | {user: .user.login, path: .path, body: (.body | if length > 500 then .[:500] + "..." else . end), created_at: .created_at}]' 2>/dev/null || echo 'null')

# Compact issue comments
ISSUE_COMMENTS_COMPACT=$(echo "$ISSUE_COMMENTS" | jq '[.[] | {user: .user.login, body: (.body | if length > 500 then .[:500] + "..." else . end), created_at: .created_at}]' 2>/dev/null || echo 'null')

# Compact commits
COMMITS_COMPACT=$(echo "$COMMITS" | jq '[.[] | {sha: .sha[:7], message: (.commit.message | split("\n")[0]), author: .commit.author.name}]' 2>/dev/null || echo 'null')

# Compact repo
REPO_COMPACT=$(echo "$REPO_INFO" | jq '{
  language: .language,
  default_branch: .default_branch,
  open_issues: .open_issues_count,
  stargazers: .stargazers_count,
  archived: .archived,
  fork: .fork
}' 2>/dev/null || echo 'null')

# Compact files
FILES_COMPACT=$(echo "$FILES" | jq '[.[] | {filename: .filename, status: .status, additions: .additions, deletions: .deletions, changes: .changes}]' 2>/dev/null || echo 'null')

# Assemble final JSON
jq -n \
  --argjson pr "$PR_COMPACT" \
  --argjson files "$FILES_COMPACT" \
  --argjson diff_stats "$DIFF_STATS" \
  --argjson checks "$CHECKS_COMPACT" \
  --argjson reviews "$REVIEWS_COMPACT" \
  --argjson review_comments "$REVIEW_COMMENTS_COMPACT" \
  --argjson issue_comments "$ISSUE_COMMENTS_COMPACT" \
  --argjson commits "$COMMITS_COMPACT" \
  --argjson repo "$REPO_COMPACT" \
  --argjson author_history "$AUTHOR_PRS" \
  --argjson has_codeowners "$HAS_CODEOWNERS" \
  --argjson has_contributing "$HAS_CONTRIBUTING" \
  '{
    pr: $pr,
    files: $files,
    diff_stats: $diff_stats,
    checks: $checks,
    reviews: $reviews,
    review_comments: $review_comments,
    issue_comments: $issue_comments,
    commits: $commits,
    repo: $repo,
    author_history: $author_history,
    has_codeowners: $has_codeowners,
    has_contributing: $has_contributing
  }'
