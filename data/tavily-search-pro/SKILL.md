---
name: tavily-search-pro
slug: tavily-search-pro
description: >
  Tavily AI search platform with 5 modes: Search (web/news/finance), Extract (URL content),
  Crawl (website crawling), Map (sitemap discovery), and Research (deep research with citations).
  Use for: web search with LLM answers, content extraction, site crawling, deep research.
version: 1.0.0
author: Leo 🦁
tags: [search, tavily, web, news, finance, extract, crawl, research, api]
metadata: {"clawdbot":{"emoji":"🔎","requires":{"env":["TAVILY_API_KEY"]},"primaryEnv":"TAVILY_API_KEY","install":[{"id":"pip","kind":"pip","package":"tavily-python","label":"Install dependencies (pip)"}]}}
allowed-tools: [exec]
---

# Tavily Search 🔎

AI-powered web search platform with 5 modes: Search, Extract, Crawl, Map, and Research.

## Requirements

- `TAVILY_API_KEY` environment variable

## Configuration

| Env Variable | Default | Description |
|---|---|---|
| `TAVILY_API_KEY` | — | **Required.** Tavily API key |

Set in OpenClaw config:
```json
{
  "env": {
    "TAVILY_API_KEY": "tvly-..."
  }
}
```

## Script Location

```bash
python3 skills/tavily/lib/tavily_search.py <command> "query" [options]
```

---

## Commands

### search — Web Search (Default)

General-purpose web search with optional LLM-synthesized answer.

```bash
python3 lib/tavily_search.py search "query" [options]
```

**Examples:**
```bash
# Basic search
python3 lib/tavily_search.py search "latest AI news"

# With LLM answer
python3 lib/tavily_search.py search "what is quantum computing" --answer

# Advanced depth (better results, 2 credits)
python3 lib/tavily_search.py search "climate change solutions" --depth advanced

# Time-filtered
python3 lib/tavily_search.py search "OpenAI announcements" --time week

# Domain filtering
python3 lib/tavily_search.py search "machine learning" --include-domains arxiv.org,nature.com

# Country boost
python3 lib/tavily_search.py search "tech startups" --country US

# With raw content and images
python3 lib/tavily_search.py search "solar energy" --raw --images -n 10

# JSON output
python3 lib/tavily_search.py search "bitcoin price" --json
```

**Output format (text):**
```
Answer: <LLM-synthesized answer if --answer>

Results:
  1. Result Title
     https://example.com/article
     Content snippet from the page...

  2. Another Result
     https://example.com/other
     Another snippet...
```

---

### news — News Search

Search optimized for news articles. Sets `topic=news`.

```bash
python3 lib/tavily_search.py news "query" [options]
```

**Examples:**
```bash
python3 lib/tavily_search.py news "AI regulation"
python3 lib/tavily_search.py news "Israel tech" --time day --answer
python3 lib/tavily_search.py news "stock market" --time week -n 10
```

---

### finance — Finance Search

Search optimized for financial data and news. Sets `topic=finance`.

```bash
python3 lib/tavily_search.py finance "query" [options]
```

**Examples:**
```bash
python3 lib/tavily_search.py finance "NVIDIA stock analysis"
python3 lib/tavily_search.py finance "cryptocurrency market trends" --time month
python3 lib/tavily_search.py finance "S&P 500 forecast 2026" --answer
```

---

### extract — Extract Content from URLs

Extract readable content from one or more URLs.

```bash
python3 lib/tavily_search.py extract URL [URL...] [options]
```

**Parameters:**
- `urls`: One or more URLs to extract (positional args)
- `--depth basic|advanced`: Extraction depth
- `--format markdown|text`: Output format (default: markdown)
- `--query "text"`: Rerank extracted chunks by relevance to query

**Examples:**
```bash
# Extract single URL
python3 lib/tavily_search.py extract "https://example.com/article"

# Extract multiple URLs
python3 lib/tavily_search.py extract "https://url1.com" "https://url2.com"

# Advanced extraction with relevance reranking
python3 lib/tavily_search.py extract "https://arxiv.org/paper" --depth advanced --query "transformer architecture"

# Text format output
python3 lib/tavily_search.py extract "https://example.com" --format text
```

**Output format:**
```
URL: https://example.com/article
─────────────────────────────────
<Extracted content in markdown/text>

URL: https://another.com/page
─────────────────────────────────
<Extracted content>
```

---

### crawl — Crawl a Website

Crawl a website starting from a root URL, following links.

```bash
python3 lib/tavily_search.py crawl URL [options]
```

