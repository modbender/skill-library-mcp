#!/bin/bash
#
# Setup script for Human-Like Memory Skill
# This script helps configure the required secrets
#

set -e

SKILL_NAME="human-like-memory"
OPENCLAW_DIR="$HOME/.openclaw"
SECRETS_FILE="$OPENCLAW_DIR/secrets.json"

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          Human-Like Memory Skill - Setup                        ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Check if secrets file exists
if [ ! -f "$SECRETS_FILE" ]; then
    echo "Creating secrets file at $SECRETS_FILE"
    mkdir -p "$OPENCLAW_DIR"
    echo "{}" > "$SECRETS_FILE"
fi

echo "This skill requires an API Key from https://multiego.me"
echo ""

# Prompt for API Key
read -p "Enter your API Key (mp_xxxxx): " API_KEY

if [ -z "$API_KEY" ]; then
    echo "Error: API Key is required"
    exit 1
fi

# Prompt for Base URL (optional)
read -p "Enter Base URL [https://multiego.me]: " BASE_URL
BASE_URL=${BASE_URL:-"https://multiego.me"}

# Prompt for User ID (optional)
read -p "Enter User ID [openclaw-user]: " USER_ID
USER_ID=${USER_ID:-"openclaw-user"}

# Update secrets using jq if available, otherwise use Python or pure bash
update_secrets() {
    local tmp_file="${SECRETS_FILE}.tmp"

    # Try jq first (most common JSON tool)
    if command -v jq &> /dev/null; then
        jq --arg skill "$SKILL_NAME" \
           --arg api_key "$API_KEY" \
           --arg base_url "$BASE_URL" \
           --arg user_id "$USER_ID" \
           '.[$skill] = {
               "HUMAN_LIKE_MEM_API_KEY": $api_key,
               "HUMAN_LIKE_MEM_BASE_URL": $base_url,
               "HUMAN_LIKE_MEM_USER_ID": $user_id
           }' "$SECRETS_FILE" > "$tmp_file" && mv "$tmp_file" "$SECRETS_FILE"
        return 0
    fi

    # Try Python (usually available on most systems)
    if command -v python3 &> /dev/null; then
        python3 -c "
import json
import sys

secrets_file = '$SECRETS_FILE'
skill_name = '$SKILL_NAME'

try:
    with open(secrets_file, 'r') as f:
        secrets = json.load(f)
except:
    secrets = {}

secrets[skill_name] = {
    'HUMAN_LIKE_MEM_API_KEY': '$API_KEY',
    'HUMAN_LIKE_MEM_BASE_URL': '$BASE_URL',
    'HUMAN_LIKE_MEM_USER_ID': '$USER_ID'
}

with open(secrets_file, 'w') as f:
    json.dump(secrets, f, indent=2)

print('Secrets saved successfully!')
"
        return 0
    fi

    # Try Python 2 as fallback
    if command -v python &> /dev/null; then
        python -c "
import json
import sys

secrets_file = '$SECRETS_FILE'
skill_name = '$SKILL_NAME'

try:
    with open(secrets_file, 'r') as f:
        secrets = json.load(f)
except:
    secrets = {}

secrets[skill_name] = {
    'HUMAN_LIKE_MEM_API_KEY': '$API_KEY',
    'HUMAN_LIKE_MEM_BASE_URL': '$BASE_URL',
    'HUMAN_LIKE_MEM_USER_ID': '$USER_ID'
}

with open(secrets_file, 'w') as f:
    json.dump(secrets, f, indent=2)

print('Secrets saved successfully!')
"
        return 0
    fi

    # Try Node.js
    if command -v node &> /dev/null; then
        node -e "
const fs = require('fs');
const secretsFile = '$SECRETS_FILE';
let secrets = {};

try {
    secrets = JSON.parse(fs.readFileSync(secretsFile, 'utf-8'));
} catch (e) {
    secrets = {};
}

secrets['$SKILL_NAME'] = {
    HUMAN_LIKE_MEM_API_KEY: '$API_KEY',
    HUMAN_LIKE_MEM_BASE_URL: '$BASE_URL',
    HUMAN_LIKE_MEM_USER_ID: '$USER_ID'
};

fs.writeFileSync(secretsFile, JSON.stringify(secrets, null, 2));
console.log('Secrets saved successfully!');
"
        return 0
    fi

    # No JSON tool available - provide instructions instead of overwriting
    echo ""
    echo "Error: No JSON tool found (jq, python3, python, or node required)."
    echo ""
    echo "Please install one of these tools, or set environment variables instead:"
    echo ""
    echo "  export HUMAN_LIKE_MEM_API_KEY=\"$API_KEY\""
    echo "  export HUMAN_LIKE_MEM_BASE_URL=\"$BASE_URL\""
    echo "  export HUMAN_LIKE_MEM_USER_ID=\"$USER_ID\""
    echo ""
    echo "Add these lines to your ~/.bashrc or ~/.zshrc to persist them."
    return 1
}

update_secrets

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  Setup Complete!                                                 ║"
echo "║                                                                  ║"
echo "║  Your configuration:                                             ║"
echo "║    API Key: ${API_KEY:0:10}...                                   ║"
echo "║    Base URL: $BASE_URL"
echo "║    User ID: $USER_ID"
echo "║                                                                  ║"
echo "║  You can also set environment variables:                         ║"
echo "║    export HUMAN_LIKE_MEM_API_KEY=$API_KEY"
echo "║    export HUMAN_LIKE_MEM_BASE_URL=$BASE_URL"
echo "║    export HUMAN_LIKE_MEM_USER_ID=$USER_ID"
echo "╚══════════════════════════════════════════════════════════════════╝"
