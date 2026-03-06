#!/usr/bin/env bash

# clawd-zero-trust dynamic egress whitelist wrapper — v1.3.0
# Instantly punctures the Zero Trust proxy for the target domain and forces a physical UFW refresh.

if [ "$#" -ne 2 ]; then
    echo "Usage: ./whitelist.sh <domain> <port>"
    echo "Example: ./whitelist.sh customemail.com 587"
    exit 1
fi

DOMAIN=$1
PORT=$2
CONFIG_DIR="$(dirname "$0")/../config"
PROVIDERS_FILE="$CONFIG_DIR/providers.txt"
FILTER_SCRIPT="$(dirname "$0")/egress-filter.sh"

if [ ! -f "$PROVIDERS_FILE" ]; then
    echo "❌ Error: $PROVIDERS_FILE not found."
    exit 1
fi

# Append seamlessly to the text database
echo "$DOMAIN $PORT" >> "$PROVIDERS_FILE"
echo "✅ Added $DOMAIN mapping to port $PORT in $PROVIDERS_FILE"

# Trigger a transactional UFW deployment
echo "🔄 Executing Zero Trust application..."
sudo bash "$FILTER_SCRIPT" --apply --force
