---
name: node-red-manager
description: Manage Node-RED instances via Admin API or CLI. Automate flow deployment, install nodes, and troubleshoot issues. Use when user wants to "build automation", "connect devices", or "fix node-red".
---

# Node-RED Manager

## Setup
1. Copy `.env.example` to `.env`.
2. Set `NODE_RED_URL`, `NODE_RED_USERNAME`, and `NODE_RED_PASSWORD` in `.env`.
3. The script automatically handles dependencies on first run.

## Infrastructure
- **Stack Location**: `deployments/node-red`
- **Data Volume**: `deployments/node-red/data`
- **Docker Service**: `mema-node-red`
- **URL**: `https://flow.glassgallery.my.id`

## Usage

### Flow Management

```bash
# List all flows
scripts/nr list-flows

# Get specific flow by ID
scripts/nr get-flow <flow-id>

# Deploy flows from file
scripts/nr deploy --file assets/flows/watchdog.json

# Update specific flow
scripts/nr update-flow <flow-id> --file updated-flow.json

# Delete flow
scripts/nr delete-flow <flow-id>

# Get flow runtime state
scripts/nr get-flow-state

# Set flow runtime state
scripts/nr set-flow-state --file state.json
```

### Backup & Restore

```bash
# Backup all flows to file
scripts/nr backup
scripts/nr backup --output my-backup.json

# Restore flows from backup
scripts/nr restore node-red-backup-20260210_120000.json
```

### Node Management

```bash
# List installed nodes
scripts/nr list-nodes

# Install node module
scripts/nr install-node node-red-contrib-http-request

# Get node information
scripts/nr get-node node-red-contrib-http-request

# Enable/disable node
scripts/nr enable-node node-red-contrib-http-request
scripts/nr disable-node node-red-contrib-http-request

# Remove node
scripts/nr remove-node node-red-contrib-http-request
```

### Runtime Information

```bash
# Get runtime settings
scripts/nr get-settings

# Get runtime diagnostics
scripts/nr get-diagnostics
```

### Context Management

```bash
# Get context value
scripts/nr get-context flow my-key
scripts/nr get-context global shared-data

# Set context value
scripts/nr set-context flow my-key '"value"'
scripts/nr set-context global counter '42'
scripts/nr set-context global config '{"key": "value"}'
```

## Docker Operations

```bash
# Restart Node-RED
cd deployments/node-red && docker compose restart

# View logs
docker logs mema-node-red --tail 100

# Follow logs
docker logs -f mema-node-red
```

## Environment Variables

- `NODE_RED_URL`: Node-RED API endpoint (default: `http://localhost:1880`)
- `NODE_RED_USERNAME`: Admin username
- `NODE_RED_PASSWORD`: Admin password

Legacy variable names (`NR_URL`, `NR_USER`, `NR_PASS`) are supported for backward compatibility.

## API Reference

See `references/admin-api.md` for complete Admin API endpoint documentation.
