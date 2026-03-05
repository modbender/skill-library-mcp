---
name: tavily-search
description: "AI-optimized search and content extraction using Tavily API. Includes deep search, news filtering, and raw content extraction for LLM processing."
homepage: https://tavily.com
metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":["node"],"env":["TAVILY_API_KEY"]}}}
---

# Tavily Search

Tavily is a search engine built specifically for AI agents (LLMs). This skill provides optimized search results and content extraction.

## Prerequisites

1.  **Node.js** installed.
2.  **Tavily API Key**: Get one at [tavily.com](https://tavily.com).
3.  **Environment Variable**: Set `TAVILY_API_KEY` in your environment.

## Usage

### Search

Perform an AI-optimized search.

```bash
node scripts/search.mjs "What are the latest developments in agentic AI?"
```

**Options:**
- `-n <number>`: Number of results (default: 5, max: 20).
- `--deep`: Use advanced search depth (more tokens, better results).
- `--topic <general|news>`: Filter by topic (default: general).
- `--days <number>`: For news topic, limit results to past N days.

## Extract content from URL

```bash
node {baseDir}/scripts/extract.mjs "https://example.com/article"
```

Notes:
- Needs `TAVILY_API_KEY` from https://tavily.com
- Tavily is optimized for AI - returns clean, relevant snippets
- Use `--deep` for complex research questions
- Use `--topic news` for current events

## Troubleshooting

-   **Missing API Key**: Ensure `TAVILY_API_KEY` is exported or set in your session.
-   **Network Errors**: Check your internet connection and API quota at Tavily.
