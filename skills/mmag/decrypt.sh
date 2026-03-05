#!/usr/bin/env bash
# decrypt.sh – Decrypt MMAG memory files encrypted with encrypt.sh
# Usage: bash decrypt.sh [--layer <layer>] [--file <path>] [--root <memory-root>]
#        bash decrypt.sh --stdout --file <path.md.enc>   # pipe decrypted content to stdout
#
# Key resolution order:
#   1. MMAG_KEY environment variable
#   2. ~/.openclaw/skills/mmag/.key file
#   3. Interactive passphrase prompt
#
# Modes:
#   Default  – decrypt .md.enc files → .md files on disk, remove .enc originals
#   --stdout – decrypt a single .md.enc to stdout (for context.sh / retrieve.sh piping)

set -euo pipefail

ROOT="memory"
LAYER="long-term"
TARGET_FILE=""
STDOUT_MODE=false
KEY_FILE="${MMAG_KEY_FILE:-$HOME/.openclaw/skills/mmag/.key}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --layer)  LAYER="$2";       shift 2 ;;
    --file)   TARGET_FILE="$2"; shift 2 ;;
    --root)   ROOT="$2";        shift 2 ;;
    --stdout) STDOUT_MODE=true; shift   ;;
    *) shift ;;
  esac
done

# ── Key resolution ─────────────────────────────────────────────────────────────
resolve_key() {
  if [ -n "${MMAG_KEY:-}" ]; then
    echo "$MMAG_KEY"
    return
  fi
  if [ -f "$KEY_FILE" ]; then
    cat "$KEY_FILE"
    return
  fi
  read -rsp "🔑 MMAG passphrase: " PASSPHRASE </dev/tty >&2
  echo "" >&2
  echo "$PASSPHRASE"
}

# ── Decrypt a single file to stdout ───────────────────────────────────────────
decrypt_to_stdout() {
  local src="$1"
  local key="$2"
  echo "$key" | openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 \
    -pass stdin \
    -in "$src" 2>/dev/null
}

# ── Decrypt a single file to disk ─────────────────────────────────────────────
decrypt_to_disk() {
  local src="$1"
  local key="$2"
  local dst="${src%.md.enc}.md"

  echo "$key" | openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 \
    -pass stdin \
    -in  "$src" \
    -out "$dst" 2>/dev/null

  rm -f "$src"
  echo "  🔓 Decrypted: $(basename "$src") → $(basename "$dst")" >&2
}

# ── Main ───────────────────────────────────────────────────────────────────────
KEY=$(resolve_key)

if [ -n "$TARGET_FILE" ]; then
  if [ ! -f "$TARGET_FILE" ]; then
    echo "❌ File not found: $TARGET_FILE" >&2; exit 1
  fi
  if $STDOUT_MODE; then
    decrypt_to_stdout "$TARGET_FILE" "$KEY"
  else
    decrypt_to_disk "$TARGET_FILE" "$KEY"
    echo "✅ Decrypted."
  fi
else
  LAYER_DIR="$ROOT/$LAYER"
  if [ ! -d "$LAYER_DIR" ]; then
    echo "❌ Layer directory not found: $LAYER_DIR (run init.sh)" >&2; exit 1
  fi

  enc_files=$(find "$LAYER_DIR" -name "*.md.enc" 2>/dev/null || true)
  if [ -z "$enc_files" ]; then
    echo "  ℹ️  No encrypted files found in $LAYER_DIR"
    exit 0
  fi

  echo "🔓 Decrypting $LAYER layer..." >&2
  while IFS= read -r f; do
    decrypt_to_disk "$f" "$KEY"
  done <<< "$enc_files"

  echo "" >&2
  echo "✅ Decryption complete." >&2
fi
