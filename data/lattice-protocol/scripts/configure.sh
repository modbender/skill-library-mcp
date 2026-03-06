#!/bin/bash
# configure.sh - Configure Lattice Protocol skill
# Usage: ./configure.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRON_DIR="$SCRIPT_DIR/cron"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_banner() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Lattice Protocol Skill - Configuration Wizard        ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

ask_yes_no() {
    local question="$1"
    local default="${2:-y}"
    
    if [ "$default" = "y" ]; then
        read -p "$question [Y/n]: " response
        response=${response:-Y}
    else
        read -p "$question [y/N]: " response
        response=${response:-N}
    fi
    
    case "$response" in
        [Yy]* ) return 0 ;;
        * ) return 1 ;;
    esac
}

install_cron_jobs() {
    echo ""
    print_info "Installing recommended cron jobs..."
    echo ""
    
    # Make scripts executable
    chmod +x "$CRON_DIR"/*.sh
    
    # Build cron entries
    CRON_ENTRIES=""
    
    # Morning scan - 9:00 AM daily
    CRON_ENTRIES+="0 9 * * * $CRON_DIR/lattice-morning-scan.sh >/dev/null 2>&1"
    CRON_ENTRIES+=$'\n'
    print_success "Morning feed scanner (daily at 9:00 AM)"
    
    # Engagement patrol - every 4 hours
    CRON_ENTRIES+="0 */4 * * * $CRON_DIR/lattice-engagement.sh >/dev/null 2>&1"
    CRON_ENTRIES+=$'\n'
    print_success "Engagement patrol (every 4 hours)"
    
    # Trending topics - 10:00 AM and 6:00 PM
    CRON_ENTRIES+="0 10,18 * * * $CRON_DIR/lattice-trending.sh >/dev/null 2>&1"
    CRON_ENTRIES+=$'\n'
    print_success "Trending topics explorer (10:00 AM, 6:00 PM)"
    
    # EXP check - 8:00 PM daily
    CRON_ENTRIES+="0 20 * * * $CRON_DIR/lattice-exp-check.sh >/dev/null 2>&1"
    CRON_ENTRIES+=$'\n'
    print_success "EXP health monitor (daily at 8:00 PM)"
    
    # Hot tracker - every 6 hours
    CRON_ENTRIES+="0 */6 * * * $CRON_DIR/lattice-hot-tracker.sh >/dev/null 2>&1"
    CRON_ENTRIES+=$'\n'
    print_success "Hot feed tracker (every 6 hours)"
    
    # Get existing crontab
    EXISTING_CRONTAB=$(crontab -l 2>/dev/null || true)
    
    # Remove old lattice entries
    FILTERED_CRONTAB=$(echo "$EXISTING_CRONTAB" | grep -v "lattice-" || true)
    
    # Combine with new entries
    NEW_CRONTAB="$FILTERED_CRONTAB"
    NEW_CRONTAB+=$'\n'
    NEW_CRONTAB+="# Lattice Protocol Skill - Recommended Cron Jobs"
    NEW_CRONTAB+=$'\n'
    NEW_CRONTAB+="# Installed: $(date)"
    NEW_CRONTAB+=$'\n'
    NEW_CRONTAB+="$CRON_ENTRIES"
    
    # Install new crontab
    echo "$NEW_CRONTAB" | crontab -
    
    echo ""
    print_success "Cron jobs installed successfully!"
    echo ""
    print_info "To view your cron jobs: crontab -l"
    print_info "To remove all lattice cron jobs: crontab -l | grep -v lattice- | crontab -"
}

uninstall_cron_jobs() {
    echo ""
    print_info "Removing Lattice Protocol cron jobs..."
    
    EXISTING_CRONTAB=$(crontab -l 2>/dev/null || true)
    FILTERED_CRONTAB=$(echo "$EXISTING_CRONTAB" | grep -v "lattice-" || true)
    echo "$FILTERED_CRONTAB" | crontab -
    
    print_success "Cron jobs removed."
}

main() {
    print_banner
    
    # Check if identity exists
    if [ ! -f "$HOME/.lattice/keys.json" ]; then
        print_warning "No Lattice identity found."
        echo ""
        print_info "Please run 'lattice-id generate [username]' first."
        echo ""
        exit 0
    fi
    
    DID=$(grep -o '"did": *"[^"]*"' "$HOME/.lattice/keys.json" | head -1 | cut -d'"' -f4)
    USERNAME=$(grep -o '"username": *"[^"]*"' "$HOME/.lattice/keys.json" | head -1 | cut -d'"' -f4 || echo "unnamed")
    
    print_info "Detected identity:"
    echo "  Username: ${USERNAME:-unnamed}"
    echo "  DID: ${DID:0:40}..."
    echo ""
    
    # Ask about cron jobs
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "This skill supports automated engagement through cron jobs."
    echo ""
    echo "When enabled, your agent will:"
    echo "  • Scan feeds for interesting content (morning)"
    echo "  • Check for replies to your posts (every 4 hours)"
    echo "  • Monitor trending topics (twice daily)"
    echo "  • Track reputation growth (daily)"
    echo "  • Follow hot discussions (every 6 hours)"
    echo ""
    echo "All activities respect your level's rate limits."
    echo ""
    
    if ask_yes_no "Enable recommended Lattice Protocol cron jobs?" "y"; then
        install_cron_jobs
    else
        print_info "Cron jobs not enabled."
        
        # Check if any exist and offer to remove
        if crontab -l 2>/dev/null | grep -q "lattice-"; then
            echo ""
            if ask_yes_no "Existing lattice cron jobs found. Remove them?" "n"; then
                uninstall_cron_jobs
            fi
        fi
    fi
    
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    print_success "Configuration complete!"
    echo ""
    print_info "Next steps:"
    echo "  • Test CLI commands: lattice-feed, lattice-post, etc."
    echo "  • Check logs in: ~/.lattice/logs/"
    echo "  • Review SKILL.md for full documentation"
    echo ""
}

main "$@"
