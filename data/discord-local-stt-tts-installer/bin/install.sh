#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This installer is macOS-only." >&2
  exit 1
fi

REPO="vilmire/discord-local-stt-tts"
INSTALL_DIR="$HOME/.openclaw/openclaw-extensions/plugins/discord-local-stt-tts"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

mkdir -p "$(dirname "$INSTALL_DIR")"

echo "Fetching latest release info for $REPO ..."
LATEST_JSON="$TMP_DIR/latest.json"
curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" -o "$LATEST_JSON"

TAG="$(python3 - <<'PY'
import json
print(json.load(open('$LATEST_JSON'))['tag_name'])
PY
)"

ZIP_URL="$(python3 - <<'PY'
import json
j=json.load(open('$LATEST_JSON'))
print(j['zipball_url'])
PY
)"

echo "Latest tag: $TAG"

echo "Downloading source zipball..."
ZIP_PATH="$TMP_DIR/src.zip"
curl -fL "$ZIP_URL" -o "$ZIP_PATH"

SRC_DIR="$TMP_DIR/src"
mkdir -p "$SRC_DIR"
unzip -q "$ZIP_PATH" -d "$SRC_DIR"

# GitHub zipball contains a single top-level folder
TOP_DIR="$(find "$SRC_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
if [[ -z "$TOP_DIR" ]]; then
  echo "Failed to locate extracted folder" >&2
  exit 1
fi

BACKUP_DIR="${INSTALL_DIR}.bak.$(date +%Y%m%d-%H%M%S)"
if [[ -d "$INSTALL_DIR" ]]; then
  echo "Backing up existing install to: $BACKUP_DIR"
  mv "$INSTALL_DIR" "$BACKUP_DIR"
fi

echo "Installing to: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp -R "$TOP_DIR"/* "$INSTALL_DIR"/

# Optional: build if dependencies exist
if command -v pnpm >/dev/null 2>&1; then
  echo "pnpm found: installing deps + building (best effort)"
  (cd "$INSTALL_DIR" && pnpm i && pnpm -s build) || true
else
  echo "pnpm not found: skipping build. If the plugin is not runnable, install pnpm and build manually."
fi

echo "Done. Next: openclaw gateway restart"
