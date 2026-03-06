#!/bin/bash
# Auto-deploy develop branch to staging
# Runs via cron, checks for new commits and restarts staging if needed

set -e

REPO_DIR="/Users/kevinhe/clawd/clawfeed"
LOG="/Users/kevinhe/clawd/logs/staging-deploy.log"
BRANCH="develop"
PLIST="com.openclaw.clawfeed-staging"

cd "$REPO_DIR"

# Fetch latest
git fetch origin "$BRANCH" --quiet 2>/dev/null

LOCAL=$(git rev-parse "$BRANCH" 2>/dev/null)
REMOTE=$(git rev-parse "origin/$BRANCH" 2>/dev/null)

if [ "$LOCAL" = "$REMOTE" ]; then
  exit 0
fi

# New commits found — pull and restart
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Deploying $BRANCH ($LOCAL -> $REMOTE)" >> "$LOG"

git checkout "$BRANCH" --quiet 2>/dev/null
git pull origin "$BRANCH" --quiet 2>/dev/null

launchctl kickstart -k "gui/$(id -u)/$PLIST" 2>/dev/null

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Staging restarted successfully" >> "$LOG"
