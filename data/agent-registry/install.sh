#!/bin/bash
# Agent Registry Skill Installer
# Installs the agent-registry skill to your Claude Code skills directory

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║       Agent Registry Skill Installer                     ║"
echo "║  Reduce agent token overhead by ~95%                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

usage() {
    echo "Usage: ./install.sh [--project|-p] [--install-deps] [--help|-h]"
    echo ""
    echo "Options:"
    echo "  --project, -p      Install to ./.claude/skills/agent-registry"
    echo "  --install-deps     Install optional dependencies (@clack/prompts)"
    echo "  --help, -h         Show this help"
}

INSTALL_DIR="$HOME/.claude/skills/agent-registry"
INSTALL_DEPS=0

for arg in "$@"; do
    case "$arg" in
        --project|-p)
            INSTALL_DIR=".claude/skills/agent-registry"
            ;;
        --install-deps)
            INSTALL_DEPS=1
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            usage
            exit 1
            ;;
    esac
done

if [ "$INSTALL_DIR" = ".claude/skills/agent-registry" ]; then
    echo -e "${YELLOW}Installing to project-level: ${INSTALL_DIR}${NC}"
else
    echo -e "${GREEN}Installing to user-level: ${INSTALL_DIR}${NC}"
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create target directory
echo -e "\n${CYAN}Creating skill directory...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/lib"
mkdir -p "$INSTALL_DIR/bin"
mkdir -p "$INSTALL_DIR/references"
mkdir -p "$INSTALL_DIR/agents"
mkdir -p "$INSTALL_DIR/hooks"

# Copy files
echo -e "${CYAN}Copying skill files...${NC}"

cp "$SCRIPT_DIR/SKILL.md" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/package.json" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/lib/"*.js "$INSTALL_DIR/lib/"
cp "$SCRIPT_DIR/bin/"*.js "$INSTALL_DIR/bin/"
chmod +x "$INSTALL_DIR/bin/"*.js
cp "$SCRIPT_DIR/hooks/"*.js "$INSTALL_DIR/hooks/"
chmod +x "$INSTALL_DIR/hooks/"*.js

# Create empty registry if it doesn't exist
if [ ! -f "$INSTALL_DIR/references/registry.json" ]; then
    echo '{"version": 1, "agents": [], "stats": {"total_agents": 0, "total_tokens": 0}}' > "$INSTALL_DIR/references/registry.json"
fi

# Install optional dependencies
if [ "$INSTALL_DEPS" -eq 1 ]; then
    echo -e "\n${CYAN}Installing optional dependencies...${NC}"
    if (cd "$INSTALL_DIR" && npm install --production >/dev/null 2>&1); then
        echo -e "${GREEN}✓ Optional dependencies installed via npm${NC}"
    elif (cd "$INSTALL_DIR" && bun install >/dev/null 2>&1); then
        echo -e "${GREEN}✓ Optional dependencies installed via bun${NC}"
    else
        echo -e "${YELLOW}! Could not install optional dependencies automatically${NC}"
        echo -e "${YELLOW}! Fallback text mode still works for init${NC}"
    fi
else
    echo -e "\n${YELLOW}Skipping dependency install (pass --install-deps to enable).${NC}"
fi

echo -e "\n${GREEN}✓ Skill installed successfully!${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo ""
echo "1. Run the migration script to copy your agents into the registry:"
echo -e "   ${YELLOW}cd $INSTALL_DIR && bun bin/init.js${NC}"
echo -e "   ${YELLOW}(use --move if you explicitly want destructive migration)${NC}"
echo ""
echo "2. After migration, Claude Code will use lazy loading for agents"
echo ""
echo "3. Verify with:"
echo -e "   ${YELLOW}cd $INSTALL_DIR && bun bin/list.js${NC}"
echo ""
echo -e "${GREEN}Installation complete!${NC}"
