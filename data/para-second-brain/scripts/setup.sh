#!/bin/bash
# Second Brain Setup Script
# Creates PARA directory structure for Clawdbot workspace

set -e

WORKSPACE="${1:-.}"

echo "🧠 Setting up Second Brain in: $WORKSPACE"

# Create directory structure
mkdir -p "$WORKSPACE/memory"
mkdir -p "$WORKSPACE/notes/projects"
mkdir -p "$WORKSPACE/notes/areas"
mkdir -p "$WORKSPACE/notes/resources"
mkdir -p "$WORKSPACE/notes/archive"

echo "✓ Created directory structure"

# Create MEMORY.md if it doesn't exist
if [ ! -f "$WORKSPACE/MEMORY.md" ]; then
  cat > "$WORKSPACE/MEMORY.md" << 'EOF'
# MEMORY.md — Long-Term Memory

## About [Human's Name]
- Role: [What they do]
- Goals: [Key objectives]
- Style: [Communication preferences]

## Active Context
- [Current focus areas]

## Preferences
- [Tools and workflows they prefer]

## Lessons Learned
- [Key insights]

---
*Last curated: $(date +%Y-%m-%d)*
EOF
  echo "✓ Created MEMORY.md template"
else
  echo "• MEMORY.md already exists, skipping"
fi

# Create today's daily log if it doesn't exist
TODAY=$(date +%Y-%m-%d)
if [ ! -f "$WORKSPACE/memory/$TODAY.md" ]; then
  cat > "$WORKSPACE/memory/$TODAY.md" << EOF
# $TODAY

## Morning Context
- Starting fresh with Second Brain setup

## Events

### $(date +%H:%M) — Second Brain Initialized
- Set up PARA structure
- Ready to capture and organize

## Learnings
- 

## Carry Forward
- [ ] 
EOF
  echo "✓ Created today's daily log"
else
  echo "• Today's log already exists, skipping"
fi

echo ""
echo "🎉 Second Brain ready!"
echo ""
echo "Structure:"
echo "  $WORKSPACE/"
echo "  ├── MEMORY.md          (curated long-term memory)"
echo "  ├── memory/"
echo "  │   └── $TODAY.md      (daily log)"
echo "  └── notes/"
echo "      ├── projects/      (active work with deadlines)"
echo "      ├── areas/         (ongoing responsibilities)"
echo "      ├── resources/     (reference material)"
echo "      └── archive/       (completed/inactive)"
echo ""
echo "Next: Add Second Brain instructions to your AGENTS.md"
