#!/usr/bin/env bash
set -euo pipefail

# Manage sample packs for strudel-music
# Usage:
#   samples-manage.sh list              — show installed packs
#   samples-manage.sh download          — download/refresh dirt-samples (idempotent)
#   samples-manage.sh add <url>         — download sample pack from URL
#   samples-manage.sh add <path>        — copy/link local directory
#   samples-manage.sh remove <name>     — remove a sample pack

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SAMPLES_DIR="$ROOT_DIR/samples"

# Configurable download limits
STRUDEL_MAX_DOWNLOAD_MB="${STRUDEL_MAX_DOWNLOAD_MB:-10240}"  # 10GB default
STRUDEL_ALLOWED_HOSTS="${STRUDEL_ALLOWED_HOSTS:-}"           # empty = allow all

mkdir -p "$SAMPLES_DIR"

_check_allowed_host() {
  local URL="$1"
  [ -z "$STRUDEL_ALLOWED_HOSTS" ] && return 0  # no allowlist = allow all
  local HOST
  HOST=$(echo "$URL" | sed -E 's|^https?://([^/:]+).*|\1|')
  IFS=',' read -ra HOSTS <<< "$STRUDEL_ALLOWED_HOSTS"
  for allowed in "${HOSTS[@]}"; do
    allowed=$(echo "$allowed" | xargs)  # trim whitespace
    [ "$HOST" = "$allowed" ] && return 0
  done
  echo "❌ Host '$HOST' not in STRUDEL_ALLOWED_HOSTS ($STRUDEL_ALLOWED_HOSTS)"
  return 1
}

_check_download_size() {
  local URL="$1"
  local MAX_BYTES=$(( STRUDEL_MAX_DOWNLOAD_MB * 1024 * 1024 ))
  local CONTENT_LENGTH
  CONTENT_LENGTH=$(curl -fsSLI "$URL" 2>/dev/null | grep -i '^content-length:' | tail -1 | tr -d '[:space:]' | cut -d: -f2)
  if [ -n "$CONTENT_LENGTH" ] && [ "$CONTENT_LENGTH" -gt "$MAX_BYTES" ] 2>/dev/null; then
    echo "❌ Download too large: $(( CONTENT_LENGTH / 1024 / 1024 ))MB exceeds ${STRUDEL_MAX_DOWNLOAD_MB}MB limit"
    echo "   Set STRUDEL_MAX_DOWNLOAD_MB to increase (current: ${STRUDEL_MAX_DOWNLOAD_MB})"
    return 1
  fi
  return 0
}

_validate_archive_mime() {
  local FILE="$1"
  local MIME
  MIME=$(file --mime-type -b "$FILE" 2>/dev/null || echo "unknown")
  case "$MIME" in
    application/zip|application/x-tar|application/gzip|application/x-gzip|audio/x-wav|audio/wav)
      return 0 ;;
    application/octet-stream)
      # Fallback: check extension for common false positives
      return 0 ;;
    *)
      echo "❌ Unexpected MIME type: $MIME (expected archive or audio)"
      return 1 ;;
  esac
}

