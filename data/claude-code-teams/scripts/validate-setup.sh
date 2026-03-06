#!/usr/bin/env bash
# validate-setup.sh - Check prerequisites for Claude Code agent teams

set -euo pipefail

echo "🎭 Claude Code Agent Teams - Setup Validation"
echo "=============================================="
echo ""

FAILED=0

# Check 1: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS environment variable
echo -n "✓ Checking CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS... "
if [ "${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-}" = "1" ] || [ "${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-}" = "true" ]; then
    echo "✅ Enabled"
else
    echo "❌ NOT SET"
    echo "  Fix: export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1"
    echo "  Or add to ~/.claude/settings.json:"
    echo '  {"env": {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}}'
    FAILED=1
fi

# Check 2: claude CLI available
echo -n "✓ Checking claude CLI... "
if command -v claude &> /dev/null; then
    CLAUDE_VERSION=$(claude --version 2>&1 || echo "unknown")
    echo "✅ Found ($CLAUDE_VERSION)"
else
    echo "❌ NOT FOUND"
    echo "  Fix: Install Claude Code from https://github.com/anthropics/claude-code"
    FAILED=1
fi

# Check 3: tmux (optional, but recommended for split-pane display)
echo -n "✓ Checking tmux (optional)... "
if command -v tmux &> /dev/null; then
    TMUX_VERSION=$(tmux -V)
    echo "✅ Found ($TMUX_VERSION)"
else
    echo "⚠️  NOT FOUND (optional)"
    echo "  Note: tmux enables split-pane display mode for teams"
    echo "  Install: brew install tmux (macOS) or apt install tmux (Ubuntu)"
fi

# Check 4: PTY support (verify terminal is interactive)
echo -n "✓ Checking PTY support... "
if [ -t 0 ]; then
    echo "✅ Terminal is interactive"
else
    echo "⚠️  Non-interactive terminal"
    echo "  Note: Agent teams require interactive PTY mode"
fi

echo ""
echo "=============================================="

if [ $FAILED -eq 0 ]; then
    echo "✅ Setup validation PASSED"
    echo ""
    echo "Next steps:"
    echo "  1. Choose a template: cd templates/ && ls"
    echo "  2. Start Claude Code: claude --pty"
    echo "  3. Paste spawn prompt from template"
    echo "  4. Monitor progress: ./scripts/team-monitor.sh (in separate terminal)"
    exit 0
else
    echo "❌ Setup validation FAILED"
    echo ""
    echo "Fix the issues above, then re-run: ./scripts/validate-setup.sh"
    exit 1
fi
