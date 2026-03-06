#!/bin/bash
# Memory Compression System - Status Script
# Version: 3.0.0

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="$SKILL_DIR/config/default.conf"
DATA_DIR="$SKILL_DIR/data"
COMPRESSED_DIR="$DATA_DIR/compressed"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Load configuration
[ -f "$CONFIG_FILE" ] && source "$CONFIG_FILE" 2>/dev/null

# Default values
DETAILED=false
JSON_OUTPUT=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --detailed|-d)
            DETAILED=true
            shift
            ;;
        --json|-j)
            JSON_OUTPUT=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -d, --detailed    Detailed status information"
            echo "  -j, --json        JSON output format"
            echo "  -h, --help        Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Get status emoji
get_status_emoji() {
    local status="$1"
    case "$status" in
        "healthy") echo "✅" ;;
        "warning") echo "⚠️" ;;
        "error") echo "❌" ;;
        *) echo "🔵" ;;
    esac
}

# Check if skill is installed
check_installation() {
    if [ ! -f "$SKILL_DIR/.installed" ]; then
        echo "Not installed"
        return 1
    fi
    
    local installed_date=$(grep "Installed:" "$SKILL_DIR/.installed" | cut -d: -f2- | xargs)
    echo "$installed_date"
    return 0
}

# Check compression status
check_compression_status() {
    local last_compression_file="$DATA_DIR/last-compression.txt"
    
    if [ ! -f "$last_compression_file" ]; then
        echo "Never"
        return 1
    fi
    
    local last_compression=$(cat "$last_compression_file" 2>/dev/null || echo "Unknown")
    local now=$(date -u +%s)
    local last_timestamp=$(date -u -d "$last_compression" +%s 2>/dev/null || echo 0)
    
    if [ "$last_timestamp" -eq 0 ]; then
        echo "Unknown"
        return 1
    fi
    
    local diff_seconds=$((now - last_timestamp))
    
    if [ "$diff_seconds" -lt 3600 ]; then
        echo "<1 hour ago"
    elif [ "$diff_seconds" -lt 86400 ]; then
        echo "$((diff_seconds / 3600)) hours ago"
    else
        echo "$((diff_seconds / 86400)) days ago"
    fi
    
    return 0
}

# Get compression statistics
get_compression_stats() {
    local stats=()
    
    # Count compressed files by format
    if [ -d "$COMPRESSED_DIR" ]; then
        local base64_count=$(find "$COMPRESSED_DIR" -name "*.base64" -o -name "*.b64c" | wc -l)
        local binary_count=$(find "$COMPRESSED_DIR" -name "*.binary" -o -name "*.cbin" | wc -l)
        local ultra_count=$(find "$COMPRESSED_DIR" -name "*.ultra" -o -name "*.ucmp" | wc -l)
        local total_count=$((base64_count + binary_count + ultra_count))
        
        stats+=("total:$total_count")
        stats+=("base64:$base64_count")
        stats+=("binary:$binary_count")
        stats+=("ultra:$ultra_count")
        
        # Calculate total size
        local total_size=$(find "$COMPRESSED_DIR" -type f -exec stat -c %s {} \; 2>/dev/null | awk '{sum+=$1} END {print sum}')
        if [ -n "$total_size" ]; then
            if [ "$total_size" -lt 1024 ]; then
                stats+=("size:${total_size}B")
            elif [ "$total_size" -lt 1048576 ]; then
                stats+=("size:$((total_size / 1024))KB")
            else
                stats+=("size:$((total_size / 1048576))MB")
            fi
        fi
    else
        stats+=("total:0")
        stats+=("size:0B")
    fi
    
    echo "${stats[@]}"
}

# Check cron job status
check_cron_status() {
    if command -v openclaw &> /dev/null; then
        # Check if cron job exists via OpenClaw
        local cron_output=$(openclaw cron list --json 2>/dev/null | grep -i "memory.compression" || true)
        if [ -n "$cron_output" ]; then
            echo "active"
            return 0
        fi
    fi
    
    # Check system crontab
    if crontab -l 2>/dev/null | grep -q "memory-compression-system"; then
        echo "active"
        return 0
    fi
    
    echo "inactive"
    return 1
}

