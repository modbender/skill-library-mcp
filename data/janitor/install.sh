#!/bin/bash

###############################################################################
# OpenClaw Janitor Installation Script
#
# Installs and configures the Janitor skill with session management
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
SKILL_NAME="openclaw-janitor"
SKILL_DIR="$OPENCLAW_HOME/workspace/$SKILL_NAME"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Functions
print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║         OpenClaw Janitor Installation Wizard                ║"
    echo "║              Session Management v1.1.0                       ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $@"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $@"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $@"
}

log_error() {
    echo -e "${RED}[✗]${NC} $@"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi

    local node_version=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$node_version" -lt 14 ]; then
        log_error "Node.js version 14 or higher is required (found: $(node -v))"
        exit 1
    fi

    log_success "Node.js $(node -v) found"

    # Check OpenClaw directory
    if [ ! -d "$OPENCLAW_HOME" ]; then
        log_warning "OpenClaw directory not found at $OPENCLAW_HOME"
        read -p "Create it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            mkdir -p "$OPENCLAW_HOME/workspace"
            log_success "Created OpenClaw directory"
        else
            log_error "Installation cancelled"
            exit 1
        fi
    fi

    log_success "Prerequisites check passed"
}

# Install skill
install_skill() {
    log_info "Installing Janitor skill..."

    # Create workspace directory
    mkdir -p "$OPENCLAW_HOME/workspace"

    # Copy skill files
    if [ "$SCRIPT_DIR" != "$SKILL_DIR" ]; then
        log_info "Copying skill files to $SKILL_DIR..."

        # Remove old installation if exists
        if [ -d "$SKILL_DIR" ]; then
            log_warning "Removing old installation..."
            rm -rf "$SKILL_DIR"
        fi

        cp -r "$SCRIPT_DIR" "$SKILL_DIR"
        log_success "Skill files copied"
    else
        log_info "Already in skill directory"
    fi

    # Make scripts executable
    chmod +x "$SKILL_DIR/scripts/pre-start-cleanup.sh"
    chmod +x "$SKILL_DIR/install.sh"

    log_success "Janitor skill installed"
}

# Configure monitoring
configure_monitoring() {
    echo
    log_info "Configuring session monitoring..."

    read -p "Enable automatic session monitoring? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Install as systemd service? (requires sudo) (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_systemd_service
        else
            log_info "You can start monitoring manually with:"
            echo "  cd $SKILL_DIR"
            echo "  node index.js monitor start"
        fi
    fi
}

# Install systemd service
install_systemd_service() {
    log_info "Setting up systemd service..."

    echo
    echo "To install the systemd service, you need to manually create the service file."
    echo "Please follow these steps:"
    echo
    echo "1. Open the systemd setup guide:"
    echo "   cat $SKILL_DIR/systemd/README.md"
    echo
    echo "2. Or visit the guide directly:"
    echo "   less $SKILL_DIR/systemd/README.md"
    echo
    echo "3. Copy the service file content and create:"
    echo "   sudo nano /etc/systemd/system/janitor-monitor@.service"
    echo
    echo "4. Then enable and start the service:"
    echo "   sudo systemctl daemon-reload"
    echo "   sudo systemctl enable janitor-monitor@$USER"
    echo "   sudo systemctl start janitor-monitor@$USER"
    echo

    read -p "Press Enter to view the setup guide now, or Ctrl+C to skip..."
    less "$SKILL_DIR/systemd/README.md" || cat "$SKILL_DIR/systemd/README.md"
}

# Configure notifications
configure_notifications() {
    echo
    log_info "Configuring notifications..."

    echo "Available notification channels:"
    echo "  1) Log only (default)"
    echo "  2) Telegram"
    echo "  3) Discord"
    echo "  4) All channels"

    read -p "Choose notification channel (1-4): " choice

    case $choice in
        2)
            configure_telegram
            ;;
        3)
            configure_discord
            ;;
        4)
            configure_telegram
            configure_discord
            ;;
        *)
            log_info "Using log-only notifications"
            ;;
    esac
}

