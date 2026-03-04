---
name: clawbrain-startup
description: "Refresh ClawBrain memory on startup and save sessions"
metadata:
  {
    "clawdbot":
      {
        "emoji": "🧠",
        "events": ["gateway:startup", "command:new"],
        "requires": { "files": ["scripts/brain_bridge.py"] },
        "install": [{ "id": "workspace", "kind": "workspace", "label": "ClawBrain Skill Hook" }],
      },
    "openclaw":
      {
        "emoji": "🧠",
        "events": ["gateway:startup", "command:new"],
        "requires": { "files": ["scripts/brain_bridge.py"] },
        "install": [{ "id": "workspace", "kind": "workspace", "label": "ClawBrain Skill Hook" }],
      },
  }
---

# ClawBrain Startup Hook

Refreshes the ClawBrain memory system on gateway startup and saves session context to brain on /new command.

## Events

- **gateway:startup** - Refresh brain memory on gateway startup  
- **command:new** - Save session context to brain memory

## How It Works

1. **On Gateway Startup** (`gateway:startup`):
   - Automatically refreshes brain memory
   - Loads and indexes recent memories
   - Reports memory count to logs

2. **On Session Reset** (`command:new`):
   - Saves current session summary to brain memory
   - Creates searchable memory entry for future recall

## Installation

```bash
# Copy to hooks directory
cp -r hooks/clawbrain-startup ~/clawd/hooks/

# Or install via clawdbot
clawdbot hooks install /path/to/clawbrain/hooks/clawbrain-startup
```

## Requirements

- ClawBrain skill must be installed in `~/clawd/skills/clawbrain`
- Python 3.8+ with clawbrain module accessible

## Configuration

No configuration required. The hook automatically uses the ClawBrain skill from the skills directory.

## Disabling

```bash
clawdbot hooks disable clawbrain-startup
```

Or via config:

```json
{
  "hooks": {
    "internal": {
      "entries": {
        "clawbrain-startup": { "enabled": false }
      }
    }
  }
}
```
