#!/bin/bash
set -e

# OpenClaw Workspace Pro - Installation Script
# Version: 1.0.0

WORKSPACE_DIR="${WORKSPACE_DIR:-/data/.openclaw/workspace}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Installing OpenClaw Workspace Pro..."
echo ""

# Backup existing files
backup_if_exists() {
    local file=$1
    if [ -f "$WORKSPACE_DIR/$file" ]; then
        echo "📦 Backing up existing $file..."
        cp "$WORKSPACE_DIR/$file" "$WORKSPACE_DIR/$file.backup.$(date +%Y%m%d-%H%M%S)"
    fi
}

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p "$WORKSPACE_DIR/artifacts/"{reports,code,data,exports}
mkdir -p "$WORKSPACE_DIR/memory/archive"
echo "   ✅ artifacts/ created"
echo "   ✅ memory/archive/ created"

# Install .gitignore
echo ""
echo "🛡 Installing .gitignore..."
if [ ! -f "$WORKSPACE_DIR/.gitignore" ]; then
    cp "$SKILL_DIR/templates/gitignore" "$WORKSPACE_DIR/.gitignore"
    echo "   ✅ .gitignore created"
else
    echo "   ⚠️  .gitignore exists, skipping (see templates/gitignore for reference)"
fi

# Install .env template
echo ""
echo "🔒 Installing .env template..."
if [ ! -f "$WORKSPACE_DIR/.env" ]; then
    cp "$SKILL_DIR/templates/env.example" "$WORKSPACE_DIR/.env"
    echo "   ✅ .env created (populate with your secrets)"
else
    echo "   ⚠️  .env exists, preserving (see templates/env.example for reference)"
fi

# Install MEMORY-COMPACTION.md
echo ""
echo "🧠 Installing memory compaction workflow..."
cp "$SKILL_DIR/templates/MEMORY-COMPACTION.md" "$WORKSPACE_DIR/MEMORY-COMPACTION.md"
echo "   ✅ MEMORY-COMPACTION.md installed"

# Update AGENTS.md
echo ""
echo "📝 Updating AGENTS.md..."
backup_if_exists "AGENTS.md"
if [ -f "$WORKSPACE_DIR/AGENTS.md" ]; then
    # Check if already has Workspace Pro markers
    if grep -q "## 📦 Artifact Workflow" "$WORKSPACE_DIR/AGENTS.md"; then
        echo "   ⚠️  AGENTS.md already has Workspace Pro sections, skipping"
    else
        # Append Workspace Pro sections
        cat "$SKILL_DIR/templates/AGENTS-additions.md" >> "$WORKSPACE_DIR/AGENTS.md"
        echo "   ✅ AGENTS.md updated"
    fi
else
    echo "   ⚠️  AGENTS.md not found, skipping (create workspace first)"
fi

# Update TOOLS.md
echo ""
echo "🔧 Updating TOOLS.md..."
backup_if_exists "TOOLS.md"
if [ -f "$WORKSPACE_DIR/TOOLS.md" ]; then
    if grep -q "### Network Security - Approved Domains" "$WORKSPACE_DIR/TOOLS.md"; then
        echo "   ⚠️  TOOLS.md already has network security section, skipping"
    else
        cat "$SKILL_DIR/templates/TOOLS-additions.md" >> "$WORKSPACE_DIR/TOOLS.md"
        echo "   ✅ TOOLS.md updated"
    fi
else
    echo "   ⚠️  TOOLS.md not found, skipping (create workspace first)"
fi

# Summary
echo ""
echo "✨ Installation complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Populate .env with your API credentials"
echo "   2. Review AGENTS.md additions (artifact workflow, secrets management)"
echo "   3. Read MEMORY-COMPACTION.md for maintenance workflow"
echo "   4. Start using artifacts/ for all deliverables"
echo ""
echo "📚 Documentation: $SKILL_DIR/SKILL.md"
echo "🐛 Issues: https://github.com/Eugene9D/openclaw-workspace-pro/issues"
echo ""
echo "Happy building! 🚀"
