#!/usr/bin/env bash
set -euo pipefail

REMOTE_TARGET="${REMOTE_TARGET:-neill@<YOUR_REMOTE_HOST>}"

# Connectivity + host identity check
ssh "${REMOTE_TARGET}" 'echo "connected: $(hostname)" && date -Iseconds'

# Placeholder: bird read command on REMOTE
# Example: ssh "${REMOTE_TARGET}" 'birdc show protocols'
ssh "${REMOTE_TARGET}" 'echo "TODO: replace with bird read command"'

# Placeholder: puppeteer environment check on REMOTE
ssh "${REMOTE_TARGET}" 'command -v node >/dev/null && command -v chromium >/dev/null && echo "puppeteer prereqs present" || echo "missing node/chromium"'
