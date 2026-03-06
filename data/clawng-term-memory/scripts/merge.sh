#!/bin/bash
# Daily merge: collect all agent MEMORY.md files and write them to /tmp
# for the AI synthesis agent to read and produce SHARED_MEMORY.md

set -e

WORKSPACE="${CLAWNG_WORKSPACE:-$HOME/.openclaw/workspace}"
STAGING_DIR="/tmp/clawng-merge-$$"

cd "$WORKSPACE"

mkdir -p "$STAGING_DIR"

echo "[merge] Fetching all remote branches..."
git fetch origin

# Collect MEMORY.md from each agent branch
AGENT_BRANCHES=$(git branch -r | grep 'origin/agent/' | sed 's|.*origin/||' | tr -d ' ')

if [ -z "$AGENT_BRANCHES" ]; then
  echo "[merge] No agent branches found."
  rm -rf "$STAGING_DIR"
  exit 0
fi

for branch in $AGENT_BRANCHES; do
  agent_id=$(echo "$branch" | sed 's|agent/||')
  memory=$(git show "origin/$branch:MEMORY.md" 2>/dev/null || echo "")
  if [ -n "$memory" ]; then
    echo "=== $agent_id ===" >> "$STAGING_DIR/all-memories.txt"
    echo "$memory" >> "$STAGING_DIR/all-memories.txt"
    echo "" >> "$STAGING_DIR/all-memories.txt"
  fi
done

echo "[merge] Staged memory files from: $AGENT_BRANCHES"
echo "[merge] Output at: $STAGING_DIR/all-memories.txt"
cat "$STAGING_DIR/all-memories.txt"
