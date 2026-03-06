#!/bin/bash
set -e

echo "Installing patrick-cli..."

# Determine install directory
INSTALL_DIR="${PATRICK_DATA_PATH:-$HOME/.patrick}/bin"
mkdir -p "$INSTALL_DIR"

# Detect platform
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
case "$OS" in
    darwin) OS="macos" ;;
    mingw*|msys*|cygwin*) OS="windows" ;;
esac
ARCH=$(uname -m)

# Map architecture names
case "$ARCH" in
    x86_64)
        ARCH="x86_64"
        ;;
    arm64|aarch64)
        ARCH="aarch64"
        ;;
    *)
        echo "Error: Unsupported architecture: $ARCH"
        exit 1
        ;;
esac

# Build binary name
BINARY_NAME="patrick-cli-${OS}-${ARCH}"
if [ "$OS" = "windows" ]; then
    BINARY_NAME="${BINARY_NAME}.exe"
fi

# Download base URL — defaults to hosted server, overridable via env
BASE_URL="${PATRICK_SERVER_URL:-https://portal.patrickbot.io}/downloads/latest"

echo "Downloading patrick-cli for ${OS}-${ARCH}..."
echo "URL: ${BASE_URL}/${BINARY_NAME}"

# Download the binary
if command -v curl &> /dev/null; then
    curl -fL "${BASE_URL}/${BINARY_NAME}" -o "$INSTALL_DIR/patrick-cli"
elif command -v wget &> /dev/null; then
    wget "${BASE_URL}/${BINARY_NAME}" -O "$INSTALL_DIR/patrick-cli"
else
    echo "Error: Neither curl nor wget found. Please install one of them."
    exit 1
fi

# Verify SHA256 checksum
echo "Verifying checksum..."
CHECKSUMS=$(mktemp)
if command -v curl &> /dev/null; then
    curl -fsSL "${BASE_URL}/checksums-sha256.txt" -o "$CHECKSUMS"
elif command -v wget &> /dev/null; then
    wget -q "${BASE_URL}/checksums-sha256.txt" -O "$CHECKSUMS"
fi

if [ -s "$CHECKSUMS" ]; then
    EXPECTED=$(grep "$BINARY_NAME" "$CHECKSUMS" | awk '{print $1}')
    if [ -n "$EXPECTED" ]; then
        if command -v sha256sum &> /dev/null; then
            ACTUAL=$(sha256sum "$INSTALL_DIR/patrick-cli" | awk '{print $1}')
        elif command -v shasum &> /dev/null; then
            ACTUAL=$(shasum -a 256 "$INSTALL_DIR/patrick-cli" | awk '{print $1}')
        else
            echo "Warning: No sha256sum or shasum found, skipping checksum verification"
            ACTUAL="$EXPECTED"
        fi

        if [ "$EXPECTED" != "$ACTUAL" ]; then
            echo "Error: Checksum mismatch!"
            echo "  Expected: $EXPECTED"
            echo "  Got:      $ACTUAL"
            rm -f "$INSTALL_DIR/patrick-cli"
            rm -f "$CHECKSUMS"
            exit 1
        fi
        echo "  Checksum verified OK"
    else
        echo "  Warning: Binary not found in checksums file, skipping verification"
    fi
else
    echo "  Warning: Could not download checksums, skipping verification"
fi
rm -f "$CHECKSUMS"

# Make it executable
chmod +x "$INSTALL_DIR/patrick-cli"

echo "Patrick CLI installed to $INSTALL_DIR/patrick-cli"
echo ""
echo "Make sure $INSTALL_DIR is in your PATH:"
echo "  export PATH=\"$INSTALL_DIR:\$PATH\""
echo ""
echo "Next steps:"
echo "  1. Get your license at: https://patrickbot.io"
echo "  2. Initialize Patrick: patrick-cli fetch initialize"
echo "  3. Set up cronjobs for daily briefings (see install.md)"
