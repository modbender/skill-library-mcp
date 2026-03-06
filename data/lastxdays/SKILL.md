---
name: lastxdays
description: Research and summarize what happened in the last N days (or a date range) about a topic, optionally using Reddit API and X ingestion via x-cli/API/archive with graceful fallback to web.
---

# lastXdays Skill

Summarize what happened in the **last N days** (or a specific **YYYY-MM-DD → YYYY-MM-DD** range) about a user-provided topic.

Default behavior is web-first (`web_search` + selective `web_fetch`). If optional credentials/data are available, you may ingest **Reddit via API** and **X via x-cli (preferred), API, or local archive**, falling back to web search if unavailable.

## Trigger Patterns

Activate when the user message contains any of:
- `lastXdays` / `lastxdays`
- `last x days`
- A question like: **"what happened in the last N days"** (optionally followed by a topic)

## Default Model

Default to `sonnet` (`anthropic/claude-sonnet-4-6`) when spawning as a subagent.

Use `flash` (`openrouter/google/gemini-2.0-flash-001`) **only** for simple single-source lookups (one topic, one platform, straightforward synthesis with no file reading required). Flash is unreliable for multi-step agentic work requiring tool chaining (search → fetch → read files → synthesize → report). When in doubt, use sonnet.

## Input Parsing

Parse from the user message:

### 1) Date range (preferred if explicit)
If the user supplies a range like:
- `from 2026-01-10 to 2026-02-08`
- `2026-01-10 → 2026-02-08`

Then:
- `start = YYYY-MM-DD`
- `end = YYYY-MM-DD`
- Ignore `N` if both are present.

### 2) Days (N)
Otherwise, infer `N`:
- Look for an integer `N` associated with the request, e.g.:
  - `lastxdays 7 <topic>`
  - `7 lastxdays <topic>`
  - `what happened in the last 14 days (about|re:) <topic>`
- Default: `N = 30`
- Clamp: `N = min(max(N, 1), 365)`

### 3) Sources (optional)
Supported: `web|reddit|x|all`.

Accept any of:
- `for web` / `sources web`
- `for reddit` / `sources reddit`
- `for x` / `sources x`
- `for all` / `sources all`

If unspecified: `sources = all`.

### 4) Topic
- The remaining text (after removing trigger words, N/range, and source phrases) is the topic.
- If topic is empty/unclear, ask exactly one clarifying question and stop.

## Date Range (freshness)

Use an **inclusive** range in **local time**:
- `freshness = start + "to" + end`  (e.g., `2026-01-10to2026-02-08`)

Helper for “last N days”:
- `node scripts/lastxdays_range.js <N>`

## Optional non-web ingestion (Reddit/X)

Use this helper to ingest Reddit/X when possible:
- `node scripts/lastxdays_ingest.js --source=reddit|x --topic "..." --start YYYY-MM-DD --end YYYY-MM-DD --limit 40`

The script attempts:
- **Reddit:** official API via OAuth (if credentials exist), else returns `fallback:true`
- **X:** `x-cli` search first (if installed/configured), then Twitter API v2 *recent search* (if bearer token + range <= ~7 days), then local archive at `~/clawd/data/x-archive/`, else returns `fallback:true`

Required environment variables (if you want API mode):

- Reddit:
  - `REDDIT_CLIENT_ID`
  - `REDDIT_CLIENT_SECRET`
  - either `REDDIT_REFRESH_TOKEN` (recommended) **or** `REDDIT_USERNAME` + `REDDIT_PASSWORD`
  - optional: `REDDIT_USER_AGENT`

- X API (optional; only works for recent ranges on most tiers):
  - `X_BEARER_TOKEN` (also accepts `TWITTER_BEARER_TOKEN`)

- x-cli (optional, preferred for agent use):
  - Install: `uv tool install x-cli` (or from source)
  - Configure credentials in `~/.config/x-cli/.env` (supports shared setup with x-mcp)
  - If present, `lastxdays_ingest.js` uses it before raw API/archive for X search

Credentials loader:
- Reads `~/.config/last30days/.env` if present (does not hard-fail if missing)
- Environment variables override `.env` values (file only fills blanks)

## Research Procedure

1) Compute `start/end/freshness`.

2) For each requested source:

### Web
- Query: `<topic>`
- Run `web_search` with `freshness` (count 5–8)
- Optionally `web_fetch` 2–6 best links

### Reddit
Preferred:
- Run `node scripts/lastxdays_ingest.js --source=reddit ...`
- If it returns `fallback:false`, treat returned `items[]` as “Notable links” (each has a Reddit permalink URL).
- If `items[]` is empty / too small to be useful (e.g., <3), you may *also* run the web fallback to broaden coverage.

Fallback (if `fallback:true`):
- Run `web_search` with query `site:reddit.com/r <topic>` and the same `freshness`

### X
Preferred:
- Run `node scripts/lastxdays_ingest.js --source=x ...`
- If `mode=x-cli`, `mode=api`, or `mode=archive`, treat returned `items[]` as “Notable links” (each has a URL)
  - If `mode=x-cli`, note that X results came from local `x-cli` execution
  - If `mode=archive`, note that links come from the local X archive
- If `items[]` is empty / too small to be useful (e.g., <3), you may *also* run the web fallback to broaden coverage.

Fallback (if `fallback:true`):
- Run `web_search` with query `site:x.com <topic>` and the same `freshness`
- Expect `web_fetch` to fail often on `x.com`; rely on snippets when needed

3) Select and deduplicate links/items:
- Prefer authoritative sources for Web
- Prefer high-engagement or highly-informative posts for Reddit/X
- Keep total links/items shown to ~10–20 max

## Output Format (Markdown)

Title:
- `## lastXdays — <N> days — <topic>`
  - If an explicit range was used, you may replace `<N> days` with `YYYY-MM-DD → YYYY-MM-DD`.

Then include sections in this order:

1) **Date range used**
- `YYYY-MM-DD → YYYY-MM-DD` (and optionally the freshness string)

2) **Top themes**
- 3–7 bullets summarizing the dominant storylines/trends

3) **Notable links**
Group by platform **in this order**, including only platforms actually searched:
- **Web**
- **Reddit**
- **X**

For each link/item:
- Markdown link
- One line: why it matters
- If snippet-only (fetch failed/unavailable), say so

4) **What to follow up on**
- 3 copy/pasteable next searches

## Smoke tests (local)

Date range helper:
- `node scripts/lastxdays_range.js 7`

Reddit ingest (requires creds or it will return fallback=true):
- `node scripts/lastxdays_ingest.js --source=reddit --topic "OpenClaw security vulnerability CVE" --start 2026-02-07 --end 2026-02-08 --limit 20 --pretty`

X ingest (x-cli if installed; else API if bearer token + <=7 days; else local archive; else fallback=true):
- `node scripts/lastxdays_ingest.js --source=x --topic "OpenClaw" --start 2026-02-07 --end 2026-02-08 --limit 20 --pretty`

Optional x-cli direct smoke test:
- `x-cli -v -j tweet search "OpenClaw since:2026-02-07 until:2026-02-09" --max 20`

## Examples

- `lastxdays AI agents for web`
- `last x days 10 bitcoin ETF flows`
- `what happened in the last 7 days about OpenAI for reddit`
- `14 lastXdays Apple Vision Pro for web`
- `lastxdays 30 OpenAI sources all`
- `lastxdays from 2026-01-01 to 2026-01-15 about Anthropic sources reddit`
