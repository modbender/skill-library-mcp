# Total Recall: Dream Cycle

The overnight memory consolidation system. While you sleep, an agent reviews `observations.md`, archives stale items, and adds semantic hooks so nothing useful is actually lost.

**Status: Shipped. Phase 1 live.**

Read more: [Do Agents Dream of Electric Sheep? I Built One That Does.](https://gavlahh.substack.com/p/do-agents-dream)

---

## How It Works

Nine stages run in sequence:

1. **Preflight** — backs up `observations.md`, takes a git snapshot
2. **Read inputs** — loads `observations.md`, `favorites.md`, today's daily file
3. **Classify** — assigns impact (critical / high / medium / low / minimal) and age to every observation
4. **Future-date protection** — reminders and deadlines are never archived
5. **Archive set** — decides what to archive based on age + impact thresholds
6. **Write archive** — archived items go to `memory/archive/observations/YYYY-MM-DD.md`
7. **Semantic hooks** — each archived item gets a hook in `observations.md` so it stays findable
8. **Atomic update** — applies the new `observations.md` safely
9. **Validate** — checks token count, writes dream log + metrics JSON; rolls back on failure

Nothing is deleted. Every archived item is preserved in the archive and referenced by a hook.

---

## Files

| File | Description |
|------|-------------|
| `../scripts/dream-cycle.sh` | Shell helper for safe file operations (preflight, archive, update, validate, rollback) |
| `../prompts/dream-cycle-prompt.md` | Agent prompt — paste into your Dream Cycle cron job |

---

## Quick Setup

1. Run setup (creates required directories):
   ```bash
   bash scripts/setup.sh
   ```

2. Add a nightly cron job (3am or whenever you sleep):
   ```
   0 3 * * * OPENCLAW_WORKSPACE=~/your-workspace bash ~/your-workspace/skills/total-recall/scripts/dream-cycle.sh preflight
   ```

3. Configure your cron agent to use `prompts/dream-cycle-prompt.md` as the system prompt.

4. Set `READ_ONLY_MODE=true` for the first 2-3 nights. Check `memory/dream-logs/` after each run.

5. When satisfied, switch to `READ_ONLY_MODE=false` for live mode.

---

## Results (3 Nights)

| Night | Mode | Tokens Before | Tokens After | Reduction | Archived |
|-------|------|--------------|-------------|-----------|----------|
| Night 1 | Dry run | 9,445 | 8,309 | 12% | 53 |
| Night 2 | Dry run | 16,900 | 6,800 | 60% | 248 |
| Night 3 | Live | 11,688 | 2,930 | 75% | 15, 0 false archives |

Cost per run: ~$0.003. Models: Claude Sonnet (Dreamer) + Gemini Flash (Observer).

---

## Outputs

```
memory/
  archive/
    observations/        # Nightly archive files (YYYY-MM-DD.md)
  dream-logs/            # Run reports (YYYY-MM-DD.md)
  .dream-backups/        # Pre-run backups of observations.md
research/
  dream-cycle-metrics/
    daily/               # JSON metrics (YYYY-MM-DD.json)
```

---

See [SKILL.md](../SKILL.md) for full documentation.