# Check system health
check_system_health() {
    local issues=0
    local warnings=0
    
    # Check disk space
    local disk_usage=$(df "$SKILL_DIR" | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        ((issues++))
    elif [ "$disk_usage" -gt 75 ]; then
        ((warnings++))
    fi
    
    # Check if directories exist
    if [ ! -d "$COMPRESSED_DIR" ]; then
        ((warnings++))
    fi
    
    # Check if scripts are executable
    for script in "$SCRIPT_DIR"/*.sh; do
        if [ -f "$script" ] && [ ! -x "$script" ]; then
            ((warnings++))
        fi
    done
    
    if [ "$issues" -gt 0 ]; then
        echo "error"
    elif [ "$warnings" -gt 0 ]; then
        echo "warning"
    else
        echo "healthy"
    fi
}

# Generate JSON output
generate_json_output() {
    local installed=$(check_installation)
    local last_compression=$(check_compression_status)
    local cron_status=$(check_cron_status)
    local health=$(check_system_health)
    
    # Parse compression stats
    local stats=$(get_compression_stats)
    declare -A stat_map
    for stat in $stats; do
        key="${stat%%:*}"
        value="${stat#*:}"
        stat_map["$key"]="$value"
    done
    
    cat << EOF
{
  "skill": {
    "name": "memory-compression-system",
    "version": "3.0.0",
    "installed": "$installed",
    "health": "$health"
  },
  "compression": {
    "last_run": "$last_compression",
    "total_files": "${stat_map[total]:-0}",
    "formats": {
      "base64": "${stat_map[base64]:-0}",
      "binary": "${stat_map[binary]:-0}",
      "ultra": "${stat_map[ultra]:-0}"
    },
    "total_size": "${stat_map[size]:-0B}"
  },
  "automation": {
    "cron_status": "$cron_status",
    "compression_enabled": "${COMPRESSION_ENABLED:-true}",
    "search_enabled": "${SEARCH_ENABLED:-true}"
  },
  "configuration": {
    "default_format": "${DEFAULT_FORMAT:-ultra}",
    "retention_days": "${RETENTION_DAYS:-30}",
    "max_files": "${MAX_COMPRESSED_FILES:-100}"
  },
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
}

# Generate detailed output
generate_detailed_output() {
    local installed=$(check_installation)
    local last_compression=$(check_compression_status)
    local cron_status=$(check_cron_status)
    local health=$(check_system_health)
    local health_emoji=$(get_status_emoji "$health")
    
    echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║    MEMORY COMPRESSION SYSTEM - STATUS REPORT        ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Skill Information
    echo -e "${BLUE}📦 SKILL INFORMATION${NC}"
    echo -e "  Name:    memory-compression-system"
    echo -e "  Version: 3.0.0"
    echo -e "  Installed: $installed"
    echo -e "  Health:   $health_emoji $health"
    echo ""
    
    # Compression Status
    echo -e "${BLUE}📊 COMPRESSION STATUS${NC}"
    echo -e "  Last compression: $last_compression"
    
    local stats=$(get_compression_stats)
    declare -A stat_map
    for stat in $stats; do
        key="${stat%%:*}"
        value="${stat#*:}"
        stat_map["$key"]="$value"
    done
    
    echo -e "  Total files: ${stat_map[total]:-0}"
    echo -e "  Base64 files: ${stat_map[base64]:-0}"
    echo -e "  Binary files: ${stat_map[binary]:-0}"
    echo -e "  Ultra files: ${stat_map[ultra]:-0}"
    echo -e "  Total size: ${stat_map[size]:-0B}"
    echo ""
    
    # Automation Status
    echo -e "${BLUE}⚙️ AUTOMATION STATUS${NC}"
    echo -e "  Cron job: $cron_status"
    echo -e "  Compression: ${COMPRESSION_ENABLED:-true}"
    echo -e "  Search: ${SEARCH_ENABLED:-true}"
    echo ""
    
    # Configuration
    echo -e "${BLUE}⚙️ CONFIGURATION${NC}"
    echo -e "  Default format: ${DEFAULT_FORMAT:-ultra}"
    echo -e "  Retention days: ${RETENTION_DAYS:-30}"
    echo -e "  Max files: ${MAX_COMPRESSED_FILES:-100}"
    echo ""
    
    # Directories
    echo -e "${BLUE}📁 DIRECTORIES${NC}"
    echo -e "  Skill: $SKILL_DIR"
    echo -e "  Data: $DATA_DIR"
    echo -e "  Compressed: $COMPRESSED_DIR"
    echo ""
    
    # Quick Actions
    echo -e "${BLUE}🚀 QUICK ACTIONS${NC}"
    echo -e "  Run compression: ${SCRIPT_DIR}/compress.sh"
    echo -e "  Check health: ${SCRIPT_DIR}/health.sh"
    echo -e "  View logs: ${SCRIPT_DIR}/logs.sh"
    echo ""
    
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo -e "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}

# Generate simple output
generate_simple_output() {
    local installed=$(check_installation)
    local last_compression=$(check_compression_status)
    local cron_status=$(check_cron_status)
    local health=$(check_system_health)
    local health_emoji=$(get_status_emoji "$health")
    
    local stats=$(get_compression_stats)
    declare -A stat_map
    for stat in $stats; do
        key="${stat%%:*}"
        value="${stat#*:}"
        stat_map["$key"]="$value"
    done
    
    echo -e "${health_emoji} Memory Compression System v3.0.0"
    echo -e "  Status: $health"
    echo -e "  Last compression: $last_compression"
    echo -e "  Files: ${stat_map[total]:-0} (${stat_map[size]:-0B})"
    echo -e "  Cron: $cron_status"
    echo -e "  Format: ${DEFAULT_FORMAT:-ultra}"
}

# Main function
main() {
    if [ "$JSON_OUTPUT" = true ]; then
        generate_json_output
    elif [ "$DETAILED" = true ]; then
        generate_detailed_output
    else
        generate_simple_output
    fi
}

# Run main function
main