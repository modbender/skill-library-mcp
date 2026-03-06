#!/bin/bash
# MindGraph Server Setup
# Downloads the pre-built binary from GitHub Releases

set -e

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BINARY="$SCRIPTS_DIR/mindgraph-server"
REPO="shuruheel/mindgraph-rs"
VERSION="${MINDGRAPH_VERSION:-latest}"

# Check if already installed
if [ -f "$BINARY" ] && [ -x "$BINARY" ]; then
  echo "✅ mindgraph-server already installed at $BINARY"
  exit 0
fi

# Detect platform
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

if [ "$OS" != "linux" ] || [ "$ARCH" != "x86_64" ]; then
  echo "⚠️  Pre-built binary is only available for Linux x86_64."
  echo "   To build from source:"
  echo "   git clone https://github.com/$REPO.git && cd mindgraph-rs && cargo build --release"
  echo "   cp target/release/mindgraph-server $BINARY"
  exit 1
fi

echo "📦 Downloading mindgraph-server from GitHub Releases..."

if [ "$VERSION" = "latest" ]; then
  DOWNLOAD_URL="https://github.com/$REPO/releases/latest/download/mindgraph-server"
else
  DOWNLOAD_URL="https://github.com/$REPO/releases/download/$VERSION/mindgraph-server"
fi

curl -fsSL "$DOWNLOAD_URL" -o "$BINARY"
chmod +x "$BINARY"

echo "✅ mindgraph-server installed at $BINARY"
echo ""
echo "Start the server with:"
echo "  bash $SCRIPTS_DIR/start.sh"
