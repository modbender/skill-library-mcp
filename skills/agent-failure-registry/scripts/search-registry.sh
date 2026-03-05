#!/bin/bash

# search-registry.sh - Search the Agent Failure Registry
# Usage: ./search-registry.sh [--category CATEGORY] [--tag TAG] [--keyword KEYWORD] [--all]

set -e

REPO_URL="https://github.com/unleashedbelial/agent-failure-registry"
REPO_DIR="/tmp/agent-failure-registry"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Arguments
CATEGORIES=()
TAGS=()
KEYWORDS=()
SHOW_ALL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --category)
            CATEGORIES+=("$2")
            shift 2
            ;;
        --tag)
            TAGS+=("$2")
            shift 2
            ;;
        --keyword)
            KEYWORDS+=("$2")
            shift 2
            ;;
        --all)
            SHOW_ALL=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--category CATEGORY] [--tag TAG] [--keyword KEYWORD] [--all]"
            echo ""
            echo "Search the Agent Failure Registry for documented failures and solutions."
            echo ""
            echo "Options:"
            echo "  --category CATEGORY  Search by failure category"
            echo "  --tag TAG           Search by tag (repeatable)"
            echo "  --keyword KEYWORD   Free-text search (repeatable)"
            echo "  --all               Show all entries"
            echo "  -h, --help          Show this help"
            echo ""
            echo "Examples:"
            echo "  $0 --category api_failure"
            echo "  $0 --tag twitter --keyword puppeteer"
            echo "  $0 --all"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Use --help for usage information." >&2
            exit 1
            ;;
    esac
done

# Function to clone or update repository
setup_repo() {
    echo -e "${BLUE}Setting up Agent Failure Registry...${NC}"
    
    if [ -d "$REPO_DIR" ]; then
        echo "Repository exists, pulling latest changes..."
        cd "$REPO_DIR"
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || echo "Pull failed, using existing repo"
    else
        echo "Cloning repository..."
        git clone "$REPO_URL" "$REPO_DIR"
        cd "$REPO_DIR"
    fi
    
    echo -e "${GREEN}Repository ready at $REPO_DIR${NC}"
}

# Function to check if PyYAML is available
has_pyyaml() {
    python3 -c "import yaml" 2>/dev/null
}

# Function to search using Python + PyYAML
search_with_python() {
    local search_dirs="$1"
    
    python3 << EOF
import os
import yaml
import sys
import re
from pathlib import Path

def load_yaml_safe(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        return None

def matches_criteria(data, categories, tags, keywords):
    if not data:
        return False
    
    # Check categories
    if categories and data.get('category') not in categories:
        return False
    
    # Check tags
    if tags:
        entry_tags = data.get('tags', [])
        if not any(tag in entry_tags for tag in tags):
            return False
    
    # Check keywords (search in all text fields)
    if keywords:
        search_text = ' '.join([
            str(data.get('title', '')),
            str(data.get('summary', '')),
            str(data.get('root_cause', '')),
            str(data.get('fix', '')),
            str(data.get('lessons', '')),
            str(data.get('prevention', ''))
        ]).lower()
        
        if not any(keyword.lower() in search_text for keyword in keywords):
            return False
    
    return True

def format_entry(data, file_path):
    if not data:
        return ""
    
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"📋 {data.get('title', 'Untitled')}")
    output.append(f"📁 Category: {data.get('category', 'unknown')}")
    output.append(f"🏷️  Tags: {', '.join(data.get('tags', []))}")
    output.append(f"📄 Source: {file_path}")
    output.append(f"{'='*60}")
    
    if data.get('summary'):
        output.append(f"\n💡 SUMMARY:")
        output.append(f"{data['summary']}")
    
    if data.get('root_cause'):
        output.append(f"\n🔍 ROOT CAUSE:")
        output.append(f"{data['root_cause']}")
    
    if data.get('fix'):
        output.append(f"\n✅ FIX:")
        output.append(f"{data['fix']}")
    
    if data.get('prevention'):
        output.append(f"\n🛡️  PREVENTION:")
        output.append(f"{data['prevention']}")
    
    if data.get('lessons'):
        output.append(f"\n📚 LESSONS LEARNED:")
        output.append(f"{data['lessons']}")
    
    confidence = data.get('confidence', 'unknown')
    output.append(f"\n🎯 Confidence: {confidence}/5")
    
    return '\n'.join(output)

# Parse arguments from environment
categories = []
tags = []
keywords = []

if 'SEARCH_CATEGORIES' in os.environ:
    categories = os.environ['SEARCH_CATEGORIES'].split('|') if os.environ['SEARCH_CATEGORIES'] else []

if 'SEARCH_TAGS' in os.environ:
    tags = os.environ['SEARCH_TAGS'].split('|') if os.environ['SEARCH_TAGS'] else []

if 'SEARCH_KEYWORDS' in os.environ:
    keywords = os.environ['SEARCH_KEYWORDS'].split('|') if os.environ['SEARCH_KEYWORDS'] else []

show_all = os.environ.get('SEARCH_ALL', 'false') == 'true'

# Search through YAML files
found_count = 0
search_dirs = os.environ.get('SEARCH_DIRS', '').split(':')

for search_dir in search_dirs:
    if not search_dir or not os.path.exists(search_dir):
        continue
        
    for yaml_file in Path(search_dir).rglob('*.yaml'):
        if yaml_file.name == 'template.yaml':
            continue
            
        data = load_yaml_safe(yaml_file)
        
        if show_all or matches_criteria(data, categories, tags, keywords):
            print(format_entry(data, str(yaml_file.relative_to(os.environ.get('REPO_DIR', '.')))))
            found_count += 1

if found_count == 0:
    print("\n🔍 No matching entries found.")
    print("\nTry:")
    print("  • Broader search terms")
    print("  • Different categories or tags")
    print("  • --all to browse everything")
else:
    print(f"\n✅ Found {found_count} matching entries.")

EOF
}

