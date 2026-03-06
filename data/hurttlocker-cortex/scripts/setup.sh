#!/usr/bin/env bash
# Cortex setup — download binary + create wrapper + initialize DB
set -euo pipefail

CORTEX_VERSION="${CORTEX_VERSION:-latest}"
INSTALL_DIR="${CORTEX_INSTALL_DIR:-$HOME/bin}"
DB_PATH="${CORTEX_DB:-$HOME/.cortex/cortex.db}"
REPO="hurttlocker/cortex"

# Detect OS and arch
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"
case "$ARCH" in
    x86_64|amd64) ARCH="amd64" ;;
    arm64|aarch64) ARCH="arm64" ;;
    *) echo "ERROR: Unsupported architecture: $ARCH" >&2; exit 1 ;;
esac

echo "🧠 Cortex Setup"
echo "  OS: $OS  Arch: $ARCH"
echo "  Install to: $INSTALL_DIR/cortex"
echo "  Database: $DB_PATH"
echo ""

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$(dirname "$DB_PATH")"

# Check if already installed
if [[ -x "$INSTALL_DIR/cortex" ]]; then
    CURRENT="$("$INSTALL_DIR/cortex" version 2>/dev/null || echo "unknown")"
    echo "  Existing install: $CURRENT"
fi

# Download binary
if [[ "$CORTEX_VERSION" == "latest" ]]; then
    DOWNLOAD_URL="https://github.com/$REPO/releases/latest/download/cortex-${OS}-${ARCH}"
else
    DOWNLOAD_URL="https://github.com/$REPO/releases/download/$CORTEX_VERSION/cortex-${OS}-${ARCH}"
fi

echo "  Downloading: $DOWNLOAD_URL"
if command -v curl &>/dev/null; then
    curl -fSL "$DOWNLOAD_URL" -o "$INSTALL_DIR/cortex" 2>/dev/null
elif command -v wget &>/dev/null; then
    wget -q "$DOWNLOAD_URL" -O "$INSTALL_DIR/cortex"
else
    echo "ERROR: Need curl or wget" >&2; exit 1
fi
chmod +x "$INSTALL_DIR/cortex"

# Verify
VERSION="$("$INSTALL_DIR/cortex" version 2>/dev/null || echo "FAILED")"
if [[ "$VERSION" == "FAILED" ]]; then
    echo "ERROR: Binary not working after download" >&2
    exit 1
fi
echo "  Installed: $VERSION"

# Ensure ~/bin is in PATH
if ! echo "$PATH" | tr ':' '\n' | grep -q "$INSTALL_DIR"; then
    SHELL_RC=""
    if [[ -f "$HOME/.zshrc" ]]; then
        SHELL_RC="$HOME/.zshrc"
    elif [[ -f "$HOME/.bashrc" ]]; then
        SHELL_RC="$HOME/.bashrc"
    fi
    if [[ -n "$SHELL_RC" ]]; then
        echo "" >> "$SHELL_RC"
        echo "# Cortex CLI" >> "$SHELL_RC"
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_RC"
        echo "  Added $INSTALL_DIR to PATH in $SHELL_RC"
    fi
fi

echo ""
echo "✅ Cortex ready."
echo "  Binary: $INSTALL_DIR/cortex"
echo "  Next: Import your memory files:"
echo "    cortex import /path/to/notes --extract"
echo "    cortex search \"what you're looking for\""
