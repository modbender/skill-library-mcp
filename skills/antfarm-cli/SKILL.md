# Antfarm CLI Skill

Always use full path: `node ~/.openclaw/workspace/antfarm/dist/cli/cli.js`

## Commands

### Workflow
```bash
# List available workflows
node ~/.openclaw/workspace/antfarm/dist/cli/cli.js workflow list

# Install workflow
node ~/.openclaw/workspace/antfarm/dist/cli/cli.js workflow install <name>

# Run workflow
node ~/.openclaw/workspace/antfarm/dist/cli/cli.js workflow run <workflow-id> "<task>"

# Check status
node ~/.openclaw/workspace/antfarm/dist/cli/cli.js workflow status "<query>"
```

### Dashboard
```bash
# Start
node ~/.openclaw/workspace/antfarm/dist/cli/cli.js dashboard start

# Status
node ~/.openclaw/workspace/antfarm/dist/cli/cli.js dashboard status
```

### Logs
```bash
# Recent activity
node ~/.openclaw/workspace/antfarm/dist/cli/cli.js logs

# Specific run
node ~/.openclaw/workspace/antfarm/dist/cli/cli.js logs <run-id>
```
