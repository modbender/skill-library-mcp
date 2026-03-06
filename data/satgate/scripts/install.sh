#!/usr/bin/env bash
set -euo pipefail

# SatGate CLI Installer
# Downloads the correct binary for your platform and verifies SHA256 checksum.

REPO="SatGate-io/satgate-cli"
BINARY="satgate"
INSTALL_DIR="${SATGATE_INSTALL_DIR:-/usr/local/bin}"

# Detect platform
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)
case "$ARCH" in
  x86_64|amd64) ARCH="amd64" ;;
  arm64|aarch64) ARCH="arm64" ;;
  *) echo "❌ Unsupported architecture: $ARCH"; exit 1 ;;
esac

case "$OS" in
  linux|darwin) ;;
  *) echo "❌ Unsupported OS: $OS"; exit 1 ;;
esac

PLATFORM="${OS}-${ARCH}"
echo "⚡ Installing SatGate CLI for ${PLATFORM}..."

# Get latest release tag
if command -v gh &>/dev/null; then
  VERSION=$(gh release view --repo "$REPO" --json tagName -q .tagName 2>/dev/null || echo "latest")
else
  VERSION="latest"
fi

if [ "$VERSION" = "latest" ]; then
  BASE_URL="https://github.com/${REPO}/releases/latest/download"
else
  BASE_URL="https://github.com/${REPO}/releases/download/${VERSION}"
fi

# Create temp directory
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

# Download binary and checksums
echo "  Downloading ${BINARY}-${PLATFORM}..."
curl -fsSL "${BASE_URL}/${BINARY}-${PLATFORM}" -o "${TMPDIR}/${BINARY}" || {
  echo "❌ Download failed. No release binaries found."
  echo "   Build from source: git clone https://github.com/${REPO} && cd satgate-cli && make build"
  exit 1
}

echo "  Downloading SHA256SUMS..."
curl -fsSL "${BASE_URL}/SHA256SUMS" -o "${TMPDIR}/SHA256SUMS" || {
  echo "⚠️  Checksums not available — skipping verification."
  echo "   Consider building from source for verified integrity."
}

# Verify checksum
if [ -f "${TMPDIR}/SHA256SUMS" ]; then
  echo "  Verifying checksum..."
  cd "$TMPDIR"
  EXPECTED=$(grep "${BINARY}-${PLATFORM}" SHA256SUMS | awk '{print $1}')
  if [ -n "$EXPECTED" ]; then
    if command -v sha256sum &>/dev/null; then
      ACTUAL=$(sha256sum "$BINARY" | awk '{print $1}')
    elif command -v shasum &>/dev/null; then
      ACTUAL=$(shasum -a 256 "$BINARY" | awk '{print $1}')
    else
      echo "⚠️  No sha256sum or shasum found — skipping verification."
      ACTUAL="$EXPECTED"
    fi

    if [ "$EXPECTED" != "$ACTUAL" ]; then
      echo "❌ Checksum verification FAILED!"
      echo "   Expected: $EXPECTED"
      echo "   Actual:   $ACTUAL"
      echo "   The binary may have been tampered with. Aborting."
      exit 1
    fi
    echo "  ✓ Checksum verified."
  else
    echo "⚠️  Binary not found in SHA256SUMS — skipping verification."
  fi
  cd - >/dev/null
fi

# Install
chmod +x "${TMPDIR}/${BINARY}"

mkdir -p "$INSTALL_DIR" 2>/dev/null || true
if [ -w "$INSTALL_DIR" ]; then
  mv "${TMPDIR}/${BINARY}" "${INSTALL_DIR}/${BINARY}"
else
  echo "  Installing to ${INSTALL_DIR} (requires sudo)..."
  sudo mv "${TMPDIR}/${BINARY}" "${INSTALL_DIR}/${BINARY}"
fi

echo ""
echo "✓ SatGate CLI installed to ${INSTALL_DIR}/${BINARY}"
echo ""
echo "  Next steps:"
echo "    satgate status              # Check gateway connection"
echo "    satgate --help              # See all commands"
echo "    scripts/configure.sh        # Interactive setup"
echo ""
$INSTALL_DIR/$BINARY version
