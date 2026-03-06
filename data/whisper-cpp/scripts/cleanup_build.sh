#!/usr/bin/env bash
set -euo pipefail

# Removes whisper.cpp build/repo directories to save space.
# Safe if you've already installed whisper-cli + libs into ~/.local.

REPO="$HOME/.local/share/whisper.cpp/repo"

# Remove the repo (includes build output). Keep ~/.local/bin + ~/.local/lib + ~/.cache/whisper.
rm -rf "$REPO" || true

echo "[OK] Removed: $REPO"
