#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════╗
# ║           YFinance MCP Server — Install Script               ║
# ║                                                              ║
# ║  Installs the yfinance MCP server, registers it in           ║
# ║  mcporter, and optionally installs the OpenClaw skill.       ║
# ╚══════════════════════════════════════════════════════════════╝
set -euo pipefail

# ── Configurable Defaults ────────────────────────────────────────
PROJECT_DIR="${YFINANCE_PROJECT_DIR:-$(cd "$(dirname "$0")" && pwd)}"
PYTHON_VERSION="${YFINANCE_PYTHON_VERSION:-3.12}"
VENV_DIR="${YFINANCE_VENV_DIR:-$PROJECT_DIR/.venv}"
REPO_URL="${YFINANCE_REPO_URL:-https://github.com/rizkydwicmt/yfinance-mcp-server.git}"
MCPORTER_CONFIG="${MCPORTER_CONFIG:-}"
CLAWD_DIR="${CLAWD_DIR:-/root/clawd}"
SKILLS_DIR="${CLAWD_DIR}/skills/yfinance"
SKIP_SKILL="${SKIP_SKILL:-false}"
SKIP_MCPORTER="${SKIP_MCPORTER:-false}"
AUTO_YES="${YFINANCE_YES:-false}"

# ── Colors & Helpers ─────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()    { echo -e "${BLUE}ℹ${NC}  $*"; }
success() { echo -e "${GREEN}✅${NC} $*"; }
warn()    { echo -e "${YELLOW}⚠${NC}  $*"; }
error()   { echo -e "${RED}❌${NC} $*" >&2; }
step()    { echo -e "\n${CYAN}${BOLD}── $* ──${NC}"; }

# ── Banner ───────────────────────────────────────────────────────
echo -e "${BOLD}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         YFinance MCP Server — Installer v1.0            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo "  Project:  $PROJECT_DIR"
echo "  Python:   $PYTHON_VERSION"
echo "  Venv:     $VENV_DIR"
echo ""

# ── Pre-flight Checks ───────────────────────────────────────────
step "1/6 — Pre-flight Checks"

if [ ! -f "$PROJECT_DIR/pyproject.toml" ]; then
    info "pyproject.toml not found in $PROJECT_DIR"
    info "Bootstrapping project by cloning from GitHub..."

    if ! command -v git &>/dev/null; then
        error "git is required to clone the repository."
        exit 1
    fi

    CLONE_DIR="$PROJECT_DIR/yfinance-mcp-server"
    if [ -f "$CLONE_DIR/pyproject.toml" ]; then
        info "Using existing clone at $CLONE_DIR"
    else
        git clone "$REPO_URL" "$CLONE_DIR" 2>&1
    fi

    PROJECT_DIR="$CLONE_DIR"
    if [ -z "${YFINANCE_VENV_DIR:-}" ]; then
        VENV_DIR="$PROJECT_DIR/.venv"
    fi
    success "Project bootstrapped at $PROJECT_DIR"
fi
success "Project directory found"

# ── Install uv (if not present) ─────────────────────────────────
step "2/6 — Python Environment (uv)"

UV_BIN=""
if command -v uv &>/dev/null; then
    UV_BIN="$(command -v uv)"
    success "uv already installed at $UV_BIN"
elif [ -f "$HOME/.local/bin/uv" ]; then
    UV_BIN="$HOME/.local/bin/uv"
    success "uv found at $UV_BIN"
elif [ -f "/root/.local/bin/uv" ]; then
    UV_BIN="/root/.local/bin/uv"
    success "uv found at $UV_BIN"
else
    info "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh 2>&1
    if [ -f "$HOME/.local/bin/uv" ]; then
        UV_BIN="$HOME/.local/bin/uv"
    elif [ -f "/root/.local/bin/uv" ]; then
        UV_BIN="/root/.local/bin/uv"
    else
        error "Failed to install uv. Install manually: https://docs.astral.sh/uv/"
        exit 1
    fi
    success "uv installed at $UV_BIN"
