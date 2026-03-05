---
name: web_search
description: Web search and URL fetching via Perplexity (default: sonar, optional: sonar-pro). Use when searching the web, looking up information, fetching URL content, or configuring web search settings. Covers web_search tool (Perplexity direct API) and web_fetch tool (HTML to markdown extraction).
homepage: https://github.com/aligurelli/clawd/tree/main/skills/web_search
metadata: {"clawdbot":{"emoji":"🔎"}}
---

# Web Search Skill

Web search via Perplexity (default: sonar) and URL content fetching. Sonar-pro is optional for deeper analysis.

## Credentials

This skill uses the Perplexity key configured in your OpenClaw setup. No shared or third-party keys are used.

If your environment is not already configured, set `PERPLEXITY_API_KEY` or configure the key in OpenClaw config.

**Recommended default (cost-effective):**
```json5
{
  tools: {
    web: {
      search: {
        provider: "perplexity",
        perplexity: {
          apiKey: "<your-perplexity-api-key>",
          baseUrl: "https://api.perplexity.ai",
          model: "sonar"
        }
      }
    }
  }
}
```

**Optional deep mode (higher quality, higher cost):**
```json5
{
  tools: {
    web: {
      search: {
        perplexity: {
          model: "sonar-pro"
        }
      }
    }
  }
}
```

Use `sonar-pro` only when you explicitly need deeper analysis.

Get your API key at: https://www.perplexity.ai/settings/api

## Data Handling

- All search queries are sent to Perplexity's API (`https://api.perplexity.ai`)
- `web_fetch` fetched page contents are processed locally by OpenClaw (not sent to Perplexity)
- This instruction-only skill does not persist data by itself; query handling/retention is governed by OpenClaw + Perplexity policies
- Search queries are sent to Perplexity; do not include secrets or private data in queries
- Your own Perplexity API key and account terms apply

## web_search

Search the web. Returns AI-synthesized answers with citations.

Parameters:
- `query` (required) — search query
- `count` (1-10) — number of results
- `country` — 2-letter code: TR, US, DE, ALL
- `search_lang` — result language: tr, en, de, fr
- `freshness` — time filter: pd (day), pw (week), pm (month), py (year)

### Including Social Platform Results

For market research or user feedback queries, add social platform names naturally to the query. This makes Perplexity include results from Reddit, Twitter, Quora etc. alongside normal web results — no filtering, no restriction, just broader coverage.

```
web_search(query="cell tower finder app complaints features users want reddit twitter quora")
```

Perplexity will pull from both regular websites AND social platforms in one search.

For cases where you ONLY want a specific platform, use `site:` operator:
```
web_search(query="site:reddit.com best stud finder app")
```

Examples:
```
web_search(query="latest Flutter updates", freshness="pw")
web_search(query="İstanbul hava durumu", country="TR", search_lang="tr")
web_search(query="AI news", count=5, freshness="pd")
web_search(query="GLP-1 tracker app wish features complaints reddit twitter quora")
```

## web_fetch

Fetch URL content as markdown/text. No JS execution. Content is extracted locally.

Parameters:
- `url` (required) — HTTP/HTTPS URL
- `extractMode` — markdown (default) or text
- `maxChars` — truncation limit

## Perplexity Models (User Choice)

- `sonar` (default) — fast Q&A + web search, cost-effective
- `sonar-pro` — multi-step reasoning + web search (use when deeper analysis is needed)
- `sonar-reasoning-pro` — deep chain-of-thought research (expensive, use sparingly)

Set the model in config based on your budget/quality preference.
