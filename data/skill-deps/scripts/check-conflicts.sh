#!/bin/bash
# Check for conflicting skills

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

# Collect all installed skills
declare -A ALL_SKILLS
declare -A SKILL_CONFLICTS

echo -e "\n${GREEN}🔍 Checking for Skill Conflicts${NC}\n"

# Find all skills
for skills_dir in "$BUILTIN_SKILLS" "$USER_SKILLS" "$LOCAL_SKILLS"; do
    if [[ -d "$skills_dir" ]]; then
        for skill in "$skills_dir"/*/; do
            if [[ -d "$skill" && -f "$skill/SKILL.md" ]]; then
                name=$(basename "$skill")
                ALL_SKILLS[$name]="$skill"
            fi
        done
    fi
done

echo -e "${CYAN}📊 Scanning ${#ALL_SKILLS[@]} installed skills...${NC}\n"

# Extract conflicts from each skill
get_conflicts() {
    local skill_md="$1"
    sed -n '/^---$/,/^---$/p' "$skill_md" 2>/dev/null | \
        awk '/^conflicts:$/,/^[a-z]/' | grep "^  - " | sed 's/^  - //' | tr -d '"'
}

# Check each skill for conflicts
CONFLICT_COUNT=0

for skill_name in "${!ALL_SKILLS[@]}"; do
    skill_dir="${ALL_SKILLS[$skill_name]}"
    skill_md="$skill_dir/SKILL.md"
    
    conflicts=$(get_conflicts "$skill_md")
    
    while IFS= read -r conflict; do
        if [[ -n "$conflict" && -n "${ALL_SKILLS[$conflict]}" ]]; then
            echo -e "${RED}❌ Conflict detected!${NC}"
            echo -e "   ${YELLOW}$skill_name${NC} conflicts with ${YELLOW}$conflict${NC}"
            echo -e "   Both are installed - this may cause issues.\n"
            CONFLICT_COUNT=$((CONFLICT_COUNT + 1))
        fi
    done <<< "$conflicts"
done

if [[ $CONFLICT_COUNT -eq 0 ]]; then
    echo -e "${GREEN}✅ No conflicts found!${NC}\n"
else
    echo -e "${RED}Found $CONFLICT_COUNT conflict(s).${NC}"
    echo -e "Consider removing one of the conflicting skills.\n"
fi
