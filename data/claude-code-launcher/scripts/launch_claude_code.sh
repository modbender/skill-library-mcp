#!/bin/bash

###############################################################################
# Claude Code Launcher — Automate Claude Code startup with Remote Control
###############################################################################

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

PROJECT_PATH="${1:-.}"
VERBOSE="${VERBOSE:-0}"
SCREENSHOT_DIR="${HOME}/.openclaw/workspace/logs/claude-code-launcher"
LOG_FILE="${SCREENSHOT_DIR}/launch-$(date +%s).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Logging & Output
# ============================================================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

info() {
    echo -e "${BLUE}ℹ${NC} $*"
    log "INFO: $*"
}

success() {
    echo -e "${GREEN}✅${NC} $*"
    log "SUCCESS: $*"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $*"
    log "WARN: $*"
}

error() {
    echo -e "${RED}❌${NC} $*"
    log "ERROR: $*"
}

debug() {
    if [[ $VERBOSE -eq 1 ]]; then
        echo -e "${BLUE}🐛${NC} $*"
    fi
    log "DEBUG: $*"
}

# ============================================================================
# Setup
# ============================================================================

setup() {
    mkdir -p "$SCREENSHOT_DIR"
    
    # Check required tools
    if ! command -v peekaboo &> /dev/null; then
        error "peekaboo not found. Install with: brew install steipete/tap/peekaboo"
        exit 1
    fi
    
    if ! command -v claude &> /dev/null; then
        error "claude CLI not found. Install with: npm install -g @anthropic-ai/claude-cli"
        exit 1
    fi
    
    # Check system permissions
    if ! osascript -e 'tell app "System Events" to every process' &> /dev/null; then
        warn "Accessibility permissions may be required"
    fi
    
    log "Setup complete"
}

# ============================================================================
# Project Validation
# ============================================================================

validate_project() {
    local project="$1"
    
    # Expand ~ to home directory
    project="${project/#\~/$HOME}"
    
    if [[ ! -d "$project" ]]; then
        error "Project path does not exist: $project"
        error "Did you mean one of these?"
        ls -d ~/dev/* 2>/dev/null | head -5 || true
        exit 1
    fi
    
    if [[ ! -w "$project" ]]; then
        error "No write permission for: $project"
        exit 1
    fi
    
    success "Project validated: $(basename "$project")"
    echo "$project"
}

# ============================================================================
# Terminal & Claude Code Execution
# ============================================================================

open_terminal() {
    info "Opening new Terminal window..."
    
    # Open Terminal app
    open -a Terminal
    sleep 2
    
    # Create new window via keyboard shortcut
    if peekaboo hotkey --keys "cmd,n" --app Terminal 2>/dev/null; then
        success "New Terminal window opened"
        sleep 1
    else
        error "Failed to create new Terminal window"
        return 1
    fi
}

navigate_to_project() {
    local project="$1"
    
    info "Navigating to project: $project"
    
    if peekaboo type "cd \"$project\"" --app Terminal --return 2>/dev/null; then
        success "Navigated to project"
        sleep 1
    else
        error "Failed to navigate to project"
        return 1
    fi
}

start_claude_code() {
    info "Starting Claude Code..."
    
    if peekaboo type "claude code" --app Terminal --return 2>/dev/null; then
        success "Claude Code command sent"
        sleep 5  # Wait for Claude Code interface to load
    else
        error "Failed to start Claude Code"
        return 1
    fi
}

activate_remote_control() {
    info "Activating Remote Control..."
    
    # Type /remote-control command
    if peekaboo type "/remote-control" --app Terminal --return 2>/dev/null; then
        success "Remote Control command sent"
        sleep 3  # Wait for Remote Control menu to appear
    else
        error "Failed to send Remote Control command"
        return 1
    fi
}

confirm_remote_control() {
    info "Confirming Remote Control activation..."
    
    # Press Enter to confirm
    if peekaboo press return --app Terminal 2>/dev/null; then
        success "Remote Control confirmed"
        sleep 3  # Wait for activation
    else
        error "Failed to confirm Remote Control"
        return 1
    fi
}

# ============================================================================
# Screenshot & Results
# ============================================================================

capture_screenshot() {
    local output_file="${SCREENSHOT_DIR}/result-$(date +%s).png"
    
    info "Capturing screenshot..."
    
    if peekaboo image --mode screen --path "$output_file" 2>/dev/null; then
        success "Screenshot saved: $output_file"
        echo "$output_file"
    else
        error "Failed to capture screenshot"
        return 1
    fi
}

display_results() {
    local screenshot="$1"
    
    success ""
    success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    success "Claude Code is now running with Remote Control!"
    success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    success ""
    info "You can now:"
    info "  📱 Scan the QR code from your phone (Claude app)"
    info "  🔗 Open the session URL in your browser"
    info "  💻 Access from any device"
    success ""
    info "Screenshot: $screenshot"
    log "Launch completed successfully"
}

# ============================================================================
# Error Recovery
# ============================================================================

handle_error() {
    local line_num="$1"
    error "Script failed at line $line_num"
    error "Check log: $LOG_FILE"
    
    info ""
    warn "Troubleshooting tips:"
    warn "  1. Ensure Terminal.app is in the foreground"
    warn "  2. Check System Settings → Privacy & Security → Screen Recording"
    warn "  3. Verify Claude Code is installed: which claude"
    warn "  4. Check Peekaboo permissions: peekaboo permissions"
    
    exit 1
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    trap 'handle_error $LINENO' ERR
    
    info "=== Claude Code Launcher v1.0 ==="
    log "Starting with project: $PROJECT_PATH"
    
    # Validate
    PROJECT_PATH=$(validate_project "$PROJECT_PATH")
    
    # Execute
    open_terminal
    navigate_to_project "$PROJECT_PATH"
    start_claude_code
    activate_remote_control
    confirm_remote_control
    
    # Capture result
    SCREENSHOT=$(capture_screenshot)
    
    # Display success
    display_results "$SCREENSHOT"
}

# ============================================================================
# Entry Point
# ============================================================================

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    setup
    main "$@"
fi
