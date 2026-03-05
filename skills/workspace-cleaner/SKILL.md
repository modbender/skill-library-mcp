# Workspace Cleaner

Safe, automated cleanup for OpenClaw workspaces. Finds temp files, duplicates, and cruft while protecting important data.

## Quick Start

```bash
# Preview what would be deleted (safe - no changes)
python3 {{SKILL_DIR}}/scripts/cleanup.py

# Actually clean up (uses trash for recovery)
python3 {{SKILL_DIR}}/scripts/cleanup.py --execute

# Custom workspace path
python3 {{SKILL_DIR}}/scripts/cleanup.py --workspace /path/to/workspace
```

## Features

- **Dry-run by default** — Always previews before deleting
- **Uses trash** — Files go to system trash, recoverable
- **Size-aware** — Shows sizes, can filter by threshold
- **Age filtering** — Target files older than N days
- **Customizable patterns** — Edit config to match your workflow
- **JSON output** — Machine-readable for automation
- **Safe defaults** — Never touches .git, memory/, core configs

## Commands

### Preview (Default)
```bash
python3 {{SKILL_DIR}}/scripts/cleanup.py
```
Shows what would be deleted with sizes. Makes no changes.

### Execute Cleanup
```bash
python3 {{SKILL_DIR}}/scripts/cleanup.py --execute
```
Moves items to trash. Recoverable via system trash.

### Filter by Size
```bash
# Only show items larger than 100MB
python3 {{SKILL_DIR}}/scripts/cleanup.py --min-size 100
```

### Filter by Age
```bash
# Only show items older than 30 days
python3 {{SKILL_DIR}}/scripts/cleanup.py --min-age 30
```

### JSON Output
```bash
# For automation/parsing
python3 {{SKILL_DIR}}/scripts/cleanup.py --json
```

### Custom Config
```bash
# Use custom patterns file
python3 {{SKILL_DIR}}/scripts/cleanup.py --config /path/to/patterns.json
```

## What Gets Cleaned

Default patterns (customizable via config):

| Category | Patterns | Safe? |
|----------|----------|-------|
| Temp downloads | `*.skill` in root | ✅ |
| Generated images | `*.png`, `*.jpg` in root | ✅ |
| macOS cruft | `.DS_Store` | ✅ |
| Logs | `*.log` | ✅ |
| Temp files | `*.tmp`, `*.bak`, `*~` | ✅ |
| Node modules | `node_modules/` in root | ✅ |
| Python venvs | `.venv*/`, `venv/` (except known) | ⚠️ |
| Duplicate repos | Same remote as projects/* | ⚠️ |

## What's Protected

Never deleted, regardless of patterns:
- `.git/` directories
- `memory/` directory
- `MEMORY.md`, `SOUL.md`, `USER.md`, `AGENTS.md`
- `projects/` directory contents
- `skills/` directory contents
- Files modified in last 24 hours (unless `--include-recent`)

## Configuration

Edit `{{SKILL_DIR}}/config/patterns.json` to customize:

```json
{
  "temp_extensions": [".tmp", ".bak", ".log", ".skill"],
  "temp_patterns": ["*~", "#*#"],
  "image_extensions": [".png", ".jpg", ".jpeg", ".gif"],
  "protected_dirs": ["memory", "skills", "projects", ".git"],
  "protected_files": ["MEMORY.md", "SOUL.md", "USER.md", "AGENTS.md"],
  "known_venvs": [".venv-skill-scanner"]
}
```

## HEARTBEAT Integration

Add to your `HEARTBEAT.md` for periodic cleanup checks:

```markdown
## Weekly Cleanup Check
- Run workspace cleaner in preview mode
- Alert if >500MB of cruft found
- Auto-clean items >30 days old and <10MB
```

## Safety Notes

1. **Always preview first** — Run without `--execute` to see what would be deleted
2. **Check the trash** — Files go to system trash, not permanent delete
3. **Exclude patterns** — Use `--exclude` for files that look like cruft but aren't
4. **Backup first** — For large cleanups, consider a backup

## Examples

### Regular Maintenance
```bash
# Weekly cleanup of obvious cruft
python3 {{SKILL_DIR}}/scripts/cleanup.py --min-age 7 --execute
```

### Find Space Hogs
```bash
# What's taking up space?
python3 {{SKILL_DIR}}/scripts/cleanup.py --min-size 50 --json | jq '.items | sort_by(.size_mb) | reverse'
```

### Pre-Commit Cleanup
```bash
# Clean before committing
python3 {{SKILL_DIR}}/scripts/cleanup.py --execute && git status
```

## Requirements

- Python 3.8+
- `trash` command (macOS: `brew install trash`, Linux: `trash-cli`)
