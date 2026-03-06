#!/usr/bin/env bash

set -euo pipefail

REPO="Ikana/temporal"
DEFAULT_VERSION="v0.1.0"

# Detect supported platform.
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case "$OS" in
  darwin) OS="darwin" ;;
  linux) OS="linux" ;;
  *)
    echo "Unsupported OS: $OS. Supported OS values are: darwin, linux." >&2
    exit 1
    ;;
esac

case "$ARCH" in
  arm64|aarch64) ARCH="arm64" ;;
  x86_64) ARCH="x64" ;;
  *)
    echo "Unsupported architecture: $ARCH" >&2
    exit 1
    ;;
esac

VERSION="${TEMPORAL_VERSION:-$DEFAULT_VERSION}"
FILE="temporal-${OS}-${ARCH}"

resolve_latest_version() {
  local tag
  if ! tag="$(
    curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
      | sed -n 's/.*"tag_name":[[:space:]]*"\([^"]*\)".*/\1/p' \
      | head -n1
  )"; then
    echo "Failed to resolve latest release tag for ${REPO}: unable to query GitHub API (network issue or API rate limiting)." >&2
    exit 1
  fi
  if [ -z "$tag" ]; then
    echo "Failed to resolve latest release tag for ${REPO}" >&2
    exit 1
  fi
  printf '%s' "$tag"
}

lookup_bundled_checksum() {
  case "${VERSION}:${FILE}" in
    "v0.1.0:temporal-darwin-arm64") echo "e8301eb9ef0f3d30528521aba539ed6c68d4c692b8d896c08ebf6c4037402ab1" ;;
    "v0.1.0:temporal-darwin-x64") echo "332a764aa5c218a1a22809e673d5db566595d49d5115e5157fc9bde15969ba28" ;;
    "v0.1.0:temporal-linux-arm64") echo "41ad177664c33f93d1062776b29facc90d1505a9b4effa7b0d72edf516687c5f" ;;
    "v0.1.0:temporal-linux-x64") echo "06e9e6c22653a74dd895357cf122e2950b508d7bc607e56272947d91e024a0d5" ;;
    *) return 1 ;;
  esac
}

if [ "$VERSION" = "latest" ]; then
  VERSION="$(resolve_latest_version)"
fi

RELEASE_URL="https://github.com/${REPO}/releases/download/${VERSION}"

if [ -n "${TEMPORAL_SHA256:-}" ]; then
  EXPECTED_SUM="${TEMPORAL_SHA256}"
elif EXPECTED_SUM="$(lookup_bundled_checksum)"; then
  :
else
  echo "No bundled checksum available for ${VERSION} (${FILE})." >&2
  echo "Set TEMPORAL_SHA256 to an independently obtained SHA-256 digest to continue." >&2
  exit 1
fi

if ! printf '%s' "$EXPECTED_SUM" | grep -Eq '^[A-Fa-f0-9]{64}$'; then
  echo "Invalid TEMPORAL_SHA256/expected checksum: must be a 64-character hex digest." >&2
  exit 1
fi
EXPECTED_SUM="$(printf '%s' "$EXPECTED_SUM" | tr '[:upper:]' '[:lower:]')"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

curl -fsSL "${RELEASE_URL}/${FILE}" -o "${TMP_DIR}/${FILE}"

if command -v sha256sum >/dev/null 2>&1; then
  ACTUAL_SUM="$(sha256sum "${TMP_DIR}/${FILE}" | awk '{ print $1 }')"
elif command -v shasum >/dev/null 2>&1; then
  ACTUAL_SUM="$(shasum -a 256 "${TMP_DIR}/${FILE}" | awk '{ print $1 }')"
else
  echo "No SHA-256 tool found (expected sha256sum or shasum)." >&2
  exit 1
fi
ACTUAL_SUM="$(printf '%s' "$ACTUAL_SUM" | tr '[:upper:]' '[:lower:]')"

if [ "$ACTUAL_SUM" != "$EXPECTED_SUM" ]; then
  echo "Checksum mismatch for ${FILE}" >&2
  exit 1
fi

INSTALL_DIR="${TEMPORAL_INSTALL_DIR:-/usr/local/bin}"
if [ -z "${TEMPORAL_INSTALL_DIR:-}" ] && { [ ! -d "$INSTALL_DIR" ] || [ ! -w "$INSTALL_DIR" ]; }; then
  INSTALL_DIR="${HOME}/.local/bin"
fi

mkdir -p "$INSTALL_DIR"
install -m 0755 "${TMP_DIR}/${FILE}" "${INSTALL_DIR}/temporal"
echo "Installed temporal ${VERSION} to ${INSTALL_DIR}/temporal"
