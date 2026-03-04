#!/usr/bin/env bash
# inner-life-core: Initialize state files with defaults
# Usage: ./init.sh [workspace_dir]

set -euo pipefail

WORKSPACE="${1:-${OPENCLAW_WORKSPACE:-$(pwd)}}"
MEMORY_DIR="$WORKSPACE/memory"
TASKS_DIR="$WORKSPACE/tasks"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATES="$SKILL_DIR/templates"

echo "Initializing inner-life state files in $WORKSPACE..."

mkdir -p "$MEMORY_DIR" "$MEMORY_DIR/diary" "$MEMORY_DIR/dreams" "$TASKS_DIR"

for file in inner-state.json drive.json habits.json relationship.json; do
  target="$MEMORY_DIR/$file"
  if [ -f "$target" ]; then
    echo "  EXISTS: $target (skipping)"
  else
    cp "$TEMPLATES/$file" "$target"
    # Set initial lastUpdate
    tmp=$(jq --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '.lastUpdate = $now' "$target")
    echo "$tmp" > "$target"
    echo "  CREATED: $target"
  fi
done

# Create BRAIN.md if not exists
if [ ! -f "$WORKSPACE/BRAIN.md" ]; then
  cp "$TEMPLATES/BRAIN.md" "$WORKSPACE/BRAIN.md"
  echo "  CREATED: $WORKSPACE/BRAIN.md"
else
  echo "  EXISTS: $WORKSPACE/BRAIN.md (skipping)"
fi

# Create SELF.md if not exists
if [ ! -f "$WORKSPACE/SELF.md" ]; then
  cat > "$WORKSPACE/SELF.md" << 'SELFEOF'
# SELF.md — Who I'm Becoming

> Living observations. Updated through reflection, not forced.

## Tendencies

## Preferences

## Blind Spots

## Evolution
SELFEOF
  echo "  CREATED: $WORKSPACE/SELF.md"
else
  echo "  EXISTS: $WORKSPACE/SELF.md (skipping)"
fi

# Create questions.md if not exists
if [ ! -f "$MEMORY_DIR/questions.md" ]; then
  cat > "$MEMORY_DIR/questions.md" << 'QEOF'
# Curiosity Backlog

## Open Questions

## Leads

## Dead Ends
QEOF
  echo "  CREATED: $MEMORY_DIR/questions.md"
else
  echo "  EXISTS: $MEMORY_DIR/questions.md (skipping)"
fi

# Create QUEUE.md if not exists
if [ ! -f "$TASKS_DIR/QUEUE.md" ]; then
  cat > "$TASKS_DIR/QUEUE.md" << 'QUEOF'
# Task Queue

## Ready

## In Progress

## Blocked

## Done Today
QUEOF
  echo "  CREATED: $TASKS_DIR/QUEUE.md"
else
  echo "  EXISTS: $TASKS_DIR/QUEUE.md (skipping)"
fi

echo "Done. Your agent now has an inner life."
