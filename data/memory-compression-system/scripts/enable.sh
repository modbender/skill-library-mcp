#!/bin/bash
# Memory Compression System - Enable Script
# Version: 3.0.0

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="$SKILL_DIR/config/default.conf"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load configuration
[ -f "$CONFIG_FILE" ] && source "$CONFIG_FILE" 2>/dev/null

echo -e "${BLUE}Enabling Memory Compression System v3.0.0${NC}"
echo ""

# Check if already enabled
check_enabled() {
    if [ -f "$SKILL_DIR/.enabled" ]; then
        echo -e "${YELLOW}System is already enabled${NC}"
        echo "Enabled on: $(cat "$SKILL_DIR/.enabled")"
        return 0
    fi
    return 1
}

# Enable compression in config
enable_compression_config() {
    echo "Enabling compression in configuration..."
    
    if [ -f "$CONFIG_FILE" ]; then
        # Update configuration
        sed -i 's/^COMPRESSION_ENABLED=.*/COMPRESSION_ENABLED=true/' "$CONFIG_FILE"
        sed -i 's/^SEARCH_ENABLED=.*/SEARCH_ENABLED=true/' "$CONFIG_FILE"
        echo "Configuration updated"
    else
        echo -e "${YELLOW}Configuration file not found: $CONFIG_FILE${NC}"
    fi
}

# Create cron job
create_cron_job() {
    echo "Creating cron job..."
    
    # Check if openclaw command is available
    if command -v openclaw &> /dev/null; then
        echo "Creating OpenClaw cron job..."
        
        # Check if cron job already exists
        local existing_job=$(openclaw cron list --json 2>/dev/null | grep -i "memory.compression" || true)
        
        if [ -n "$existing_job" ]; then
            echo -e "${YELLOW}Cron job already exists${NC}"
            return 0
        fi
        
        # Create new cron job
        local cron_job=$(cat << 'EOF'
{
  "name": "Memory Compression System",
  "schedule": {
    "kind": "every",
    "everyMs": 21600000
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Run Memory Compression System auto compression: cd /home/node/.openclaw/workspace/skills/memory-compression-system && ./scripts/compress.sh --auto",
    "timeoutSeconds": 300
  },
  "delivery": {
    "mode": "announce"
  }
}
EOF
        )
        
        if openclaw cron add --json "$cron_job" &> /dev/null; then
            echo -e "${GREEN}OpenClaw cron job created successfully${NC}"
        else
            echo -e "${YELLOW}Failed to create OpenClaw cron job${NC}"
            echo "You may need to create it manually via: openclaw cron add"
        fi
    else
        echo -e "${YELLOW}openclaw command not found${NC}"
        echo "Manual cron setup required. Add to crontab:"
        echo "0 */6 * * * cd $SKILL_DIR && ./scripts/compress.sh --auto"
    fi
}

# Create enabled marker
create_enabled_marker() {
    echo "Creating enabled marker..."
    date -u +"%Y-%m-%dT%H:%M:%SZ" > "$SKILL_DIR/.enabled"
    echo -e "${GREEN}Enabled marker created${NC}"
}

# Test the system
test_system() {
    echo "Testing system..."
    
    # Test status script
    if "$SCRIPT_DIR/status.sh" &> /dev/null; then
        echo -e "${GREEN}Status script: OK${NC}"
    else
        echo -e "${YELLOW}Status script: WARNING${NC}"
    fi
    
    # Test compression script (dry run)
    if "$SCRIPT_DIR/compress.sh" --test &> /dev/null; then
        echo -e "${GREEN}Compression script: OK${NC}"
    else
        echo -e "${YELLOW}Compression script: WARNING${NC}"
    fi
    
    # Test cleanup script (dry run)
    if "$SCRIPT_DIR/cleanup.sh" --dry-run &> /dev/null; then
        echo -e "${GREEN}Cleanup script: OK${NC}"
    else
        echo -e "${YELLOW}Cleanup script: WARNING${NC}"
    fi
}

# Main enable function
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  ENABLING MEMORY COMPRESSION SYSTEM  ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # Check if already enabled
    if check_enabled; then
        echo ""
        echo -e "${YELLOW}To re-enable, first run: ./scripts/disable.sh${NC}"
        exit 0
    fi
    
    # Enable steps
    enable_compression_config
    echo ""
    
    create_cron_job
    echo ""
    
    create_enabled_marker
    echo ""
    
    test_system
    echo ""
    
    # Show status
    echo -e "${BLUE}Final Status:${NC}"
    "$SCRIPT_DIR/status.sh"
    echo ""
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  MEMORY COMPRESSION SYSTEM ENABLED!  ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Next steps:"
    echo "1. System will automatically compress every 6 hours"
    echo "2. Check status anytime: ./scripts/status.sh"
    echo "3. Run manual compression: ./scripts/compress.sh"
    echo "4. View logs: ./scripts/logs.sh"
    echo ""
    echo "To disable: ./scripts/disable.sh"
}

# Run main function
main