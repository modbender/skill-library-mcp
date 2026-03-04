#!/bin/bash
# Setup kasia-mcp: install dependencies and add to mcporter config
# Usage: setup.sh <kasia-mcp-path> [--mnemonic <phrase>] [--network <network>] [--indexer-url <url>]
set -euo pipefail

KASIA_MCP_PATH="${1:?Usage: setup.sh <kasia-mcp-path> [--mnemonic <phrase>] [--network <network>]}"
shift

MNEMONIC=""
NETWORK="mainnet"
INDEXER_URL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mnemonic) MNEMONIC="$2"; shift 2 ;;
    --network) NETWORK="$2"; shift 2 ;;
    --indexer-url) INDEXER_URL="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# Resolve absolute path
KASIA_MCP_PATH="$(cd "$KASIA_MCP_PATH" && pwd)"

# Check dist exists
if [ ! -f "$KASIA_MCP_PATH/dist/index.js" ]; then
  echo "Building kasia-mcp..."
  (cd "$KASIA_MCP_PATH" && npm install && npm run build)
fi

# Find mcporter config
MCPORTER_CONFIG="${MCPORTER_CONFIG:-./config/mcporter.json}"
if [ ! -f "$MCPORTER_CONFIG" ]; then
  MCPORTER_CONFIG="$HOME/.openclaw/workspace/config/mcporter.json"
fi

if [ ! -f "$MCPORTER_CONFIG" ]; then
  echo "Creating mcporter config at $MCPORTER_CONFIG"
  mkdir -p "$(dirname "$MCPORTER_CONFIG")"
  echo '{"mcpServers": {}, "imports": []}' > "$MCPORTER_CONFIG"
fi

# Build env object
ENV_JSON=$(python3 -c "
import json
env = {'KASPA_NETWORK': '$NETWORK'}
if '$MNEMONIC': env['KASPA_MNEMONIC'] = '$MNEMONIC'
if '$INDEXER_URL': env['KASIA_INDEXER_URL'] = '$INDEXER_URL'
print(json.dumps(env))
")

# Add kasia to mcporter config
python3 -c "
import json
with open('$MCPORTER_CONFIG') as f:
    config = json.load(f)

config.setdefault('mcpServers', {})
config['mcpServers']['kasia'] = {
    'command': 'node $KASIA_MCP_PATH/dist/index.js',
    'env': $ENV_JSON
}

with open('$MCPORTER_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
    f.write('\n')

print('Added kasia to', '$MCPORTER_CONFIG')
"

# Verify
if command -v mcporter &>/dev/null; then
  echo "Verifying..."
  mcporter list kasia 2>&1 || echo "Warning: mcporter list failed — check config"
else
  echo "mcporter not found — install with: npm install -g mcporter"
fi

echo "Done. Call tools with: mcporter call kasia.<tool>"