fi

# ── Create Virtual Environment ──────────────────────────────────
step "3/6 — Virtual Environment"

if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/python" ]; then
    EXISTING_VER=$("$VENV_DIR/bin/python" --version 2>&1 | awk '{print $2}')
    info "Existing venv found (Python $EXISTING_VER)"
    if [ "$AUTO_YES" = "true" ]; then
        response="y"
    else
        read -r -p "  Recreate venv? [y/N] " response
    fi
    if [[ "$response" =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_DIR"
        info "Removed old venv"
    else
        info "Keeping existing venv"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    info "Creating venv with Python $PYTHON_VERSION..."
    "$UV_BIN" venv "$VENV_DIR" --python "$PYTHON_VERSION" 2>&1
    success "Venv created at $VENV_DIR"
else
    success "Venv ready at $VENV_DIR"
fi

# ── Install Package ─────────────────────────────────────────────
step "4/6 — Install Package"

info "Installing yfinance-mcp-server + dependencies..."
"$UV_BIN" pip install -e "$PROJECT_DIR" --python "$VENV_DIR/bin/python" 2>&1 | tail -5
success "Package installed"

# Verify entry point
if [ -f "$VENV_DIR/bin/yfin-mcp" ]; then
    success "Entry point: $VENV_DIR/bin/yfin-mcp"
else
    error "Entry point yfin-mcp not found in $VENV_DIR/bin/"
    exit 1
fi

# Verify tools load
info "Verifying tools load..."
TOOL_COUNT=$("$VENV_DIR/bin/python" -c "
from yfinance_mcp.server import mcp
print(len(mcp._tool_manager._tools))
" 2>&1)

if [ "$TOOL_COUNT" = "12" ]; then
    success "All 12 tools loaded"
else
    warn "Expected 12 tools, got: $TOOL_COUNT"
fi

# ── Configure mcporter ──────────────────────────────────────────
step "5/6 — mcporter Configuration"

if [ "$SKIP_MCPORTER" = "true" ]; then
    info "Skipping mcporter config (SKIP_MCPORTER=true)"
else
    # Auto-detect mcporter config
    if [ -z "$MCPORTER_CONFIG" ]; then
        if [ -f "$CLAWD_DIR/config/mcporter.json" ]; then
            MCPORTER_CONFIG="$CLAWD_DIR/config/mcporter.json"
        elif [ -f "./config/mcporter.json" ]; then
            MCPORTER_CONFIG="./config/mcporter.json"
        fi
    fi

    if [ -n "$MCPORTER_CONFIG" ] && [ -f "$MCPORTER_CONFIG" ]; then
        info "mcporter config: $MCPORTER_CONFIG"

        # Check if yfinance already configured
        if grep -q '"yfinance"' "$MCPORTER_CONFIG" 2>/dev/null; then
            info "yfinance already in mcporter config"
            if [ "$AUTO_YES" = "true" ]; then
                response="y"
            else
                read -r -p "  Update command path? [y/N] " response
            fi
            if [[ ! "$response" =~ ^[Yy]$ ]]; then
                success "Keeping existing mcporter config"
            else
                # Update the command path using Python
                python3 -c "
import json
config = json.load(open('$MCPORTER_CONFIG'))
config['mcpServers']['yfinance']['command'] = '$VENV_DIR/bin/yfin-mcp'
json.dump(config, open('$MCPORTER_CONFIG', 'w'), indent=2)
print('Updated')
" 2>&1
                success "mcporter config updated"
            fi
        else
            # Add yfinance to config
            python3 -c "
import json
config = json.load(open('$MCPORTER_CONFIG'))
if 'mcpServers' not in config:
    config['mcpServers'] = {}
config['mcpServers']['yfinance'] = {
    'command': '$VENV_DIR/bin/yfin-mcp'
}
json.dump(config, open('$MCPORTER_CONFIG', 'w'), indent=2)
print('Added')
" 2>&1
            success "yfinance added to mcporter config"
        fi

        # Verify with mcporter
        if command -v mcporter &>/dev/null; then
            info "Testing mcporter integration..."
            TOOL_LIST=$(mcporter --config "$MCPORTER_CONFIG" list yfinance 2>&1 | head -5)
            if echo "$TOOL_LIST" | grep -q "yfinance"; then
                success "mcporter recognizes yfinance server"
            else
                warn "mcporter may need the --config flag:"
                warn "  mcporter --config $MCPORTER_CONFIG list yfinance"
            fi
        fi
    else
        warn "No mcporter config found"
        info "To configure manually, add to your mcporter.json:"
        echo ""
        echo "  {\"mcpServers\": {\"yfinance\": {\"command\": \"$VENV_DIR/bin/yfin-mcp\"}}}"
        echo ""
    fi
fi

# ── Install OpenClaw Skill ──────────────────────────────────────
step "6/6 — OpenClaw Skill"

if [ "$SKIP_SKILL" = "true" ]; then
    info "Skipping skill install (SKIP_SKILL=true)"
elif [ -d "$CLAWD_DIR" ]; then
    info "OpenClaw detected at $CLAWD_DIR"
    mkdir -p "$SKILLS_DIR"

    if [ -f "$PROJECT_DIR/SKILL.md" ]; then
        cp "$PROJECT_DIR/SKILL.md" "$SKILLS_DIR/SKILL.md"
        success "SKILL.md installed → $SKILLS_DIR/SKILL.md"
    else
        warn "SKILL.md not found in project — skipping skill install"
    fi

    if [ -f "$PROJECT_DIR/README.md" ]; then
        cp "$PROJECT_DIR/README.md" "$SKILLS_DIR/README.md"
        success "README.md installed → $SKILLS_DIR/README.md"
    fi
else
    info "OpenClaw not detected at $CLAWD_DIR — skipping skill install"
    info "Set CLAWD_DIR to your OpenClaw directory to enable"
fi

# ── Summary ──────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║                  Installation Complete                   ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  📦 Package:     yfinance-mcp-server v1.0.0"
echo "  🐍 Python:      $("$VENV_DIR/bin/python" --version 2>&1)"
echo "  🔧 Entry point: $VENV_DIR/bin/yfin-mcp"
echo "  🧰 Tools:       $TOOL_COUNT loaded"
[ -n "$MCPORTER_CONFIG" ] && [ -f "$MCPORTER_CONFIG" ] && \
echo "  ⚙️  mcporter:    $MCPORTER_CONFIG"
[ -d "$SKILLS_DIR" ] && [ -f "$SKILLS_DIR/SKILL.md" ] && \
echo "  🎯 Skill:       $SKILLS_DIR/"
echo ""
echo -e "${BOLD}Quick Test:${NC}"
if [ -n "$MCPORTER_CONFIG" ] && [ -f "$MCPORTER_CONFIG" ]; then
echo "  mcporter --config $MCPORTER_CONFIG call yfinance.tool_get_stock_price symbol=AAPL"
else
echo "  $VENV_DIR/bin/yfin-mcp"
fi
echo ""
echo -e "${BOLD}Environment Variables:${NC}"
echo "  YFINANCE_PROJECT_DIR   Project location (default: script dir)"
echo "  YFINANCE_REPO_URL      Git repository URL for bootstrap clone"
echo "  YFINANCE_PYTHON_VERSION Python version (default: 3.12)"
echo "  YFINANCE_VENV_DIR      Venv location (default: \$PROJECT/.venv)"
echo "  MCPORTER_CONFIG        Path to mcporter.json (auto-detected)"
echo "  CLAWD_DIR              OpenClaw directory (default: /root/clawd)"
echo "  SKIP_MCPORTER=true     Skip mcporter config step"
echo "  SKIP_SKILL=true        Skip OpenClaw skill install"
echo "  YFINANCE_YES=true      Auto-accept all prompts (non-interactive)"
echo ""
