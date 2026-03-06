---
name: gitea-workflow-dispatch
description: Trigger Gitea/Forgejo workflow_dispatch via API.
metadata:
  openclaw:
    emoji: "🚀"
    requires:
      bins: ["node"]
      env: ["GITEA_URL", "GITEA_TOKEN"]
    primaryEnv: "GITEA_TOKEN"
---

# Gitea Workflow Dispatch

Trigger Gitea/Forgejo workflow_dispatch via API.

## Environment Variables

- `GITEA_URL` - Gitea API URL (e.g., `http://8.137.50.76:10000`)
- `GITEA_TOKEN` - Gitea API token

## Usage

```bash
node -e "
const dispatch = require('~/.openclaw/skills/gitea-workflow-dispatch/index.js');
dispatch({
  owner: 'gg',
  repo: 'web3-mini-game',
  workflow: 'deploy-vercel.yml',
  ref: 'master'
}).then(r => console.log(r.status, r.ok)).catch(console.error);
"
```

## Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| owner | string | ✅ | Repository owner |
| repo | string | ✅ | Repository name |
| workflow | string | ✅ | Workflow file name |
| ref | string | ❌ | Git ref (default: master) |
| inputs | object | ❌ | Workflow inputs |
| dryRun | boolean | ❌ | Test without sending |
