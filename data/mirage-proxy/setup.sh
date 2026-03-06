#!/bin/bash
# mirage-proxy setup for OpenClaw
# Usage: bash setup.sh [--uninstall]
set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="${HOME}/.openclaw/workspace"
MIRAGE_BIN="${WORKSPACE}/mirage-proxy-bin"
MIRAGE_LOG="${WORKSPACE}/mirage-proxy.log"
WRAPPER="${WORKSPACE}/start-mirage.sh"
VERSION="0.5.15"
REPO="chandika/mirage-proxy"

# SHA256 checksums for each platform binary (v0.5.15)
sha256_macos_arm64="d54af281c92d3684d55700421eb19df5da8034d98fe645c66eead096771be53c"
sha256_macos_x86_64="e21812e3eef34cc14c17c9a4b3264cfd86f9c2bf6a75f62c13be77570d9c746a"
sha256_linux_arm64="c12929f003407be1c668da7047bd6e82b9e491b0a93f5e01324266e3a2aacd0c"
sha256_linux_x86_64="f8477878836c282c6acdd1821702cfb7f6e37d6e8c663b3b7813d35d42092311"

# Detect platform
detect_platform() {
  local arch=$(uname -m)
  local os=$(uname -s | tr '[:upper:]' '[:lower:]')
  case "$arch" in
    aarch64|arm64) arch="arm64" ;;
    x86_64) arch="x86_64" ;;
    *) echo "Unsupported arch: $arch"; exit 1 ;;
  esac
  case "$os" in
    darwin) echo "macos-${arch}" ;;
    linux) echo "linux-${arch}" ;;
    *) echo "Unsupported OS: $os"; exit 1 ;;
  esac
}

# Get expected SHA256 for a platform string
expected_sha256() {
  local plat="$1"
  case "$plat" in
    macos-arm64)  echo "$sha256_macos_arm64" ;;
    macos-x86_64) echo "$sha256_macos_x86_64" ;;
    linux-arm64)  echo "$sha256_linux_arm64" ;;
    linux-x86_64) echo "$sha256_linux_x86_64" ;;
    *) echo ""; ;;
  esac
}

# Verify SHA256 of a file
verify_sha256() {
  local file="$1"
  local expected="$2"
  local actual

  if command -v sha256sum >/dev/null 2>&1; then
    actual=$(sha256sum "$file" | awk '{print $1}')
  elif command -v shasum >/dev/null 2>&1; then
    actual=$(shasum -a 256 "$file" | awk '{print $1}')
  else
    echo "  ⚠ No sha256sum or shasum found — skipping integrity check"
    return 0
  fi

  if [ "$actual" = "$expected" ]; then
    echo "  ✓ SHA256 verified"
    return 0
  else
    echo "  ✗ SHA256 mismatch!"
    echo "    Expected: $expected"
    echo "    Got:      $actual"
    echo "  The downloaded binary does not match the expected checksum."
    echo "  This could indicate a network issue or a tampered file. Aborting."
    rm -f "$file"
    exit 1
  fi
}

install() {
  echo "🔧 Installing mirage-proxy v${VERSION}..."

  # Download binary
  local plat=$(detect_platform)
  local url="https://github.com/${REPO}/releases/download/v${VERSION}/mirage-proxy-v${VERSION}-${plat}"
  local expected=$(expected_sha256 "$plat")

  echo "  ↓ Downloading ${plat} binary..."
  curl -sL -o "${MIRAGE_BIN}" "${url}"
  chmod +x "${MIRAGE_BIN}"

  # Verify integrity
  if [ -n "$expected" ]; then
    verify_sha256 "${MIRAGE_BIN}" "$expected"
  else
    echo "  ⚠ No checksum on record for platform ${plat} — skipping verification"
  fi

  # Verify it runs
  if ! "${MIRAGE_BIN}" --version >/dev/null 2>&1; then
    echo "  ⚠ Binary failed (glibc mismatch?). Building from source..."
    if command -v cargo >/dev/null 2>&1; then
      cargo install --git "https://github.com/${REPO}" --root "${WORKSPACE}/.cargo-mirage"
      cp "${WORKSPACE}/.cargo-mirage/bin/mirage-proxy" "${MIRAGE_BIN}"
    else
      echo "  ✗ No cargo found. Install Rust: https://rustup.rs"
      exit 1
    fi
  fi

  echo "  ✓ $(${MIRAGE_BIN} --version)"

  # Create auto-restart wrapper
  cat > "${WRAPPER}" << 'SCRIPT'
#!/bin/sh
while true; do
  MIRAGE_BIN_PATH --log-level info >> MIRAGE_LOG_PATH 2>&1
  sleep 2
done
SCRIPT
  sed -i "s|MIRAGE_BIN_PATH|${MIRAGE_BIN}|g" "${WRAPPER}" 2>/dev/null || \
    sed "s|MIRAGE_BIN_PATH|${MIRAGE_BIN}|g" "${WRAPPER}" > "${WRAPPER}.tmp" && mv "${WRAPPER}.tmp" "${WRAPPER}"
  sed -i "s|MIRAGE_LOG_PATH|${MIRAGE_LOG}|g" "${WRAPPER}" 2>/dev/null || \
    sed "s|MIRAGE_LOG_PATH|${MIRAGE_LOG}|g" "${WRAPPER}" > "${WRAPPER}.tmp" && mv "${WRAPPER}.tmp" "${WRAPPER}"
  chmod +x "${WRAPPER}"

  # Start it
  nohup "${WRAPPER}" > /dev/null 2>&1 &
  sleep 2

  # Verify it's running
  local status=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8686/ 2>/dev/null || echo "000")
  if [ "$status" = "502" ] || [ "$status" = "404" ]; then
    echo "  ✓ mirage-proxy running on :8686"
  else
    echo "  ✗ mirage-proxy failed to start (status: ${status})"
    echo "    Check logs: ${MIRAGE_LOG}"
    exit 1
  fi

  echo ""
  echo "✅ mirage-proxy installed and running!"
  echo ""
  echo "Next steps:"
  echo "  1. Ask your OpenClaw agent to configure mirage-proxy providers"
  echo "     (it will read the mirage-proxy skill and patch the config)"
  echo ""
  echo "  2. For persistence across container restarts, add to docker-compose.yml:"
  echo "     command: sh -c \"nohup ${WRAPPER} > /dev/null 2>&1 & exec openclaw start\""
  echo ""
  echo "  3. Switch models:"
  echo "     /model mirage-opus     → Anthropic Opus via mirage"
  echo "     /model anthropic-opus  → Anthropic Opus direct"
}

uninstall() {
  echo "🗑  Removing mirage-proxy..."
  kill $(ps aux | grep start-mirage | grep -v grep | awk '{print $2}') 2>/dev/null || true
  kill $(ps aux | grep mirage-proxy | grep -v grep | awk '{print $2}') 2>/dev/null || true
  rm -f "${MIRAGE_BIN}" "${WRAPPER}" "${MIRAGE_LOG}"
  echo "  ✓ Removed. Provider config in openclaw.json left untouched (remove manually if needed)."
}

case "${1:-}" in
  --uninstall) uninstall ;;
  *) install ;;
esac
