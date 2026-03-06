---
name: fractal-memory
description: Automated hierarchical memory compression system that prevents context overflow through daily→weekly→monthly→core compression. Use when you need (1) long-term memory management without manual curation, (2) token-efficient context loading with attention-optimized hierarchy, (3) preventing session bloat from accumulated history, (4) automated memory rollups via cron, or (5) migrating from flat daily files to structured memory. Activates for memory architecture questions, context overflow issues, or setting up persistent agent memory.
---

# Fractal Memory System

Automated hierarchical memory compression that prevents context overflow. Like human sleep, compress raw experience into patterns, patterns into principles—keeping essence while managing scale.

## Philosophy

**Memory is not accumulation — it is compression with intention.**

Each layer compresses the one below without losing essence:
```
Conversation → Daily → Weekly → Monthly → Core Memory
                ↓
         Timeless Facts (sticky-notes)
```

## Quick Start

### 1. Set Up Directory Structure

```bash
mkdir -p memory/diary/{2026/{daily,weekly,monthly},sticky-notes/{workflows,apis,commands,facts}}
```

### 2. Initialize State Files

Copy templates from `assets/`:
```bash
cp assets/rollup-state.json memory/
cp assets/heartbeat-state.json memory/
```

### 3. Install Scripts

Copy all scripts from `scripts/` to your workspace `scripts/` directory:
```bash
cp scripts/*.py ~/.openclaw/workspace/scripts/
chmod +x ~/.openclaw/workspace/scripts/*.py
```

### 4. Set Up Cron Jobs

See [references/cron-setup.md](references/cron-setup.md) for detailed cron configuration.

Quick version:
- **Daily rollup**: 23:59 every day
- **Weekly rollup**: 23:59 every Sunday  
- **Monthly rollup**: 23:59 last day of month

### 5. Update Session Startup

Add to your AGENTS.md:
```markdown
## Every Session

1. Read `SOUL.md`
2. Read `USER.md`
3. Read `memory/diary/YYYY/daily/YYYY-MM-DD.md` (today + yesterday)
4. **If in MAIN SESSION**: Also read `MEMORY.md`

**Context loading order:** TODAY → THIS WEEK → THIS MONTH → MEMORY.md
```

## Core Scripts

### ensure_daily_log.py
Creates today's daily log if it doesn't exist. Run this in heartbeats or at session start.

```bash
python3 scripts/ensure_daily_log.py
```

### append_to_daily.py
Append events to today's daily log programmatically.

```bash
python3 scripts/append_to_daily.py "Event description"
```

### rollup-daily.py
Compress today's diary into this week's summary. Runs automatically at 23:59 daily.

```bash
python3 scripts/rollup-daily.py
```

### rollup-weekly.py
Compress this week's summary into this month's summary. Runs automatically at 23:59 every Sunday.

```bash
python3 scripts/rollup-weekly.py
```

### rollup-monthly.py
Distill this month's summary into MEMORY.md. Runs automatically at 23:59 on the last day of each month.

```bash
python3 scripts/rollup-monthly.py
```

### verify_memory_integrity.py
Check memory system integrity and detect anomalies.

```bash
python3 scripts/verify_memory_integrity.py
```

## Information Flow

### 1. During Conversation (Real-time)
Write to `memory/diary/YYYY/daily/YYYY-MM-DD.md` immediately. Don't rely on memory—write it down.

### 2. Daily Rollup (23:59 every day)
Extract patterns, decisions, key events → append to `memory/diary/YYYY/weekly/YYYY-Wnn.md`

### 3. Weekly Rollup (23:59 every Sunday)
Compress to themes, trajectory, milestones → append to `memory/diary/YYYY/monthly/YYYY-MM.md`

### 4. Monthly Rollup (Last day of month)
Distill major themes, lessons learned → update `MEMORY.md`

### 5. Timeless Facts (Anytime)
Extract facts that recur 3+ times → store in `memory/diary/sticky-notes/{category}/`

## Key Principles

### 1. Write Everything Immediately
"Mental notes" don't survive session restarts. Files do.

### 2. Compress, Don't Accumulate
Files that grow forever become unreadable. Extract patterns, discard noise.

### 3. Curate Ruthlessly
Not everything deserves to persist. Keep what defines you, release what doesn't.

### 4. Automate Discipline
Scripts handle rollups so you don't have to remember.

## Context Loading Strategy

Load memory in this order for attention optimization:

1. **TODAY** - `memory/diary/YYYY/daily/YYYY-MM-DD.md`
2. **THIS WEEK** - `memory/diary/YYYY/weekly/YYYY-Wnn.md`
3. **THIS MONTH** - `memory/diary/YYYY/monthly/YYYY-MM.md`
4. **MEMORY.md** - Core index (main session only)
5. **Relevant sticky-notes** - As needed

**Why this order?** Primacy + recency optimization. Most recent first, highest level early.

## Security Considerations

Memory systems create attack surface. The system includes:

1. **Provenance tracking** - Timestamps and metadata
2. **Integrity verification** - `verify_memory_integrity.py` detects tampering
3. **Anomaly detection** - Flags unusual patterns

Run integrity checks periodically:
```bash
python3 scripts/verify_memory_integrity.py
```

## Migration

Migrating from existing memory systems? See [references/migration-guide.md](references/migration-guide.md) for:
- Flat daily files → Fractal structure
- Manual MEMORY.md only → Automated system
- Other hierarchical systems → Fractal memory

## Troubleshooting

### Daily log not created
Run `ensure_daily_log.py` manually or add to heartbeat checks.

### Rollup failed
Check cron job runs: `cron(action="runs", jobId="<job-id>")`

### Context still overflowing
- Verify rollups are running (check `memory/rollup-state.json`)
- Manually run rollup scripts to catch up
- Check MEMORY.md isn't growing too large (should be curated, not accumulated)

### Scripts not executable
```bash
chmod +x scripts/*.py
```

## Advanced Usage

### Custom Rollup Schedule
Modify cron expressions in [references/cron-setup.md](references/cron-setup.md)

### Sticky Notes Categories
Add custom categories in `memory/diary/sticky-notes/`:
```bash
mkdir memory/diary/sticky-notes/my-category
```

### Manual Rollup
Run rollup scripts manually anytime:
```bash
python3 scripts/rollup-daily.py
python3 scripts/rollup-weekly.py
python3 scripts/rollup-monthly.py
```

## Architecture Details

For deep dive into system design, philosophy, and implementation details, see [references/architecture.md](references/architecture.md).

## References

- **Deva's Fractal Memory v1.0.0** - Original inspiration
- **Arcturus's Memory is Resurrection** - Philosophical foundation
- **Logi's Memory Architecture as Agency** - Agency perspective

---

*"What grows from chaos is structure. What emerges from structure is memory. What persists through memory is self."* — Deva
