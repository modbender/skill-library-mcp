#!/bin/bash
# Check for missing skill dependencies

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Skill locations
BUILTIN_SKILLS="/usr/lib/node_modules/openclaw/skills"
USER_SKILLS="$HOME/.openclaw/workspace/skills"
LOCAL_SKILLS="./skills"

# Collect all skill names
declare -A ALL_SKILLS
declare -A MISSING_DEPS

# Find all skills
for skills_dir in "$BUILTIN_SKILLS" "$USER_SKILLS" "$LOCAL_SKILLS"; do
    if [[ -d "$skills_dir" ]]; then
        for skill in "$skills_dir"/*/; do
            if [[ -d "$skill" && -f "$skill/SKILL.md" ]]; then
                name=$(basename "$skill")
                ALL_SKILLS[$name]=1
            fi
        done
    fi
done

# Check each skill's dependencies
check_skill() {
    local skill_dir="$1"
    local skill_name=$(basename "$skill_dir")
    local skill_md="$skill_dir/SKILL.md"
    
    if [[ ! -f "$skill_md" ]]; then
        return
    fi
    
    # Extract depends from frontmatter
    local deps=$(sed -n '/^---$/,/^---$/p' "$skill_md" 2>/dev/null | \
        awk '/^depends:$/,/^[a-z]/' | grep "^  - " | sed 's/^  - //' | tr -d '"')
    
    local missing=""
    while IFS= read -r dep; do
        if [[ -n "$dep" && -z "${ALL_SKILLS[$dep]}" ]]; then
            missing="$missing $dep"
        fi
    done <<< "$deps"
    
    if [[ -n "$missing" ]]; then
        MISSING_DEPS[$skill_name]="$missing"
    fi
}

# Main
echo -e "\n${GREEN}🔍 Checking Skill Dependencies${NC}\n"

echo -e "${CYAN}📊 Found ${#ALL_SKILLS[@]} installed skills${NC}\n"

# Check all skills
for skills_dir in "$BUILTIN_SKILLS" "$USER_SKILLS" "$LOCAL_SKILLS"; do
    if [[ -d "$skills_dir" ]]; then
        for skill in "$skills_dir"/*/; do
            if [[ -d "$skill" ]]; then
                check_skill "$skill"
            fi
        done
    fi
done

# Report
if [[ ${#MISSING_DEPS[@]} -eq 0 ]]; then
    echo -e "${GREEN}✅ All dependencies satisfied!${NC}\n"
else
    echo -e "${RED}❌ Skills with missing dependencies:${NC}\n"
    for skill in "${!MISSING_DEPS[@]}"; do
        echo -e "${YELLOW}$skill${NC}"
        echo -e "   Missing:${MISSING_DEPS[$skill]}"
        echo ""
    done
fi
