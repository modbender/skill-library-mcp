#!/usr/bin/env bash
set -euo pipefail

SAPCONET_TARGET="${SAPCONET_TARGET:-neill@100.110.24.44}"

# Connectivity + host identity check
ssh "${SAPCONET_TARGET}" 'echo "connected: $(hostname)" && date -Iseconds'

# Placeholder: bird read command on SAPCONET
# Example: ssh "${SAPCONET_TARGET}" 'birdc show protocols'
ssh "${SAPCONET_TARGET}" 'echo "TODO: replace with bird read command"'

# Placeholder: puppeteer environment check on SAPCONET
ssh "${SAPCONET_TARGET}" 'command -v node >/dev/null && command -v chromium >/dev/null && echo "puppeteer prereqs present" || echo "missing node/chromium"'
