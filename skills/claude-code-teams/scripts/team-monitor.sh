#!/usr/bin/env bash
# team-monitor.sh - Monitor Claude Code agent team status

set -euo pipefail

echo "🎭 Claude Code Agent Teams - Monitor"
echo "===================================="
echo ""
echo "This script monitors your active Claude Code team."
echo "Press Ctrl+C to exit."
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Monitor Claude Code agent team status.

OPTIONS:
    -h, --help         Show this help message
    -i, --interval N   Update interval in seconds (default: 5)
    -o, --once         Run once and exit (no loop)

EXAMPLES:
    $0                    # Monitor with 5s refresh
    $0 -i 10              # Monitor with 10s refresh
    $0 --once             # Check status once

NOTES:
    - Requires active Claude Code session with agent teams
    - Use Ctrl+T in Claude Code to toggle task list view
    - This script provides external monitoring

EOF
    exit 0
}

# Default settings
INTERVAL=5
ONCE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -i|--interval)
            INTERVAL="$2"
            shift 2
            ;;
        -o|--once)
            ONCE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Function to check Claude Code process
check_claude_process() {
    if pgrep -f "claude.*pty" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to monitor (placeholder - actual implementation would parse Claude Code state)
monitor_team() {
    local timestamp=$(date '+%H:%M:%S')
    
    echo -e "${BLUE}[$timestamp] Team Status${NC}"
    echo "----------------------------------------"
    
    # Check if Claude Code is running
    if ! check_claude_process; then
        echo -e "${RED}❌ No Claude Code process detected${NC}"
        echo ""
        echo "Start Claude Code with: claude --pty"
        return 1
    fi
    
    echo -e "${GREEN}✅ Claude Code process running${NC}"
    echo ""
    
    # NOTE: This is a placeholder. Actual implementation would:
    # 1. Check Claude Code session directory for task list state
    # 2. Parse teammate status files
    # 3. Read message queue
    # 4. Display structured output
    
    echo "📋 Task List:"
    echo "  (Use Ctrl+T in Claude Code to view full task list)"
    echo ""
    
    echo "👥 Active Teammates:"
    echo "  (Teammate status appears in Claude Code session)"
    echo ""
    
    echo "💬 Recent Messages:"
    echo "  (Inter-agent messages visible in Claude Code)"
    echo ""
    
    echo "ℹ️  Tip: For real-time monitoring, use Ctrl+T in Claude Code"
    echo "         to toggle task list and teammate status view."
    echo ""
    
    return 0
}

# Main monitoring loop
main() {
    if [ "$ONCE" = true ]; then
        monitor_team
        exit $?
    fi
    
    echo "Monitoring every ${INTERVAL}s (press Ctrl+C to exit)"
    echo ""
    
    while true; do
        clear
        monitor_team
        
        if [ $? -ne 0 ]; then
            echo "Retrying in ${INTERVAL}s..."
        fi
        
        sleep "$INTERVAL"
    done
}

# Trap Ctrl+C for clean exit
trap 'echo ""; echo "Monitoring stopped."; exit 0' INT

main
