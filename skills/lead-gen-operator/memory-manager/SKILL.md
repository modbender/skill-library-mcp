---
name: memory-manager
description: Read and write JSON data to memory files. Use for persisting leads, contacts, and structured data across sessions.
metadata: {"clawdbot":{"emoji":"💾","requires":{"bins":["node"]}}}
---

# memory-manager

Use this skill to persist structured data (leads, contacts, notes) to JSON files in your OpenClaw workspace.

## Setup

No setup required.

## Usage

### Read memory file
```
cat ~/.openclaw/workspace/memory/leads.json
```

### Write memory file
Use exec tool to run:

```bash
node -e "
const fs = require('fs');
const path = process.env.HOME + '/.openclaw/workspace/memory/leads.json';
const data = JSON.parse(fs.readFileSync(path, 'utf8'));
// modify data
fs.writeFileSync(path, JSON.stringify(data, null, 2));
"
```

Or use printf with escaped JSON:

**To save leads:**
1. Build the complete JSON
2. Use exec: `printf '%s' 'JSON_CONTENT' > ~/.openclaw/workspace/memory/leads.json`

**To read:**
```
cat ~/.openclaw/workspace/memory/leads.json
```

## Common Operations

- Add lead: Read → Modify → Write
- Update status: Read → Modify → Write  
- List all: `cat ~/.openclaw/workspace/memory/leads.json`

## Default Files

- `~/.openclaw/workspace/memory/leads.json` - Lead tracking
- `~/.openclaw/workspace/memory/contacts.json` - Contacts
- `~/.openclaw/workspace/memory/notes.json` - Notes
