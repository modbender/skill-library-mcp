#!/bin/bash
# Install skill from ClawHub with dependency resolution

set -e

SKILL_SPEC="${1:-}"

if [[ -z "$SKILL_SPEC" ]]; then
    echo "Usage: skill-install.sh <skill-name>[@version]"
    echo "Example: skill-install.sh weather"
    echo "Example: skill-install.sh weather@1.2.0"
    exit 1
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Parse skill@version
SKILL_NAME="${SKILL_SPEC%%@*}"
SKILL_VERSION="${SKILL_SPEC#*@}"
[[ "$SKILL_VERSION" == "$SKILL_NAME" ]] && SKILL_VERSION="latest"

# Skill locations
USER_SKILLS="$HOME/.openclaw/workspace/skills"
CLAWHUB_API="https://clawhub.com/api"

# Check if clawhub CLI is available
if ! command -v clawhub &> /dev/null; then
    # Try openclaw skill command
    if command -v openclaw &> /dev/null; then
        USE_OPENCLAW=1
    else
        echo -e "${YELLOW}⚠️  ClawHub CLI not found. Using direct download...${NC}"
        USE_DIRECT=1
    fi
fi

echo -e "\n${GREEN}📦 Installing $SKILL_NAME${NC}"
[[ "$SKILL_VERSION" != "latest" ]] && echo -e "   Version: $SKILL_VERSION"
echo ""

# Function to get skill metadata from ClawHub
get_skill_info() {
    local name="$1"
    # Try ClawHub API
    curl -s "$CLAWHUB_API/skills/$name" 2>/dev/null || echo "{}"
}

# Function to extract dependencies from skill info
get_dependencies() {
    local info="$1"
    echo "$info" | jq -r '.depends // {} | to_entries[] | "\(.key)@\(.value)"' 2>/dev/null
}

# Function to check if skill is installed
is_installed() {
    local name="$1"
    [[ -d "$USER_SKILLS/$name" ]] || [[ -d "/usr/lib/node_modules/openclaw/skills/$name" ]]
}

# Resolve dependencies recursively
declare -A TO_INSTALL
declare -A RESOLVED

resolve_deps() {
    local name="$1"
    local version="$2"
    
    [[ -n "${RESOLVED[$name]}" ]] && return
    RESOLVED[$name]=1
    
    echo -e "   ${CYAN}├── Resolving $name...${NC}"
    
    local info=$(get_skill_info "$name")
    local deps=$(get_dependencies "$info")
    
    TO_INSTALL[$name]="$version"
    
    while IFS= read -r dep; do
        if [[ -n "$dep" ]]; then
            local dep_name="${dep%%@*}"
            local dep_version="${dep#*@}"
            
            if ! is_installed "$dep_name"; then
                resolve_deps "$dep_name" "$dep_version"
            else
                echo -e "   ${GREEN}│   └── $dep_name (already installed)${NC}"
            fi
        fi
    done <<< "$deps"
}

echo -e "${BLUE}🔍 Resolving dependencies...${NC}"
resolve_deps "$SKILL_NAME" "$SKILL_VERSION"

# Check for conflicts
echo -e "\n${BLUE}🔍 Checking conflicts...${NC}"
CONFLICTS_FOUND=0

for skill in "${!TO_INSTALL[@]}"; do
    local info=$(get_skill_info "$skill")
    local conflicts=$(echo "$info" | jq -r '.conflicts // [] | .[]' 2>/dev/null)
    
    while IFS= read -r conflict; do
        if [[ -n "$conflict" ]] && is_installed "$conflict"; then
            echo -e "   ${RED}❌ $skill conflicts with $conflict (installed)${NC}"
            CONFLICTS_FOUND=1
        fi
    done <<< "$conflicts"
done

if [[ $CONFLICTS_FOUND -eq 1 ]]; then
    echo -e "\n${RED}Cannot install due to conflicts. Remove conflicting skills first.${NC}\n"
    exit 1
fi
echo -e "   ${GREEN}└── No conflicts found ✅${NC}"

# Install skills
echo -e "\n${BLUE}📥 Installing ${#TO_INSTALL[@]} skill(s)...${NC}"

for skill in "${!TO_INSTALL[@]}"; do
    version="${TO_INSTALL[$skill]}"
    
    if [[ -n "$USE_OPENCLAW" ]]; then
        openclaw skill install "$skill" --yes 2>/dev/null && \
            echo -e "   ${GREEN}✅ $skill${NC}" || \
            echo -e "   ${YELLOW}⚠️  $skill (may need manual install)${NC}"
    elif command -v clawhub &> /dev/null; then
        clawhub install "$skill" 2>/dev/null && \
            echo -e "   ${GREEN}✅ $skill${NC}" || \
            echo -e "   ${YELLOW}⚠️  $skill (may need manual install)${NC}"
    else
        # Direct install attempt
        echo -e "   ${YELLOW}⚠️  $skill (manual install required)${NC}"
        echo -e "      Run: openclaw skill install $skill"
    fi
done

echo -e "\n${GREEN}✅ Done!${NC}\n"