**Parameters:**
- `url`: Root URL to start crawling
- `--depth basic|advanced`: Crawl depth
- `--max-depth N`: Maximum link depth to follow (default: 2)
- `--max-breadth N`: Maximum pages per depth level (default: 10)
- `--limit N`: Maximum total pages (default: 10)
- `--instructions "text"`: Natural language crawl instructions
- `--select-paths p1,p2`: Only crawl these path patterns
- `--exclude-paths p1,p2`: Skip these path patterns
- `--format markdown|text`: Output format

**Examples:**
```bash
# Basic crawl
python3 lib/tavily_search.py crawl "https://docs.example.com"

# Focused crawl with instructions
python3 lib/tavily_search.py crawl "https://docs.python.org" --instructions "Find all asyncio documentation" --limit 20

# Crawl specific paths only
python3 lib/tavily_search.py crawl "https://example.com" --select-paths "/blog,/docs" --max-depth 3
```

**Output format:**
```
Crawled 5 pages from https://docs.example.com

Page 1: https://docs.example.com/intro
─────────────────────────────────
<Content>

Page 2: https://docs.example.com/guide
─────────────────────────────────
<Content>
```

---

### map — Sitemap Discovery

Discover all URLs on a website (sitemap).

```bash
python3 lib/tavily_search.py map URL [options]
```

**Parameters:**
- `url`: Root URL to map
- `--max-depth N`: Depth to follow (default: 2)
- `--max-breadth N`: Breadth per level (default: 20)
- `--limit N`: Maximum URLs (default: 50)

**Examples:**
```bash
# Map a site
python3 lib/tavily_search.py map "https://example.com"

# Deep map
python3 lib/tavily_search.py map "https://docs.python.org" --max-depth 3 --limit 100
```

**Output format:**
```
Sitemap for https://example.com (42 URLs found):

  1. https://example.com/
  2. https://example.com/about
  3. https://example.com/blog
  ...
```

---

### research — Deep Research

Comprehensive AI-powered research on a topic with citations.

```bash
python3 lib/tavily_search.py research "query" [options]
```

**Parameters:**
- `query`: Research question
- `--model mini|pro|auto`: Research model (default: auto)
  - `mini`: Faster, cheaper
  - `pro`: More thorough
  - `auto`: Let Tavily decide
- `--json`: JSON output (supports structured output schema)

**Examples:**
```bash
# Basic research
python3 lib/tavily_search.py research "Impact of AI on healthcare in 2026"

# Pro model for thorough research
python3 lib/tavily_search.py research "Comparison of quantum computing approaches" --model pro

# JSON output
python3 lib/tavily_search.py research "Electric vehicle market analysis" --json
```

**Output format:**
```
Research: Impact of AI on healthcare in 2026

<Comprehensive research report with citations>

Sources:
  [1] https://source1.com
  [2] https://source2.com
  ...
```

---

## Options Reference

| Option | Applies To | Description | Default |
|---|---|---|---|
| `--depth basic\|advanced` | search, news, finance, extract | Search/extraction depth | basic |
| `--time day\|week\|month\|year` | search, news, finance | Time range filter | none |
| `-n NUM` | search, news, finance | Max results (0-20) | 5 |
| `--answer` | search, news, finance | Include LLM answer | off |
| `--raw` | search, news, finance | Include raw page content | off |
| `--images` | search, news, finance | Include image URLs | off |
| `--include-domains d1,d2` | search, news, finance | Only these domains | none |
| `--exclude-domains d1,d2` | search, news, finance | Exclude these domains | none |
| `--country XX` | search, news, finance | Boost country results | none |
| `--json` | all | Structured JSON output | off |
| `--format markdown\|text` | extract, crawl | Content format | markdown |
| `--query "text"` | extract | Relevance reranking query | none |
| `--model mini\|pro\|auto` | research | Research model | auto |
| `--max-depth N` | crawl, map | Max link depth | 2 |
| `--max-breadth N` | crawl, map | Max pages per level | 10/20 |
| `--limit N` | crawl, map | Max total pages/URLs | 10/50 |
| `--instructions "text"` | crawl | Natural language instructions | none |
| `--select-paths p1,p2` | crawl | Include path patterns | none |
| `--exclude-paths p1,p2` | crawl | Exclude path patterns | none |

---

## Error Handling

- **Missing API key:** Clear error message with setup instructions.
- **401 Unauthorized:** Invalid API key.
- **429 Rate Limit:** Rate limit exceeded, try again later.
- **Network errors:** Descriptive error with cause.
- **No results:** Clean "No results found." message.
- **Timeout:** 30-second timeout on all HTTP requests.

---

## Credits & Pricing

| API | Basic | Advanced |
|---|---|---|
| Search | 1 credit | 2 credits |
| Extract | 1 credit/URL | 2 credits/URL |
| Crawl | 1 credit/page | 2 credits/page |
| Map | 1 credit | 1 credit |
| Research | Varies by model | - |

---

## Install

```bash
bash skills/tavily/install.sh
```
