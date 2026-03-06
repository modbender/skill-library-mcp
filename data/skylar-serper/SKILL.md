---
name: serper
description: Search Google programmatically using Serper.dev API. Use when you need to perform web searches, find information online, or research topics. Supports query parameters, result limiting, and geographic/language targeting.
metadata:
  openclaw:
    requires:
      env:
        - name: SERPER_API_KEY
          description: Serper.dev API key for Google search
          required: true
---

# Serper.dev Google Search

Search Google via Serper.dev API. Clean, structured results without scraping.

## Quick Start

Requires `SERPER_API_KEY` environment variable.

```javascript
serper_search({
  q: "OpenClaw AI agent",
  num: 5,
  gl: "us",
  hl: "en"
})
```

## Parameters

| Param | Required | Default | Description |
|-------|----------|---------|-------------|
| `q` | Yes | — | Search query |
| `num` | No | 5 | Results count (1-100) |
| `gl` | No | — | Country code (us, uk, th) |
| `hl` | No | — | Language code (en, th) |

## Setup

1. Get API key: https://serper.dev
2. Set environment: `export SERPER_API_KEY=your_key`

## Tool Location

`tools/serper_search.js`
