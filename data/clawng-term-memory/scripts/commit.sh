#!/bin/bash
# Commit and push changes to agent's own branch (agent/<hostname>)
# Each machine has its own branch — daily merge consolidates into main

set -e

WORKSPACE="${CLAWNG_WORKSPACE:-$HOME/.openclaw/workspace}"
AGENT_BRANCH="agent/$(hostname)"
MSG="${1:-"chore: update core knowledge files"}"

cd "$WORKSPACE"

# Ensure we're on the correct agent branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "$AGENT_BRANCH" ]; then
  git checkout -B "$AGENT_BRANCH" 2>/dev/null || git checkout "$AGENT_BRANCH"
fi

# Stage all tracked core files
git add \
  SOUL.md MEMORY.md USER.md TOOLS.md IDENTITY.md AGENTS.md HEARTBEAT.md \
  memory/ skills/ \
  .gitignore \
  2>/dev/null || true

# Check if there's anything to commit
if git diff --cached --quiet; then
  echo "Nothing to commit — no changes in core files."
  exit 0
fi

git commit -m "$MSG"

# Pull rebase from own branch before push (handles concurrent writes)
git pull --rebase origin "$AGENT_BRANCH" 2>/dev/null || true
git push origin "$AGENT_BRANCH" 2>/dev/null || echo "[warn] Push failed — committed locally"

echo "Committed + pushed to $AGENT_BRANCH: $MSG"
git log --oneline -1
