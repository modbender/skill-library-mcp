---
name: token-optimizer
description: Automatically analyze and reduce OpenClaw token waste through context compression, tool-call deduplication insights, model selection guidance, and session hygiene checks. Use when sessions are nearing context limits, costs are climbing, or you want proactive token optimization before expensive tasks.
---

# Token Optimizer

## Overview

Use this skill to optimize OpenClaw token usage with a local CLI that performs analysis, compression snapshots, health checks, cleanup planning, and preflight token budgeting.

## Quick Start

```bash
$OPENCLAW_SKILLS_DIR/token-optimizer/scripts/token-optimize --analyze --period 7d
```

## Core Commands

1) Enable local optimizer config:

```bash
$OPENCLAW_SKILLS_DIR/token-optimizer/scripts/token-optimize --enable
```

2) Optimization analysis:

```bash
$OPENCLAW_SKILLS_DIR/token-optimizer/scripts/token-optimize --analyze --period 7d
```

3) Force context compression snapshot:

```bash
$OPENCLAW_SKILLS_DIR/token-optimizer/scripts/token-optimize --compress --threshold 0.7 --session agent:main:main
```

4) Session health check:

```bash
$OPENCLAW_SKILLS_DIR/token-optimizer/scripts/token-optimize --health-check --active-minutes 120
```

5) Auto-cleanup planning and apply:

```bash
$OPENCLAW_SKILLS_DIR/token-optimizer/scripts/token-optimize --cleanup
$OPENCLAW_SKILLS_DIR/token-optimizer/scripts/token-optimize --cleanup --apply
```

## Preflight Optimization

Use preflight planning before expensive task batches:

```bash
$OPENCLAW_SKILLS_DIR/token-optimizer/scripts/token-optimize \
  --preflight /path/to/actions.json \
  --session-limit 180000
```

`actions.json` should be a JSON array of planned operations, for example:

```json
[
  {"type": "web_search", "query": "..."},
  {"type": "web_fetch", "url": "..."},
  {"type": "summarize", "target": "youtube"}
]
```

## Output Artifacts

- Compression snapshots: `$OPENCLAW_WORKSPACE/token-usage/compressed/`
- Optional JSON output: `--format json --output /path/file.json`
- Baseline config (from `--enable`): `$OPENCLAW_WORKSPACE/token-usage/token-optimizer.config.json`

## Defaults

Default behavior is configured in:

- `config/defaults.json`

Override with:

```bash
$OPENCLAW_SKILLS_DIR/token-optimizer/scripts/token-optimize --config /path/custom.json --analyze
```

## Resources

- `scripts/token_optimize.py`: main CLI
- `src/optimizer.py`: core optimization engine
- `src/models.py`: model selection logic
- `src/compression.py`: context compression helpers
- `src/cleanup.py`: session hygiene evaluation
- `references/operating-notes.md`: implementation details and safe-operating guidance

## Validation

```bash
python3 $OPENCLAW_SKILLS_DIR/.system/skill-creator/scripts/quick_validate.py \
  $OPENCLAW_SKILLS_DIR/token-optimizer
```
