# exo-installer

> E.x.O. Ecosystem Manager — install, update, and monitor E.x.O. tools

## Quick Start

```bash
# Install the CLI
npm install -g exo-installer

# Install all E.x.O. packages
exo install --all

# Check health of all tools
exo doctor

# Check for updates
exo update --check
```

## Commands

| Command | Description |
|---------|-------------|
| `exo install [packages...]` | Install packages (or `--all`) |
| `exo list` | List available packages |
| `exo doctor` | Health check all installed tools |
| `exo status` | Quick status of installed tools |
| `exo update [--check]` | Check for or apply updates |
| `exo cron setup` | Setup daily health check cron |
| `exo help` | Show help |

## Packages

| Package | Category | Description |
|---------|----------|-------------|
| jasper-recall | Memory | Local RAG for AI agent memory |
| hopeids | Security | Intrusion detection for AI agents |
| jasper-configguard | Config | Safe OpenClaw config management |
| context-compactor | Memory | Token-based context compaction |
| hopeclaw | Metacognition | Meta-cognitive agent (dev) |
| moraclaw | Scheduling | Temporal orchestration (dev) |

## Health Checks

Each package provides a `doctor --json` command that returns:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "checks": {
    "component": "ok"
  }
}
```

The `exo doctor` command aggregates these and can send Telegram alerts:

```bash
# Check all and alert on issues
exo doctor --telegram
```

## Cron Integration

Set up daily health checks with Telegram notifications:

```bash
exo cron setup
```

This creates an OpenClaw cron job that runs daily at 9am and alerts if issues are found.

## JSON Output

```bash
# Get health status as JSON
exo doctor --json
```

Output:
```json
{
  "results": [
    {
      "id": "jasper-recall",
      "name": "jasper-recall",
      "version": "0.4.2",
      "latestVersion": "0.4.2",
      "updateAvailable": false,
      "health": { "status": "healthy" }
    }
  ],
  "timestamp": "2026-02-11T08:00:00.000Z"
}
```

## Links

- **GitHub:** https://github.com/E-x-O-Entertainment-Studios-Inc/exo-installer
- **npm:** https://www.npmjs.com/package/exo-installer

## License

MIT
