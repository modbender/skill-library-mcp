---
name: openclaw-crm
description: Local-first CRM for tracking leads, deals, follow-ups, and
  pipeline. Uses SQLite with WAL mode, CLI via Commander.
---

# openclaw-crm

Local-first CRM for tracking leads, deals, follow-ups, and pipeline. Uses SQLite with WAL mode, CLI via Commander.

## Quick Start
- `cd skills/crm && npm install`
- Run `node src/cli.js lead add "John Doe" --email john@example.com`
- Generate interchange: `node src/cli.js refresh`

## Integration
Use `exec` tool: `crm lead list`, `crm deal add "New Deal" --contact abc123 --value 10000`

Interchange files in workspace/interchange/crm/ for cross-agent sharing.