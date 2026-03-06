#!/usr/bin/env bash
# Collect metrics — placeholder for automated collection in v2
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
node "$SCRIPT_DIR/../src/cli.js" aggregate
node "$SCRIPT_DIR/../src/cli.js" refresh
echo "✅ Metrics collected and interchange refreshed"
