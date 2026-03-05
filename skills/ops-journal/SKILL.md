# ops-journal — Automated Ops Logging & Incident Timeline for OpenClaw

Structured operational journal that captures deployments, incidents, changes, and decisions. Creates a searchable ops log with incident timeline reconstruction and automated postmortem generation.

## Quick Start

```bash
# Initialize journal
python3 scripts/journal.py init

# Log an event
python3 scripts/journal.py log "Upgraded nginx to 1.25" --category deploy
python3 scripts/journal.py log "Disk cleanup, freed 5GB" --category maintenance --tags storage

# Start an incident
python3 scripts/journal.py incident open "API latency spike" --severity high

# Resolve an incident
python3 scripts/journal.py incident resolve INC-001 "Root cause: disk full on /var"

# Search logs
python3 scripts/journal.py search "nginx" --since 7d
python3 scripts/journal.py search --category incident --severity high

# Generate reports
python3 scripts/journal.py summary --period week
python3 scripts/journal.py timeline INC-001

# Export
python3 scripts/journal.py export --format markdown --since 30d
```

## Entry Categories

| Category | Description | Auto-logged |
|----------|------------|-------------|
| `deploy` | Deployments, upgrades, rollbacks | Via hooks |
| `incident` | Incidents, outages, degradations | Via watchdog integration |
| `config` | Configuration changes | Via hooks |
| `maintenance` | Scheduled maintenance, cleanup | Manual or cron |
| `security` | Security events, audits, patches | Via security skills |
| `note` | General observations, decisions | Manual |

## Severity Levels

- `info` — Normal operations (default)
- `warn` — Something worth noting
- `high` — Important event requiring attention
- `critical` — Major incident or outage

## Commands

### `log` — Create a journal entry
```bash
python3 scripts/journal.py log "message" [--category CAT] [--severity SEV] [--tags tag1,tag2]
```

### `incident` — Incident management
```bash
python3 scripts/journal.py incident open "description" [--severity SEV]
python3 scripts/journal.py incident resolve ID "resolution"
python3 scripts/journal.py incident list [--status open|resolved|all]
python3 scripts/journal.py incident show ID
```

### `search` — Search journal entries
```bash
python3 scripts/journal.py search [query] [--category CAT] [--severity SEV] [--since Nd|Nw|Nm] [--limit N]
```

### `summary` — Generate period summary
```bash
python3 scripts/journal.py summary [--period day|week|month] [--json]
```

### `timeline` — Incident timeline
```bash
python3 scripts/journal.py timeline ID [--format markdown|json]
```

### `export` — Export journal
```bash
python3 scripts/journal.py export [--format markdown|json|csv] [--since Nd] [--output file]
```

### `stats` — Journal statistics
```bash
python3 scripts/journal.py stats [--period month]
```

## Output Modes

- **Human:** Colored terminal output with category icons and severity highlighting
- **JSON:** Machine-readable output for integration (`--json`)
- **Markdown:** Report-ready markdown for sharing (`--format markdown`)
- **CSV:** Spreadsheet-compatible export (`--format csv`)

## Integration with infra-watchdog

When `infra-watchdog` detects an issue, ops-journal can auto-log it:
```bash
# In a cron or hook:
python3 scripts/journal.py log "Monitor CRITICAL: Gateway down" --category incident --severity critical
```

## OpenClaw Cron Integration

```
# Daily summary at 09:00
python3 scripts/journal.py summary --period day --json

# Weekly digest on Monday
python3 scripts/journal.py summary --period week
```

## Storage

All data stored in `~/.openclaw/workspace/ops-journal/`:
- `journal.db` — SQLite database with all entries
- `incidents/` — Individual incident files (markdown)

## Files

- `scripts/journal.py` — Main journal engine
- `SKILL.md` — This file
