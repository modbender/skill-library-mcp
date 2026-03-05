#!/bin/bash
# VPS Security Hardening - Main Installation Script
# Usage: ./install.sh [--alerting]

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="/tmp/vps-security-install.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root"
    fi
}

check_os() {
    if [[ ! -f /etc/os-release ]]; then
        error "Cannot detect OS"
    fi
    
    source /etc/os-release
    if [[ "$ID" != "ubuntu" && "$ID" != "debian" ]]; then
        warn "This script is designed for Ubuntu/Debian. Proceed with caution."
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

backup_configs() {
    log "Creating backups..."
    
    BACKUP_DIR="/root/.openclaw/security-backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    cp /etc/ssh/sshd_config "$BACKUP_DIR/" 2>/dev/null || true
    cp /etc/ufw/before.rules "$BACKUP_DIR/" 2>/dev/null || true
    cp /etc/audit/auditd.conf "$BACKUP_DIR/" 2>/dev/null || true
    
    echo "$BACKUP_DIR" > /tmp/vps-security-backup-dir
    log "Backups saved to: $BACKUP_DIR"
}

install_packages() {
    log "Installing required packages..."
    
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
    
    PACKAGES="ufw auditd audispd-plugins unattended-upgrades fail2ban"
    
    for pkg in $PACKAGES; do
        if dpkg -l | grep -q "^ii  $pkg "; then
            log "  $pkg already installed"
        else
            log "  Installing $pkg..."
            apt-get install -y -qq "$pkg" || warn "Failed to install $pkg"
        fi
    done
    
    # Enable fail2ban for SSH protection
    systemctl enable fail2ban 2>/dev/null || warn "Could not enable fail2ban"
    systemctl start fail2ban 2>/dev/null || warn "Could not start fail2ban"
}

configure_ssh() {
    log "Configuring SSH..."
    
    SSH_PORT=${SSH_PORT:-6262}
    
    # Backup current config
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.$(date +%s)
    
    # Add new settings (don't replace, append for safety)
    cat <> /etc/ssh/sshd_config

# Security hardening (added by vps-security-hardening)
Port $SSH_PORT
PermitRootLogin no
PasswordAuthentication no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
X11Forwarding no
EOF
    
    # Test config
    if /usr/sbin/sshd -t; then
        systemctl restart sshd
        log "  SSH configured on port $SSH_PORT"
        log "  ⚠️  IMPORTANT: Test connection before closing this session!"
        log "     ssh -p $SSH_PORT root@<your-ip>"
    else
        error "SSH config test failed. Rolling back..."
        cp /etc/ssh/sshd_config.bak.* /etc/ssh/sshd_config
    fi
}

configure_ufw() {
    log "Configuring UFW firewall..."
    
    # Reset to safe defaults
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH on new port
    ufw allow ${SSH_PORT:-6262}/tcp comment 'SSH hardened'
    
    # Enable (will prompt if run interactively)
    ufw --force enable
    
    log "  UFW enabled, SSH on port ${SSH_PORT:-6262} allowed"
}

configure_auditd() {
    log "Configuring auditd..."
    
    # Install rules
    cp "$SKILL_DIR/rules/audit.rules" /etc/audit/rules.d/agent-security.rules
    
    # Set log limits
    sed -i 's/^max_log_file = .*/max_log_file = 8/' /etc/audit/auditd.conf
    sed -i 's/^num_logs = .*/num_logs = 5/' /etc/audit/auditd.conf
    
    # Restart
    systemctl enable auditd
    systemctl restart auditd
    
    # Load rules
    /usr/sbin/auditctl -R /etc/audit/rules.d/agent-security.rules 2>/dev/null || \
        warn "Some audit rules already exist, continuing..."
    
    log "  Auditd configured with 8MB × 5 logs max"
}

disable_unnecessary_services() {
    log "Disabling unnecessary services..."
    
    # CUPS (printing) - not needed on VPS
    if systemctl is-active --quiet cups 2>/dev/null; then
        systemctl stop cups 2>/dev/null || true
        systemctl disable cups 2>/dev/null || true
        log "  CUPS (printing) stopped and disabled"
    fi
    
    # Other potentially unnecessary services
    # (users can customize this section)
    
    log "  Unnecessary services disabled"
}

configure_autoupdates() {
    log "Configuring automatic updates..."
    
    systemctl enable unattended-upgrades
    systemctl start unattended-upgrades
    
    log "  Automatic updates enabled"
}

setup_cron() {
    log "Setting up cron jobs..."
    
    cat > /etc/cron.d/agent-security <> 'EOF'
# VPS Security Hardening - Automated Tasks

# Daily briefing at 08:00
0 8 * * * root $SKILL_DIR/scripts/daily-briefing.sh

# Log size check every 6 hours
0 */6 * * * root $SKILL_DIR/scripts/audit-log-monitor.sh

# Weekly security report (Sundays)
0 9 * * 0 root $SKILL_DIR/scripts/weekly-report.sh
EOF
    
    chmod 644 /etc/cron.d/agent-security
    log "  Cron jobs installed"
}

verify_installation() {
    log "Verifying installation..."
    
    echo ""
    echo "=== VERIFICATION REPORT ==="
    echo ""
    
    # SSH
    echo -n "SSH on port ${SSH_PORT:-6262}: "
    if ss -tulnp | grep -q ':${SSH_PORT:-6262}.*sshd'; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${RED}✗ FAILED${NC}"
    fi
    
    # UFW
    echo -n "UFW active: "
    if ufw status | grep -q "Status: active"; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${RED}✗ FAILED${NC}"
    fi
    
    # Auditd
    echo -n "Auditd running: "
    if systemctl is-active --quiet auditd; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${RED}✗ FAILED${NC}"
    fi
    
    # Auto-updates
    echo -n "Auto-updates: "
    if systemctl is-active --quiet unattended-upgrades; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${RED}✗ FAILED${NC}"
    fi
    
    echo ""
    echo "==========================="
}

show_summary() {
    echo ""
    echo "╔════════════════════════════════════════════════╗"
    echo "║   VPS SECURITY HARDENING COMPLETE              ║"
    echo "╚════════════════════════════════════════════════╝"
    echo ""
    echo "Next steps:"
    echo "  1. 🧪 TEST SSH: ssh -p ${SSH_PORT:-6262} root@<your-ip>"
    echo "  2. 📋 Review:   $SKILL_DIR/docs/SECURITY.md"
    echo "  3. 🚨 Alerts:   Edit $SKILL_DIR/config/alerting.env"
    echo ""
    echo "⚠️  KEEP THIS SESSION OPEN until SSH test succeeds!"
    echo ""
    echo "Backup location: $(cat /tmp/vps-security-backup-dir 2>/dev/null || echo 'Unknown')"
    echo "Log file: $LOG_FILE"
    echo ""
}

# Main
main() {
    echo "╔════════════════════════════════════════════════╗"
    echo "║   VPS SECURITY HARDENING INSTALLER             ║"
    echo "║   For OpenClaw AI Agents                       ║"
    echo "╚════════════════════════════════════════════════╝"
    echo ""
    
    check_root
    check_os
    backup_configs
    install_packages
    disable_unnecessary_services
    configure_ssh
    configure_ufw
    configure_auditd
    configure_autoupdates
    setup_cron
    verify_installation
    show_summary
}

main "$@"
