#!/bin/bash
# Initialize access-control.json in the agent's memory directory
# Usage: bash init-access-control.sh [memory-dir] [agent-name]

MEMORY_DIR="${1:-memory}"
AGENT_NAME="${2:-Assistant}"

mkdir -p "$MEMORY_DIR"

if [ -f "$MEMORY_DIR/access-control.json" ]; then
    echo "⚠️  $MEMORY_DIR/access-control.json already exists. Skipping."
    echo "   Delete it first if you want to reinitialize."
    exit 0
fi

cat > "$MEMORY_DIR/access-control.json" << HEREDOC
{
  "ownerIds": [],
  "approvedContacts": {},
  "pendingApprovals": {},
  "blockedIds": [],
  "strangerMessage": "Hi there! 👋 I'm ${AGENT_NAME}, an AI assistant. I'm currently set up to help my owner with personal tasks, so I'm not able to chat freely just yet. I've let them know you reached out — if they'd like to connect us, they'll set that up. Have a great day! 😊",
  "notifyChannel": "",
  "notifyTarget": "",
  "rateLimits": {}
}
HEREDOC

echo "✅ Created $MEMORY_DIR/access-control.json"
echo ""
echo "Next steps:"
echo "  1. Add your owner IDs to ownerIds[]"
echo "  2. Set notifyChannel (telegram/whatsapp/discord/signal)"
echo "  3. Set notifyTarget (your ID on that channel)"
echo "  4. Customize strangerMessage if desired"
