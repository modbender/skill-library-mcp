#!/bin/bash

# PARA + Proactive Agent Workspace Setup Script
# Usage: ./setup-workspace.sh [target-directory]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../assets/templates"
TARGET_DIR="${1:-.}"

echo "🦞📁 PARA + Proactive Agent Workspace Setup"
echo "============================================"
echo ""

# Check if target exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "Creating directory: $TARGET_DIR"
    mkdir -p "$TARGET_DIR"
fi

cd "$TARGET_DIR"
TARGET_DIR="$(pwd)"

echo "Target: $TARGET_DIR"
echo ""

# Check if already initialized
if [ -f "README.md" ] && grep -q "PARA + Proactive Agent" README.md 2>/dev/null; then
    echo "⚠️  This directory appears to already have a workspace structure."
    read -p "Overwrite? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

# Copy template files
echo "📁 Creating directory structure..."

# PARA directories
mkdir -p 1-projects 2-areas 3-resources 4-archives "+inbox" "+temp"

# Agent directories
mkdir -p .agents .learnings memory

# Copy files
cp "$TEMPLATE_DIR/README.md" .
cp "$TEMPLATE_DIR/AGENTS.md" . 2>/dev/null || true
cp "$TEMPLATE_DIR/SOUL.md" . 2>/dev/null || true
cp "$TEMPLATE_DIR/USER.md" . 2>/dev/null || true
cp "$TEMPLATE_DIR/HEARTBEAT.md" . 2>/dev/null || true
cp "$TEMPLATE_DIR/MEMORY.md" . 2>/dev/null || true
cp "$TEMPLATE_DIR/ONBOARDING.md" . 2>/dev/null || true
cp "$TEMPLATE_DIR/SESSION-STATE.md" . 2>/dev/null || true
cp "$TEMPLATE_DIR/TOOLS.md" . 2>/dev/null || true
cp "$TEMPLATE_DIR/.gitignore" . 2>/dev/null || true

# Copy PARA READMEs
cp "$TEMPLATE_DIR/1-projects/README.md" 1-projects/
cp "$TEMPLATE_DIR/2-areas/README.md" 2-areas/
cp "$TEMPLATE_DIR/3-resources/README.md" 3-resources/
cp "$TEMPLATE_DIR/4-archives/README.md" 4-archives/
cp "$TEMPLATE_DIR/+inbox/README.md" "+inbox/"
cp "$TEMPLATE_DIR/+temp/README.md" "+temp/"

# Copy agent files
cp "$TEMPLATE_DIR/.agents/README.md" .agents/
cp "$TEMPLATE_DIR/.learnings/LEARNINGS.md" .learnings/ 2>/dev/null || touch .learnings/LEARNINGS.md
cp "$TEMPLATE_DIR/memory/working-buffer.md" memory/ 2>/dev/null || touch memory/working-buffer.md

# Create state.json if not exists
if [ ! -f ".agents/state.json" ]; then
cat > .agents/state.json << 'EOF'
{
  "onboarding": {
    "state": "not_started",
    "progress": 0,
    "lastUpdated": ""
  },
  "heartbeat": {
    "lastChecks": {
      "email": null,
      "calendar": null,
      "memory": null
    }
  }
}
EOF
fi

# Create example project
mkdir -p 1-projects/example-project/docs 1-projects/example-project/assets
cat > 1-projects/example-project/README.md << 'EOF'
# Example Project

This is a sample project to demonstrate the workspace structure.

## Overview

**Goal:** Demonstrate PARA + Proactive Agent workflow  
**Deadline:** 2026-03-01  
**Status:** In Progress

## Structure

- `docs/` - Project documentation
- `assets/` - Project files and media
- `notes.md` - Working notes

## Tasks

- [x] Set up workspace structure
- [ ] Add content
- [ ] Review and archive

## Notes

See `notes.md` for detailed working notes.
EOF

cat > 1-projects/example-project/notes.md << 'EOF'
# Example Project - Working Notes

## $(date +%Y-%m-%d)

Created project structure. Using PARA method + Proactive Agent architecture.

### Decisions
- Using numbered prefixes for PARA folders (1-, 2-, 3-, 4-, +)
- +inbox for temporary items
- +temp for scratch space

### Next Steps
- Populate with real projects
- Set up daily notes habit
- Configure heartbeat checks
EOF

echo "✅ Workspace structure created!"
echo ""
echo "📂 Structure:"
find . -maxdepth 1 -type d | sort | sed 's/^\.\//  📁 /'
find . -maxdepth 1 -type f -name "*.md" | sort | sed 's/^\.\//  📄 /'
echo ""
echo "🚀 Next steps:"
echo "  1. Read README.md for full documentation"
echo "  2. Complete ONBOARDING.md to set up your profile"
echo "  3. Create your first project in 1-projects/"
echo "  4. Delete example-project when ready"
echo ""
echo "Happy organizing! 🦞📁"
