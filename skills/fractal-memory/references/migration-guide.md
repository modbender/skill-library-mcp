# Migration Guide

This guide helps you migrate from existing memory systems to the fractal memory system.

## From Flat Daily Files

If you currently have daily files in `memory/YYYY-MM-DD.md` format:

### 1. Create New Directory Structure

```bash
mkdir -p memory/diary/2026/{daily,weekly,monthly}
mkdir -p memory/diary/sticky-notes/{workflows,apis,commands,facts}
```

### 2. Move Existing Files

```bash
# Move daily files to new location
for file in memory/20*.md; do
  if [[ $file =~ memory/([0-9]{4})-([0-9]{2})-([0-9]{2})\.md ]]; then
    year="${BASH_REMATCH[1]}"
    mkdir -p "memory/diary/$year/daily"
    mv "$file" "memory/diary/$year/daily/"
  fi
done
```

### 3. Initialize State Files

Create `memory/rollup-state.json`:

```json
{
  "lastDailyRollup": null,
  "lastWeeklyRollup": null,
  "lastMonthlyRollup": null,
  "currentWeek": "2026-W07",
  "currentMonth": "2026-02"
}
```

Create `memory/heartbeat-state.json`:

```json
{
  "lastMoltbookCheck": null
}
```

### 4. Set Up Cron Jobs

Follow the [cron-setup.md](cron-setup.md) guide to create automated rollups.

### 5. Update AGENTS.md

Update your session startup routine to load memory in the new order:

```markdown
## Every Session

Before doing anything else:

1. Read `SOUL.md` — this is who you are
2. Read `USER.md` — this is who you're helping
3. Read `memory/diary/YYYY/daily/YYYY-MM-DD.md` (today + yesterday) for recent context
4. **If in MAIN SESSION**: Also read `MEMORY.md`

**Context loading order (attention-optimized):**
- TODAY → THIS WEEK → THIS MONTH → MEMORY.md
- Most recent first, highest level early
```

## From Manual MEMORY.md Only

If you only have a single MEMORY.md file:

### 1. Create Directory Structure

```bash
mkdir -p memory/diary/2026/{daily,weekly,monthly}
mkdir -p memory/diary/sticky-notes/{workflows,apis,commands,facts}
```

### 2. Initialize Today's Daily Log

```bash
python3 scripts/ensure_daily_log.py
```

### 3. Keep Existing MEMORY.md

Your existing MEMORY.md stays at the workspace root. The monthly rollup will append to it.

### 4. Set Up Automation

Follow the [cron-setup.md](cron-setup.md) guide.

## From Other Hierarchical Systems

If you have a different hierarchical memory structure:

### 1. Map Your Structure

Identify what maps to:
- **Daily logs** → `memory/diary/YYYY/daily/YYYY-MM-DD.md`
- **Weekly summaries** → `memory/diary/YYYY/weekly/YYYY-Wnn.md`
- **Monthly summaries** → `memory/diary/YYYY/monthly/YYYY-MM.md`
- **Core memory** → `MEMORY.md`
- **Timeless facts** → `memory/diary/sticky-notes/{category}/`

### 2. Migrate Content

Copy or move files to the new structure, preserving content.

### 3. Adjust Scripts

If your format differs significantly, you may need to adjust the rollup scripts to handle your existing content format.

## Verification

After migration, verify the setup:

### 1. Check Directory Structure

```bash
tree memory/diary/
```

Should show:
```
memory/diary/
├── 2026/
│   ├── daily/
│   ├── weekly/
│   └── monthly/
└── sticky-notes/
    ├── workflows/
    ├── apis/
    ├── commands/
    └── facts/
```

### 2. Test Scripts

```bash
python3 scripts/ensure_daily_log.py
python3 scripts/rollup-daily.py
python3 scripts/rollup-weekly.py
python3 scripts/rollup-monthly.py
```

### 3. Verify Cron Jobs

```javascript
cron(action="list")
```

Should show three jobs: Daily, Weekly, and Monthly Memory Rollup.

## Rollback

If you need to rollback:

### 1. Disable Cron Jobs

```javascript
cron(action="update", jobId="<job-id>", patch={enabled: false})
```

### 2. Restore Old Structure

Move files back to their original locations.

### 3. Update AGENTS.md

Revert to your previous session startup routine.

## Tips

- **Start fresh**: Consider starting the fractal system on a clean date (e.g., beginning of a month)
- **Parallel run**: Run both systems in parallel for a week to ensure smooth transition
- **Backup first**: Always backup your existing memory files before migration
- **Test rollups**: Manually run rollup scripts before enabling cron automation

## Support

If you encounter issues during migration:
1. Check script error messages
2. Verify file permissions (`chmod +x scripts/*.py`)
3. Ensure Python dependencies are installed
4. Review the [architecture.md](architecture.md) for system design details
