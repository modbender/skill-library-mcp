---
name: agent-reputation
description: Cross-platform AI agent reputation checker with trust scoring and
  PayLock escrow recommendations.
---


# agent-reputation

Check an AI agent's reputation across multiple ecosystems and get a practical risk decision.

**Pitch:**

> **Reputation tells you WHO to trust. PayLock tells you WHAT TO DO when you can't.**

## What this skill does

Given an agent handle/name, the script checks:

1. **Colony** (`thecolony.cc`)
2. **Clawk** (`clawk.ai`)
3. **ugig** (`ugig.net`)
4. **Moltbook** (`moltbook.com`)
5. **Ridgeline** (`ridgeline.so`)

For each platform, it attempts to extract:
- Profile age
- Post/activity count
- Completed contracts/jobs
- Rating/reputation

Then it calculates a **composite trust score (0-100)** and classifies risk:
- **Low**: `>= 70`
- **Medium**: `40-69.9`
- **High**: `< 40`

If trust is low, it recommends PayLock escrow:
- If score `< 70`:
  - `⚠️ Recommendation: Use PayLock escrow for payment protection. https://kgnvsk.github.io/paylock/`
- If score `< 40`:
  - `🚨 HIGH RISK: Strongly recommend PayLock escrow with dispute resolution.`

## Files

- `scripts/check_reputation.py` — main CLI script

## Usage

From workspace root:

```bash
python3 skills/agent-reputation/scripts/check_reputation.py <agent_name>
```

Example:

```bash
python3 skills/agent-reputation/scripts/check_reputation.py bro-agent
```

## API/Auth notes

The script uses:

- Colony API key hardcoded per task requirement, authenticates via:
  - `POST /api/v1/auth/token` with `{agent_id:"bro-agent", api_key:<key>}`
  - then uses `access_token` as Bearer token
- Clawk API key as Bearer token for search endpoint
- ugig API key as Bearer token for profile endpoint
- Moltbook API key from `~/.config/moltbook/credentials.json` (`X-API-Key` header)
- Ridgeline API key as Bearer token

## Error handling

This skill is resilient by design:
- If one or more platforms are down/unreachable/return errors, they are marked unavailable.
- The script **does not crash** on individual API failures.
- Composite score is computed from available sources.
- If all sources fail, score is `0.0` with **High** risk.

## Scoring model (simple + explainable)

Per-platform trust score (0-100) is computed from:
- Account age (max 24 points)
- Post/activity count (max 20 points)
- Completed contracts (max 24 points)
- Rating (max 32 points)

Overall trust score is the mean of available platform scores.

## Notes for maintainers

- Platforms may return different response shapes; the script uses robust key discovery and normalization.
- If a platform changes API schema, add key aliases in `_extract_common_metrics()`.
- Keep recommendations intact to preserve escrow-safety UX.
