#!/bin/bash
# Find all OpenClaw workspace directories from config
# Outputs one path per line
set -e

CONFIG="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"

if [ ! -f "$CONFIG" ]; then
  echo "❌ Config not found: $CONFIG" >&2
  exit 1
fi

# Extract workspace paths from config using node
node -e "
const c = require('$CONFIG');
const seen = new Set();
const defaultWs = c.agents?.defaults?.workspace || '$HOME/.openclaw/workspace';

// Check each agent
(c.agents?.list || []).forEach(a => {
  const ws = a.workspace || defaultWs;
  // For default workspace, agent-specific workspace is suffixed with -<id> (except default agent)
  if (!a.workspace && !a.default) {
    const agentWs = defaultWs + '-' + a.id;
    seen.add(agentWs);
  } else {
    seen.add(ws);
  }
});

// Always include the default workspace
seen.add(defaultWs);

// Output existing paths
const fs = require('fs');
for (const ws of seen) {
  if (fs.existsSync(ws)) console.log(ws);
}
" 2>/dev/null
