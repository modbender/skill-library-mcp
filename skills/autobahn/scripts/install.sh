#!/usr/bin/env bash
set -euo pipefail

VERSION="${AUTOBAHN_VERSION:-v0.4.0}"
INSTALL_DIR="${AUTOBAHN_INSTALL_DIR:-$HOME/.autobahn/bin}"
REPO="unifiedh/autobahn-releases"

# Detect platform
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case "$ARCH" in
  arm64|aarch64) ARCH_SUFFIX="arm64" ;;
  x86_64|amd64)  ARCH_SUFFIX="x64" ;;
  *) echo "Unsupported architecture: $ARCH" >&2; exit 1 ;;
esac

case "$OS" in
  darwin|linux) ;;
  *) echo "Unsupported OS: $OS" >&2; exit 1 ;;
esac

ASSET="autobahn-${OS}-${ARCH_SUFFIX}"
URL="https://github.com/${REPO}/releases/download/${VERSION}/${ASSET}"

VERSION_FILE="${INSTALL_DIR}/.autobahn-version"

# Check if already installed at the requested version
if [ -x "${INSTALL_DIR}/autobahn" ] && [ -f "$VERSION_FILE" ] && [ "$(cat "$VERSION_FILE")" = "$VERSION" ]; then
  echo "autobahn ${VERSION} already installed at ${INSTALL_DIR}/autobahn" >&2
  echo "${INSTALL_DIR}/autobahn"
  exit 0
fi

echo "Downloading autobahn ${VERSION} for ${OS}-${ARCH_SUFFIX}..." >&2

mkdir -p "$INSTALL_DIR"

if command -v curl >/dev/null 2>&1; then
  curl -fsSL -o "${INSTALL_DIR}/autobahn" "$URL"
elif command -v wget >/dev/null 2>&1; then
  wget -q -O "${INSTALL_DIR}/autobahn" "$URL"
else
  echo "Neither curl nor wget found" >&2
  exit 1
fi

chmod +x "${INSTALL_DIR}/autobahn"
echo "$VERSION" > "$VERSION_FILE"
echo "Installed autobahn ${VERSION} to ${INSTALL_DIR}/autobahn" >&2
echo "${INSTALL_DIR}/autobahn"