# Function to search using grep (fallback)
search_with_grep() {
    local search_dirs="$1"
    echo -e "${YELLOW}Using grep-based search (PyYAML not available)${NC}"
    
    local found_files=()
    
    # Collect matching files
    while IFS= read -r -d '' file; do
        if [[ "$(basename "$file")" == "template.yaml" ]]; then
            continue
        fi
        
        local matches=true
        
        # Check categories
        for category in "${CATEGORIES[@]}"; do
            if ! grep -q "category: $category" "$file"; then
                matches=false
                break
            fi
        done
        
        # Check tags
        for tag in "${TAGS[@]}"; do
            if ! grep -q "- $tag" "$file"; then
                matches=false
                break
            fi
        done
        
        # Check keywords
        for keyword in "${KEYWORDS[@]}"; do
            if ! grep -iq "$keyword" "$file"; then
                matches=false
                break
            fi
        done
        
        if [ "$matches" = true ] || [ "$SHOW_ALL" = true ]; then
            found_files+=("$file")
        fi
        
    done < <(find $search_dirs -name "*.yaml" -print0 2>/dev/null)
    
    # Display results
    if [ ${#found_files[@]} -eq 0 ]; then
        echo -e "\n🔍 No matching entries found."
        return
    fi
    
    for file in "${found_files[@]}"; do
        echo -e "\n${'='*60}"
        echo -e "${BOLD}📄 $(basename "$file")${NC}"
        echo -e "📁 Source: ${file#$REPO_DIR/}"
        echo -e "${'='*60}"
        
        # Extract and display key fields
        echo -e "\n${BOLD}Content:${NC}"
        grep -E "^(title|category|summary|root_cause|fix|prevention|lessons|confidence):" "$file" 2>/dev/null | head -20
    done
    
    echo -e "\n✅ Found ${#found_files[@]} matching entries."
}

# Main execution
main() {
    echo -e "${BOLD}🔍 Agent Failure Registry Search${NC}"
    
    # Setup repository
    setup_repo
    
    # Prepare search directories
    local search_dirs="$REPO_DIR/examples:$REPO_DIR/submissions"
    
    # Show search criteria
    if [ "$SHOW_ALL" = true ]; then
        echo -e "${BLUE}📋 Showing all entries${NC}"
    else
        echo -e "${BLUE}📋 Search criteria:${NC}"
        [ ${#CATEGORIES[@]} -gt 0 ] && echo "   Categories: ${CATEGORIES[*]}"
        [ ${#TAGS[@]} -gt 0 ] && echo "   Tags: ${TAGS[*]}"
        [ ${#KEYWORDS[@]} -gt 0 ] && echo "   Keywords: ${KEYWORDS[*]}"
    fi
    
    echo ""
    
    # Execute search
    if has_pyyaml; then
        echo -e "${GREEN}Using Python + PyYAML for search${NC}"
        
        # Export search criteria as environment variables for Python script
        export SEARCH_CATEGORIES=$(IFS='|'; echo "${CATEGORIES[*]}")
        export SEARCH_TAGS=$(IFS='|'; echo "${TAGS[*]}")
        export SEARCH_KEYWORDS=$(IFS='|'; echo "${KEYWORDS[*]}")
        export SEARCH_ALL=$([ "$SHOW_ALL" = true ] && echo "true" || echo "false")
        export SEARCH_DIRS="$search_dirs"
        export REPO_DIR="$REPO_DIR"
        
        search_with_python "$search_dirs"
    else
        search_with_grep "$search_dirs"
    fi
}

# Run main function
main "$@"