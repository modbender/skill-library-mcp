#!/usr/bin/env bash
# Shows OS-specific installation instructions for torrent clients.
# Usage: ./install-guide.sh [transmission|aria2]

set -euo pipefail

client="${1:-transmission}"

# --- OS Detection ---
os_name=$(uname -s)
distro="unknown"

case "$os_name" in
  Linux)
    if [ -f /etc/os-release ]; then
      # shellcheck source=/dev/null
      distro=$(. /etc/os-release && echo "${ID:-unknown}")
    fi
    ;;
  Darwin)
    distro="macos"
    ;;
  MINGW*|MSYS*|CYGWIN*)
    distro="windows"
    ;;
esac

echo "=== Install $client ==="
echo ""

case "$client" in
  transmission)
    case "$distro" in
      ubuntu|debian|pop|linuxmint|elementary)
        echo "Ubuntu/Debian:"
        echo "  sudo apt update && sudo apt install -y transmission-cli transmission-daemon"
        echo ""
        echo "Start daemon:"
        echo "  sudo systemctl start transmission-daemon"
        ;;
      fedora|rhel|centos|rocky|alma)
        echo "Fedora/RHEL:"
        echo "  sudo dnf install -y transmission-cli transmission-daemon"
        echo ""
        echo "Start daemon:"
        echo "  sudo systemctl start transmission-daemon"
        ;;
      arch|manjaro|endeavouros)
        echo "Arch Linux:"
        echo "  sudo pacman -S transmission-cli"
        echo ""
        echo "Start daemon:"
        echo "  sudo systemctl start transmission"
        ;;
      macos)
        echo "macOS:"
        echo "  brew install transmission-cli"
        echo ""
        echo "Start daemon:"
        echo "  transmission-daemon"
        ;;
      windows)
        echo "Windows:"
        echo "  Option 1: Use WSL and install with apt (recommended)"
        echo "    wsl sudo apt install -y transmission-cli transmission-daemon"
        echo ""
        echo "  Option 2: Download Transmission for Windows"
        echo "    https://transmissionbt.com/download/"
        ;;
      *)
        echo "Install transmission-cli using your distribution's package manager."
        echo "Package name is usually: transmission-cli or transmission-daemon"
        ;;
    esac
    echo ""
    echo "Verify installation:"
    echo "  transmission-remote --version"
    ;;
  aria2)
    case "$distro" in
      ubuntu|debian|pop|linuxmint|elementary)
        echo "Ubuntu/Debian:"
        echo "  sudo apt update && sudo apt install -y aria2"
        ;;
      fedora|rhel|centos|rocky|alma)
        echo "Fedora/RHEL:"
        echo "  sudo dnf install -y aria2"
        ;;
      arch|manjaro|endeavouros)
        echo "Arch Linux:"
        echo "  sudo pacman -S aria2"
        ;;
      macos)
        echo "macOS:"
        echo "  brew install aria2"
        ;;
      windows)
        echo "Windows:"
        echo "  Option 1: Use WSL and install with apt (recommended)"
        echo "    wsl sudo apt install -y aria2"
        echo ""
        echo "  Option 2: Download aria2 for Windows"
        echo "    https://github.com/aria2/aria2/releases"
        ;;
      *)
        echo "Install aria2 using your distribution's package manager."
        echo "Package name is usually: aria2"
        ;;
    esac
    echo ""
    echo "Verify installation:"
    echo "  aria2c --version"
    echo ""
    echo "Optional - Start RPC daemon for remote control:"
    echo "  aria2c --enable-rpc --rpc-listen-port=6800 --daemon"
    ;;
  *)
    echo "Unknown client: $client"
    echo "Supported clients: transmission, aria2"
    exit 1
    ;;
esac
