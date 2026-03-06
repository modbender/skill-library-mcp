#!/usr/bin/env bash
set -euo pipefail

# Installs the wrapper into ~/.local/bin for stable PATH + systemd usage.
# Creates ONE symlink (no extension) pointing at the skill's wrapper source.

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_REL="$SKILL_DIR/bin/openclaw-whisper-stt.sh"
SRC="$(readlink -f "$SRC_REL")"

DST_DIR="$HOME/.local/bin"
DST_PRIMARY="$DST_DIR/openclaw-whisper-stt"

mkdir -p "$DST_DIR"

# Ensure the target is executable (symlink itself doesn't carry exec perms).
chmod +x "$SRC"

# Primary symlink (no extension)
ln -sf "$SRC" "$DST_PRIMARY"

# Sanity checks
[ -L "$DST_PRIMARY" ] || { echo "Expected symlink: $DST_PRIMARY" >&2; exit 2; }
[ -x "$DST_PRIMARY" ] || { echo "Not executable: $DST_PRIMARY" >&2; exit 3; }

echo "[OK] Linked: $DST_PRIMARY -> $SRC"
