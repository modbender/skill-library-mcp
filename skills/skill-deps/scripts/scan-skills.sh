#!/bin/bash
# Scan OpenClaw skills and extract dependency information

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Skill locations
BUILTIN_SKILLS="/usr/lib/node_modules/openclaw/skills"
USER_SKILLS="$HOME/.openclaw/workspace/skills"
LOCAL_SKILLS="./skills"

FILTER_SKILL="${1:-}"

# Extract frontmatter from SKILL.md
extract_frontmatter() {
    local file="$1"
    sed -n '/^---$/,/^---$/p' "$file" 2>/dev/null | sed '1d;$d'
}

# Get field from YAML frontmatter
get_yaml_field() {
    local yaml="$1"
    local field="$2"
    echo "$yaml" | grep "^$field:" | sed "s/^$field: *//" | tr -d '"'
}

# Get list field from YAML (handles both inline and multi-line)
get_yaml_list() {
    local yaml="$1"
    local field="$2"
    
    # Try inline format: depends: [a, b, c]
    local inline=$(echo "$yaml" | grep "^$field:" | sed "s/^$field: *\[//" | sed "s/\]//" | tr ',' '\n' | tr -d ' "')
    if [[ -n "$inline" ]]; then
        echo "$inline"
        return
    fi
    
    # Try multi-line format
    echo "$yaml" | awk "/^$field:$/,/^[a-z]/" | grep "^  - " | sed 's/^  - //' | tr -d '"'
}

# Scan a skill directory
scan_skill() {
    local skill_dir="$1"
    local skill_name=$(basename "$skill_dir")
    local skill_md="$skill_dir/SKILL.md"
    local skill_json="$skill_dir/skill.json"
    
    if [[ -n "$FILTER_SKILL" && "$skill_name" != "$FILTER_SKILL" ]]; then
        return
    fi
    
    if [[ ! -f "$skill_md" ]]; then
        return
    fi
    
    echo -e "${CYAN}📦 $skill_name${NC}"
    
    # Get frontmatter
    local fm=$(extract_frontmatter "$skill_md")
    local desc=$(get_yaml_field "$fm" "description")
    
    # Truncate description
    if [[ ${#desc} -gt 60 ]]; then
        desc="${desc:0:57}..."
    fi
    echo -e "   ${BLUE}$desc${NC}"
    
    # Check for dependencies in frontmatter
    local depends=$(get_yaml_list "$fm" "depends")
    local optional=$(get_yaml_list "$fm" "optional")
    
    # Also check skill.json if exists
    if [[ -f "$skill_json" ]]; then
        local json_deps=$(jq -r '.depends // {} | keys[]' "$skill_json" 2>/dev/null)
        local json_opt=$(jq -r '.optional // {} | keys[]' "$skill_json" 2>/dev/null)
        depends="$depends"$'\n'"$json_deps"
        optional="$optional"$'\n'"$json_opt"
    fi
    
    # Clean and dedupe
    depends=$(echo "$depends" | sort -u | grep -v '^$' || true)
    optional=$(echo "$optional" | sort -u | grep -v '^$' || true)
    
    if [[ -n "$depends" ]]; then
        echo -e "   ${GREEN}Depends:${NC}"
        echo "$depends" | while read -r dep; do
            [[ -n "$dep" ]] && echo -e "      └── $dep"
        done
    fi
    
    if [[ -n "$optional" ]]; then
        echo -e "   ${YELLOW}Optional:${NC}"
        echo "$optional" | while read -r opt; do
            [[ -n "$opt" ]] && echo -e "      └── $opt"
        done
    fi
    
    if [[ -z "$depends" && -z "$optional" ]]; then
        echo -e "   ${GREEN}No dependencies${NC}"
    fi
    
    echo ""
}

# Main
echo -e "\n${GREEN}🔍 Scanning OpenClaw Skills${NC}\n"

# Scan all skill directories
for skills_dir in "$BUILTIN_SKILLS" "$USER_SKILLS" "$LOCAL_SKILLS"; do
    if [[ -d "$skills_dir" ]]; then
        if [[ -z "$FILTER_SKILL" ]]; then
            echo -e "${YELLOW}📁 $skills_dir${NC}\n"
        fi
        
        for skill in "$skills_dir"/*/; do
            if [[ -d "$skill" ]]; then
                scan_skill "$skill"
            fi
        done
    fi
done

echo -e "${GREEN}✅ Scan complete${NC}\n"
