#!/usr/bin/env bash
# keygen.sh – Generate and store a MMAG encryption key
# Usage: bash keygen.sh [--output <path>]
#
# Generates a 32-byte random key and saves it to ~/.openclaw/skills/mmag/.key
# The key file is chmod 600 (owner read-only).
# Set MMAG_KEY_FILE to override the default location.

set -euo pipefail

KEY_FILE="${MMAG_KEY_FILE:-$HOME/.openclaw/skills/mmag/.key}"
OUTPUT="${1:-}"

if [ -n "$OUTPUT" ]; then
  KEY_FILE="$OUTPUT"
fi

# Parse --output flag
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output) KEY_FILE="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [ -f "$KEY_FILE" ]; then
  echo "⚠️  Key file already exists: $KEY_FILE"
  read -rp "   Overwrite? [y/N] " confirm </dev/tty
  if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "   Aborting."
    exit 0
  fi
fi

# Create parent directory if needed
mkdir -p "$(dirname "$KEY_FILE")"

# Generate a 32-byte (256-bit) random key, base64-encoded
openssl rand -base64 32 > "$KEY_FILE"
chmod 600 "$KEY_FILE"

echo ""
echo "✅ Key generated: $KEY_FILE"
echo "   Permissions: $(ls -la "$KEY_FILE" | awk '{print $1, $3, $4}')"
echo ""
echo "   ⚠️  Back up this key file. Without it, encrypted memories cannot be recovered."
echo ""
echo "Next steps:"
echo "  Encrypt long-term layer:  bash skill/encrypt.sh --layer long-term"
echo "  Decrypt when needed:      bash skill/decrypt.sh --layer long-term"
echo ""
echo "  Or set the key inline (no file):  export MMAG_KEY=\$(cat $KEY_FILE)"
