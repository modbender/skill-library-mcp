---
name: clawned
description: Security agent that inventories installed OpenClaw skills, analyzes them for threats, and syncs results to your Clawned dashboard.
metadata:
  {
    "openclaw":
      {
        "emoji": "🛡️",
        "requires": { "bins": ["python3"], "env": ["CLAWNED_API_KEY"] },
        "optionalEnv": ["CLAWNED_SERVER"],
        "homepage": "https://clawned.io",
      },
  }
---

# Clawned — Security Agent for OpenClaw

Automatically discovers all installed skills, analyzes them for security threats, and syncs results to your Clawned dashboard.

## Setup

Configure your API key in `openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "clawned": {
        "enabled": true,
        "env": {
          "CLAWNED_API_KEY": "cg_your_api_key_here",
          "CLAWNED_SERVER": "https://api.clawned.io"
        }
      }
    }
  }
}
```

## Commands

### Sync all installed skills to dashboard

```bash
python3 {baseDir}/scripts/agent.py sync
```

### Scan a single skill locally

```bash
python3 {baseDir}/scripts/agent.py scan --path <skill-directory>
```

### List all discovered skills

```bash
python3 {baseDir}/scripts/agent.py inventory
```

### Check agent status

```bash
python3 {baseDir}/scripts/agent.py status
```

## Data & Privacy

**During `sync` (default operation):**
- Sends only skill metadata: name, owner, slug, version
- No file contents are uploaded
- No `.env` files or secrets are ever read

**During `scan --path` (explicit user action only):**
- Reads source files (`.md`, `.py`, `.js`, etc.) from the specified skill directory for analysis
- `.env` files are excluded from scanning
- File contents are sent to the Clawned server for security analysis

**Local config access:**
- Reads `~/.openclaw/openclaw.json` only to locate skill directories (extraDirs paths)
- No credentials or secrets are read from config files

## Automatic Sync

Schedule every 6 hours via OpenClaw cron:

```json
{
  "jobs": [
    {
      "schedule": "0 */6 * * *",
      "command": "Run clawned sync to check all installed skills",
      "description": "Security scan every 6 hours"
    }
  ]
}
```
