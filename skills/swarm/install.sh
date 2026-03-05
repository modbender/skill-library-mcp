#!/bin/bash
#
# Node Scaling Installer for Clawdbot
# https://github.com/Chair4ce/node-scaling
#
# Usage: curl -fsSL https://raw.githubusercontent.com/clawdbot/node-scaling/main/install.sh | bash
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Node Scaling Installer for Clawdbot${NC}"
echo ""

# Check prerequisites
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is required but not installed.${NC}"
    echo "   Install from: https://nodejs.org"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${YELLOW}⚠️  Node.js 18+ recommended. You have: $(node -v)${NC}"
fi

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is required but not installed.${NC}"
    exit 1
fi

# Determine install location
CLAWDBOT_HOME="${CLAWDBOT_HOME:-$HOME/clawd}"
SKILL_DIR="$CLAWDBOT_HOME/skills/node-scaling"

echo -e "📁 Install location: ${BLUE}$SKILL_DIR${NC}"
echo ""

# Clone or update
if [ -d "$SKILL_DIR" ]; then
    echo "Updating existing installation..."
    cd "$SKILL_DIR"
    git pull --quiet
    echo -e "${GREEN}✓ Updated${NC}"
else
    echo "Cloning repository..."
    mkdir -p "$CLAWDBOT_HOME/skills"
    git clone --quiet https://github.com/Chair4ce/node-scaling.git "$SKILL_DIR"
    echo -e "${GREEN}✓ Cloned${NC}"
fi

# Install dependencies
echo "Installing dependencies..."
cd "$SKILL_DIR"
npm install --production --quiet 2>/dev/null || npm install --production
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check if already configured
CONFIG_PATH="$HOME/.config/clawdbot/node-scaling.yaml"
if [ -f "$CONFIG_PATH" ]; then
    echo ""
    echo -e "${YELLOW}Existing configuration found at: $CONFIG_PATH${NC}"
    read -p "Run setup wizard again? [y/N]: " RERUN
    if [[ ! "$RERUN" =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${GREEN}✅ Node Scaling is ready!${NC}"
        echo ""
        echo "Try asking Clawdbot:"
        echo '  "Research the top 5 AI companies and compare them"'
        echo ""
        exit 0
    fi
fi

# Run setup wizard
echo ""
echo "Starting setup wizard..."
echo ""
node bin/setup.js

echo ""
echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""

# Display post-install recommendations
INSTALL_MD="$SKILL_DIR/INSTALL.md"
if [ -f "$INSTALL_MD" ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}📋 RECOMMENDED: Workspace Integration${NC}"
    echo ""
    echo "Swarm works best when integrated into your agent's workflow."
    echo ""
    echo -e "Read the full guide: ${BLUE}$INSTALL_MD${NC}"
    echo ""
    echo "Quick summary:"
    echo "  • Add rules to AGENTS.md → Agent auto-detects parallel tasks"
    echo "  • Add notes to TOOLS.md  → Quick reference for your setup"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # If running interactively, offer to show the file
    if [ -t 0 ]; then
        read -p "View integration guide now? [Y/n]: " VIEW_GUIDE
        if [[ ! "$VIEW_GUIDE" =~ ^[Nn]$ ]]; then
            echo ""
            cat "$INSTALL_MD"
            echo ""
        fi
    fi
fi

echo "Try asking your agent:"
echo '  "Research the top 5 AI companies and compare them"'
echo ""
