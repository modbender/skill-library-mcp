#!/bin/bash
# Memory Health Check Script
# Validates memory integrity and repairs issues

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/config.json"

# Default values
MEMORY_PATH="./memory"
AUTO_FIX=false

# Load config if exists
if [[ -f "$CONFIG_FILE" ]]; then
    MEMORY_PATH=$(jq -r '.memory.base_path // "./memory"' "$CONFIG_FILE")
    AUTO_FIX=$(jq -r '.health_check.auto_fix // false' "$CONFIG_FILE")
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0
FIXED=0

# Functions
log_error() {
    echo -e "${RED}❌ ERROR:${NC} $1"
    ((ERRORS++))
}

log_warning() {
    echo -e "${YELLOW}⚠️  WARNING:${NC} $1"
    ((WARNINGS++))
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_info() {
    echo "ℹ️  $1"
}

check_directory_structure() {
    log_info "Checking directory structure..."
    
    local required_dirs=("semantic" "episodic" "procedural" "working" "index")
    
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$MEMORY_PATH/$dir" ]]; then
            if [[ "$AUTO_FIX" == true ]]; then
                mkdir -p "$MEMORY_PATH/$dir"
                log_success "Created missing directory: $dir"
                ((FIXED++))
            else
                log_error "Missing directory: $dir"
            fi
        fi
    done
    
    if [[ $ERRORS -eq 0 ]] && [[ $FIXED -eq 0 ]]; then
        log_success "Directory structure is valid"
    fi
}

check_version() {
    log_info "Checking version..."
    
    if [[ ! -f "$MEMORY_PATH/.version" ]]; then
        if [[ "$AUTO_FIX" == true ]]; then
            echo "1.0.0" > "$MEMORY_PATH/.version"
            log_success "Created version file"
            ((FIXED++))
        else
            log_warning "Missing version file"
        fi
    else
        local version=$(cat "$MEMORY_PATH/.version")
        log_success "Version: $version"
    fi
}

check_orphaned_files() {
    log_info "Checking for orphaned files..."
    
    # Check for files not referenced in index
    local found_orphaned=false
    
    # This is a simplified check - in production, you'd compare against index
    for file in "$MEMORY_PATH"/episodic/*.md; do
        if [[ -f "$file" ]]; then
            local filename=$(basename "$file")
            if [[ "$filename" != "*.md" ]] && [[ ! "$filename" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$ ]]; then
                log_warning "Potentially orphaned file: $filename"
                found_orphaned=true
            fi
        fi
    done
    
    if [[ "$found_orphaned" == false ]]; then
        log_success "No orphaned files detected"
    fi
}

check_index_integrity() {
    log_info "Checking index integrity..."
    
    local index_files=("tags.json" "timeline.json")
    
    for file in "${index_files[@]}"; do
        local filepath="$MEMORY_PATH/index/$file"
        if [[ ! -f "$filepath" ]]; then
            if [[ "$AUTO_FIX" == true ]]; then
                echo '{"tags": [], "last_updated": ""}' > "$filepath"
                log_success "Created missing index file: $file"
                ((FIXED++))
            else
                log_error "Missing index file: $file"
            fi
        else
            # Validate JSON
            if ! jq empty "$filepath" 2>/dev/null; then
                log_error "Invalid JSON in: $file"
            fi
        fi
    done
}

check_file_permissions() {
    log_info "Checking file permissions..."
    
    local unreadable=0
    while IFS= read -r -d '' file; do
        if [[ ! -r "$file" ]]; then
            log_error "Unreadable file: $file"
            ((unreadable++))
        fi
    done < <(find "$MEMORY_PATH" -type f -print0 2>/dev/null)
    
    if [[ $unreadable -eq 0 ]]; then
        log_success "All files are readable"
    fi
}

generate_report() {
    echo ""
    echo "========================================"
    echo "         HEALTH CHECK REPORT"
    echo "========================================"
    echo "Memory Path: $MEMORY_PATH"
    echo "Timestamp: $(date -Iseconds)"
    echo "----------------------------------------"
    echo "Errors:   $ERRORS"
    echo "Warnings: $WARNINGS"
    echo "Fixed:    $FIXED"
    echo "----------------------------------------"
    
    if [[ $ERRORS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
        echo -e "${GREEN}✅ Memory system is healthy!${NC}"
        return 0
    elif [[ $ERRORS -eq 0 ]]; then
        echo -e "${YELLOW}⚠️  Memory system has warnings${NC}"
        return 0
    else
        echo -e "${RED}❌ Memory system has errors${NC}"
        return 1
    fi
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            AUTO_FIX=true
            shift
            ;;
        --path)
            MEMORY_PATH="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🔍 Memory Health Check"
echo "======================"
echo ""

# Run checks
check_directory_structure
check_version
check_orphaned_files
check_index_integrity
check_file_permissions

# Generate report
generate_report
