#!/bin/bash
# Create a new agent workspace with shared brain symlinks
# Usage: create_agent.sh <agent_id>

set -euo pipefail

AGENT_ID="${1:?Usage: create_agent.sh <agent_id>}"
MAIN="$HOME/.openclaw/workspace"
WS="$HOME/.openclaw/workspace-$AGENT_ID"

if [ -d "$WS" ]; then
  echo "ERROR: Workspace already exists at $WS"
  exit 1
fi

echo "Creating agent workspace: $AGENT_ID"

# Create workspace and .openclaw dir
mkdir -p "$WS/.openclaw"

# Symlink shared brain files
for f in .learnings IDENTITY.md MEMORY.md ROADMAP.md TOOLS.md USER.md; do
  ln -sf "../workspace/$f" "$WS/$f"
done

# Symlink shared resource directories
for d in agents content memory projects scripts skills; do
  ln -sf "../workspace/$d" "$WS/$d"
done

# Create placeholder unique files
cat > "$WS/SOUL.md" << 'EOF'
# SOUL.md — TODO

_Replace this with the agent's personality and identity._
EOF

cat > "$WS/AGENTS.md" << 'EOF'
# AGENTS.md — TODO

_Replace this with the agent's instructions, responsibilities, and budget rules._
EOF

cat > "$WS/HEARTBEAT.md" << 'EOF'
# HEARTBEAT.md
If nothing needs attention, reply HEARTBEAT_OK.
EOF

# Create agent directory in shared workspace
mkdir -p "$MAIN/agents/$AGENT_ID"
touch "$MAIN/agents/$AGENT_ID/INBOX.md"
touch "$MAIN/agents/$AGENT_ID/OUTBOX.md"

# Create budget file
TODAY=$(date +%Y-%m-%d)
cat > "$MAIN/agents/$AGENT_ID/BUDGET.json" << EOF
{
  "daily_limit_output_tokens": 50000,
  "today": "$TODAY",
  "used_output_tokens": 0,
  "spawns": [],
  "status": "active",
  "warnings": [],
  "consecutive_overbudget_days": 0
}
EOF

echo ""
echo "✅ Agent workspace created at: $WS"
echo ""
echo "Next steps:"
echo "  1. Edit $WS/SOUL.md — give the agent a personality"
echo "  2. Edit $WS/AGENTS.md — define responsibilities + budget rules"
echo "  3. Register in openclaw.json under agents.list[]"
echo "  4. Update other agents' allowAgents to include '$AGENT_ID'"
echo "  5. Validate: python3 -c \"import json; json.load(open('openclaw.json'))\""
echo "  6. Run: openclaw doctor"
echo "  7. Restart gateway: launchctl stop ai.openclaw.gateway && sleep 2 && launchctl start ai.openclaw.gateway"
