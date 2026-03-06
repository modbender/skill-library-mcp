---
name: n2-free-search
description: Free, unlimited web search for AI agents via SearXNG — no API keys needed.
homepage: https://nton2.com
user-invocable: true
---

# 🔍 N2 Free Search — MCP Server Skill

Free, private, unlimited web search for your AI agent. No API keys, no credit cards, no rate limits.

## Why Use This?

| | Brave Search API | Google Custom Search | **N2 Free Search** |
|---|---|---|---|
| **Cost** | $5 / 1,000 queries | $5 / 1,000 queries | **Free forever** |
| **API Key** | Required | Required | **Not needed** |
| **Search Engines** | Brave only | Google only | **70+ engines** |

## Quick Setup

### Option 1: Public Mode (Zero Setup)
Add to your MCP config:
```json
{
  "mcpServers": {
    "n2-free-search": {
      "command": "npx",
      "args": ["-y", "n2-free-search"]
    }
  }
}
```

### Option 2: Self-Hosted (Maximum Privacy)
```json
{
  "mcpServers": {
    "n2-free-search": {
      "command": "npx",
      "args": ["-y", "n2-free-search"],
      "env": {
        "SEARXNG_URL": "http://localhost:8080"
      }
    }
  }
}
```

## Available Tools
- **n2_web_search** — Search the web (Google, Bing, DuckDuckGo + 70 more)
- **n2_news_search** — Search recent news articles
- **n2_image_search** — Search for images
- **n2_video_search** — Search for videos
- **n2_suggest** — Get search suggestions / autocomplete

## Links
- NPM: https://www.npmjs.com/package/n2-free-search
- GitHub: https://github.com/choihyunsus/n2-free-search
- Website: https://nton2.com

---
*Part of the N2 AI Body series — Building the Body for AI*
