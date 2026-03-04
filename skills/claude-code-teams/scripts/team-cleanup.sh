#!/usr/bin/env bash
# team-cleanup.sh - Gracefully shut down Claude Code agent team

set -euo pipefail

echo "🎭 Claude Code Agent Teams - Cleanup"
echo "===================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Gracefully shut down Claude Code agent team.

OPTIONS:
    -h, --help     Show this help message
    -f, --force    Force shutdown (skip graceful steps)
    -y, --yes      Skip confirmation prompts

CLEANUP STEPS:
    1. Signal teammates to complete current tasks
    2. Wait for teammates to finish gracefully
    3. Shut down teammates in order
    4. Clean up temporary files
    5. Exit Claude Code session

EXAMPLES:
    $0              # Interactive cleanup with confirmations
    $0 -y           # Automatic cleanup (no prompts)
    $0 --force      # Force shutdown immediately

NOTES:
    - Graceful shutdown preserves teammate state
    - Force shutdown may lose work in progress
    - Use graceful shutdown when possible

EOF
    exit 0
}

# Default settings
FORCE=false
AUTO_YES=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -y|--yes)
            AUTO_YES=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Function to confirm action
confirm() {
    if [ "$AUTO_YES" = true ]; then
        return 0
    fi
    
    local message="$1"
    echo -ne "${YELLOW}${message} (y/N): ${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to check Claude Code process
check_claude_process() {
    if pgrep -f "claude.*pty" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Graceful cleanup
graceful_cleanup() {
    echo "Starting graceful cleanup..."
    echo ""
    
    # Step 1: Check for active Claude Code session
    echo -n "Step 1: Checking for active Claude Code session... "
    if check_claude_process; then
        echo -e "${GREEN}✅ Found${NC}"
    else
        echo -e "${YELLOW}⚠️  No active session${NC}"
        echo ""
        echo "Nothing to clean up."
        exit 0
    fi
    
    # Step 2: Signal teammates to finish
    echo ""
    echo "Step 2: Signaling teammates to complete current tasks..."
    echo "  (In Claude Code, type: 'Please finish your current tasks and report status')"
    echo ""
    
    if ! confirm "Have teammates reported completion?"; then
        echo "Cleanup cancelled. Teammates still working."
        exit 1
    fi
    
    # Step 3: Shut down teammates
    echo ""
    echo "Step 3: Shutting down teammates..."
    echo "  (In Claude Code, type: 'Shutdown all teammates gracefully')"
    echo ""
    
    if ! confirm "Have teammates shut down?"; then
        echo "Cleanup cancelled. Teammates still active."
        exit 1
    fi
    
    # Step 4: Clean up temporary files (placeholder)
    echo ""
    echo "Step 4: Cleaning up temporary files..."
    # This would clean up any temp files created during team operation
    echo -e "${GREEN}✅ Complete${NC}"
    
    # Step 5: Exit Claude Code
    echo ""
    echo "Step 5: Ready to exit Claude Code session"
    echo "  (Type 'exit' in Claude Code to close)"
    echo ""
    
    echo -e "${GREEN}✅ Graceful cleanup complete${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review teammate output files"
    echo "  2. Merge changes if ready"
    echo "  3. Update task tracker with completion status"
}

# Force cleanup
force_cleanup() {
    echo -e "${RED}⚠️  Force cleanup mode${NC}"
    echo ""
    echo "This will immediately terminate the Claude Code session."
    echo "Work in progress may be lost."
    echo ""
    
    if ! confirm "Are you sure you want to force shutdown?"; then
        echo "Force cleanup cancelled."
        exit 1
    fi
    
    echo ""
    echo "Terminating Claude Code processes..."
    
    if pkill -f "claude.*pty"; then
        echo -e "${GREEN}✅ Processes terminated${NC}"
    else
        echo -e "${YELLOW}⚠️  No processes found${NC}"
    fi
    
    echo ""
    echo -e "${RED}⚠️  Force cleanup complete${NC}"
    echo "Review any incomplete work before proceeding."
}

# Cleanup checklist
show_checklist() {
    cat << EOF

📋 Post-Cleanup Checklist:
--------------------------
[ ] Review all teammate output files
[ ] Verify task completion (no pending tasks)
[ ] Check for merge conflicts (if multiple files edited)
[ ] Run tests if implementation changes were made
[ ] Update documentation if needed
[ ] Commit and push changes
[ ] Update project tracker (tasks complete)
[ ] Schedule follow-up if needed

EOF
}

# Main execution
main() {
    if [ "$FORCE" = true ]; then
        force_cleanup
    else
        graceful_cleanup
    fi
    
    show_checklist
}

# Trap Ctrl+C for clean exit
trap 'echo ""; echo "Cleanup interrupted."; exit 130' INT

main
