#!/bin/bash
# =============================================================================
# bootstrap.sh — Fresh VPS → Fully Operational OpenClaw
# =============================================================================
# Usage: bash bootstrap.sh
# Tested on: Ubuntu 24.04 LTS, Debian 12
# Time: ~15-20 minutes on a standard VPS
# =============================================================================

set -euo pipefail

# Configuration (edit these)
OPENCLAW_PORT="${OPENCLAW_PORT:-18789}"
ENABLE_FIREWALL="${ENABLE_FIREWALL:-true}"
ENABLE_FAIL2BAN="${ENABLE_FAIL2BAN:-true}"
INSTALL_CHROME="${INSTALL_CHROME:-true}"
NODE_MAJOR="${NODE_MAJOR:-22}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; exit 1; }

echo "============================================"
echo "  OpenClaw VPS Bootstrap"
echo "  $(date)"
echo "============================================"
echo

# --- Step 1: System packages ------------------------------------------------
log "Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    build-essential curl git jq unzip wget gnupg2 \
    ca-certificates lsb-release software-properties-common \
    htop tmux ncdu tree ripgrep fd-find \
    libsecret-tools pass \
    2>/dev/null | tail -1
log "System packages installed"

# --- Step 2: Node.js --------------------------------------------------------
if command -v node &>/dev/null; then
    NODE_VER=$(node --version)
    log "Node.js already installed: $NODE_VER"
else
    log "Installing Node.js ${NODE_MAJOR}..."
    curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | sudo -E bash - 2>/dev/null
    sudo apt-get install -y -qq nodejs 2>/dev/null
    log "Node.js $(node --version) installed"
fi

# --- Step 3: Google Chrome (for browser tools) ------------------------------
if [ "$INSTALL_CHROME" = "true" ]; then
    if command -v google-chrome &>/dev/null; then
        log "Chrome already installed: $(google-chrome --version 2>/dev/null | head -1)"
    else
        log "Installing Google Chrome..."
        wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
        sudo dpkg -i /tmp/chrome.deb 2>/dev/null || sudo apt-get install -f -y -qq 2>/dev/null
        rm -f /tmp/chrome.deb

        # Create headless shim for OpenClaw browser tools
        sudo tee /usr/local/bin/chrome-shim > /dev/null << 'SHIM'
#!/bin/bash
exec google-chrome --headless --no-sandbox --disable-gpu --disable-dev-shm-usage "$@"
SHIM
        sudo chmod +x /usr/local/bin/chrome-shim
        log "Chrome installed with headless shim"
    fi
fi

# --- Step 4: OpenClaw -------------------------------------------------------
if command -v openclaw &>/dev/null; then
    log "OpenClaw already installed: $(openclaw --version 2>/dev/null | head -1)"
    log "Updating OpenClaw..."
    npm update -g openclaw 2>/dev/null || npm install -g openclaw
else
    log "Installing OpenClaw..."
    npm install -g openclaw
fi
log "OpenClaw $(openclaw --version 2>/dev/null | head -1) ready"

# --- Step 5: Security baseline ----------------------------------------------
if [ "$ENABLE_FIREWALL" = "true" ]; then
    log "Configuring UFW firewall..."
    sudo ufw --force reset >/dev/null 2>&1
    sudo ufw default deny incoming >/dev/null
    sudo ufw default allow outgoing >/dev/null
    sudo ufw allow ssh >/dev/null
    sudo ufw --force enable >/dev/null
    log "Firewall enabled (SSH only)"
fi

if [ "$ENABLE_FAIL2BAN" = "true" ]; then
    log "Installing and configuring Fail2Ban..."
    sudo apt-get install -y -qq fail2ban 2>/dev/null
    sudo tee /etc/fail2ban/jail.local > /dev/null << 'F2B'
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 5
bantime = 3600
findtime = 600
F2B
    sudo systemctl enable fail2ban >/dev/null 2>&1
    sudo systemctl restart fail2ban >/dev/null 2>&1
    log "Fail2Ban configured"
fi

# Harden SSH (key-only, no root)
if grep -q "^PasswordAuthentication yes" /etc/ssh/sshd_config 2>/dev/null; then
    log "Hardening SSH..."
    sudo sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    sudo sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
    sudo systemctl reload sshd 2>/dev/null || sudo systemctl reload ssh 2>/dev/null
    log "SSH hardened (key-only, no root login)"
else
    log "SSH already hardened"
fi

# --- Step 6: Gateway service ------------------------------------------------
log "Setting up OpenClaw gateway service..."
sudo loginctl enable-linger "$(whoami)" 2>/dev/null || true
openclaw gateway install 2>/dev/null || true
openclaw gateway start 2>/dev/null || true

# Enable boot hook
openclaw hooks enable boot-md 2>/dev/null || true

# --- Step 7: GPG + Pass (secret store) --------------------------------------
if ! gpg --list-keys 2>/dev/null | grep -q "pub"; then
    log "Setting up GPG key for secret store..."
    read -p "Enter email for GPG key (or press Enter for default): " GPG_EMAIL
    GPG_EMAIL="${GPG_EMAIL:-openclaw@localhost}"
    
    cat > /tmp/gpg-params << GPGEOF
%no-protection
Key-Type: RSA
Key-Length: 4096
Name-Real: OpenClaw Agent
Name-Email: ${GPG_EMAIL}
Expire-Date: 0
%commit
GPGEOF
    gpg --batch --gen-key /tmp/gpg-params 2>/dev/null
    rm -f /tmp/gpg-params
    pass init "${GPG_EMAIL}" 2>/dev/null || true
    log "GPG key + password store initialized"
else
    log "GPG key already exists"
fi

# --- Final verification ------------------------------------------------------
echo
echo "============================================"
echo "  Bootstrap Complete!"
echo "============================================"
echo
log "OpenClaw: $(openclaw --version 2>/dev/null | head -1)"
log "Node.js: $(node --version)"
log "Gateway port: ${OPENCLAW_PORT}"
[ "$INSTALL_CHROME" = "true" ] && log "Chrome: $(google-chrome --version 2>/dev/null | head -1)"
[ "$ENABLE_FIREWALL" = "true" ] && log "Firewall: $(sudo ufw status | head -1)"
[ "$ENABLE_FAIL2BAN" = "true" ] && log "Fail2Ban: $(sudo fail2ban-client status sshd 2>/dev/null | grep 'Currently banned' || echo 'active')"
echo
echo "Next steps:"
echo "  1. Run 'openclaw' to configure your agent"
echo "  2. If restoring from backup: bash restore.sh <backup.tar.gz>"
echo "  3. Run 'bash verify.sh' to confirm everything works"
echo
