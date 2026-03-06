---
name: token-counter
description: Track and analyze OpenClaw token usage across main, cron, and sub-agent sessions with category, client, model, and tool attribution. Use when the user asks where tokens are being spent, wants daily/weekly token reports, needs per-session drilldowns, or is planning token-cost optimizations and needs evidence from transcript data.
---

# Token Counter

## Overview

Use this skill to produce token usage reports from local OpenClaw data. It parses session transcripts (`.jsonl`), session metadata, and cron definitions, then reports usage by category, client, tool, model, and top token consumers.

## Quick Start

Run:

```bash
$OPENCLAW_SKILLS_DIR/token-counter/scripts/token-counter --period 7d
```

## Common Commands

1) Basic report:

```bash
$OPENCLAW_SKILLS_DIR/token-counter/scripts/token-counter --period 7d
```

2) Focus on selected breakdowns:

```bash
$OPENCLAW_SKILLS_DIR/token-counter/scripts/token-counter \
  --period 1d \
  --breakdown tools,category,client
```

3) Analyze one session:

```bash
$OPENCLAW_SKILLS_DIR/token-counter/scripts/token-counter \
  --session agent:main:cron:d3d76f7a-7090-41c3-bb19-e2324093f9b1
```

4) Export JSON:

```bash
$OPENCLAW_SKILLS_DIR/token-counter/scripts/token-counter \
  --period 30d \
  --format json \
  --output $OPENCLAW_WORKSPACE/token-usage/token-usage-30d.json
```

5) Persist daily snapshot:

```bash
$OPENCLAW_SKILLS_DIR/token-counter/scripts/token-counter \
  --period 1d \
  --save
```

This writes JSON to:
`$OPENCLAW_WORKSPACE/token-usage/daily/YYYY-MM-DD.json`

## Defaults and Data Sources

- Sessions index: `$OPENCLAW_DATA_DIR/agents/main/sessions/sessions.json`
- Session transcripts: `$OPENCLAW_DATA_DIR/agents/main/sessions/*.jsonl`
- Cron definitions: `$OPENCLAW_DATA_DIR/cron/jobs.json`

The parser reads assistant `usage` fields for token counts and uses tool-call records for attribution.

## Notes on Attribution

- Tool token attribution is heuristic: assistant-message tokens are split across tool calls in that message.
- Session `totalTokens` may come from either session index metadata or transcript usage sums (max is used).
- Client detection is rules-based (`personal`, `bonsai`, `mixed`, `unknown`) using path/domain/email markers.

## Validation

Run:

```bash
python3 $OPENCLAW_SKILLS_DIR/skill-creator/scripts/quick_validate.py \
  $OPENCLAW_SKILLS_DIR/token-counter
```

## References

See:
- `references/classification-rules.md` for category/client detection logic and keyword mapping.
