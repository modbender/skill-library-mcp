# Safe Defaults Reference

## Philosophy

The workspace cleaner follows a "safe by default" approach:

1. **Preview first** — Never deletes without explicit `--execute`
2. **Trash, not delete** — Uses system trash for recovery
3. **Protect memory** — Never touches MEMORY.md or memory/
4. **Skip recent** — Files < 24 hours old are skipped by default
5. **Whitelist approach** — Only deletes known patterns

## Protected Locations

These are NEVER deleted, regardless of settings:

### Directories
- `memory/` — Your persistent memory
- `skills/` — Installed skills
- `projects/` — Project repos (each has own git)
- `.git/` — Git repositories
- `archive/` — Archived templates

### Files
- `MEMORY.md` — Long-term memory
- `SOUL.md` — Personality definition
- `USER.md` — User profile
- `AGENTS.md` — Agent behavior
- `TOOLS.md` — Tool configuration
- `HEARTBEAT.md` — Periodic checks
- `IDENTITY.md` — Identity info
- `BOOTSTRAP.md` — First-run config

## Default Cleanup Targets

### Safe to Delete (Auto-detected)

| Pattern | Reason | Risk |
|---------|--------|------|
| `*.skill` | Temp skill downloads | None |
| `*.log` | Log files | None |
| `*.tmp`, `*.bak` | Temp/backup files | None |
| `*~`, `#*#` | Editor temps | None |
| `.DS_Store` | macOS metadata | None |
| `node_modules/` (root) | Stray dependencies | Low |

### Requires Review (Flagged but check first)

| Pattern | Reason | Risk |
|---------|--------|------|
| `*.png`, `*.jpg` (root) | Generated images | Medium - might be intentional |
| `.venv*/` | Python venvs | Medium - might have custom deps |
| Duplicate repos | Same remote as projects/* | Medium - might have local changes |

## Customization

### Adding Patterns

Edit `config/patterns.json`:

```json
{
  "temp_extensions": [".tmp", ".bak", ".log", ".skill", ".cache"],
  "protected_files": ["MEMORY.md", "MY_CUSTOM_FILE.md"]
}
```

### Excluding Specific Items

Use command line:
```bash
# Coming soon: --exclude pattern
python3 cleanup.py --exclude "important-image.png"
```

### Per-Run Filters

```bash
# Only large items
python3 cleanup.py --min-size 100

# Only old items  
python3 cleanup.py --min-age 30

# Combine filters
python3 cleanup.py --min-size 10 --min-age 7
```

## Recovery

All deleted items go to system trash:

### macOS
- Trash location: `~/.Trash/`
- Restore: Open Trash in Finder, right-click → Put Back

### Linux (trash-cli)
- Trash location: `~/.local/share/Trash/`
- Restore: `trash-restore`

## Integration Examples

### HEARTBEAT.md Weekly Check
```markdown
## Cleanup Check (Weekly)
Run `python3 skills/workspace-cleaner/scripts/cleanup.py --json`
If total_size_mb > 500, alert user
Auto-clean items with --min-age 30 --min-size 0 --execute
```

### Pre-Commit Hook
```bash
#!/bin/bash
python3 ~/clawd/skills/workspace-cleaner/scripts/cleanup.py --min-age 1 --execute --quiet
```

### Cron Job (Monthly Deep Clean)
```json
{
  "schedule": {"kind": "cron", "expr": "0 3 1 * *"},
  "payload": {
    "kind": "agentTurn",
    "message": "Run workspace cleanup with --min-age 30 --execute and report results"
  }
}
```
