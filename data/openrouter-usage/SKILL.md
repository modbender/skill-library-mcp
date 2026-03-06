---
name: openrouter-usage
description: 'Fetch real-time OpenRouter usage totals and historical per-model spend. Use when the user asks for usage, spend, cost breakdown, or OpenRouter stats. Not for system health or non-LLM metrics.'
license: Apache-2.0
compatibility: Requires internet access. Primary path uses python3. Optional fallback uses curl (+ jq if available).
required-env-vars:
  - OPENROUTER_API_KEY
optional-env-vars:
  - OPENROUTER_MGMT_KEY
primary-credential: OPENROUTER_API_KEY
credential-description: OpenRouter API key
metadata:
  author: Arkology Studio
  version: "1.1"
allowed-tools: Bash(python3:*) Bash(curl:*) Bash(jq:*) Read
---

# OpenRouter Usage Monitor

## What this skill does
Retrieves OpenRouter usage and cost data via:
- **Live totals (Today / Week / Month)** from `/auth/key`
- **Historical per-model breakdown** from `/activity` (completed UTC days only)

---
## How to run (recommended)
Set environment variables (recommended) or create a `credentials.env` file:

```bash
export OPENROUTER_API_KEY=your_key_here
export OPENROUTER_MGMT_KEY=your_mgmt_key_here  # optional, enables model breakdown
```

Then execute: `python3 scripts/stats.py`

Alternatively, create `credentials.env` in the skill directory:
```
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MGMT_KEY=your_mgmt_key_here
```

---
## Fallback method (no Python)
If Python is unavailable, query endpoints directly:

**Live totals**
curl -sS -H "Authorization: Bearer $OPENROUTER_API_KEY"
https://openrouter.ai/api/v1/auth/key

**Per-model activity (7d)**
curl -sS -H "Authorization: Bearer $OPENROUTER_MGMT_KEY"
https://openrouter.ai/api/v1/activity
---
## Configuration
**Required:**
- `OPENROUTER_API_KEY` - Required for real-time usage totals and balance

**Optional:**
- `OPENROUTER_MGMT_KEY` - Enables per-model spend breakdown from activity endpoint

Credentials can be provided via:
1. Environment variables (recommended for security)
2. `credentials.env` file in skill directory (fallback)

---
## Output format
💰 OpenRouter Usage
Today: $X.XX* | Week: $X.XX | Month: $X.XX
Balance: $X.XX / $X.XX

Recent Models (7d):
• model-name: $X.XX (N)
...
`*` indicates live totals that may not yet appear in model breakdowns.
---

## Edge cases
- `/activity` only returns completed UTC days.
- Today’s spend may appear in totals but not per-model data until next UTC rollover.
- Invalid keys → 401/403.
- Rate limiting → 429.
- Network failures should be retried or surfaced.