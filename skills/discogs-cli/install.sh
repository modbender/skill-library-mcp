#!/bin/bash
# Exit immediately if a command exits with a non-zero status.
set -e

# Get the absolute path of the directory containing this script.
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$SKILL_DIR/scripts"
BIN_DIR="$SKILL_DIR/bin"
BINARY_PATH="$BIN_DIR/discogs-cli"

echo "==> Starting installation for discogs-cli skill..."

# 1. Create the bin directory
echo "==> Creating binary directory at $BIN_DIR"
mkdir -p "$BIN_DIR"

# 2. Navigate to the source directory
echo "==> Changing directory to $SCRIPTS_DIR"
cd "$SCRIPTS_DIR"

# 3. Build the Go binary
echo "==> Building Go binary..."
go build -o "$BINARY_PATH" .

# 4. Make the binary executable
chmod +x "$BINARY_PATH"

echo "==> Build complete. The binary is located at $BINARY_PATH"
echo "==> Installation successful!"
