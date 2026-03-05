#!/bin/bash
# uninstall.sh
# Clean removal of Claude Code Mastery components

set -e

echo "🗑️  Claude Code Mastery Uninstaller"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Parse arguments
FORCE=0
KEEP_CLAUDE_CODE=0
while [[ $# -gt 0 ]]; do
    case $1 in
        --force|-f)
            FORCE=1
            shift
            ;;
        --keep-claude-code)
            KEEP_CLAUDE_CODE=1
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --force, -f         Skip confirmation prompts"
            echo "  --keep-claude-code  Don't remove Claude Code CLI itself"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "This script removes:"
            echo "  - Subagents installed by this skill"
            echo "  - Claude-mem plugin (if installed)"
            echo "  - Claude Code CLI (unless --keep-claude-code)"
            echo ""
            echo "This script does NOT remove:"
            echo "  - Your ~/.claude/settings.json"
            echo "  - Your ~/.claude/projects/ history"
            echo "  - Any project-level .claude/ directories"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Confirmation
if [[ $FORCE -eq 0 ]]; then
    echo "This will remove:"
    echo "  - Subagents from ~/.claude/agents/"
    echo "  - Claude-mem plugin from ~/.claude/plugins/"
    if [[ $KEEP_CLAUDE_CODE -eq 0 ]]; then
        echo "  - Claude Code CLI from ~/.local/bin/claude"
    fi
    echo ""
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

echo ""

# Track what we remove
REMOVED=0

# 1. Stop claude-mem worker if running
PLUGIN_DIR="$HOME/.claude/plugins/marketplaces/thedotmack"
if [[ -d "$PLUGIN_DIR" ]]; then
    echo "🛑 Stopping claude-mem worker..."
    cd "$PLUGIN_DIR"
    if command -v bun &>/dev/null; then
        bun plugin/scripts/worker-service.cjs stop 2>/dev/null || true
    fi
    cd - >/dev/null
fi

# Kill any orphan claude-mem processes
if pgrep -f "claude-mem" >/dev/null 2>&1; then
    echo "🛑 Killing orphan claude-mem processes..."
    pkill -f "claude-mem" 2>/dev/null || true
    echo "   Killed orphan processes"
fi

# Kill any worker processes on the default port
if pgrep -f "worker-service" >/dev/null 2>&1; then
    echo "🛑 Killing worker-service processes..."
    pkill -f "worker-service" 2>/dev/null || true
fi

# 2. Remove subagents installed by this skill
AGENTS_DIR="$HOME/.claude/agents"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
AGENTS_SRC="$SKILL_DIR/agents"

if [[ -d "$AGENTS_DIR" ]] && [[ -d "$AGENTS_SRC" ]]; then
    echo "🗑️  Removing subagents..."
    for agent_file in "$AGENTS_SRC"/*.md; do
        if [[ -f "$agent_file" ]]; then
            filename=$(basename "$agent_file")
            dest_file="$AGENTS_DIR/$filename"
            if [[ -f "$dest_file" ]]; then
                rm "$dest_file"
                echo "   Removed: $filename"
                REMOVED=$((REMOVED + 1))
            fi
        fi
    done
fi

# 3. Remove claude-mem plugin
if [[ -d "$PLUGIN_DIR" ]]; then
    echo "🗑️  Removing claude-mem plugin..."
    rm -rf "$PLUGIN_DIR"
    REMOVED=$((REMOVED + 1))
    echo "   Removed: $PLUGIN_DIR"
fi

# 4. Remove claude-mem database (optional - prompt user)
if [[ -d "$HOME/.claude-mem" ]]; then
    if [[ $FORCE -eq 1 ]]; then
        rm -rf "$HOME/.claude-mem"
        echo "   Removed: ~/.claude-mem (database)"
        REMOVED=$((REMOVED + 1))
    else
        read -p "Remove claude-mem database (~/.claude-mem)? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$HOME/.claude-mem"
            echo "   Removed: ~/.claude-mem"
            REMOVED=$((REMOVED + 1))
        else
            echo "   Kept: ~/.claude-mem"
        fi
    fi
fi

# 5. Remove Claude Code CLI
if [[ $KEEP_CLAUDE_CODE -eq 0 ]]; then
    CLAUDE_BIN="$HOME/.local/bin/claude"
    if [[ -f "$CLAUDE_BIN" ]]; then
        echo "🗑️  Removing Claude Code CLI..."
        rm "$CLAUDE_BIN"
        REMOVED=$((REMOVED + 1))
        echo "   Removed: $CLAUDE_BIN"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Removed: $REMOVED items"
echo ""
echo "Preserved (not removed):"
echo "  - ~/.claude/settings.json (your settings)"
echo "  - ~/.claude/projects/ (session history)"
echo "  - Project .claude/ directories"
echo ""
echo "✅ Uninstall complete!"
