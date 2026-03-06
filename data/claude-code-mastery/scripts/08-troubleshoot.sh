#!/usr/bin/env bash
#
# Claude Code Troubleshooting Script
# Diagnoses common issues with Claude Code installation and configuration
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
ISSUES_FOUND=0
WARNINGS_FOUND=0

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Claude Code Troubleshooting Diagnostic                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Helper functions
check_pass() {
    echo -e "  ${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "  ${RED}✗${NC} $1"
    ((ISSUES_FOUND++))
}

check_warn() {
    echo -e "  ${YELLOW}⚠${NC} $1"
    ((WARNINGS_FOUND++))
}

check_info() {
    echo -e "  ${BLUE}ℹ${NC} $1"
}

# 1. Check Node.js
echo -e "${BLUE}1. Checking Node.js...${NC}"
if command -v node &>/dev/null; then
    NODE_VERSION=$(node --version | sed 's/v//')
    NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d. -f1)
    if [ "$NODE_MAJOR" -ge 18 ]; then
        check_pass "Node.js $NODE_VERSION (requires 18+)"
    else
        check_fail "Node.js $NODE_VERSION is too old (requires 18+)"
        echo "       → Fix: Install Node.js 18+ from https://nodejs.org"
    fi
else
    check_fail "Node.js not found"
    echo "       → Fix: Install Node.js from https://nodejs.org"
fi
echo ""

# 2. Check Claude Code installation
echo -e "${BLUE}2. Checking Claude Code installation...${NC}"
if command -v claude &>/dev/null; then
    CLAUDE_PATH=$(which claude)
    check_pass "Claude Code found at: $CLAUDE_PATH"
    
    if claude --version &>/dev/null; then
        CLAUDE_VERSION=$(claude --version 2>/dev/null | head -1)
        check_pass "Version: $CLAUDE_VERSION"
    else
        check_warn "Could not determine Claude Code version"
    fi
else
    check_fail "Claude Code not found in PATH"
    echo "       → Fix: Add ~/.local/bin to PATH:"
    echo "         export PATH=\"\$HOME/.local/bin:\$PATH\""
fi
echo ""

# 3. Check PATH
echo -e "${BLUE}3. Checking PATH configuration...${NC}"
if [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
    check_pass "~/.local/bin is in PATH"
else
    check_warn "~/.local/bin is not in PATH"
    echo "       → Fix: Add to your shell config:"
    echo "         echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc"
fi
echo ""

# 4. Check authentication
echo -e "${BLUE}4. Checking authentication...${NC}"
AUTH_FILE="$HOME/.config/claude-code/auth.json"
AUTH_FILE_ALT="$HOME/.claude.json"

if [ -f "$AUTH_FILE" ]; then
    check_pass "Auth file exists: $AUTH_FILE"
elif [ -f "$AUTH_FILE_ALT" ]; then
    check_pass "Auth file exists: $AUTH_FILE_ALT"
else
    check_warn "No auth file found - may need to login"
    echo "       → Fix: Run 'claude' and complete authentication"
fi
echo ""

# 5. Check network connectivity
echo -e "${BLUE}5. Checking network connectivity...${NC}"
if curl -s --connect-timeout 5 https://api.anthropic.com &>/dev/null; then
    check_pass "Can reach api.anthropic.com"
else
    check_fail "Cannot reach api.anthropic.com"
    echo "       → Check: VPN, firewall, or proxy settings"
fi
echo ""

# 6. Check for common environment issues
echo -e "${BLUE}6. Checking environment...${NC}"

# Check for proxy settings
if [ -n "$ALL_PROXY" ]; then
    check_warn "ALL_PROXY is set (may cause issues with SOCKS5)"
    echo "       → If using SOCKS5, try: unset ALL_PROXY"
fi

if [ -n "$HTTP_PROXY" ] || [ -n "$HTTPS_PROXY" ]; then
    check_info "Proxy configured: ${HTTP_PROXY:-$HTTPS_PROXY}"
fi

# Check WSL
if grep -qi microsoft /proc/version 2>/dev/null; then
    check_info "Running in WSL"
    
    # Check if using Windows npm
    NPM_PATH=$(which npm 2>/dev/null || echo "")
    if [[ "$NPM_PATH" == /mnt/* ]]; then
        check_warn "Using Windows npm in WSL"
        echo "       → Fix: Install npm via nvm in WSL"
    fi
fi

echo ""

# 7. Check claude-mem (if installed)
echo -e "${BLUE}7. Checking claude-mem (optional)...${NC}"
if pgrep -f "worker-service" >/dev/null 2>&1; then
    check_pass "claude-mem worker is running"
else
    check_info "claude-mem worker not running (optional)"
fi

CLAUDE_MEM_DIR="$HOME/.claude/plugins/marketplaces/thedotmack"
if [ -d "$CLAUDE_MEM_DIR" ]; then
    check_pass "claude-mem plugin installed"
else
    check_info "claude-mem not installed (optional)"
fi
echo ""

# 8. Check ripgrep (for search)
echo -e "${BLUE}8. Checking ripgrep (for search/discovery)...${NC}"
if command -v rg &>/dev/null; then
    RG_VERSION=$(rg --version | head -1)
    check_pass "ripgrep installed: $RG_VERSION"
else
    check_warn "ripgrep not installed (search may be limited)"
    echo "       → Fix: brew install ripgrep (macOS)"
    echo "               apt install ripgrep (Ubuntu)"
fi
echo ""

# 9. Check disk space
echo -e "${BLUE}9. Checking disk space...${NC}"
DISK_FREE=$(df -h ~ | tail -1 | awk '{print $4}')
check_info "Available disk space: $DISK_FREE"
echo ""

# 10. Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"

if [ $ISSUES_FOUND -eq 0 ] && [ $WARNINGS_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Claude Code should work correctly.${NC}"
elif [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS_FOUND warning(s) found, but no critical issues.${NC}"
else
    echo -e "${RED}✗ $ISSUES_FOUND issue(s) and $WARNINGS_FOUND warning(s) found.${NC}"
    echo ""
    echo "Recommended actions:"
    echo "  1. Fix the issues marked with ✗ above"
    echo "  2. Run 'claude doctor' for more detailed diagnostics"
    echo "  3. See docs/troubleshooting.md for solutions"
fi

echo ""
echo "For more help:"
echo "  • Run: claude doctor"
echo "  • Docs: https://code.claude.com/docs/en/troubleshooting"
echo "  • Report bugs: /bug command in Claude Code"
echo ""
