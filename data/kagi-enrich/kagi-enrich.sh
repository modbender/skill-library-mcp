#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$BASE_DIR/.bin"
BIN="$BIN_DIR/kagi-enrich"

needs_build=0
if [[ ! -x "$BIN" ]]; then
  needs_build=1
else
  for src in "$BASE_DIR"/*.go "$BASE_DIR"/go.mod; do
    if [[ -e "$src" && "$src" -nt "$BIN" ]]; then
      needs_build=1
      break
    fi
  done
fi

if [[ "$needs_build" -eq 1 ]]; then
  mkdir -p "$BIN_DIR"

  if command -v go >/dev/null 2>&1; then
    GO_VERSION="$(go env GOVERSION 2>/dev/null || true)"
    if [[ -n "$GO_VERSION" ]]; then
      GO_VERSION="${GO_VERSION#go}"
      GO_MAJOR="${GO_VERSION%%.*}"
      GO_REST="${GO_VERSION#*.}"
      GO_MINOR="${GO_REST%%.*}"
      if [[ "$GO_MAJOR" -lt 1 || ( "$GO_MAJOR" -eq 1 && "$GO_MINOR" -lt 26 ) ]]; then
        echo "Warning: Go 1.26+ required to build, found go${GO_VERSION}. Falling back to pre-built binary." >&2
      else
        echo "Building kagi-enrich from source..." >&2
        (cd "$BASE_DIR" && go build -o "$BIN" .)
      fi
    fi
  fi

  if [[ ! -x "$BIN" ]]; then
    OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
    ARCH="$(uname -m)"
    case "$ARCH" in
      x86_64)        ARCH="amd64" ;;
      aarch64|arm64) ARCH="arm64" ;;
    esac

    if command -v curl >/dev/null 2>&1; then
      RELEASE_META="$(curl -fsSL "https://api.github.com/repos/joelazar/kagi-skills/releases/latest")"
    elif command -v wget >/dev/null 2>&1; then
      RELEASE_META="$(wget -qO- "https://api.github.com/repos/joelazar/kagi-skills/releases/latest")"
    else
      echo "Error: Neither curl nor wget found. Please download the binary manually from:" >&2
      echo "  https://github.com/joelazar/kagi-skills/releases/latest" >&2
      exit 1
    fi

    TAG="$(printf '%s\n' "$RELEASE_META" | grep -m1 '"tag_name"' | cut -d'"' -f4 || true)"
    if [[ -z "$TAG" ]]; then
      echo "Error: Could not resolve latest release tag from GitHub API." >&2
      echo "Please download manually from: https://github.com/joelazar/kagi-skills/releases/latest" >&2
      exit 1
    fi

    BINARY="kagi-enrich_${TAG}_${OS}_${ARCH}"
    URL="https://github.com/joelazar/kagi-skills/releases/download/${TAG}/${BINARY}"

    echo "kagi-enrich binary not found. Download pre-built binary from GitHub releases?" >&2
    echo "  $URL" >&2
    read -r -p "Download? [Y/n] " reply >&2 </dev/tty
    case "${reply:-Y}" in
      [Yy]*|"") ;;
      *) echo "Aborted. Install Go 1.26+ to build from source, or download manually:" >&2
         echo "  $URL" >&2
         exit 1 ;;
    esac

    if command -v curl >/dev/null 2>&1; then
      curl -fsSL "$URL" -o "$BIN"
    else
      wget -qO "$BIN" "$URL"
    fi

    chmod +x "$BIN"
  fi
fi

exec "$BIN" "$@"
