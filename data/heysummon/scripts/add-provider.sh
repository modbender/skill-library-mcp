#!/bin/bash
# HeySummon Consumer — Add/register a provider
# Usage: add-provider.sh <api-key> [alias]
#
# Fetches provider info from the platform and stores it in providers.json
# If alias is not given, uses the provider name from the platform.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
[ -f "$SKILL_DIR/.env" ] && set -a && source "$SKILL_DIR/.env" && set +a

BASE_URL="${HEYSUMMON_BASE_URL:-http://localhost:3445}"
PROVIDERS_FILE="${HEYSUMMON_PROVIDERS_FILE:-$SKILL_DIR/providers.json}"

API_KEY="$1"
ALIAS="$2"

if [ -z "$API_KEY" ]; then
  echo "Usage: add-provider.sh <api-key> [alias]" >&2
  echo "" >&2
  echo "  api-key   Client key (hs_cli_... or htl_...) linked to the provider" >&2
  echo "  alias     Optional friendly name (default: provider name from platform)" >&2
  exit 1
fi

# Validate key prefix
if [[ "$API_KEY" =~ ^htl_prov_ ]] || [[ "$API_KEY" =~ ^hs_prov_ ]]; then
  echo "❌ This is a provider key. You need a CLIENT key (hs_cli_... or htl_...)." >&2
  exit 1
fi

if [[ ! "$API_KEY" =~ ^hs_cli_ ]] && [[ ! "$API_KEY" =~ ^htl_ ]]; then
  echo "❌ Invalid key format. Must start with 'hs_cli_' or 'htl_'." >&2
  exit 1
fi

# Fetch provider info
RESPONSE=$(curl -s "${BASE_URL}/api/v1/whoami" -H "x-api-key: ${API_KEY}")
ERROR=$(echo "$RESPONSE" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{const j=JSON.parse(d);if(j.error)console.log(j.error)}catch(e){}})" 2>/dev/null)

if [ -n "$ERROR" ]; then
  echo "❌ API error: $ERROR" >&2
  exit 1
fi

PROVIDER_NAME=$(echo "$RESPONSE" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{const j=JSON.parse(d);console.log(j.provider?.name||j.expert?.name||'')}catch(e){}})" 2>/dev/null)
PROVIDER_ID=$(echo "$RESPONSE" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{const j=JSON.parse(d);console.log(j.provider?.id||j.expert?.id||'')}catch(e){}})" 2>/dev/null)

if [ -z "$PROVIDER_NAME" ]; then
  echo "❌ Could not fetch provider info. Is the key valid?" >&2
  exit 1
fi

# Use alias or provider name
NAME="${ALIAS:-$PROVIDER_NAME}"
NAME_LOWER=$(echo "$NAME" | tr '[:upper:]' '[:lower:]')

# Initialize providers.json if needed
if [ ! -f "$PROVIDERS_FILE" ]; then
  echo '{"providers":[]}' > "$PROVIDERS_FILE"
fi

# Add or update provider
node -e "
const fs = require('fs');
const file = process.argv[1];
const data = JSON.parse(fs.readFileSync(file, 'utf8'));

const entry = {
  name: process.argv[2],
  nameLower: process.argv[3],
  apiKey: process.argv[4],
  providerId: process.argv[5],
  providerName: process.argv[6],
  addedAt: new Date().toISOString()
};

// Remove existing entry with same key or name
data.providers = data.providers.filter(p => 
  p.apiKey !== entry.apiKey && p.nameLower !== entry.nameLower
);
data.providers.push(entry);

fs.writeFileSync(file, JSON.stringify(data, null, 2));
console.log('✅ Provider added: ' + entry.name + ' (' + entry.providerName + ')');
console.log('📋 Providers registered: ' + data.providers.length);
" "$PROVIDERS_FILE" "$NAME" "$NAME_LOWER" "$API_KEY" "$PROVIDER_ID" "$PROVIDER_NAME"
