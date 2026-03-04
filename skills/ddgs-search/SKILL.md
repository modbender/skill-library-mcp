---
name: ddgs-search
description: Free multi-engine web search via ddgs CLI (DuckDuckGo, Google, Bing, Brave, Yandex, Yahoo, Wikipedia) + arXiv API search. No API keys required. Use when user needs web search, research paper discovery, or when other skills need a search backend. Drop-in replacement for web-search-plus.
metadata: {"openclaw":{"requires":{"bins":["python3"]}}}
---

# ddgs-search

## Why This Skill?

🆓 **Completely free** — no API keys, no subscriptions, no rate limits, no billing surprises.

🔍 **8 search engines in one** — Google, Bing, DuckDuckGo, Brave, Yandex, Yahoo, Wikipedia, and Mojeek. Switch engines with a single flag. Most search skills only support one.

🎓 **Built-in arXiv research search** — search academic papers directly via arXiv's free API. Returns authors, categories, abstracts, and publication dates. Perfect for researchers, students, and AI/ML practitioners.

🔌 **Drop-in replacement** — outputs web-search-plus compatible JSON, so it works with any skill or tool that expects that format. Zero config migration.

⚡ **Lightweight** — single pip package, no browser automation, no headless Chrome. Searches complete in 1-3 seconds.

## Install

```bash
python3 scripts/install.py
```

Works on **macOS, Linux, and Windows**. Installs the `ddgs` package, verifies CLI access, and runs a quick search test.

### Manual install
```bash
pip install ddgs
```

## Web Search

### CLI wrapper (recommended)

The `ddgs-search` wrapper outputs clean JSON to stdout with no interactive prompts or abort issues:

```bash
# Google (default)
ddgs-search "your query" 5 google

# Other engines
ddgs-search "your query" 3 duckduckgo
ddgs-search "your query" 5 brave
ddgs-search "your query" 10 yandex
```

### Python script (web-search-plus compatible JSON)

```bash
# Google (default)
python3 scripts/search.py -q "your query" -m 5

# Other engines
python3 scripts/search.py -q "your query" -b duckduckgo
python3 scripts/search.py -q "your query" -b brave
python3 scripts/search.py -q "your query" -b yandex
python3 scripts/search.py -q "your query" -b yahoo
python3 scripts/search.py -q "your query" -b wikipedia
```

Output (web-search-plus compatible JSON):
```json
{
  "provider": "ddgs",
  "results": [
    {"title": "...", "url": "...", "snippet": "...", "published_date": "..."}
  ]
}
```

## arXiv Search

```bash
# Search by topic
python3 scripts/arxiv_search.py -q "3D gaussian splatting" -m 10

# Field-specific search (title, abstract, category)
python3 scripts/arxiv_search.py -q "ti:transformer AND cat:cs.CV" -m 5

# Sort by relevance instead of date
python3 scripts/arxiv_search.py -q "reinforcement learning" --sort-by relevance
```

Returns authors, categories, abstracts — same JSON format.

## Direct CLI

> ⚠️ The raw `ddgs text` CLI has a pagination bug (`input()` call → `Aborted!` + exit code 1 in non-TTY contexts). Use `ddgs-search` wrapper or `-o file.json` instead.

```bash
ddgs text -q "query" -m 5 -b google -o /tmp/results.json
```

## Integration

Set `WEB_SEARCH_PLUS_PATH` to use as a search backend for other skills:
```bash
export WEB_SEARCH_PLUS_PATH="path/to/ddgs-search/scripts/search.py"
```
