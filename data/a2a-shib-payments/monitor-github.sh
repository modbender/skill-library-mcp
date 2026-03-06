#!/bin/bash
# GitHub Repository Monitor
# Checks for PRs, issues, stars, and other activity

REPO="marcus20232023/a2a-shib-payments"
STATE_FILE="/home/marc/projects/a2a-shib-payments/.github-monitor-state.json"

# Initialize state file if doesn't exist
if [ ! -f "$STATE_FILE" ]; then
  echo '{"lastCheckTime":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","stars":0,"forks":0,"openIssues":0,"openPRs":0,"lastPR":"","lastIssue":""}' > "$STATE_FILE"
fi

# Read previous state (default to 0 if not set)
PREV_STARS=$(jq -r '.stars // 0' "$STATE_FILE" 2>/dev/null || echo "0")
PREV_FORKS=$(jq -r '.forks // 0' "$STATE_FILE" 2>/dev/null || echo "0")
PREV_ISSUES=$(jq -r '.openIssues // 0' "$STATE_FILE" 2>/dev/null || echo "0")
PREV_PRS=$(jq -r '.openPRs // 0' "$STATE_FILE" 2>/dev/null || echo "0")

# Get current repo stats
REPO_DATA=$(gh repo view "$REPO" --json stargazerCount,forkCount)
CURRENT_STARS=$(echo "$REPO_DATA" | jq -r '.stargazerCount')
CURRENT_FORKS=$(echo "$REPO_DATA" | jq -r '.forkCount')

# Get issue count
ISSUE_DATA=$(gh issue list --repo "$REPO" --state open --limit 100 --json number)
CURRENT_ISSUES=$(echo "$ISSUE_DATA" | jq 'length')

# Get PRs
PR_DATA=$(gh pr list --repo "$REPO" --json number,title,author,createdAt --limit 5)
CURRENT_PRS=$(echo "$PR_DATA" | jq 'length')

# Check for changes and alert
ALERTS=""

if [ "$CURRENT_STARS" -gt "$PREV_STARS" ]; then
  NEW_STARS=$((CURRENT_STARS - PREV_STARS))
  ALERTS="${ALERTS}⭐ +${NEW_STARS} new star(s)! Total: ${CURRENT_STARS}\n"
fi

if [ "$CURRENT_FORKS" -gt "$PREV_FORKS" ]; then
  NEW_FORKS=$((CURRENT_FORKS - PREV_FORKS))
  ALERTS="${ALERTS}🍴 +${NEW_FORKS} new fork(s)! Total: ${CURRENT_FORKS}\n"
fi

if [ "$CURRENT_ISSUES" -gt "$PREV_ISSUES" ]; then
  NEW_ISSUES=$((CURRENT_ISSUES - PREV_ISSUES))
  ALERTS="${ALERTS}📝 +${NEW_ISSUES} new issue(s)! Total: ${CURRENT_ISSUES}\n"
  # Get latest issue details
  LATEST_ISSUE=$(gh issue list --repo "$REPO" --limit 1 --json number,title,author --jq '.[0]')
  if [ "$LATEST_ISSUE" != "null" ]; then
    ISSUE_NUM=$(echo "$LATEST_ISSUE" | jq -r '.number')
    ISSUE_TITLE=$(echo "$LATEST_ISSUE" | jq -r '.title')
    ISSUE_AUTHOR=$(echo "$LATEST_ISSUE" | jq -r '.author.login')
    ALERTS="${ALERTS}  Issue #${ISSUE_NUM}: \"${ISSUE_TITLE}\" by @${ISSUE_AUTHOR}\n"
  fi
fi

if [ "$CURRENT_PRS" -gt "$PREV_PRS" ]; then
  NEW_PRS=$((CURRENT_PRS - PREV_PRS))
  ALERTS="${ALERTS}🎉 +${NEW_PRS} new PR(s)! Total: ${CURRENT_PRS}\n"
  # Get latest PR details with full info
  LATEST_PR=$(echo "$PR_DATA" | jq -r '.[0]')
  if [ "$LATEST_PR" != "null" ]; then
    PR_NUM=$(echo "$LATEST_PR" | jq -r '.number')
    PR_TITLE=$(echo "$LATEST_PR" | jq -r '.title')
    PR_AUTHOR=$(echo "$LATEST_PR" | jq -r '.author.login')
    PR_URL="https://github.com/${REPO}/pull/${PR_NUM}"
    
    # Get detailed PR info
    PR_DETAIL=$(gh pr view "$PR_NUM" --repo "$REPO" --json additions,deletions,changedFiles,files 2>/dev/null)
    if [ $? -eq 0 ]; then
      ADDITIONS=$(echo "$PR_DETAIL" | jq -r '.additions')
      DELETIONS=$(echo "$PR_DETAIL" | jq -r '.deletions')
      CHANGED_FILES=$(echo "$PR_DETAIL" | jq -r '.changedFiles')
      
      ALERTS="${ALERTS}  PR #${PR_NUM}: \"${PR_TITLE}\" by @${PR_AUTHOR}\n"
      ALERTS="${ALERTS}  📊 Changes: ${CHANGED_FILES} files, +${ADDITIONS}/-${DELETIONS}\n"
      ALERTS="${ALERTS}  🔗 ${PR_URL}\n"
      ALERTS="${ALERTS}\n  ✅ Suggested Actions:\n"
      ALERTS="${ALERTS}  1. Review the code changes\n"
      ALERTS="${ALERTS}  2. Check if tests are included\n"
      ALERTS="${ALERTS}  3. Test locally if needed\n"
      ALERTS="${ALERTS}  4. Approve or request changes\n"
    else
      ALERTS="${ALERTS}  PR #${PR_NUM}: \"${PR_TITLE}\" by @${PR_AUTHOR}\n"
      ALERTS="${ALERTS}  🔗 ${PR_URL}\n"
    fi
  fi
fi

# Send alerts if any
if [ -n "$ALERTS" ]; then
  echo -e "🚀 GitHub Activity Alert - $(date)\n"
  echo -e "$ALERTS"
  echo ""
  
  # Send Telegram notification
  MESSAGE="🚀 *GitHub Activity Alert*\n\n${ALERTS}\nRepo: https://github.com/${REPO}"
  openclaw message send --channel telegram --to 5275167911 --message "$MESSAGE" 2>/dev/null || true
fi

# Update state file
cat > "$STATE_FILE" << EOF
{
  "lastCheckTime": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "stars": $CURRENT_STARS,
  "forks": $CURRENT_FORKS,
  "openIssues": $CURRENT_ISSUES,
  "openPRs": $CURRENT_PRS
}
EOF

# Always show current stats
echo "📊 Current Stats ($(date '+%Y-%m-%d %H:%M:%S'))"
echo "⭐ Stars: $CURRENT_STARS"
echo "🍴 Forks: $CURRENT_FORKS"
echo "📝 Issues: $CURRENT_ISSUES"
echo "🔀 PRs: $CURRENT_PRS"
