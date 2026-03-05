# Gauge Memory 📊

**Status:** 📋 Agent Guideline | **Module:** gauge | **Part of:** Agent Brain

Confidence classification and self-awareness. Honest about what is known vs. unknown.

## What It Does

Guides how the agent interprets and communicates confidence in memory-based claims. Does NOT assign numeric scores.

## Confidence Categories

| Level | Meaning | When to Use | Language |
|-------|---------|-------------|----------|
| **SURE** | Directly stated by user, or 3+ successful applications | User said "Remember: X", or `success` called 3+ times | State it as fact |
| **LIKELY** | Non-user source, or inferred with some evidence | Ingested content, single indirect mention | "You mentioned..." |
| **UNCERTAIN** | Inferred from context, not directly stated | Pattern detected, not confirmed | "I think..." / "It seems like..." |
| **UNKNOWN** | No relevant memory exists | Nothing in archive | "I don't have info on that" |

## How Confidence is Assigned

Confidence is set at creation time based on the source:

```
source: "user"      → sure    (directly stated by user)
source: "inferred"  → likely  (detected by agent, not confirmed)
source: "ingested"  → likely  (from external content)
```

Confidence changes over time via:
- `success` command: At 3+ successes, auto-upgrades to `sure`
- `update` command: Manual upgrade/downgrade
- `correct` command: Supersedes old entry, creates correction with `sure`
- Decay: `sure` → `likely` → `uncertain` when entries go unused (30 * (1 + access_count) days)

## Confidence Changes

### User Confirms
When a user confirms something you retrieved:
```bash
./scripts/memory.sh update <id> confidence sure
```

### User Corrects You
When a user says you got something wrong:
```bash
./scripts/memory.sh correct <wrong_id> "Correct information" "Why the old entry was wrong"
```
This supersedes the wrong entry and creates a correction record for learning.

### Successful Application
When a memory was used and the outcome was positive:
```bash
./scripts/memory.sh success <id>
```
At 3+ successes, confidence auto-upgrades to SURE.

## When to Apply Gauge

Gauge is a guideline for retrieval, not a standalone step:

1. Archive retrieves entries matching the query
2. Each entry already has a `confidence` field
3. The agent reads that field and adjusts language accordingly

## Self-Monitoring

### Before Responding
- Do retrieved memories actually answer the question?
- Are there conflicting entries? (→ run `conflicts`)
- Is confidence level appropriate for the stakes?

### After Responding
- Did the user correct you? → Use `correct` to track the mistake
- Did the user confirm? → Use `update` to upgrade confidence

## What Gauge Does NOT Do

- Assign 0.0-1.0 numeric confidence scores (fake precision)
- Automatically determine confidence from access count at creation time
- Run as code — it's a guideline for how the agent interprets the `confidence` field
