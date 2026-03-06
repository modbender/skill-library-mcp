#!/usr/bin/env bash
# Install stegstr-cli from source. Requires Rust (rustup) and git.
set -e

REPO_URL="${STEGSTR_REPO_URL:-https://github.com/brunkstr/Stegstr.git}"
INSTALL_DIR="${STEGSTR_INSTALL_DIR:-$HOME/.local/stegstr}"
BIN_DIR="${STEGSTR_BIN_DIR:-$HOME/.local/bin}"

echo "Cloning Stegstr..."
mkdir -p "$(dirname "$INSTALL_DIR")"
if [ -d "$INSTALL_DIR" ]; then
  (cd "$INSTALL_DIR" && git pull)
else
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

echo "Building stegstr-cli..."
(cd "$INSTALL_DIR/src-tauri" && cargo build --release --bin stegstr-cli)

mkdir -p "$BIN_DIR"
ln -sf "$INSTALL_DIR/src-tauri/target/release/stegstr-cli" "$BIN_DIR/stegstr-cli"

echo "Installed stegstr-cli to $BIN_DIR/stegstr-cli"
echo "Ensure $BIN_DIR is in your PATH."
echo ""
echo "Usage:"
echo "  stegstr-cli decode image.png"
echo "  stegstr-cli detect image.png"
echo "  stegstr-cli embed cover.png -o out.png --payload @bundle.json --encrypt"
echo "  stegstr-cli post \"message\" --output bundle.json"
