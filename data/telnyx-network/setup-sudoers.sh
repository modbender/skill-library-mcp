#!/bin/bash
#
# setup-sudoers.sh - Enable passwordless sudo for WireGuard (one-time setup)
#
# This allows OpenClaw to manage WireGuard interfaces autonomously.
# Run once with: sudo ./setup-sudoers.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Detect WireGuard binary locations
WG_PATHS=""
for path in /usr/bin/wg /usr/bin/wg-quick /opt/homebrew/bin/wg /opt/homebrew/bin/wg-quick /usr/local/bin/wg /usr/local/bin/wg-quick; do
    if [ -x "$path" ]; then
        if [ -n "$WG_PATHS" ]; then
            WG_PATHS="$WG_PATHS, $path"
        else
            WG_PATHS="$path"
        fi
    fi
done

if [ -z "$WG_PATHS" ]; then
    echo -e "${RED}❌ WireGuard not found${NC}"
    echo "Install WireGuard first:"
    echo "  macOS:  brew install wireguard-tools"
    echo "  Ubuntu: sudo apt install wireguard"
    exit 1
fi

# Get the actual user (not root if running with sudo)
TARGET_USER="${SUDO_USER:-$USER}"

if [ "$TARGET_USER" = "root" ]; then
    echo -e "${RED}❌ Don't run this as root${NC}"
    echo "Run as: sudo ./setup-sudoers.sh"
    exit 1
fi

# Build sudoers line
SUDOERS_LINE="$TARGET_USER ALL=(ALL) NOPASSWD: $WG_PATHS"
SUDOERS_FILE="/etc/sudoers.d/wireguard-$TARGET_USER"

echo ""
echo -e "${YELLOW}🔐 WireGuard Passwordless Sudo Setup${NC}"
echo "========================================"
echo ""
echo "This enables OpenClaw to manage WireGuard without password prompts."
echo ""
echo "User: $TARGET_USER"
echo "File: $SUDOERS_FILE"
echo ""
echo "Will add:"
echo -e "  ${GREEN}$SUDOERS_LINE${NC}"
echo ""
echo "This allows ONLY these specific commands without password:"
echo "$WG_PATHS" | tr ',' '\n' | while read -r path; do
    path=$(echo "$path" | xargs)  # trim whitespace
    [ -n "$path" ] && echo "  • $path"
done
echo ""

# Check if already configured
if [ -f "$SUDOERS_FILE" ]; then
    echo -e "${YELLOW}⚠️  Sudoers file already exists${NC}"
    echo "Current contents:"
    cat "$SUDOERS_FILE"
    echo ""
    read -p "Overwrite? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ This script needs sudo${NC}"
    echo "Run as: sudo ./setup-sudoers.sh"
    exit 1
fi

read -p "Continue? [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Write sudoers file
    echo "$SUDOERS_LINE" > "$SUDOERS_FILE"
    chmod 440 "$SUDOERS_FILE"
    
    # Validate syntax
    if visudo -c -f "$SUDOERS_FILE" > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✅ Done!${NC}"
        echo ""
        echo "OpenClaw can now manage WireGuard without password prompts."
        echo ""
        echo "Test it:"
        echo "  sudo wg --version"
        echo ""
        echo "To undo later:"
        echo "  sudo rm $SUDOERS_FILE"
    else
        echo -e "${RED}❌ Invalid sudoers syntax - removing${NC}"
        rm -f "$SUDOERS_FILE"
        exit 1
    fi
else
    echo "Cancelled."
fi
