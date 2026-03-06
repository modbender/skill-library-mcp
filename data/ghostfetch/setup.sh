#!/bin/bash
# Ghostfetch — Setup Script
# Clones the repo at a pinned commit and builds the Go binary

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$HOME/.openclaw/workspace/tools"

# Pinned commit for reproducible builds
PINNED_COMMIT="6e6876a90470d4bb53e38be32e8f43e67b695b48"
REPO_URL="https://github.com/neothelobster/ghostfetch.git"

echo "=== Ghostfetch Setup ==="
echo "Source: $REPO_URL"
echo "Pinned: $PINNED_COMMIT"

# Check for Go
if ! command -v go &>/dev/null; then
    echo "ERROR: Go is not installed."
    echo "Install Go from https://go.dev/dl/ (requires Go 1.21+)"
    exit 1
fi

# Check for git
if ! command -v git &>/dev/null; then
    echo "ERROR: git is not installed."
    exit 1
fi

# Clone at pinned commit
REPO_DIR="/tmp/ghostfetch-build"
rm -rf "$REPO_DIR"
echo "Cloning ghostfetch at pinned commit..."
git clone "$REPO_URL" "$REPO_DIR"
git -C "$REPO_DIR" checkout "$PINNED_COMMIT"

# Verify checkout
ACTUAL_COMMIT="$(git -C "$REPO_DIR" rev-parse HEAD)"
if [ "$ACTUAL_COMMIT" != "$PINNED_COMMIT" ]; then
    echo "ERROR: Commit verification failed."
    echo "Expected: $PINNED_COMMIT"
    echo "Got:      $ACTUAL_COMMIT"
    exit 1
fi
echo "Commit verified: $PINNED_COMMIT"

# Build
echo "Building ghostfetch..."
cd "$REPO_DIR"
go build -o ghostfetch .

# Install
mkdir -p "$TOOLS_DIR"
cp ghostfetch "$TOOLS_DIR/ghostfetch"
chmod +x "$TOOLS_DIR/ghostfetch"

# Verify binary works
if "$TOOLS_DIR/ghostfetch" --help >/dev/null 2>&1; then
    echo ""
    echo "=== Setup complete ==="
    echo "Installed: $TOOLS_DIR/ghostfetch"
    echo "Run: ghostfetch --help"
else
    echo "ERROR: Built binary failed to run."
    exit 1
fi
