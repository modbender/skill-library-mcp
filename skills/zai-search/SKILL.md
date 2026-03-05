---
name: z.ai-web-search
description: AI-optimized web search via Z.AI Web Search API. Returns structured results (title, URL, summary) for LLM processing.
homepage: https://docs.z.ai/guides/tools/web-search
metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":["node"],"env":["ZAI_API_KEY"]},"primaryEnv":"ZAI_API_KEY"}}
---

# Z.AI Web Search

AI-optimized web search using Z.AI Web Search API. Designed for LLMs – returns structured results with titles, URLs, summaries, site names and favicons.

## Search

```bash
node {baseDir}/scripts/search.mjs "query"
node {baseDir}/scripts/search.mjs "query" -n 15
node {baseDir}/scripts/search.mjs "query" --domain sohu.com
node {baseDir}/scripts/search.mjs "query" --recency oneWeek
node {baseDir}/scripts/search.mjs "query" --days 7
```

## Options

- `-n <count>`: Number of results (default: 10, max: 50)
- `--domain <domain>`: Limit results to specified domain (e.g. `sohu.com`, `www.example.com`)
- `--recency <filter>`: Time range – `oneDay`, `oneWeek`, `oneMonth`, `oneYear`, `noLimit` (default)
- `--days <n>`: Shorthand for recency (1→oneDay, 7→oneWeek, 30→oneMonth, 365→oneYear)

## Extract content from URL

```bash
node {baseDir}/scripts/extract.mjs "https://example.com/article"
```

Note: Z.AI does not provide an extract API. This script uses native fetch to retrieve pages and strips HTML for basic text extraction. For richer content, use search results (they include summaries).

## Setup

- Get API key at [Z.AI Platform](https://chat.z.ai)
- Set `ZAI_API_KEY` in your environment
- Docs: [Web Search Guide](https://docs.z.ai/guides/tools/web-search)
