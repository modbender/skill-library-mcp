# Memory Template — Apple Health

Create `~/apple-health/memory.md` with this structure:

```markdown
# Apple Health Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending
mode: csv-export

## Integration Snapshot
client: unknown
mcp_server: @neiltron/apple-health-mcp
health_data_dir: not_set
last_export_date: unknown
freshness: unknown

## User Intent
<!-- What they want from Apple Health data -->
<!-- Examples: sleep trends, resting heart rate baseline, workout consistency -->

## Constraints
<!-- Privacy constraints, reporting preferences, no-go topics -->

## Notes
<!-- Query caveats, unit normalization choices, schema oddities -->

---
*Updated: YYYY-MM-DD*
```

## integrations.md Template

Create `~/apple-health/integrations.md`:

```markdown
# Apple Health Integrations

## Active Client
- Client: [name]
- Config file: [path]
- Validation: pass | fail
- Last checked: YYYY-MM-DD

## MCP Command
- command: npx
- args: @neiltron/apple-health-mcp
- HEALTH_DATA_DIR: /absolute/path

## Known Issues
- [Issue]: [Fix]
```

## query-log.md Template

Create `~/apple-health/query-log.md`:

```markdown
# Apple Health Query Log

## YYYY-MM-DD
- Goal:
- Query/report used:
- Date window:
- Result summary:
- Caveats:
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Normal state | Keep refining integration and analysis habits |
| `complete` | Stable setup | Skip setup prompts, go straight to analysis |
| `paused` | User postponed integration | Do not push setup, only answer planning questions |
| `never_ask` | User declined setup | Never re-prompt integration unless user requests |

## Key Principles

- Prefer reproducible queries over ad-hoc analysis.
- Record freshness to avoid misleading "latest" claims.
- Keep health data handling minimal and privacy-first.
