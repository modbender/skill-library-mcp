#!/bin/bash

# Meegle MCP Skill Setup Script
# This script helps you configure the Meegle MCP skill for OpenClaw

set -e

echo "================================================"
echo "Meegle MCP Skill Setup"
echo "================================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "Skill directory: $SKILL_DIR"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✓${NC} Node.js is installed ($(node --version))"

# Prompt for user key
echo ""
echo "Please enter your Meegle User Key:"
echo "(You can find this in your Meegle workspace settings)"
read -p "User Key: " USER_KEY

if [ -z "$USER_KEY" ]; then
    echo -e "${RED}Error: User Key is required${NC}"
    exit 1
fi

# Prompt for MCP key
echo ""
echo "Please enter your Meegle MCP Key:"
echo "(You can find this in your Meegle workspace settings)"
read -p "MCP Key: " MCP_KEY

if [ -z "$MCP_KEY" ]; then
    echo -e "${RED}Error: MCP Key is required${NC}"
    exit 1
fi

# Setup environment variables
echo ""
echo "Setting up environment variables..."

# Detect shell
SHELL_CONFIG=""
if [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="${HOME}/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    if [ -f "${HOME}/.bash_profile" ]; then
        SHELL_CONFIG="${HOME}/.bash_profile"
    else
        SHELL_CONFIG="${HOME}/.bashrc"
    fi
fi

if [ -n "$SHELL_CONFIG" ]; then
    echo ""
    echo "Adding MEEGLE_USER_KEY and MEEGLE_MCP_KEY to $SHELL_CONFIG"

    # Check if MEEGLE_USER_KEY already exists
    if grep -q "MEEGLE_USER_KEY" "$SHELL_CONFIG"; then
        echo -e "${YELLOW}Warning: MEEGLE_USER_KEY already exists in $SHELL_CONFIG${NC}"
        read -p "Overwrite? (y/n): " OVERWRITE
        if [ "$OVERWRITE" == "y" ]; then
            sed -i.bak '/MEEGLE_USER_KEY/d' "$SHELL_CONFIG"
        fi
    fi

    # Check if MEEGLE_MCP_KEY already exists
    if grep -q "MEEGLE_MCP_KEY" "$SHELL_CONFIG"; then
        echo -e "${YELLOW}Warning: MEEGLE_MCP_KEY already exists in $SHELL_CONFIG${NC}"
        read -p "Overwrite? (y/n): " OVERWRITE
        if [ "$OVERWRITE" == "y" ]; then
            sed -i.bak '/MEEGLE_MCP_KEY/d' "$SHELL_CONFIG"
        fi
    fi

    echo "export MEEGLE_USER_KEY=\"$USER_KEY\"" >> "$SHELL_CONFIG"
    echo "export MEEGLE_MCP_KEY=\"$MCP_KEY\"" >> "$SHELL_CONFIG"
    echo -e "${GREEN}✓${NC} Added to $SHELL_CONFIG"

    # Export for current session
    export MEEGLE_USER_KEY="$USER_KEY"
    export MEEGLE_MCP_KEY="$MCP_KEY"
else
    echo -e "${YELLOW}Warning: Could not detect shell config file${NC}"
    echo "Please manually add:"
    echo "  export MEEGLE_USER_KEY=\"$USER_KEY\""
    echo "  export MEEGLE_MCP_KEY=\"$MCP_KEY\""
fi

# Make proxy script executable
chmod +x "${SKILL_DIR}/scripts/mcp-proxy.js"
echo -e "${GREEN}✓${NC} Made mcp-proxy.js executable"

echo ""
echo "================================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Restart your shell (or run: source ~/.zshrc)"
echo "2. Restart OpenClaw"
echo "3. Verify installation: openclaw skills list | grep meegle"
echo ""
echo "Test the skill with:"
echo "  openclaw ask 'List my Meegle projects'"
echo ""
echo "For troubleshooting, check logs:"
echo "  openclaw logs --filter=meegle"
echo ""
