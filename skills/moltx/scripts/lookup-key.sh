#!/usr/bin/env bash
# Extract MoltX API key from credentials store
set -euo pipefail
grep -i "moltx" "$HOME/.openclaw/secrets/credentials.md" | grep -oP 'moltx_sk_[a-f0-9]+' | head -1
