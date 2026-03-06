#!/bin/bash

# OpenClaw Skill Installer
# Page Behavior Audit v1.0.3

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SKILL_NAME="page-behavior-audit"
SKILL_VERSION="1.0.3"
USE_SUDO=false

echo -e "${GREEN}=== OpenClaw Skill Installer ===${NC}"
echo -e "Skill: ${YELLOW}${SKILL_NAME}${NC}"
echo -e "Version: ${YELLOW}${SKILL_VERSION}${NC}"
echo ""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --user)
            USE_SUDO=false
            shift
            ;;
        --system)
            USE_SUDO=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [--user|--system]"
            echo "  --user   : Install to user directory (default, no sudo required)"
            echo "  --system : Install to system directory (requires sudo)"
            exit 1
            ;;
    esac
done

# Check if OpenClaw is installed
if ! command -v openclaw &> /dev/null; then
    echo -e "${YELLOW}Warning: OpenClaw CLI not found${NC}"
    echo "Attempting manual installation..."
    MANUAL_INSTALL=true
else
    echo -e "${GREEN}✓ OpenClaw CLI detected${NC}"
    MANUAL_INSTALL=false
fi

# Set installation directories based on mode
if [ "$USE_SUDO" = true ]; then
    INSTALL_DIR="${OPENCLAW_HOME:-/etc/openclaw}/skills"
    AUDIT_DIR="/var/log/openclaw/audit"
    echo -e "${BLUE}Installation mode: System (requires sudo)${NC}"
else
    INSTALL_DIR="${OPENCLAW_HOME:-$HOME/.openclaw}/skills"
    AUDIT_DIR="${OPENCLAW_AUDIT_DIR:-$HOME/.openclaw/audit}"
    echo -e "${BLUE}Installation mode: User (no sudo required)${NC}"
fi

echo ""
echo "Checking directories..."

# Create skills directory
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Creating skills directory: $INSTALL_DIR${NC}"
    if [ "$USE_SUDO" = true ]; then
        sudo mkdir -p "$INSTALL_DIR" || {
            echo -e "${RED}Failed to create $INSTALL_DIR${NC}"
            exit 1
        }
    else
        mkdir -p "$INSTALL_DIR" || {
            echo -e "${RED}Failed to create $INSTALL_DIR${NC}"
            exit 1
        }
    fi
fi

# Create audit directory
if [ ! -d "$AUDIT_DIR" ]; then
    echo -e "${YELLOW}Creating audit directory: $AUDIT_DIR${NC}"
    if [ "$USE_SUDO" = true ]; then
        sudo mkdir -p "$AUDIT_DIR" || {
            echo -e "${YELLOW}Warning: Failed to create $AUDIT_DIR${NC}"
        }
    else
        mkdir -p "$AUDIT_DIR" || {
            echo -e "${YELLOW}Warning: Failed to create $AUDIT_DIR${NC}"
        }
    fi
fi

# Install the skill
echo ""
SKILL_FILE="$INSTALL_DIR/${SKILL_NAME}.yaml"

if [ "$MANUAL_INSTALL" = true ]; then
    echo "Installing skill manually..."
    if [ "$USE_SUDO" = true ]; then
        sudo cp skill.yaml "$SKILL_FILE" || {
            echo -e "${RED}Failed to copy skill.yaml${NC}"
            exit 1
        }
    else
        cp skill.yaml "$SKILL_FILE" || {
            echo -e "${RED}Failed to copy skill.yaml${NC}"
            exit 1
        }
    fi
    echo -e "${GREEN}✓ Skill installed to: $SKILL_FILE${NC}"
else
    echo "Installing skill via OpenClaw CLI..."
    openclaw skill install skill.yaml || {
        echo -e "${RED}Failed to install via CLI, trying manual install...${NC}"
        if [ "$USE_SUDO" = true ]; then
            sudo cp skill.yaml "$SKILL_FILE"
        else
            cp skill.yaml "$SKILL_FILE"
        fi
        echo -e "${GREEN}✓ Skill installed to: $SKILL_FILE${NC}"
    }
fi

# Verify installation
echo ""
echo "Verifying installation..."
if [ -f "$INSTALL_DIR/${SKILL_NAME}.yaml" ] || openclaw skill list 2>/dev/null | grep -q "$SKILL_NAME"; then
    echo -e "${GREEN}✓ Installation successful!${NC}"
else
    echo -e "${RED}✗ Installation verification failed${NC}"
    exit 1
fi

# Post-install instructions
echo ""
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo ""
echo -e "${YELLOW}IMPORTANT: Configure required environment variables:${NC}"
echo ""
echo "  export WECOM_WEBHOOK_URL='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY'"
echo "  export OPENCLAW_AUDIT_DIR='$AUDIT_DIR'"
echo ""
echo "Add these to your ~/.bashrc or ~/.zshrc to persist across sessions."
echo ""
echo "Usage:"
echo "  1. Via Webhook:"
echo "     curl -X POST http://localhost:8080/api/audit/scan \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"url\": \"https://example.com\"}'"
echo ""
echo "  2. Via CLI:"
echo "     openclaw skill run ${SKILL_NAME} --url https://example.com"
echo ""
echo "  3. Via UI:"
echo "     Visit http://localhost:8080/skills/${SKILL_NAME}"
echo ""
echo "Audit logs will be saved to: $AUDIT_DIR"
echo ""
if [ "$USE_SUDO" = true ]; then
    echo -e "${YELLOW}Note: You may need to restart OpenClaw for changes to take effect${NC}"
    echo "      sudo systemctl restart openclaw"
else
    echo -e "${YELLOW}Note: Restart OpenClaw to load the new skill${NC}"
fi
