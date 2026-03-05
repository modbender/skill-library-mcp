#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 '<CLOUDFLARE_TUNNEL_TOKEN>'" >&2
  exit 2
fi

TOKEN="$1"

sudo cloudflared service install "$TOKEN"

# Ensure it's running
sudo systemctl enable --now cloudflared
sudo systemctl is-active cloudflared