_add_from_url() {
  local URL="$1"
  local TMP FILENAME

  # Host allowlist check
  _check_allowed_host "$URL" || return 1

  # Pre-flight size check
  _check_download_size "$URL" || return 1

  TMP=$(mktemp -d)
  FILENAME=$(basename "$URL")
  # Sanitize filename — strip path traversal chars
  FILENAME="${FILENAME//\.\./}"
  FILENAME="${FILENAME//\//}"
  if [ -z "$FILENAME" ]; then
    echo "❌ Invalid URL filename"
    rm -rf "$TMP"
    return 1
  fi
  local MAX_BYTES=$(( STRUDEL_MAX_DOWNLOAD_MB * 1024 * 1024 ))
  echo "Downloading $URL (limit: ${STRUDEL_MAX_DOWNLOAD_MB}MB)..."
  curl -fsSL --max-filesize "$MAX_BYTES" "$URL" -o "$TMP/$FILENAME" || {
    echo "❌ Download failed or exceeded ${STRUDEL_MAX_DOWNLOAD_MB}MB size limit"
    rm -rf "$TMP"
    return 1
  }

  # MIME type validation
  _validate_archive_mime "$TMP/$FILENAME" || {
    rm -rf "$TMP"
    return 1
  }

  case "$FILENAME" in
    *.zip)
      echo "Extracting ZIP..."
      # Zip slip protection: extract to temp, then validate all paths
      unzip -q "$TMP/$FILENAME" -d "$TMP/extracted"
      # Check for path traversal in extracted files
      while IFS= read -r entry; do
        RESOLVED=$(realpath -m "$TMP/extracted/$entry" 2>/dev/null)
        if [[ "$RESOLVED" != "$TMP/extracted"* ]]; then
          echo "❌ ZIP SLIP DETECTED: $entry escapes extraction directory. Aborting."
          rm -rf "$TMP"
          return 1
        fi
      done < <(unzip -l "$TMP/$FILENAME" 2>/dev/null | awk 'NR>3{print $NF}' | grep -v '^$' | head -1000)
      ;;
    *.tar.gz|*.tgz)
      echo "Extracting tar.gz..."
      mkdir -p "$TMP/extracted"
      # Tar automatically strips leading ../ but verify anyway
      tar xzf "$TMP/$FILENAME" -C "$TMP/extracted" --no-same-owner 2>&1 | grep -i "refused\|absolute\|\.\./" && {
        echo "❌ Archive contains suspicious paths. Aborting."
        rm -rf "$TMP"
        return 1
      } || true
      ;;
    *.tar)
      echo "Extracting tar..."
      mkdir -p "$TMP/extracted"
      tar xf "$TMP/$FILENAME" -C "$TMP/extracted" --no-same-owner 2>&1 | grep -i "refused\|absolute\|\.\./" && {
        echo "❌ Archive contains suspicious paths. Aborting."
        rm -rf "$TMP"
        return 1
      } || true
      ;;
    *.wav|*.WAV)
      local NAME="${FILENAME%.*}"
      mkdir -p "$SAMPLES_DIR/$NAME"
      cp "$TMP/$FILENAME" "$SAMPLES_DIR/$NAME/"
      echo "✅ Added single sample: $NAME (1 file)"
      rm -rf "$TMP"
      return 0
      ;;
    *)
      echo "❌ Unsupported format: $FILENAME (expected .zip, .tar.gz, .tar, or .wav)"
      rm -rf "$TMP"
      return 1
      ;;
  esac

  local FOUND=0
  while IFS= read -r wav; do
    local DIR NAME COUNT
    DIR=$(dirname "$wav")
    NAME=$(basename "$DIR")
    if [ "$NAME" != "extracted" ]; then
      mkdir -p "$SAMPLES_DIR/$NAME"
      cp "$DIR"/*.wav "$DIR"/*.WAV "$SAMPLES_DIR/$NAME/" 2>/dev/null || true
      COUNT=$(find "$SAMPLES_DIR/$NAME" -name "*.wav" -o -name "*.WAV" | wc -l)
      echo "  ✅ $NAME: $COUNT samples"
      FOUND=$((FOUND + 1))
    fi
  done < <(find "$TMP/extracted" -name "*.wav" -o -name "*.WAV" | head -500)

  if [ "$FOUND" -eq 0 ]; then
    local NAME="${FILENAME%.*}"
    NAME="${NAME%.tar}"
    mkdir -p "$SAMPLES_DIR/$NAME"
    find "$TMP/extracted" \( -name "*.wav" -o -name "*.WAV" \) -exec cp {} "$SAMPLES_DIR/$NAME/" \;
    local COUNT
    COUNT=$(find "$SAMPLES_DIR/$NAME" -name "*.wav" -o -name "*.WAV" | wc -l)
    if [ "$COUNT" -gt 0 ]; then
      echo "✅ Added pack: $NAME ($COUNT samples)"
    else
      echo "❌ No WAV files found in download"
    fi
  fi

  rm -rf "$TMP"
}

case "${1:-help}" in
  list)
    echo "=== Installed Sample Packs ==="
    total=0
    for d in "$SAMPLES_DIR"/*/; do
      [ -d "$d" ] || continue
      name=$(basename "$d")
      count=$(find "$d" -maxdepth 1 -name "*.wav" -o -name "*.WAV" | wc -l)
      echo "  $name: $count samples"
      total=$((total + count))
    done
    echo ""
    echo "Total: $total samples in $(ls -d "$SAMPLES_DIR"/*/ 2>/dev/null | wc -l) packs"
    echo "Location: $SAMPLES_DIR"
    ;;

  download)
    exec bash "$SCRIPT_DIR/download-samples.sh"
    ;;

  add)
    SOURCE="${2:-}"
    if [ -z "$SOURCE" ]; then
      echo "Usage: $0 add <url-or-path>"
      echo ""
      echo "  URL:  Downloads and extracts (ZIP/tar.gz) into samples/"
      echo "  Path: Copies directory into samples/"
      exit 1
    fi

    if [[ "$SOURCE" == http* ]]; then
      _add_from_url "$SOURCE"
    elif [ -d "$SOURCE" ]; then
      NAME=$(basename "$SOURCE")
      echo "Copying $SOURCE → samples/$NAME/"
      cp -r "$SOURCE" "$SAMPLES_DIR/$NAME"
      COUNT=$(find "$SAMPLES_DIR/$NAME" -name "*.wav" -o -name "*.WAV" | wc -l)
      echo "✅ Added $NAME: $COUNT samples"
    elif [ -f "$SOURCE" ]; then
      NAME="${SOURCE%.*}"
      NAME=$(basename "$NAME")
      mkdir -p "$SAMPLES_DIR/$NAME"
      cp "$SOURCE" "$SAMPLES_DIR/$NAME/"
      echo "✅ Added single sample: $NAME"
    else
      echo "❌ Not found: $SOURCE"
      exit 1
    fi
    ;;

  remove)
    NAME="${2:-}"
    if [ -z "$NAME" ]; then
      echo "Usage: $0 remove <pack-name>"
      exit 1
    fi
    # Path traversal protection — reject names with slashes, dots, or special chars
    if [[ "$NAME" == */* ]] || [[ "$NAME" == ..* ]] || [[ "$NAME" == .* ]]; then
      echo "❌ Invalid pack name: $NAME (no paths, dots, or slashes allowed)"
      exit 1
    fi
    SAFE_PATH="$SAMPLES_DIR/$NAME"
    # Verify resolved path is still under SAMPLES_DIR
    RESOLVED=$(cd "$SAMPLES_DIR" 2>/dev/null && realpath -m "$NAME" 2>/dev/null)
    if [[ "$RESOLVED" != "$SAMPLES_DIR/"* ]]; then
      echo "❌ Path traversal detected: $NAME"
      exit 1
    fi
    if [ -d "$SAFE_PATH" ]; then
      COUNT=$(find "$SAFE_PATH" -name "*.wav" -o -name "*.WAV" | wc -l)
      rm -rf "${SAFE_PATH:?}"
      echo "✅ Removed $NAME ($COUNT samples)"
    else
      echo "❌ Pack not found: $NAME"
      exit 1
    fi
    ;;

  help|*)
    echo "strudel-music sample manager"
    echo ""
    echo "Usage: $0 <command> [args]"
    echo ""
    echo "Commands:"
    echo "  list              Show installed sample packs"
    echo "  download          Download/refresh default dirt-samples (idempotent)"
    echo "  add <url>         Download and extract sample pack from URL (.zip/.tar.gz/.wav)"
    echo "  add <path>        Copy local directory or file into samples/"
    echo "  remove <name>     Remove a sample pack"
    echo ""
    echo "Sample packs are directories of WAV files in: $SAMPLES_DIR"
    echo "Use them in patterns: s(\"<dir-name>\").n(0)"
    ;;
esac
