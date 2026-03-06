#!/bin/bash
# Display dependency tree for a skill

set -e

SKILL_NAME="${1:-}"

if [[ -z "$SKILL_NAME" ]]; then
    echo "Usage: skill-tree.sh <skill-name>"
    echo "Example: skill-tree.sh weather"
    exit 1
fi

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Skill locations
BUILTIN_SKILLS="/usr/lib/node_modules/openclaw/skills"
USER_SKILLS="$HOME/.openclaw/workspace/skills"
LOCAL_SKILLS="./skills"

# Track visited to prevent infinite loops
declare -A VISITED

# Find skill directory
find_skill() {
    local name="$1"
    for dir in "$BUILTIN_SKILLS" "$USER_SKILLS" "$LOCAL_SKILLS"; do
        if [[ -d "$dir/$name" ]]; then
            echo "$dir/$name"
            return
        fi
    done
}

# Extract dependencies from skill
get_deps() {
    local skill_dir="$1"
    local skill_md="$skill_dir/SKILL.md"
    
    if [[ ! -f "$skill_md" ]]; then
        return
    fi
    
    # Extract frontmatter and get depends field
    sed -n '/^---$/,/^---$/p' "$skill_md" 2>/dev/null | \
        awk '/^depends:$/,/^[a-z]/' | grep "^  - " | sed 's/^  - //' | tr -d '"'
}

# Get optional dependencies
get_optional() {
    local skill_dir="$1"
    local skill_md="$skill_dir/SKILL.md"
    
    if [[ ! -f "$skill_md" ]]; then
        return
    fi
    
    sed -n '/^---$/,/^---$/p' "$skill_md" 2>/dev/null | \
        awk '/^optional:$/,/^[a-z]/' | grep "^  - " | sed 's/^  - //' | tr -d '"'
}

# Print tree recursively
print_tree() {
    local name="$1"
    local prefix="$2"
    local is_last="$3"
    local dep_type="${4:-required}"
    
    # Check for circular dependency
    if [[ -n "${VISITED[$name]}" ]]; then
        echo -e "${prefix}${YELLOW}⚠️  $name (circular!)${NC}"
        return
    fi
    VISITED[$name]=1
    
    local skill_dir=$(find_skill "$name")
    local status=""
    
    if [[ -z "$skill_dir" ]]; then
        status="${YELLOW}(missing!)${NC}"
    fi
    
    local type_indicator=""
    if [[ "$dep_type" == "optional" ]]; then
        type_indicator=" ${CYAN}(optional)${NC}"
    fi
    
    if [[ "$prefix" == "" ]]; then
        echo -e "${GREEN}$name${NC}$type_indicator $status"
    else
        local branch="├──"
        [[ "$is_last" == "true" ]] && branch="└──"
        echo -e "${prefix}${branch} $name$type_indicator $status"
    fi
    
    if [[ -n "$skill_dir" ]]; then
        local deps=$(get_deps "$skill_dir")
        local opts=$(get_optional "$skill_dir")
        
        local all_deps=()
        while IFS= read -r dep; do
            [[ -n "$dep" ]] && all_deps+=("$dep:required")
        done <<< "$deps"
        
        while IFS= read -r opt; do
            [[ -n "$opt" ]] && all_deps+=("$opt:optional")
        done <<< "$opts"
        
        local count=${#all_deps[@]}
        local i=0
        
        for item in "${all_deps[@]}"; do
            local dep_name="${item%%:*}"
            local dep_type="${item##*:}"
            i=$((i + 1))
            
            local new_prefix="$prefix"
            if [[ "$prefix" == "" ]]; then
                new_prefix=""
            elif [[ "$is_last" == "true" ]]; then
                new_prefix="${prefix}    "
            else
                new_prefix="${prefix}│   "
            fi
            
            local last="false"
            [[ $i -eq $count ]] && last="true"
            
            print_tree "$dep_name" "$new_prefix" "$last" "$dep_type"
        done
    fi
}

# Main
echo -e "\n${GREEN}🌳 Skill Dependency Tree: $SKILL_NAME${NC}\n"

print_tree "$SKILL_NAME" "" "true" "required"

echo ""
