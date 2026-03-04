---
name: intel-search
description: >
  Simplified search for news, earthquakes, Iran, tech, finance, layoffs. Bilingual (EN/中文). Flexible time.
  Data from World Monitor (fetch then query locally). Use when user asks "what's new", "iran", "earthquake", "layoffs".
  Fetch first, then query. No API key.
metadata:
  openclaw:
    requires:
      bins: ["node"]
allowed-tools: ["Bash(node:*)"]
---

# Intel Search

Search anything: news, earthquakes, Iran, tech, finance, layoffs. Bilingual. Flexible time. Like a simplified Google over local data.

## Language & Presentation

- Output includes `LANG: zh` or `LANG: en` based on user query language
- **If LANG: zh**: Translate retrieved content to Chinese when presenting
- **If LANG: en**: Keep English

## When to Use

User asks about: news, Iran, Middle East, earthquake, tech, finance, layoffs, or any keyword.

## Commands

### 1. Fetch (first or update)

```bash
cd {baseDir} && npm install && npx playwright install chromium
node scripts/fetch.mjs
```

### 2. Query

```bash
node scripts/query.mjs [query] [time]
```

Examples:
```bash
node scripts/query.mjs
node scripts/query.mjs iran 3h
node scripts/query.mjs earthquake
node scripts/query.mjs layoffs
node scripts/query.mjs oil
```

## Query Types

- **Topics (EN/中文)**: iran/伊朗, earthquake/地震, tech/科技, finance/财经, layoffs/裁员
- **Keywords**: Any word, full-text match
- **Time**: 30min, 1h, 3h, 2d, 1w, or omit for all

## Data Path

`~/.openclaw/intel-data/`, or set `INTEL_DATA_DIR`
