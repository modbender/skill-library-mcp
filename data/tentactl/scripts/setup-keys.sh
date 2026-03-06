#!/usr/bin/env bash
# Setup Kraken API keys from 1Password or manual input.
# Stores them in ~/.tentactl.env (chmod 600).

set -euo pipefail

ENV_FILE="$HOME/.tentactl.env"

echo "🐙 Kraken API Key Setup"
echo ""

# Try 1Password first
if command -v op &>/dev/null; then
    echo "1Password CLI detected. Searching for Kraken entries..."
    
    ITEMS=$(OP_BIOMETRIC_UNLOCK_ENABLED=true op item list --format json 2>/dev/null | \
        python3 -c "
import sys, json
items = json.load(sys.stdin)
matches = [{'id': i['id'], 'title': i['title'], 'vault': i.get('vault',{}).get('name','?')} 
           for i in items if 'kraken' in i.get('title','').lower()]
for m in matches:
    print(f\"{m['id']}|{m['title']}|{m['vault']}\")
" 2>/dev/null || true)

    if [[ -n "$ITEMS" ]]; then
        echo ""
        echo "Found Kraken items in 1Password:"
        INDEX=1
        while IFS='|' read -r id title vault; do
            echo "  $INDEX) $title ($vault)"
            INDEX=$((INDEX + 1))
        done <<< "$ITEMS"
        echo ""
        read -p "Select item number (or 's' to skip to manual): " CHOICE

        if [[ "$CHOICE" != "s" ]]; then
            ITEM_ID=$(echo "$ITEMS" | sed -n "${CHOICE}p" | cut -d'|' -f1)
            
            if [[ -n "$ITEM_ID" ]]; then
                echo "Fetching keys from 1Password..."
                
                # Try common field names
                API_KEY=$(OP_BIOMETRIC_UNLOCK_ENABLED=true op item get "$ITEM_ID" --fields label=API-key --reveal 2>/dev/null || \
                          OP_BIOMETRIC_UNLOCK_ENABLED=true op item get "$ITEM_ID" --fields label=api-key --reveal 2>/dev/null || \
                          OP_BIOMETRIC_UNLOCK_ENABLED=true op item get "$ITEM_ID" --fields label=api_key --reveal 2>/dev/null || \
                          echo "")
                
                API_SECRET=$(OP_BIOMETRIC_UNLOCK_ENABLED=true op item get "$ITEM_ID" --fields "label=Private key" --reveal 2>/dev/null || \
                             OP_BIOMETRIC_UNLOCK_ENABLED=true op item get "$ITEM_ID" --fields label=api-secret --reveal 2>/dev/null || \
                             OP_BIOMETRIC_UNLOCK_ENABLED=true op item get "$ITEM_ID" --fields label=api_secret --reveal 2>/dev/null || \
                             echo "")

                if [[ -n "$API_KEY" && -n "$API_SECRET" ]]; then
                    echo "KRAKEN_API_KEY=$API_KEY" > "$ENV_FILE"
                    echo "KRAKEN_API_SECRET=$API_SECRET" >> "$ENV_FILE"
                    chmod 600 "$ENV_FILE"
                    echo "✅ Keys saved to $ENV_FILE"
                    exit 0
                else
                    echo "⚠️  Could not find API key/secret fields. Falling back to manual."
                fi
            fi
        fi
    else
        echo "No Kraken items found in 1Password."
    fi
fi

# Manual entry
echo ""
echo "Enter your Kraken API credentials:"
echo "(Get them from https://www.kraken.com/u/security/api)"
echo ""
read -p "API Key: " API_KEY
read -sp "API Secret: " API_SECRET
echo ""

if [[ -z "$API_KEY" || -z "$API_SECRET" ]]; then
    echo "❌ Both fields are required."
    exit 1
fi

echo "KRAKEN_API_KEY=$API_KEY" > "$ENV_FILE"
echo "KRAKEN_API_SECRET=$API_SECRET" >> "$ENV_FILE"
chmod 600 "$ENV_FILE"
echo "✅ Keys saved to $ENV_FILE"
