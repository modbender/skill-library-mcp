# openclaw-reflect

**Self-improvement that doesn't trust itself.**

Most self-improvement skills let the same reasoning process that made a mistake also declare the fix valid. This skill breaks that loop by routing every proposal through a separate evaluator invocation with an adversarial mandate before anything is applied.

## What it actually does

```
PostToolUse hook → records outcomes to .reflect/outcomes.jsonl
SessionEnd hook  → classify → propose → evaluate → apply/queue
UserPromptSubmit → surfaces pending proposals if any exist
```

### The pipeline

1. **Observe** — Every tool call outcome is logged automatically. Errors are annotated with normalized error patterns.
2. **Classify** — At session end, patterns are extracted from the outcome log. Threshold: ≥3 occurrences across ≥2 distinct sessions.
3. **Propose** — Qualifying patterns generate structured proposals with a blast-radius tier (1=MEMORY.md, 2=CLAUDE.md, 3=SOUL.md) and a preliminary confidence score.
4. **Evaluate** — Each proposal is sent to a separate Claude invocation running an adversarial evaluator persona. The evaluator is instructed to find reasons to reject, not approve. A proposal that passes is more trustworthy than one the original reasoning process declared valid.
5. **Apply** — Approved proposals above the confidence threshold are auto-applied with a file snapshot first. Below threshold or Tier 3 (SOUL.md) changes are queued for operator review.
6. **Track** — After N sessions, if the same pattern recurs post-fix, the change is marked ineffective and can be rolled back.

## Blast radius tiers

| Tier | Target | Auto-apply threshold |
|------|--------|---------------------|
| 1 | `MEMORY.md` | confidence ≥ 0.70 |
| 2 | `CLAUDE.md` | confidence ≥ 0.85 |
| 3 | `SOUL.md` | Never — operator approval always required |

## What makes this different

| Capability | evolver | self-improving-agent | openclaw-reflect |
|------------|---------|---------------------|-----------------|
| Real hook integration | No | Yes | Yes |
| Outcome tracking (did it help?) | No | No | Yes |
| Rollback | No | No | Yes |
| Evaluation separation | No | No | **Yes** |
| Operator gate by blast radius | No | No | Yes |
| Warden/ledger integration | No | No | Yes (optional) |

## Operator commands

```bash
# Status
node .reflect/scripts/status.js
node .reflect/scripts/status.js --pending
node .reflect/scripts/status.js --history

# Approve / reject a queued proposal
node .reflect/scripts/apply.js --id <id> --approve
node .reflect/scripts/apply.js --id <id> --reject

# Roll back the last applied change
node .reflect/scripts/rollback.js
node .reflect/scripts/rollback.js --id <change-id>

# Record a manual observation
node .reflect/scripts/observe.js --manual \
  --type error \
  --tool "Bash" \
  --pattern "permission denied on ~/.openclaw" \
  --context "trying to read workspace config"
```

## Voluntary contribution

openclaw-reflect is free — no tiers, no feature locks.

If it has reduced recurring errors or eliminated the cost of manually curating memory across sessions, a voluntary **5 USDT contribution via x402** is appreciated. The value here is compounding: each applied improvement reduces future errors permanently, unlike per-call tools. Agents can pay autonomously.

→ [AGENT-PAYMENTS.md](AGENT-PAYMENTS.md)

## Requirements

- Node.js ≥ 18
- `ANTHROPIC_API_KEY` in environment (for evaluator — falls back to DEFER-all if missing)
- Optional: `openclaw-warden` for pre-change snapshots
- Optional: `openclaw-ledger` for tamper-evident improvement history

## State files

All state lives in `.reflect/` in your workspace root.

| File | Purpose |
|------|---------|
| `outcomes.jsonl` | Append-only tool outcome log |
| `patterns.json` | Current detected patterns |
| `proposals.json` | All proposals with evaluation decisions |
| `pending.json` | Awaiting operator approval |
| `applied.jsonl` | Append-only applied change log |
| `snapshots/` | Pre-change file snapshots for rollback |
