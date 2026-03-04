---
name: parallel-ai-search
description: Web search + URL extraction via Parallel Search/Extract APIs. Use for up-to-date research, domain-scoped searching, and extracting LLM-ready excerpts/markdown from URLs.
homepage: https://docs.parallel.ai/search/search-quickstart
metadata: {"openclaw":{"emoji":"🔎","homepage":"https://docs.parallel.ai/","requires":{"bins":["node"],"env":["PARALLEL_API_KEY"]},"primaryEnv":"PARALLEL_API_KEY"}}
---

# Parallel AI Search (OpenClaw skill)

Use this skill to run web research through **Parallel Search** (ranked, LLM-optimised excerpts) and **Parallel Extract** (clean markdown from specific URLs, including JS-heavy pages and PDFs).

The skill ships tiny **Node .mjs** helpers so the agent can call the APIs deterministically via the OpenClaw **exec** tool.

## Quick start

### 1) Provide the API key

Prefer configuring it in `~/.openclaw/openclaw.json` (host runs):

```json5
{
  skills: {
    entries: {
      "parallel-ai-search": {
        enabled: true,
        apiKey: "YOUR_PARALLEL_API_KEY"
      }
    }
  }
}
```

Notes:
- If the agent run is **sandboxed**, the Docker sandbox does **not** inherit host env. Provide the key via `agents.defaults.sandbox.docker.env` (or bake it into the image).
- This skill is gated on `PARALLEL_API_KEY`. If it’s missing, OpenClaw won’t load the skill.

### 2) Run a search

Use **exec** to run:

```bash
node {baseDir}/scripts/parallel-search.mjs \
  --objective "When was the United Nations established? Prefer UN websites." \
  --query "Founding year UN" \
  --query "Year of founding United Nations" \
  --max-results 5 \
  --mode one-shot
```

### 3) Extract content from URLs

```bash
node {baseDir}/scripts/parallel-extract.mjs \
  --url "https://www.un.org/en/about-us/history-of-the-un" \
  --objective "When was the United Nations established?" \
  --excerpts \
  --no-full-content
```

### 4) One command: search → extract top results

```bash
node {baseDir}/scripts/parallel-search-extract.mjs \
  --objective "Find recent research on quantum error correction" \
  --query "quantum error correction 2024" \
  --query "QEC algorithms" \
  --max-results 6 \
  --top 3 \
  --excerpts
```

## When to use

Trigger this skill when the user asks for:
- “Parallel search”, “parallel.ai search”, “Parallel Extract”, “Search API”, “Extract API”
- “web research with Parallel”, “LLM-optimised excerpts”, “source_policy/include_domains”, “after_date”, “fetch_policy”
- “extract clean markdown from URL/PDF”, “crawl a JS-heavy page”, “get fresh web results”

## Default workflow

1. **Search** with an *objective* + a few *search_queries*.
2. **Inspect** titles/URLs/publish dates; choose the best sources.
3. **Extract** the specific pages you actually need (top N URLs).
4. **Answer** using the extracted excerpts/full content.

Use **Search** to discover; use **Extract** to read.

## Best-practice prompting for Parallel

### Objective
Write 1–3 sentences describing:
- the real task context (why you need the info)
- freshness constraints (“prefer 2025+”, “after 2024-01-01”, “use latest docs”)
- preferred sources (“official docs”, “standards bodies”, “GitHub releases”)

### search_queries
Add 3–8 keyword queries that include:
- the specific terms, version numbers, error strings
- common synonyms
- if relevant, date terms (“2025”, “2026”, “Jan 2026”)

### Mode
- Use `mode=one-shot` for single-pass questions (default).
- Use `mode=agentic` for multi-step research loops (shorter, more token-efficient excerpts).

### Source policy
When you need tight control, set `source_policy`:
- `include_domains`: allowlist (max 10)
- `exclude_domains`: denylist (max 10)
- `after_date`: RFC3339 date (`YYYY-MM-DD`) to filter for freshness

## Scripts

All scripts print a JSON response to stdout by default.

### `scripts/parallel-search.mjs`

Calls `POST https://api.parallel.ai/v1beta/search`.

Common flags:
- `--objective "..."`
- `--query "..."` (repeatable)
- `--mode one-shot|agentic`
- `--max-results N` (1–20)
- `--include-domain example.com` (repeatable)
- `--exclude-domain example.com` (repeatable)
- `--after-date YYYY-MM-DD`
- `--excerpt-max-chars N` (per result)
- `--excerpt-max-total-chars N` (across results)
- `--fetch-max-age-seconds N` (force freshness; 0 disables)
- `--request path/to/request.json` (advanced: full request passthrough)
- `--request-json '{"objective":"..."}'` (advanced)

### `scripts/parallel-extract.mjs`

Calls `POST https://api.parallel.ai/v1beta/extract`.

Common flags:
- `--url "https://..."` (repeatable, max 10)
- `--objective "..."`
- `--query "..."` (repeatable)
- `--excerpts` / `--no-excerpts`
- `--full-content` / `--no-full-content`
- `--excerpts-max-chars N` / `--excerpts-max-total-chars N`
- `--full-max-chars N`
- `--fetch-max-age-seconds N` (min 600 when set)
- `--fetch-timeout-seconds N`
- `--disable-cache-fallback`
- `--request path/to/request.json` (advanced)

### `scripts/parallel-search-extract.mjs`

Convenience pipeline:
1) Search
2) Extract the top N URLs from the search results (single Extract call)

Common flags:
- All `parallel-search.mjs` flags
- `--top N` (1–10)
- Extraction toggles: `--excerpts`, `--full-content`, plus the extract excerpt/full settings

## Output handling conventions

When turning API output into a user-facing answer:
- Prefer **official / primary sources** when possible.
- Quote or paraphrase **only** the relevant extracted text.
- Include **URL + publish_date** (when present) for transparency.
- If results disagree, present both and say what each source claims.

## Error handling

Scripts exit with:
- `0` success
- `1` unexpected error (network, JSON parse, etc.)
- `2` invalid arguments
- `3` API error (non-2xx) — response body is printed to stderr when possible

## References

Load these only when needed:
- `references/parallel-api.md` — compact API field/shape reference
- `references/openclaw-config.md` — OpenClaw config + sandbox env notes
- `references/prompting.md` — objective/query templates and research patterns
