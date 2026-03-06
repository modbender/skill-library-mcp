#!/bin/bash

# OpenClaw Security Suite - Hook Installation Script
#
# This script installs security hooks into OpenClaw's hooks directory.
# Hooks will automatically validate user input and tool calls for security threats.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       OpenClaw Security Suite - Hook Installer          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Determine OpenClaw hooks directory
HOOKS_DIR="${HOME}/.openclaw/hooks"

# Check if custom hooks directory is set
if [ -n "$OPENCLAW_HOOKS_DIR" ]; then
    HOOKS_DIR="$OPENCLAW_HOOKS_DIR"
fi

echo -e "${BLUE}→${NC} Hooks directory: ${HOOKS_DIR}"

# Create hooks directory if it doesn't exist
if [ ! -d "$HOOKS_DIR" ]; then
    echo -e "${YELLOW}→${NC} Creating hooks directory..."
    mkdir -p "$HOOKS_DIR"
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install security-input-validator hook
echo -e "${BLUE}→${NC} Installing security-input-validator hook..."
if [ -d "$SCRIPT_DIR/security-input-validator" ]; then
    cp -r "$SCRIPT_DIR/security-input-validator" "$HOOKS_DIR/"
    echo -e "${GREEN}✓${NC} security-input-validator installed"
else
    echo -e "${RED}✗${NC} security-input-validator not found"
    exit 1
fi

# Install security-tool-validator hook
echo -e "${BLUE}→${NC} Installing security-tool-validator hook..."
if [ -d "$SCRIPT_DIR/security-tool-validator" ]; then
    cp -r "$SCRIPT_DIR/security-tool-validator" "$HOOKS_DIR/"
    echo -e "${GREEN}✓${NC} security-tool-validator installed"
else
    echo -e "${RED}✗${NC} security-tool-validator not found"
    exit 1
fi

# Create symlink to source files (for development)
# This allows hooks to access the main codebase
if [ -d "$SCRIPT_DIR/../src" ]; then
    echo -e "${BLUE}→${NC} Creating symlink to source directory..."
    # Remove old symlink if exists
    [ -L "$HOOKS_DIR/../openclaw-sec" ] && rm "$HOOKS_DIR/../openclaw-sec"
    ln -sf "$SCRIPT_DIR/.." "$HOOKS_DIR/../openclaw-sec"
    echo -e "${GREEN}✓${NC} Symlink created: $HOOKS_DIR/../openclaw-sec"
fi

# Check if openclaw CLI is available
if command -v openclaw &> /dev/null; then
    echo ""
    echo -e "${BLUE}→${NC} Enabling hooks via openclaw CLI..."
    openclaw hooks enable security-input-validator 2>/dev/null || echo -e "${YELLOW}→${NC} Note: Run 'openclaw hooks enable security-input-validator' manually"
    openclaw hooks enable security-tool-validator 2>/dev/null || echo -e "${YELLOW}→${NC} Note: Run 'openclaw hooks enable security-tool-validator' manually"
else
    echo ""
    echo -e "${YELLOW}→${NC} OpenClaw CLI not found. Hooks copied but not enabled."
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Installation Complete! ✓                    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Installed Hooks:${NC}"
echo -e "  🛡️  security-input-validator  - Validates user prompts"
echo -e "  🔒 security-tool-validator    - Validates tool calls"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Create ~/.openclaw/security-config.yaml (or use .openclaw-sec.yaml in project)"
echo -e "  2. Enable hooks: ${BLUE}openclaw hooks enable security-input-validator${NC}"
echo -e "  3. Enable hooks: ${BLUE}openclaw hooks enable security-tool-validator${NC}"
echo -e "  4. Verify installation: ${BLUE}openclaw hooks list${NC}"
echo ""
echo -e "${BLUE}Configuration:${NC}"
echo -e "  Location: ~/.openclaw/security-config.yaml or ./.openclaw-sec.yaml"
echo -e "  Example: See hooks/example-config.yaml"
echo ""
echo -e "${YELLOW}Note:${NC} Hooks require the OpenClaw Security Suite dependencies."
echo -e "Run ${BLUE}npm install${NC} in the project root if you haven't already."
echo ""
