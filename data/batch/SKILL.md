---
name: Batch
description: Process multiple items with progress tracking, checkpointing, and failure recovery.
---

## Before Starting

1. **Dry run:** Test with 2-3 items first
2. **Count:** "Processing 47 items, ~2 min estimated"
3. **Confirm destructive ops:** "This will delete 200 files. Proceed?"

## During Processing

- **Progress every 10 items:** "23/47 complete (49%)"
- **Checkpoint every 10-50 items:** Save state to resume if interrupted
- **On error:** Log it, continue with rest (don't abort entire batch)

## After Completion

Always report:
```
✅ 44 succeeded
❌ 3 failed (saved to failed.json for retry)
```

## Error Handling

| Error | Action |
|-------|--------|
| Timeout, rate limit | Retry 3x with backoff (1s, 2s, 4s) |
| Bad format, missing data | Skip, log, continue |
| Auth failed, disk full | Abort entire batch |

Check `strategies.md` for parallel vs sequential decision matrix.
Check `errors.md` for retry logic and rollback patterns.

---

**Related:** For delegating to sub-agents, see `delegate`.