# Configure Telegram
configure_telegram() {
    echo
    log_info "Configuring Telegram notifications..."

    echo "To set up Telegram notifications:"
    echo "  1. Create a bot with @BotFather on Telegram"
    echo "  2. Get your bot token"
    echo "  3. Start a chat with your bot"
    echo "  4. Get your chat ID from @userinfobot"

    read -p "Enter Telegram Bot Token: " bot_token
    read -p "Enter Telegram Chat ID: " chat_id

    # Save to environment file
    local env_file="$SKILL_DIR/.env"
    echo "TELEGRAM_BOT_TOKEN=$bot_token" >> "$env_file"
    echo "TELEGRAM_CHAT_ID=$chat_id" >> "$env_file"

    log_success "Telegram configured"

    # Test notification
    read -p "Send test notification? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$SKILL_DIR"
        node -e "
        const Notifier = require('./src/services/notifier');
        const notifier = new Notifier({
            channels: ['telegram'],
            telegram: {
                botToken: '$bot_token',
                chatId: '$chat_id'
            }
        });
        notifier.test().then(r => console.log('Test sent:', r)).catch(console.error);
        "
    fi
}

# Configure Discord
configure_discord() {
    echo
    log_info "Configuring Discord notifications..."

    echo "To set up Discord notifications:"
    echo "  1. Create a webhook in your Discord server"
    echo "  2. Copy the webhook URL"

    read -p "Enter Discord Webhook URL: " webhook_url

    # Save to environment file
    local env_file="$SKILL_DIR/.env"
    echo "DISCORD_WEBHOOK_URL=$webhook_url" >> "$env_file"

    log_success "Discord configured"
}

# Configure GitHub backup
configure_github_backup() {
    echo
    read -p "Enable GitHub backup for archives? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Configuring GitHub backup..."

        echo "Enter your GitHub repository URL for backups:"
        echo "  Example: https://github.com/username/openclaw-backups.git"

        read -p "Repository URL: " repo_url

        # Save to environment file
        local env_file="$SKILL_DIR/.env"
        echo "GITHUB_BACKUP_REPO=$repo_url" >> "$env_file"

        log_success "GitHub backup configured"

        log_info "Make sure the repository exists and you have push access"
        log_info "You may need to set up SSH keys or access tokens"
    fi
}

# Run initial cleanup
run_initial_cleanup() {
    echo
    read -p "Run initial context cleanup now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Running initial cleanup..."
        cd "$SKILL_DIR"
        node index.js context status
        node index.js context clean moderate || true
        log_success "Initial cleanup complete"
    fi
}

# Show next steps
show_next_steps() {
    echo
    log_success "Installation complete!"
    echo
    echo -e "${CYAN}Next Steps:${NC}"
    echo "  1. View context dashboard:"
    echo "     cd $SKILL_DIR"
    echo "     node index.js context"
    echo
    echo "  2. Start monitoring (if not using systemd):"
    echo "     node index.js monitor start"
    echo
    echo "  3. Configure thresholds (optional):"
    echo "     Edit config in janitor.js constructor"
    echo
    echo "  4. Check documentation:"
    echo "     cat README.md"
    echo
    echo -e "${GREEN}Janitor is now protecting your OpenClaw context!${NC}"
    echo
}

# Show security warning and get consent
show_security_warning() {
    echo
    echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║                    SECURITY WARNING                          ║${NC}"
    echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${RED}Janitor is a HIGH-PRIVILEGE skill that requires:${NC}"
    echo "  • File deletion permissions (cache, logs, sessions)"
    echo "  • Process execution (git, tar commands)"
    echo "  • Optional network access (notifications, GitHub backup)"
    echo
    echo -e "${YELLOW}Before installing, you must:${NC}"
    echo "  1. Read SECURITY.md for complete security guidelines"
    echo "  2. Understand the risks and mitigations"
    echo "  3. Review the source code if needed"
    echo "  4. Only install if you trust this skill"
    echo
    echo -e "${CYAN}Key Safety Features:${NC}"
    echo "  ✓ Protected files never deleted (package.json, .git, etc.)"
    echo "  ✓ All deletions archived before removal"
    echo "  ✓ Path traversal prevention"
    echo "  ✓ Command injection protection"
    echo "  ✓ Dry-run mode available for testing"
    echo
    read -p "Do you want to view SECURITY.md now? (recommended) (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        less "$SCRIPT_DIR/SECURITY.md" || cat "$SCRIPT_DIR/SECURITY.md"
        echo
    fi

    echo
    read -p "Have you read and understood the security implications? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Installation cancelled. Please review SECURITY.md first."
        exit 0
    fi

    echo
    read -p "Do you accept the risks and want to proceed with installation? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Installation cancelled by user."
        exit 0
    fi

    log_success "Security acknowledgment accepted. Proceeding with installation..."
}

# Main installation flow
main() {
    print_header
    show_security_warning

    check_prerequisites
    install_skill
    configure_monitoring
    configure_notifications
    configure_github_backup
    run_initial_cleanup
    show_next_steps
}

# Run installation
main

exit 0
