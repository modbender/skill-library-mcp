#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RR_SRC="$SCRIPT_DIR/rr.sh"
TARGET_DIR="${HOME}/.local/bin"
TARGET="$TARGET_DIR/rr"

mkdir -p "$TARGET_DIR"
cp "$RR_SRC" "$TARGET"
chmod +x "$TARGET"

echo "✅ Installed rr to: $TARGET"
echo "If needed, add to PATH: export PATH=\"$TARGET_DIR:\$PATH\""
