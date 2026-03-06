#!/bin/bash
# Agent Initialization Script for Memphis Brain
# Run once when setting up a new agent

set -e

echo "🔥 Memphis Agent Initialization"
echo "================================"
echo ""

# Check if already initialized
if [ -f ~/.memphis/config.yaml ]; then
    echo "⚠️  Memphis already initialized"
    read -p "Reinitialize? This will create new identity (y/N): " CONFIRM
    if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
        echo "Aborted"
        exit 0
    fi
fi

# 1. Get agent info
read -p "🤖 Agent name (e.g., Watra, Style): " AGENT_NAME
if [ -z "$AGENT_NAME" ]; then
    echo "Agent name required"
    exit 1
fi

read -p "👤 Creator name: " CREATOR_NAME
read -p "🎯 Agent purpose/role: " AGENT_PURPOSE
read -p "🌐 Agent timezone (e.g., Europe/Warsaw): " AGENT_TZ
AGENT_TZ=${AGENT_TZ:-"UTC"}

# 2. Initialize Memphis
echo ""
echo "📦 Step 1/5: Initializing Memphis..."
memphis init || echo "Already initialized"
echo ""

# 3. Create minimal config
echo "⚙️  Step 2/5: Creating configuration..."
cat > ~/.memphis/config.yaml <<EOF
providers:
  ollama:
    url: http://localhost:11434/v1
    model: qwen2.5:3b
    role: primary

embeddings:
  backend: ollama
  model: nomic-embed-text

autosummary:
  enabled: true
  threshold: 30

security:
  workspaceGuard: true

logging:
  level: info
EOF
echo "✅ Config created"
echo ""

# 4. Create identity blocks
echo "📝 Step 3/5: Creating identity blocks..."

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Identity
memphis journal "IDENTITY: $AGENT_NAME, created by $CREATOR_NAME, initialized $TIMESTAMP" --tags identity,core

# Purpose
if [ -n "$AGENT_PURPOSE" ]; then
    memphis journal "PURPOSE: $AGENT_PURPOSE" --tags identity,purpose
fi

# Preferences (defaults)
memphis journal "PREFERENCES: Response style concise, timezone $AGENT_TZ, local-first memory" --tags preferences,communication

echo "✅ Identity blocks created"
echo ""

# 5. Embed context
echo "🔢 Step 4/5: Embedding initial context..."
memphis embed --chain journal
echo ""

# 6. Build graph
echo "🕸️  Step 5/5: Building knowledge graph..."
memphis graph build
echo ""

# 7. Show status
echo "📊 Final status:"
memphis status
echo ""

# 8. Success message
cat <<EOF

✅ Agent $AGENT_NAME initialized!

📋 Next steps:
1. Install embedding model:
   ollama pull nomic-embed-text

2. (Optional) Configure cloud fallback in:
   ~/.memphis/config.yaml

3. (Optional) Add Pinata for share-sync:
   # In config.yaml:
   integrations:
     pinata:
       jwt: \${PINATA_JWT}

4. Initialize vault for secrets:
   read -rsp "Vault password: " VP && export MEMPHIS_VAULT_PASSWORD="\$VP"
   memphis vault init --password-env MEMPHIS_VAULT_PASSWORD
   unset VP

5. Start journaling:
   memphis journal "First entry" --tags test

6. Use session scripts:
   bash ~/.openclaw/workspace/skills/memphis-brain/scripts/session-start.sh

🧠 $AGENT_NAME is ready to remember everything.
EOF
