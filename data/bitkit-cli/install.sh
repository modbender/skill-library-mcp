#!/bin/sh
set -eu

REPO="synonymdev/bitkit-cli"
BINARY="bitkit"

main() {
  os="$(uname -s | tr '[:upper:]' '[:lower:]')"
  arch="$(uname -m)"

  case "$os" in
    linux)  os="unknown-linux-musl" ;;
    darwin) os="apple-darwin" ;;
    *) echo "Unsupported OS: $os" >&2; exit 1 ;;
  esac

  case "$arch" in
    x86_64|amd64) arch="x86_64" ;;
    aarch64|arm64) arch="aarch64" ;;
    *) echo "Unsupported architecture: $arch" >&2; exit 1 ;;
  esac

  target="${arch}-${os}"
  base_url="https://github.com/${REPO}/releases/latest/download"

  # Find install directory
  if [ -w /usr/local/bin ]; then
    install_dir="/usr/local/bin"
  elif [ -d "$HOME/.local/bin" ] || mkdir -p "$HOME/.local/bin" 2>/dev/null; then
    install_dir="$HOME/.local/bin"
  else
    echo "Cannot find writable install directory." >&2
    echo "Run with sudo or create ~/.local/bin" >&2
    exit 1
  fi

  tmpdir="$(mktemp -d)"
  trap 'rm -rf "$tmpdir"' EXIT

  # Determine latest tag
  tag="$(curl -sSL -o /dev/null -w '%{url_effective}' "https://github.com/${REPO}/releases/latest" | grep -o '[^/]*$')"
  archive="${BINARY}-${tag}-${target}.tar.gz"

  echo "Installing ${BINARY} ${tag} for ${target}..."

  # Download archive and checksums
  curl -sSL "${base_url}/${archive}" -o "${tmpdir}/${archive}"
  curl -sSL "${base_url}/checksums.sha256" -o "${tmpdir}/checksums.sha256"

  # Verify checksum
  cd "$tmpdir"
  if command -v sha256sum >/dev/null 2>&1; then
    grep "$archive" checksums.sha256 | sha256sum -c --quiet
  elif command -v shasum >/dev/null 2>&1; then
    grep "$archive" checksums.sha256 | shasum -a 256 -c --quiet
  else
    echo "Warning: cannot verify checksum (no sha256sum or shasum found)" >&2
  fi

  # Extract and install
  tar xzf "$archive"
  dir="${BINARY}-${tag}-${target}"
  install -m 755 "${dir}/bitkit" "${install_dir}/bitkit"
  install -m 755 "${dir}/bk" "${install_dir}/bk"

  echo "Installed to ${install_dir}/bitkit (and ${install_dir}/bk)"
  echo "Run 'bitkit --help' to get started."
}

main
