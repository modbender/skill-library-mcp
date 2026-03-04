#!/usr/bin/env bash
set -euo pipefail

# build.sh — Build the workplace file-watcher server
# Usage: build.sh [--target <rust-target>]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SERVER_DIR="$SCRIPT_DIR/rust-server"
BIN_DIR="$SKILL_DIR/assets/bin"

# Source Rust env
if [[ -f "$HOME/.cargo/env" ]]; then
  source "$HOME/.cargo/env"
fi

if ! command -v cargo &>/dev/null; then
  echo "❌ Rust toolchain not found. Install via: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
  exit 1
fi

# Detect platform
ARCH="$(uname -m)"
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"

case "$ARCH" in
  x86_64) ARCH_SUFFIX="x86_64" ;;
  arm64|aarch64) ARCH_SUFFIX="arm64" ;;
  *) ARCH_SUFFIX="$ARCH" ;;
esac

PLATFORM="${OS}-${ARCH_SUFFIX}"
BINARY_NAME="workplace-server-${PLATFORM}"

echo "🔨 Building workplace-server for $PLATFORM..."

# Parse optional target
RUST_TARGET=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) RUST_TARGET="$2"; shift 2 ;;
    *) shift ;;
  esac
done

cd "$SERVER_DIR"

if [[ -n "$RUST_TARGET" ]]; then
  cargo build --release --target "$RUST_TARGET"
  RELEASE_BIN="target/$RUST_TARGET/release/workplace-server"
else
  cargo build --release
  RELEASE_BIN="target/release/workplace-server"
fi

if [[ ! -f "$RELEASE_BIN" ]]; then
  echo "❌ Build failed — binary not found at $RELEASE_BIN"
  exit 1
fi

mkdir -p "$BIN_DIR"
cp "$RELEASE_BIN" "$BIN_DIR/$BINARY_NAME"
chmod +x "$BIN_DIR/$BINARY_NAME"

echo "✅ Built: $BIN_DIR/$BINARY_NAME"
echo "   Size: $(du -h "$BIN_DIR/$BINARY_NAME" | cut -f1)"
