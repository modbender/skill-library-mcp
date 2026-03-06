#!/usr/bin/env bash
set -euo pipefail

# install_clamav.sh — Install and configure ClamAV
# Usage: install_clamav.sh [--help]

show_help() {
    cat <<'EOF'
Usage: install_clamav.sh [OPTIONS]

Install ClamAV antivirus engine and update virus signatures.

Options:
  --skip-update    Skip signature update (freshclam)
  --daemon         Also enable clamd daemon (needs more RAM)
  --help           Show this help

Environment:
  CLAWGUARD_FRESHCLAM_CONF   Path to freshclam.conf (auto-detected)

Supports: Ubuntu/Debian (apt), RHEL/CentOS/Fedora (yum/dnf), macOS (brew)
EOF
    exit 0
}

SKIP_UPDATE=false
ENABLE_DAEMON=false

for arg in "$@"; do
    case "$arg" in
        --skip-update) SKIP_UPDATE=true ;;
        --daemon) ENABLE_DAEMON=true ;;
        --help|-h) show_help ;;
        *) echo "Unknown option: $arg"; show_help ;;
    esac
done

log() { echo "[crusty] $*"; }
warn() { echo "[crusty] WARNING: $*" >&2; }
die() { echo "[crusty] ERROR: $*" >&2; exit 1; }

# Check if already installed
if command -v clamscan &>/dev/null; then
    log "ClamAV is already installed: $(clamscan --version 2>/dev/null || echo 'unknown version')"
    if [[ "$SKIP_UPDATE" == false ]]; then
        log "Updating signatures..."
        freshclam --quiet 2>/dev/null || warn "freshclam update failed (may need root or config fix)"
    fi
    exit 0
fi

# Detect OS and install
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        echo "${ID:-linux}"
    elif [[ "$(uname)" == "Darwin" ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
log "Detected OS: $OS"

# Check available RAM (MB)
get_ram_mb() {
    if [[ -f /proc/meminfo ]]; then
        awk '/MemTotal/ {printf "%d", $2/1024}' /proc/meminfo
    elif command -v sysctl &>/dev/null; then
        sysctl -n hw.memsize 2>/dev/null | awk '{printf "%d", $1/1048576}'
    else
        echo "0"
    fi
}

RAM_MB=$(get_ram_mb)
log "Available RAM: ${RAM_MB}MB"

if [[ "$RAM_MB" -gt 0 && "$RAM_MB" -lt 1024 ]]; then
    warn "Low RAM detected (<1GB). Will use clamscan only (no daemon)."
    ENABLE_DAEMON=false
fi

SUDO=""
if [[ "$(id -u)" -ne 0 ]] && command -v sudo &>/dev/null; then
    SUDO="sudo"
fi

case "$OS" in
    ubuntu|debian|pop|linuxmint|kali)
        log "Installing via apt..."
        $SUDO apt-get update -qq
        $SUDO apt-get install -y -qq clamav clamav-freshclam
        if [[ "$ENABLE_DAEMON" == true ]]; then
            $SUDO apt-get install -y -qq clamav-daemon
        fi
        ;;
    centos|rhel|fedora|rocky|alma|amzn)
        log "Installing via yum/dnf..."
        if command -v dnf &>/dev/null; then
            PKG="dnf"
        else
            PKG="yum"
        fi
        $SUDO $PKG install -y epel-release 2>/dev/null || true
        $SUDO $PKG install -y clamav clamav-update
        if [[ "$ENABLE_DAEMON" == true ]]; then
            $SUDO $PKG install -y clamd
        fi
        ;;
    macos)
        if ! command -v brew &>/dev/null; then
            die "Homebrew not found. Install from https://brew.sh"
        fi
        log "Installing via brew..."
        brew install clamav
        # Set up freshclam config
        BREW_PREFIX=$(brew --prefix)
        if [[ ! -f "$BREW_PREFIX/etc/clamav/freshclam.conf" ]]; then
            cp "$BREW_PREFIX/etc/clamav/freshclam.conf.sample" "$BREW_PREFIX/etc/clamav/freshclam.conf" 2>/dev/null || true
            sed -i '' 's/^Example/#Example/' "$BREW_PREFIX/etc/clamav/freshclam.conf" 2>/dev/null || true
        fi
        ;;
    *)
        die "Unsupported OS: $OS. Install ClamAV manually."
        ;;
esac

# Fix freshclam.conf if needed (comment out Example line)
for conf in /etc/clamav/freshclam.conf /etc/freshclam.conf /usr/local/etc/clamav/freshclam.conf; do
    if [[ -f "$conf" ]]; then
        if grep -q "^Example" "$conf" 2>/dev/null; then
            log "Fixing freshclam.conf at $conf"
            $SUDO sed -i.bak 's/^Example/#Example/' "$conf"
        fi
        break
    fi
done

# Stop freshclam service if running (can conflict)
$SUDO systemctl stop clamav-freshclam 2>/dev/null || true
$SUDO service clamav-freshclam stop 2>/dev/null || true

# Update signatures
if [[ "$SKIP_UPDATE" == false ]]; then
    log "Updating virus signatures (this may take a minute)..."
    if $SUDO freshclam --quiet 2>/dev/null; then
        log "Signatures updated successfully."
    else
        warn "freshclam failed. Signatures may be outdated. Try running: sudo freshclam"
    fi
fi

# Restart freshclam service
$SUDO systemctl start clamav-freshclam 2>/dev/null || true

# Verify
if command -v clamscan &>/dev/null; then
    log "✅ ClamAV installed successfully: $(clamscan --version 2>/dev/null)"
else
    die "Installation failed — clamscan not found in PATH"
fi
