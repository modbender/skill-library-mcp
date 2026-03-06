#!/bin/bash
# Search for skills on ClawHub

set -e

QUERY="${1:-}"

if [[ -z "$QUERY" ]]; then
    echo "Usage: skill-search.sh <query>"
    echo "Example: skill-search.sh weather"
    exit 1
fi

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "\n${GREEN}🔍 Searching ClawHub for '$QUERY'...${NC}\n"

# Check if clawhub CLI is available
if command -v clawhub &> /dev/null; then
    clawhub search "$QUERY"
elif command -v openclaw &> /dev/null; then
    openclaw skill search "$QUERY" 2>/dev/null || {
        echo -e "${YELLOW}⚠️  Could not search ClawHub.${NC}"
        echo -e "Try: https://clawhub.com/search?q=$QUERY"
    }
else
    echo -e "${YELLOW}⚠️  ClawHub CLI not available.${NC}"
    echo -e "Search online: ${CYAN}https://clawhub.com/search?q=$QUERY${NC}"
    echo ""
    
    # Also search locally installed skills
    echo -e "${BLUE}📁 Searching locally installed skills...${NC}\n"
    
    for skills_dir in "/usr/lib/node_modules/openclaw/skills" "$HOME/.openclaw/workspace/skills"; do
        if [[ -d "$skills_dir" ]]; then
            for skill in "$skills_dir"/*/; do
                if [[ -d "$skill" ]]; then
                    name=$(basename "$skill")
                    if [[ "$name" == *"$QUERY"* ]]; then
                        desc=""
                        if [[ -f "$skill/SKILL.md" ]]; then
                            desc=$(sed -n '/^description:/p' "$skill/SKILL.md" | head -1 | sed 's/description: *//' | cut -c1-60)
                        fi
                        echo -e "${CYAN}📦 $name${NC}"
                        [[ -n "$desc" ]] && echo -e "   $desc"
                        echo ""
                    fi
                fi
            done
        fi
    done
fi
