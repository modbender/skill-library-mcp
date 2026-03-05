# Gitea Actions

Trigger and query Gitea/Forgejo Actions workflows.

## Environment Variables

- `GITEA_URL` - Gitea API URL (e.g., `http://8.137.50.76:10000`)
- `GITEA_TOKEN` - Gitea API token

## Usage

```bash
node -e "
const gitea = require('~/.openclaw/skills/gitea-actions/index.js');

// Trigger workflow
gitea({ action: 'dispatch', owner: 'gg', repo: 'web3-mini-game', workflow: 'deploy-vercel.yml', ref: 'master' })

// List runs
gitea({ action: 'runs', owner: 'gg', repo: 'web3-mini-game' })

// Get run status
gitea({ action: 'run', owner: 'gg', repo: 'web3-mini-game', runId: 123 })
"
```

## Actions

| Action | Description |
|--------|-------------|
| dispatch | Trigger a workflow dispatch |
| runs | List workflow runs |
| run | Get single run status |

## Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| action | string | ✅ | dispatch, runs, or run |
| owner | string | ✅ | Repository owner |
| repo | string | ✅ | Repository name |
| workflow | string | ❌ | Workflow file (for dispatch/runs) |
| ref | string | ❌ | Git ref (default: master) |
| runId | number | ❌ | Run ID (for run action) |
