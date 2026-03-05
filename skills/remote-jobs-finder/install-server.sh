#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/SERVER_EXTENSION_openclaw_extensions_root"
DEST_DIR="${HOME}/.openclaw/extensions"

mkdir -p "${DEST_DIR}"

cp "${SRC_DIR}/openclaw.plugin.json" "${DEST_DIR}/openclaw.plugin.json"
cp "${SRC_DIR}/index.ts" "${DEST_DIR}/index.ts"

echo "Installed extension files to ${DEST_DIR}"
echo "Now ensure RR_API_KEY is set for systemd service and restart:"
echo "  openclaw gateway restart"
