---
name: memory-tiers
version: 0.1.0
description: Tiered memory management for AI agents — LRU cache for context. Hot/warm/cold tiers with automatic promotion, demotion, and access tracking.
---

# Memory Tiers

A tiered memory system for AI agents. Like CPU cache hierarchy, but for your context window.

## Architecture

```
MEMORY.md (Tier 1 — Hot)          ← Always loaded, ~100 lines max
  ↕ promote (accessed) / demote (stale 7+ days)
memory/tier2-recent.md (Warm)     ← On-demand, last 30 days
  ↕ promote / demote (stale 30+ days)
memory/tier3-archive.md (Cold)    ← Search only, deep history
  ↕
memory/YYYY-MM-DD.md (Raw)        ← Immutable daily logs
```

## Scripts

All scripts are in `scripts/` relative to this SKILL.md.

### Track Memory Access
Scans session transcripts for memory file reads/writes/searches. Run regularly.

```bash
node scripts/track.js                    # scan last 24h
node scripts/track.js --since 72         # scan last 72 hours
```

Output: Updates `state/access-log.json` with per-file and per-section access data.

### Run Maintenance
Promotes/demotes sections between tiers based on access patterns.

```bash
node scripts/maintain.js --dry-run       # preview changes
node scripts/maintain.js                 # apply changes
node scripts/maintain.js --demote-days-t1 5   # custom T1 demotion threshold
```

Rules:
- Tier 1 sections not accessed in 7 days → demote to Tier 2
- Tier 2 sections not accessed in 30 days → demote to Tier 3
- Tier 2/3 sections accessed in last 24h → promote to Tier 1

### Manual Promote/Demote
Move a specific section between tiers.

```bash
node scripts/promote.js --list                           # show all sections
node scripts/promote.js --section "LARC" --from 3 --to 1  # promote
node scripts/promote.js --section "TextWeb" --from 1 --to 2 # demote
```

### Health Report
Show current tier sizes, staleness, and recommendations.

```bash
node scripts/report.js                   # pretty-printed
node scripts/report.js --json            # machine-readable
```

## Heartbeat Integration

Add to your heartbeat routine (every few hours):

```markdown
## Memory Maintenance
1. Run `node <skill_dir>/scripts/track.js` to update access tracking
2. Run `node <skill_dir>/scripts/maintain.js --dry-run` to check for needed changes
3. If changes look good, run without --dry-run
4. Run `node <skill_dir>/scripts/report.js` to verify health
```

## State Files

- `state/access-log.json` — Per-file and per-section access timestamps and counts
- `state/maintenance-log.json` — History of maintenance actions taken

## Tier Rules

| Rule | Threshold | Action |
|------|-----------|--------|
| T1 stale | Not accessed 7 days | Demote to T2 |
| T2 stale | Not accessed 30 days | Demote to T3 |
| T2/T3 accessed | Accessed in last 24h | Promote to T1 |
| T1 over limit | >100 lines | Demote lowest-access sections |
| Daily log | Never modified after day ends | Source of truth |

## File Conventions

Tier files should have these headers:

```markdown
# MEMORY.md — Working Memory (Tier 1)
<!-- last_maintained: YYYY-MM-DD -->
<!-- tier: 1 — hot context -->
```

Sections use `##` or `###` headers. The maintenance scripts parse these to identify movable units.

The `## Index → Deeper Tiers` section in MEMORY.md should always be last — it provides pointers to content in lower tiers.
