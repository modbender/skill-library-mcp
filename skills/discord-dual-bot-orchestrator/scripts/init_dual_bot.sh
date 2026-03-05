#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="${BASE_DIR:-$HOME/.openclaw/bots}"

mkdir -p "$BASE_DIR/bot-a/workspace/memory"
mkdir -p "$BASE_DIR/bot-b/workspace/memory"

cat > "$BASE_DIR/bot-a/.env.template" << 'EOF'
DISCORD_BOT_TOKEN=BOT_A_TOKEN
OPENCLAW_WORKSPACE=BASE_DIR/bot-a/workspace
BOT_NAME=BOT_A_NAME
BOT_ID=BOT_A_ID
EOF

cat > "$BASE_DIR/bot-b/.env.template" << 'EOF'
DISCORD_BOT_TOKEN=BOT_B_TOKEN
OPENCLAW_WORKSPACE=BASE_DIR/bot-b/workspace
BOT_NAME=BOT_B_NAME
BOT_ID=BOT_B_ID
EOF

echo "Initialized: $BASE_DIR/{bot-a,bot-b}"
echo "Next: copy .env.template -> .env and replace placeholders."
