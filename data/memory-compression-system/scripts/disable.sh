#!/bin/bash
# Memory Compression System - Disable Script
# Version: 3.0.0

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="$SKILL_DIR/config/default.conf"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load configuration
[ -f "$CONFIG_FILE" ] && source "$CONFIG_FILE" 2>/dev/null

echo -e "${BLUE}Disabling Memory Compression System v3.0.0${NC}"
echo ""

# Check if already disabled
check_disabled() {
    if [ ! -f "$SKILL_DIR/.enabled" ]; then
        echo -e "${YELLOW}System is already disabled${NC}"
        return 0
    fi
    return 1
}

# Disable compression in config
disable_compression_config() {
    echo "Disabling compression in configuration..."
    
    if [ -f "$CONFIG_FILE" ]; then
        # Update configuration
        sed -i 's/^COMPRESSION_ENABLED=.*/COMPRESSION_ENABLED=false/' "$CONFIG_FILE"
        sed -i 's/^SEARCH_ENABLED=.*/SEARCH_ENABLED=false/' "$CONFIG_FILE"
        echo "Configuration updated"
    else
        echo -e "${YELLOW}Configuration file not found: $CONFIG_FILE${NC}"
    fi
}

# Remove cron job
remove_cron_job() {
    echo "Removing cron job..."
    
    # Check if openclaw command is available
    if command -v openclaw &> /dev/null; then
        echo "Removing OpenClaw cron job..."
        
        # Find and remove cron job
        local job_id=$(openclaw cron list --json 2>/dev/null | grep -i -B2 -A2 "memory.compression" | grep '"id"' | cut -d'"' -f4 | head -1)
        
        if [ -n "$job_id" ]; then
            if openclaw cron remove --id "$job_id" &> /dev/null; then
                echo -e "${YELLOW}OpenClaw cron job removed: $job_id${NC}"
            else
                echo -e "${RED}Failed to remove OpenClaw cron job${NC}"
            fi
        else
            echo -e "${YELLOW}No OpenClaw cron job found${NC}"
        fi
    else
        echo -e "${YELLOW}openclaw command not found${NC}"
        echo "Manual cron cleanup required. Remove from crontab:"
        echo "0 */6 * * * cd $SKILL_DIR && ./scripts/compress.sh --auto"
    fi
}

# Remove enabled marker
remove_enabled_marker() {
    echo "Removing enabled marker..."
    if [ -f "$SKILL_DIR/.enabled" ]; then
        local enabled_date=$(cat "$SKILL_DIR/.enabled")
        rm -f "$SKILL_DIR/.enabled"
        echo -e "${YELLOW}Disabled (was enabled on: $enabled_date)${NC}"
    else
        echo -e "${YELLOW}No enabled marker found${NC}"
    fi
}

# Create disabled marker
create_disabled_marker() {
    echo "Creating disabled marker..."
    date -u +"%Y-%m-%dT%H:%M:%SZ" > "$SKILL_DIR/.disabled"
    echo "Disabled marker created"
}

# Show final status
show_final_status() {
    echo ""
    echo -e "${BLUE}Final Status:${NC}"
    
    if [ -f "$SKILL_DIR/.enabled" ]; then
        echo -e "${RED}⚠️  WARNING: System still appears enabled${NC}"
        echo "Enabled on: $(cat "$SKILL_DIR/.enabled")"
    else
        echo -e "${YELLOW}✓ System is disabled${NC}"
    fi
    
    # Check cron status
    if command -v openclaw &> /dev/null; then
        local cron_jobs=$(openclaw cron list --json 2>/dev/null | grep -i "memory.compression" || true)
        if [ -n "$cron_jobs" ]; then
            echo -e "${RED}⚠️  WARNING: Cron jobs still exist${NC}"
        else
            echo -e "${YELLOW}✓ No active cron jobs${NC}"
        fi
    fi
}

# Main disable function
main() {
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${BLUE}  DISABLING MEMORY COMPRESSION SYSTEM  ${NC}"
    echo -e "${BLUE}=========================================${NC}"
    echo ""
    
    # Check if already disabled
    if check_disabled; then
        echo ""
        echo -e "${YELLOW}To enable, run: ./scripts/enable.sh${NC}"
        exit 0
    fi
    
    # Confirm disable
    read -p "Are you sure you want to disable the Memory Compression System? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Disable cancelled${NC}"
        exit 0
    fi
    
    # Disable steps
    disable_compression_config
    echo ""
    
    remove_cron_job
    echo ""
    
    remove_enabled_marker
    echo ""
    
    create_disabled_marker
    echo ""
    
    show_final_status
    echo ""
    
    echo -e "${YELLOW}=========================================${NC}"
    echo -e "${YELLOW}  MEMORY COMPRESSION SYSTEM DISABLED   ${NC}"
    echo -e "${YELLOW}=========================================${NC}"
    echo ""
    echo "Note:"
    echo "• Existing compressed files are preserved"
    echo "• Configuration files are preserved"
    echo "• Manual compression still works: ./scripts/compress.sh"
    echo ""
    echo "To re-enable: ./scripts/enable.sh"
}

# Run main function
main