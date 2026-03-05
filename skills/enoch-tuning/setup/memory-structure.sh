#!/bin/bash
# enoch-tuning: create memory directory structure
WORKSPACE=${1:-~/.openclaw/workspace}

echo "Creating memory structure at $WORKSPACE..."

mkdir -p "$WORKSPACE/memory/decisions"
mkdir -p "$WORKSPACE/memory/people"
mkdir -p "$WORKSPACE/memory/lessons"
mkdir -p "$WORKSPACE/memory/commitments"
mkdir -p "$WORKSPACE/memory/preferences"
mkdir -p "$WORKSPACE/memory/projects"
mkdir -p "$WORKSPACE/memory/audits"
mkdir -p "$WORKSPACE/memory/archive"
mkdir -p "$WORKSPACE/research"
mkdir -p "$WORKSPACE/ops"

# Create VAULT_INDEX if it doesn't exist
if [ ! -f "$WORKSPACE/memory/VAULT_INDEX.md" ]; then
cat > "$WORKSPACE/memory/VAULT_INDEX.md" << 'EOF'
# VAULT_INDEX.md — Memory Index
_Scan this first before doing a full search. One-line description per note._
_Last updated: [DATE]_

## Decisions
[entries go here — format: | path | description |]

## People
[entries go here]

## Lessons
[entries go here]

## Projects
[entries go here]

## Preferences
[entries go here]

## Commitments
[entries go here]
EOF
echo "✅ VAULT_INDEX.md created"
fi

echo "✅ Memory structure created at $WORKSPACE/memory/"
echo ""
echo "Next: personalize SOUL.md, USER.md, MEMORY.md, and MISSION.md"
echo "Then run: bash setup/lock-identity.sh $WORKSPACE"
