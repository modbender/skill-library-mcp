#!/bin/bash
# setup-check.sh - First-time setup verification
# Skill: dev-team

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== Dev Team Skill Setup Check ==="
echo ""

ISSUES=0

# Check 1: Script permissions
echo "Checking script permissions..."
for script in "$SCRIPT_DIR"/*.sh; do
    if [[ -x "$script" ]]; then
        echo -e "  ✓ $(basename $script) is executable"
    else
        echo -e "  ✗ $(basename $script) is NOT executable"
        ISSUES=$((ISSUES + 1))
    fi
done
echo ""

# Check 2: tmux
echo "Checking tmux..."
if command -v tmux &> /dev/null; then
    VERSION=$(tmux -V)
    echo -e "  ✓ tmux installed: $VERSION"
else
    echo -e "  ✗ tmux NOT installed"
    echo "    Install with: brew install tmux"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# Check 3: Core CLIs
echo "Checking core CLIs..."
for cli in git gh python3; do
    if command -v $cli &> /dev/null; then
        echo -e "  ✓ $cli available"
    else
        echo -e "  ✗ $cli NOT found"
        ISSUES=$((ISSUES + 1))
    fi
done
if command -v gh &> /dev/null; then
    GH_AUTH=$(gh auth status 2>&1 || true)
    if echo "$GH_AUTH" | grep -qi "token in default is invalid\\|not logged in\\|not logged into any github hosts"; then
        echo -e "  ⚠ gh installed but auth invalid (run: gh auth login)"
    else
        echo -e "  ✓ gh auth looks OK"
    fi
fi
echo ""

# Check 4: Optional agent CLIs
echo "Checking optional agent CLIs (at least one recommended)..."
AGENT_CLI_COUNT=0
for cli in codex claude gemini cursor; do
    if command -v $cli &> /dev/null; then
        echo -e "  ✓ $cli available"
        AGENT_CLI_COUNT=$((AGENT_CLI_COUNT + 1))
    else
        echo -e "  - $cli not found (optional)"
    fi
done
if [[ $AGENT_CLI_COUNT -eq 0 ]]; then
    echo -e "  ⚠ No agent CLI found yet (install at least one before spawning tasks)"
fi
if command -v cursor &> /dev/null; then
    CURSOR_STATUS=$(cursor agent status 2>&1 || true)
    if echo "$CURSOR_STATUS" | grep -qi "not logged in"; then
        CURSOR_TMUX_OK=0
        if command -v tmux &> /dev/null; then
            PROBE_SESSION="teamdev-cursor-setup-$$"
            PROBE_FILE="/tmp/${PROBE_SESSION}.txt"
            tmux new-session -d -s "$PROBE_SESSION" "cursor agent status > '$PROBE_FILE' 2>&1" >/dev/null 2>&1 || true
            sleep 2
            if [[ -f "$PROBE_FILE" ]] && ! grep -qi "not logged in" "$PROBE_FILE"; then
                CURSOR_TMUX_OK=1
            fi
            tmux kill-session -t "$PROBE_SESSION" >/dev/null 2>&1 || true
            rm -f "$PROBE_FILE" >/dev/null 2>&1 || true
        fi
        if [[ "$CURSOR_TMUX_OK" -eq 1 ]]; then
            echo -e "  ✓ cursor login OK in tmux (non-interactive shell may misreport)"
        else
            echo -e "  ⚠ cursor installed but not logged in (run: cursor agent login)"
        fi
    else
        echo -e "  ✓ cursor login status looks OK"
    fi
fi
echo ""

# Check 5: Directories
echo "Checking directories..."
for dir in logs logs/archives references; do
    if [[ -d "$SKILL_DIR/$dir" ]]; then
        echo -e "  ✓ $dir/ exists"
    else
        echo -e "  ✗ $dir/ missing, creating..."
        mkdir -p "$SKILL_DIR/$dir"
    fi
done
echo ""

# Check 6: Maintenance scripts
echo "Checking maintenance scripts..."
for script in prune-history.sh cleanup-worktrees.sh check-agents.sh; do
    if [[ -x "$SCRIPT_DIR/$script" ]]; then
        echo -e "  ✓ $script executable"
    else
        echo -e "  ⚠ $script not executable"
    fi
done
echo ""

# Migration: move legacy runtime files from root to assets/ (one-time)
if [[ -f "$SKILL_DIR/active-tasks.json" ]] || [[ -f "$SKILL_DIR/tasks.json" ]] || [[ -f "$SKILL_DIR/notifications.json" ]] || [[ -d "$SKILL_DIR/logs" ]]; then
    echo "Migrating legacy runtime files to assets/..."
    mkdir -p "$SKILL_DIR/assets"
    [[ -f "$SKILL_DIR/active-tasks.json" ]] && [[ ! -f "$SKILL_DIR/assets/active-tasks.json" ]] && mv "$SKILL_DIR/active-tasks.json" "$SKILL_DIR/assets/" && echo "  ✓ active-tasks.json"
    [[ -f "$SKILL_DIR/tasks.json" ]] && [[ ! -f "$SKILL_DIR/assets/tasks.json" ]] && mv "$SKILL_DIR/tasks.json" "$SKILL_DIR/assets/" && echo "  ✓ tasks.json"
    [[ -f "$SKILL_DIR/notifications.json" ]] && [[ ! -f "$SKILL_DIR/assets/notifications.json" ]] && mv "$SKILL_DIR/notifications.json" "$SKILL_DIR/assets/" && echo "  ✓ notifications.json"
    if [[ -d "$SKILL_DIR/logs" ]] && [[ ! -d "$SKILL_DIR/assets/logs" ]]; then
        mv "$SKILL_DIR/logs" "$SKILL_DIR/assets/"
        echo "  ✓ logs/"
    fi
    echo ""
fi

# Check 7: Active tasks file
echo "Checking task registry..."
if [[ -f "$SKILL_DIR/assets/active-tasks.json" ]]; then
    echo -e "  ✓ active-tasks.json exists"
else
    echo -e "  ⚠ active-tasks.json not found, will be created on first use"
    mkdir -p "$SKILL_DIR/assets"
    echo '{}' > "$SKILL_DIR/assets/active-tasks.json"
fi
echo ""

# Summary
echo "=== Summary ==="
if [[ $ISSUES -eq 0 ]]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Configure cron (see references/initialization.md)"
    echo "  2. Spawn your first agent:"
    echo "     ./scripts/spawn-agent.sh --agent codex --repo my-repo --branch fix/test --description 'test' --prompt 'hello'"
else
    echo -e "${RED}✗ $ISSUES issue(s) found${NC}"
    echo ""
    echo "Please fix the issues above before continuing."
fi
