# DCG Guard — Install Instructions for OpenClaw Agents

## What This Is
A plugin that blocks dangerous shell commands (rm -rf, git push --force, git reset --hard, etc.) BEFORE they execute. Zero noise on safe commands. Hard enforcement at the OpenClaw gateway level.

## Quick Install (copy-paste into agent session)

```bash
# Install DCG binary
curl -sSL https://raw.githubusercontent.com/Dicklesworthstone/destructive_command_guard/master/install.sh | bash

# Create plugin directory
mkdir -p ~/clawd/plugins/dcg-guard

# Download plugin files
cat > ~/clawd/plugins/dcg-guard/package.json << 'EOF'
{
  "name": "dcg-guard",
  "version": "1.0.0",
  "openclaw": { "extensions": ["./index.ts"] }
}
EOF

cat > ~/clawd/plugins/dcg-guard/openclaw.plugin.json << 'EOF'
{
  "id": "dcg-guard",
  "name": "DCG Guard",
  "description": "Blocks dangerous shell commands via DCG before execution.",
  "version": "1.0.0",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "enabled": { "type": "boolean" },
      "dcgBin": { "type": "string" }
    }
  }
}
EOF

# (index.ts must be copied separately — see below or use clawhub install dcg-guard)

# Link and restart
openclaw plugins install -l ~/clawd/plugins/dcg-guard
openclaw gateway restart
```

## Verify It Works

Run this in your agent:
```
exec: rm -rf /home/test
```

Expected: blocked with "DCG Guard: [critical] core.filesystem:rm-rf-root-home"

Then run:
```
exec: echo "hello"
```

Expected: "hello" (silent passthrough)

## Add to AGENTS.md / SOUL.md

```markdown
## DCG Self-Guard
Before executing ANY potentially destructive command, DCG Guard will automatically
block it at the gateway level. If a command is blocked, do NOT retry it.
Ask the user for explicit permission before attempting alternatives.
```
