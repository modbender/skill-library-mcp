#!/bin/bash
# List registered providers
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
[ -f "$SKILL_DIR/.env" ] && set -a && source "$SKILL_DIR/.env" && set +a

PROVIDERS_FILE="${HEYSUMMON_PROVIDERS_FILE:-$SKILL_DIR/providers.json}"

if [ ! -f "$PROVIDERS_FILE" ]; then
  echo "📋 No providers registered yet."
  echo "Add one: bash $SCRIPT_DIR/add-provider.sh <api-key> [alias]"
  exit 0
fi

node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));
if (data.providers.length === 0) {
  console.log('📋 No providers registered yet.');
} else {
  console.log('📋 Registered providers (' + data.providers.length + '):');
  data.providers.forEach((p, i) => {
    console.log('  ' + (i+1) + '. ' + p.name + (p.providerName !== p.name ? ' (provider: ' + p.providerName + ')' : '') + ' — key: ' + p.apiKey.slice(0, 12) + '...');
  });
}
" "$PROVIDERS_FILE"
