---
name: openclaw-bee
description: "Install and configure BEE — the Belief Extraction Engine for OpenClaw. Gives agents persistent structured memory across sessions. Auto-extracts beliefs at session end, scopes by agent namespace, and injects recalled context on agent start. Use when: setting up agent memory, configuring belief persistence, or troubleshooting BEE. NOT for: general memory questions (use built-in memory tools instead)."
homepage: https://github.com/skysphere-labs/openclaw-bee
metadata: { "openclaw": { "emoji": "🐝", "requires": { "bins": ["npm"] } } }
---

# BEE — Belief Extraction Engine

Give your OpenClaw agents persistent, structured memory across sessions.

## What BEE Does

BEE hooks into the OpenClaw lifecycle and:
- **Extracts beliefs** at session end via a lightweight LLM call (Haiku by default)
- **Injects recalled context** before every agent spawn
- **Scopes by namespace** — each agent (VECTOR, FORGE, ORACLE, etc.) has isolated beliefs
- **Deduplicates** — cosine similarity check prevents duplicate beliefs (>0.92 → merge)
- **Tracks spawns** — monitors subagent budget per session

Beliefs live in a SQLite database (`vector.db`) and persist indefinitely across restarts.

---

## Installation

### Step 1 — Install the package

**From npm (recommended):**
```bash
npm install -g @skysphere-labs/openclaw-bee
```

**From GitHub (latest):**
```bash
npm install -g github:skysphere-labs/openclaw-bee
```

### Step 2 — Configure openclaw.json

Add BEE to your extensions in `~/.openclaw/openclaw.json`:

```json
{
  "extensions": {
    "entries": {
      "bee": {
        "enabled": true,
        "config": {
          "dbPath": "~/.openclaw/workspace/state/vector.db",
          "agentId": "main",
          "extractionEnabled": true,
          "extractionModel": "anthropic/claude-haiku-4-5",
          "maxCoreBeliefs": 10,
          "maxActiveBeliefs": 5,
          "maxRecalledBeliefs": 5
        }
      }
    }
  }
}
```

### Step 3 — Restart the gateway

```bash
openclaw gateway restart
```

BEE will run its database migration on first start and begin capturing beliefs.

---

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `dbPath` | *required* | Path to your SQLite database |
| `agentId` | `"main"` | Namespace for belief scoping |
| `extractionEnabled` | `true` | Enable/disable belief extraction |
| `extractionModel` | `"anthropic/claude-haiku-4-5"` | Model used for extraction (cheapest works well) |
| `extractionMinConfidence` | `0.55` | Minimum confidence to store a belief (0-1) |
| `maxCoreBeliefs` | `10` | Core beliefs injected into every session |
| `maxActiveBeliefs` | `5` | Recently active beliefs injected |
| `maxRecalledBeliefs` | `5` | Semantically recalled beliefs per query |
| `maxOutputChars` | `2000` | Max chars of belief context injected |
| `debug` | `false` | Enable verbose logging |
| `spawnBudgetWarning` | `20` | Warn when subagent spawns exceed this threshold |

---

## Verifying It Works

After restart, ask your agent:
> "How many beliefs do you have?"

Or check directly:
```bash
sqlite3 ~/.openclaw/workspace/state/vector.db "SELECT COUNT(*) FROM beliefs"
```

You should see beliefs accumulate after sessions complete.

---

## Multi-Agent Setup

For setups with multiple named agents (VECTOR, FORGE, ORACLE, etc.), use different `agentId` values per agent spawn. BEE scopes beliefs by `agentId` so each PM has isolated memory.

---

## Source

- GitHub: https://github.com/skysphere-labs/openclaw-bee
- npm: https://www.npmjs.com/package/@skysphere-labs/openclaw-bee
- Built by [Skysphere AI Labs](https://skysphere.ai)
