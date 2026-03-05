---
name: dataforseo-cli
description: LLM-friendly keyword research CLI for AI agents. Check search volume, CPC, keyword difficulty, and competition via DataForSEO API. Find related keywords, analyze competitor rankings. Outputs TSV by default (optimized for agent context windows). Use when doing SEO research, content planning, or competitive keyword analysis.
license: MIT
metadata:
  author: alexgusevski
  version: "1.0.6"
---

# Keyword Research with dataforseo-cli

LLM-friendly keyword research CLI. Wraps the DataForSEO API and outputs TSV by default — compact, structured, and optimized for agent context windows.

**npm:** https://www.npmjs.com/package/dataforseo-cli
**GitHub:** https://github.com/alexgusevski/dataforseo-cli

## Setup

### 1. Install from npm

```bash
npm install -g dataforseo-cli
```

### 2. Check credentials

```bash
dataforseo-cli status
```

If credentials are already configured, you're good to go. If not, authenticate:

```bash
# With login + password
dataforseo-cli --set-credentials login=YOUR_LOGIN password=YOUR_PASSWORD

# Or with base64 token (from DataForSEO email)
dataforseo-cli --set-credentials base64=YOUR_BASE64_TOKEN
```

Credentials are stored in `~/.config/dataforseo-cli/config.json`. The `locations` and `languages` commands work without credentials (local data).

## Commands

### `status` — Check credentials

Check if API credentials are configured without making any API calls.

```bash
dataforseo-cli status
```

Exits 0 if configured, exits 1 if not. Shows login username (not password).

### `volume` — Keyword metrics

Get search volume, CPC, keyword difficulty (0–100), competition level, and 12-month search trend.

```bash
dataforseo-cli volume <keywords...> [options]
```

**Arguments:**
- `<keywords...>` — One or more keywords (required). Batch multiple keywords in one call to save API requests.

**Options:**
- `-l, --location <code>` — Location code (default: `2840` = US)
- `--language <code>` — Language code (default: `en`)
- `--json` — Output as JSON array
- `--table` / `--human` — Output as human-readable table

**Example:**
```bash
dataforseo-cli volume "seo tools" "keyword research" "backlink checker"
```

**Output (TSV):**
```
keyword	volume	cpc	difficulty	competition	trend
seo tools	12500	2.35	45	HIGH	14800,13900,12500,12100,11800,12000,12500,13000,12800,12500,12200,11900
```

- `difficulty` — 0–100 scale (0-30 easy, 31-60 medium, 61-100 hard)
- `cpc` — Cost per click in USD
- `competition` — LOW / MEDIUM / HIGH
- `trend` — 12 monthly search volumes, newest first

### `related` — Keyword suggestions

Find related keyword ideas from a seed keyword.

```bash
dataforseo-cli related <seed> [options]
```

**Arguments:**
- `<seed>` — Seed keyword (required, single keyword)

**Options:**
- `-l, --location <code>` — Location code (default: `2840` = US)
- `--language <code>` — Language code (default: `en`)
- `-n, --limit <n>` — Max results (default: `50`)
- `--json` — Output as JSON array
- `--table` / `--human` — Output as human-readable table

**Example:**
```bash
dataforseo-cli related "ai agents" -n 20
```

**Output (TSV):**
```
keyword	volume	cpc	competition	difficulty
best ai agents	8100	3.10	0.82	52
ai agent framework	2400	1.85	0.65	38
```

### `competitor` — Domain keyword analysis

See what keywords a domain currently ranks for.

```bash
dataforseo-cli competitor <domain> [options]
```

**Arguments:**
- `<domain>` — Target domain (required, e.g. `ahrefs.com`)

**Options:**
- `-l, --location <code>` — Location code (default: `2840` = US)
- `--language <code>` — Language code (default: `en`)
- `-n, --limit <n>` — Max results (default: `50`)
- `--json` — Output as JSON array
- `--table` / `--human` — Output as human-readable table

**Example:**
```bash
dataforseo-cli competitor semrush.com -n 10
```

**Output (TSV):**
```
keyword	position	volume	cpc	difficulty	url
backlink checker	1	33100	4.50	72	https://ahrefs.com/backlink-checker
```

### `locations` — Look up location codes

List all available location codes, or filter by name. Works offline — no API credentials needed.

```bash
dataforseo-cli locations [search] [--json]
```

**Arguments:**
- `[search]` — Optional filter by name (e.g. `sweden`, `new york`)

**Without search** — lists all locations:
```bash
dataforseo-cli locations
```

**With search** — filters by name:
```bash
dataforseo-cli locations sweden
```

**Output (TSV):**
```
code	name	country	type
2752	Sweden	SE	Country
```

### `languages` — Look up language codes

List all available language codes, or filter by name. Works offline — no API credentials needed.

```bash
dataforseo-cli languages [search] [--json]
```

**Without search** — lists all languages:
```bash
dataforseo-cli languages
```

**With search** — filters by name:
```bash
dataforseo-cli languages swedish
```

**Output (TSV):**
```
name	code
Swedish	sv
```

## Output Formats

All data commands default to TSV (tab-separated values) — the most token-efficient structured format for LLMs.

| Flag | Description |
|------|-------------|
| *(default)* | TSV — fewest tokens, best for agent pipelines |
| `--json` | JSON array — use when you need structured parsing |
| `--table` / `--human` | Human-readable aligned table — for human review |

## Caching

Results are cached in `~/.config/dataforseo-cli/cache/` to avoid duplicate API calls and save costs. Same query + location + language = cache hit.

```bash
dataforseo-cli --print-cache
```

## Workflow: SEO Article Research

1. **Start with seed keyword:** `dataforseo-cli volume "your topic"`
2. **Expand:** `dataforseo-cli related "your topic" -n 30`
3. **Filter:** Pick keywords with volume > 100, difficulty < 60
4. **Check competitors:** `dataforseo-cli competitor competitor-domain.com -n 20`
5. **Write article** targeting the best keyword cluster

## Tips
- Batch keywords in `volume` — DataForSEO charges per API request, not per keyword
- Default location is USA (2840). Always set `--location` for local/international SEO
- Use `locations` and `languages` without arguments to see all available options
- Difficulty scale: 0-30 easy, 31-60 medium, 61-100 hard
