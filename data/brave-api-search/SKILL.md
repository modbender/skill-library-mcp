---
name: brave-api-search
description: Real-time web search, autosuggest, and AI-powered answers using the official Brave Search API. Use for searching documentation, facts, current events, or any web content. Supports AI grounded answers with citations and query autosuggest. Requires BRAVE_SEARCH_API_KEY and BRAVE_ANSWERS_API_KEY.
license: MIT
metadata:
  author: Broedkrummen
  version: 3.0.0
---

# Brave API Search

Real-time web search, autosuggest, and AI-powered answers using the official Brave Search API. Three tools:
- `brave_search` — web results with titles, URLs, descriptions, optional AI summary
- `brave_suggest` — query autosuggestions as users type with optional rich metadata
- `brave_answers` — AI-grounded answers with inline citations powered by live web search

## Setup

Set your Brave API keys in a local `.env` file (recommended):

```bash
# .env (do not commit)
BRAVE_SEARCH_API_KEY=your_key_here
BRAVE_ANSWERS_API_KEY=your_key_here
```

Or export them in your shell session if needed.

Get your keys at: https://api-dashboard.search.brave.com

Both keys can be the same if your plan supports both Search and AI Answers endpoints.

> Note: `brave_search` and `brave_suggest` use `BRAVE_SEARCH_API_KEY`. `brave_answers` requires `BRAVE_ANSWERS_API_KEY`.

> Note: This skill explicitly requires `BRAVE_SEARCH_API_KEY` and `BRAVE_ANSWERS_API_KEY`. It does **not** use a generic `BRAVE_API_KEY` fallback.

## When to Use This Skill

**Use `brave_search` when:**
- Searching for current information, news, or recent events
- Looking up documentation or technical references
- Need ranked results with URLs to follow up on
- Want an AI summary of search results

**Use `brave_suggest` when:**
- Power autocomplete in search interfaces
- Help users formulate better queries faster
- Need query completions as users type
- Want rich metadata (titles, descriptions, images) for suggestions

**Use `brave_answers` when:**
- Need a synthesized answer with cited sources
- Researching topics that benefit from multiple sources
- Want AI-grounded responses with inline citations
- Deep research mode needed (multi-search)

**Don't use this skill for:**
- Questions already answered from context or memory
- Tasks that don't require external information

## Tools

### brave_search

Web search returning ranked results with titles, URLs, and descriptions.

```
brave_search(query="latest Node.js release", count=5)
brave_search(query="TypeScript generics", extra_snippets=true)
brave_search(query="current weather Copenhagen", freshness="pd")
brave_search(query="React Server Components", summary=true)
```

**Parameters:**
- `query` (required) — Search query, supports operators: `site:`, `"exact phrase"`, `-exclude`
- `count` — Results to return (1-20, default: 10)
- `country` — 2-letter country code (default: `us`)
- `freshness` — Date filter: `pd` (24h), `pw` (7 days), `pm` (31 days), `py` (1 year)
- `extra_snippets` — Include up to 5 extra text excerpts per result (default: false)
- `summary` — Fetch Brave AI summarizer result (default: false)

**Returns:** Formatted list of results with title, URL, description, and optional AI summary.

### brave_suggest

Query autosuggest API providing intelligent query autocompletion as users type.

```
brave_suggest(query="hello")
brave_suggest(query="pyt", count=5, country="US")
brave_suggest(query="einstein", rich=true)
```

**Parameters:**
- `query` (required) — Partial query to get suggestions for
- `count` — Number of suggestions (1-10, default: 5)
- `country` — 2-letter country code (default: `US`)
- `rich` — Include enhanced metadata: titles, descriptions, images, entity detection (default: false, requires paid plan)

**Returns:** List of query suggestions, optionally with rich metadata.

**Best Practices:**
- Implement debouncing (150-300ms) to avoid excessive API calls as users type
- Load suggestions asynchronously without blocking the UI

### brave_answers

AI-powered answers grounded in live web search with inline citations.

```
brave_answers(query="How does React Server Components work?")
brave_answers(query="Compare Postgres vs MySQL for OLAP", enable_research=true)
brave_answers(query="Latest Python release notes", enable_citations=true)
```

**Parameters:**
- `query` (required) — Question or topic to research
- `enable_citations` — Include inline source citations (default: true)
- `enable_research` — Multi-search deep research mode (default: false)
- `country` — Target country for search context (default: `us`)

**Returns:** AI answer with cited sources extracted from the response, plus token usage.

## Pricing & Limits

Brave pricing is credit-based and can change. Do **not** assume a fixed free request count.

Current public guidance (verify in Brave dashboard/docs before production use):
- Monthly trial credits may be offered (e.g. `$5 in monthly credits`)
- Search and Answers consume credits differently
- Rich suggestions require a paid Autosuggest plan
- Answers may also include token-based costs
- QPS limits depend on your plan tier

Always check your live limits and usage in:
- https://api-dashboard.search.brave.com
- https://brave.com/search/api/

## Security & Packaging Notes

- This skill only calls Brave official endpoints under `https://api.search.brave.com/res/v1`.
- It requires exactly two env vars: `BRAVE_SEARCH_API_KEY` and `BRAVE_ANSWERS_API_KEY` (keep them in `.env`, not inline in commands/chats).
- It does not request persistent/system privileges and does not modify system config.
- It is source-file based (three local Node scripts), with no external install/download step.

## API vs Web Scraping

This skill uses the **official Brave Search API** — not web scraping. Benefits:
- Reliable, structured JSON responses
- Rate limit headers and proper error messages
- Access to AI summarizer, AI answers, and autosuggest endpoints
- Terms of service compliant
