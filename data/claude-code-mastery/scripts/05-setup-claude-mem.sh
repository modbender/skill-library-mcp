#!/bin/bash
# 05-setup-claude-mem.sh
# Optional: Installs and configures claude-mem for persistent memory

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Source config if exists
if [[ -f "$SKILL_DIR/config.sh" ]]; then
    source "$SKILL_DIR/config.sh"
fi

# Parse arguments
AUTO_YES=0
SKIP=0
while [[ $# -gt 0 ]]; do
    case $1 in
        --yes|-y)
            AUTO_YES=1
            shift
            ;;
        --skip|-s)
            SKIP=1
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --yes, -y    Install without prompting"
            echo "  --skip, -s   Skip claude-mem installation entirely"
            echo "  --help, -h   Show this help message"
            echo ""
            echo "Claude-mem is OPTIONAL. It provides persistent memory across"
            echo "Claude Code sessions but adds complexity. Most users don't need it."
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Skip if requested
if [[ $SKIP -eq 1 ]]; then
    echo "⏭️  Skipping claude-mem installation (--skip flag)"
    echo ""
    echo "You can install it later by running:"
    echo "  ./scripts/05-setup-claude-mem.sh --yes"
    exit 0
fi

echo "🧠 Claude-Mem Setup (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Claude-mem provides persistent memory across Claude Code sessions:"
echo "- Automatic observation capture during tool usage"
echo "- Semantic search across sessions"
echo "- ~10x token savings via progressive disclosure"
echo ""
echo "⚠️  NOTE: This is OPTIONAL and adds complexity."
echo "   Most users can skip this and still use Claude Code effectively."
echo "   This is a community-maintained plugin, not official Anthropic software."
echo ""

# Check if already installed
PLUGIN_DIR="$HOME/.claude/plugins/marketplaces/thedotmack"

if [[ -d "$PLUGIN_DIR" ]]; then
    echo "📦 Claude-mem already installed at: $PLUGIN_DIR"
    
    # Check worker status
    cd "$PLUGIN_DIR"
    STATUS=$(bun plugin/scripts/worker-service.cjs status 2>&1 || true)
    
    if echo "$STATUS" | grep -q "running"; then
        echo "✅ Worker is running"
        echo "$STATUS"
        exit 0
    else
        echo "⚠️  Worker not running"
        read -p "Start worker? (Y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            bun plugin/scripts/worker-service.cjs start
            echo "✅ Worker started"
        fi
        exit 0
    fi
fi

# Ask user if they want to install (default NO)
if [[ $AUTO_YES -eq 0 ]]; then
    echo ""
    read -p "Do you want to install claude-mem? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "⏭️  Skipping claude-mem installation."
        echo ""
        echo "You can install it later by running:"
        echo "  ./scripts/05-setup-claude-mem.sh --yes"
        echo ""
        echo "Claude Code works great without it!"
        exit 0
    fi
fi

echo ""
echo "📥 Installing claude-mem..."
echo ""

# Check dependencies
echo "🔍 Checking dependencies..."

MISSING_DEPS=0

if ! command -v bun &> /dev/null; then
    echo "❌ Bun not installed"
    echo "   Install: curl -fsSL https://bun.sh/install | bash"
    MISSING_DEPS=1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not installed"
    MISSING_DEPS=1
fi

if [[ $MISSING_DEPS -eq 1 ]]; then
    echo ""
    echo "⚠️  Missing dependencies. Install them first, then re-run this script."
    exit 1
fi

echo "✅ Dependencies satisfied"
echo ""

# Create plugin directory
mkdir -p "$HOME/.claude/plugins/marketplaces"
cd "$HOME/.claude/plugins/marketplaces"

# Clone the repo - pinned to specific commit for security/stability
# Using a known-good commit prevents supply chain attacks from upstream changes
CLAUDE_MEM_REPO="${CLAUDE_MEM_REPO:-https://github.com/thedotmack/claude-mem.git}"
CLAUDE_MEM_COMMIT="${CLAUDE_MEM_COMMIT:-1341e93fcab15b9caf48bc947d8521b4a97515d8}"

if [[ ! -d "thedotmack" ]]; then
    echo "Cloning claude-mem repository..."
    echo "   Repo: $CLAUDE_MEM_REPO"
    echo "   Commit: $CLAUDE_MEM_COMMIT (pinned for security)"
    echo ""
    git clone "$CLAUDE_MEM_REPO" thedotmack
    cd thedotmack
    git checkout "$CLAUDE_MEM_COMMIT" || {
        echo "⚠️  Warning: Could not checkout pinned commit"
        echo "   Falling back to main branch (less secure)"
        git checkout main
    }
    cd ..
fi

cd thedotmack

# Install dependencies
echo "Installing dependencies..."
bun install

# Start worker
echo ""
echo "Starting claude-mem worker..."
bun plugin/scripts/worker-service.cjs start

# Verify
echo ""
echo "🔍 Verifying installation..."
sleep 2

STATUS=$(bun plugin/scripts/worker-service.cjs status 2>&1 || true)
if echo "$STATUS" | grep -q "running"; then
    echo "✅ Claude-mem installed and running!"
    echo ""
    echo "$STATUS"
else
    echo "⚠️  Worker may not have started correctly"
    echo "Try: cd $PLUGIN_DIR && bun plugin/scripts/worker-service.cjs start"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Claude-mem Info:"
echo ""
echo "Web UI:     http://localhost:37777"
echo "Database:   ~/.claude-mem/claude-mem.db"
echo "Plugin:     $PLUGIN_DIR"
echo ""
echo "Commands:"
echo "  Status: cd $PLUGIN_DIR && bun plugin/scripts/worker-service.cjs status"
echo "  Start:  cd $PLUGIN_DIR && bun plugin/scripts/worker-service.cjs start"
echo "  Stop:   cd $PLUGIN_DIR && bun plugin/scripts/worker-service.cjs stop"
echo ""
echo "⚠️  Remember: claude-mem is community-maintained, not official Anthropic software."
echo ""
echo "✅ Setup complete!"
