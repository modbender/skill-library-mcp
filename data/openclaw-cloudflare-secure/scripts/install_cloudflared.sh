#!/usr/bin/env bash
set -euo pipefail

# Installs cloudflared from the official GitHub release .deb (amd64).
# Safe to rerun.

if command -v cloudflared >/dev/null 2>&1; then
  echo "cloudflared already installed: $(cloudflared --version)"
  exit 0
fi

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

cd "$tmpdir"
wget -qO cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i ./cloudflared.deb
cloudflared --version
