#!/bin/bash
# Mission Control Setup Script
# Copies dashboard files to your MoltBot workspace

set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$(pwd)}"

echo "🎛️ Mission Control Setup"
echo "========================"
echo "Skill directory: $SKILL_DIR"
echo "Target workspace: $WORKSPACE"
echo ""

# Check if workspace exists
if [ ! -d "$WORKSPACE" ]; then
    echo "❌ Workspace directory not found: $WORKSPACE"
    echo "Usage: mc-setup.sh <workspace-path>"
    exit 1
fi

# Check if assets exist
if [ ! -d "$SKILL_DIR/assets" ]; then
    echo "❌ Assets directory not found in skill"
    exit 1
fi

# Copy dashboard files
echo "📦 Copying dashboard files..."

# index.html
if [ -f "$SKILL_DIR/assets/index.html" ]; then
    cp "$SKILL_DIR/assets/index.html" "$WORKSPACE/"
    echo "  ✓ index.html"
fi

# data directory
if [ -d "$SKILL_DIR/assets/data" ]; then
    mkdir -p "$WORKSPACE/data"
    cp -r "$SKILL_DIR/assets/data/"* "$WORKSPACE/data/" 2>/dev/null || true
    echo "  ✓ data/"
fi

# canvas directory
if [ -d "$SKILL_DIR/assets/canvas" ]; then
    mkdir -p "$WORKSPACE/canvas"
    cp -r "$SKILL_DIR/assets/canvas/"* "$WORKSPACE/canvas/" 2>/dev/null || true
    echo "  ✓ canvas/"
fi

# .github/workflows
if [ -d "$SKILL_DIR/assets/.github" ]; then
    mkdir -p "$WORKSPACE/.github/workflows"
    cp -r "$SKILL_DIR/assets/.github/"* "$WORKSPACE/.github/" 2>/dev/null || true
    echo "  ✓ .github/workflows/"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Push to GitHub: git add -A && git commit -m 'Add Mission Control' && git push"
echo "  2. Enable GitHub Pages: Settings → Pages → Branch: main"
echo "  3. (Optional) Add SLACK_WEBHOOK_URL secret for notifications"
echo ""
echo "Dashboard will be at: https://[username].github.io/[repo]/"
