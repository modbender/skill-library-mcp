---
name: evomap-mass-publisher
description: Generate, optimize, and publish 1000+ high-quality EvoMap bundles automatically
version: 1.0.0
signals:
  - evomap
  - bundle
  - publish
  - mass generate
  - automation
---

# EvoMap Mass Publisher v1.0.0

> Generate, optimize, and publish high-quality Gene+Capsule bundles to EvoMap automatically

## Features

- **Generate** 1000+ unique bundles with proper structure
- **Optimize** bundles for EvoMap promotion requirements
- **Publish** bundles to EvoMap with rate limiting

## Requirements

### Bundle Structure
- Gene: schema_version, category, signals_match, summary (10+), strategy (array), content (50+)
- Capsule: schema_version, trigger, gene (ref), summary (20+), content (50+), confidence (≥0.9), success_streak (≥2), blast_radius
- EvolutionEvent: Optional (+6.7% GDI)

### Auto-Promotion
- confidence ≥ 0.9
- success_streak ≥ 2
- content ≥ 50 chars
- blast_radius.files ≥ 1

## Usage

```bash
# Generate 1000 bundles
node index.js generate 1000 ./evomap-assets

# Optimize bundles
node index.js optimize ./evomap-assets

# Publish with 200ms delay
node index.js publish ./evomap-assets 200

# Full pipeline: generate + optimize + publish
node index.js all 1000 ./evomap-assets
```

## Commands

| Command | Args | Description |
|---------|------|-------------|
| `generate` | count, dir | Generate N bundles |
| `optimize` | dir | Optimize all bundles in dir |
| `publish` | dir, delay | Publish with rate limit |
| `all` | count, dir | Full pipeline |

## Output

- Bundles saved as `bundle_{topic}_{index}.json`
- Each bundle contains: Gene + Capsule + EvolutionEvent
- Asset IDs computed using canonical JSON

## Cron Usage

```bash
# Daily at 1am UTC+8 (17:00 UTC)
0 17 * * * cd /root/.openclaw/workspace/skills/evomap-mass-publisher && node index.js all 1000 /root/.openclaw/workspace/skills/evomap-daily
```

## Signals

- evomap mass publish
- batch bundle generation
- automated asset creation
