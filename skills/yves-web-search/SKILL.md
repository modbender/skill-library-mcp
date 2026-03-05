---
name: web-search
description: Search the web and fetch web pages. Use when user wants to look up information, find answers, or search for anything online. Supports multiple free methods: Jina AI reader, DuckDuckGo Lite, and Python ddgs fallback. No API keys required for basic use.
metadata:
  {
    "openclaw": {
      "emoji": "🔍",
      "homepage": "https://github.com/openclaw/openclaw",
      "requires": {}
    }
  }
---

# Web Search Skill

Comprehensive web search and content extraction — free, no API keys required.

## Quick Start

**Just want to search?** Use DuckDuckGo Lite:
```
web_fetch url="https://lite.duckduckgo.com/lite/?q=YOUR+QUERY"
```

**Want full page content?** Use Jina Reader:
```
web_fetch url="https://r.jina.ai/http://TARGET_URL"
```

---

## Method 1: Jina AI Reader (Free - Recommended for Content)

Extract full page content using Jina's free reader API.

### Read a URL
```
web_fetch url="https://r.jina.ai/http://example.com"
```

### Search the Web
```
web_fetch url="https://r.jina.ai/http://duckduckgo.com/?q=YOUR+QUERY"
```

**Examples:**
| Task | Command |
|------|---------|
| Get Next.js docs | `web_fetch url="https://r.jina.ai/http://nextjs.org"` |
| Get React docs | `web_fetch url="https://r.jina.ai/http://react.dev"` |
| Get Python docs | `web_fetch url="https://r.jina.ai/http://docs.python.org"` |

### Advanced Jina Reader (with API Key)

For advanced features, get a free API key from [jina.ai/reader](https://jina.ai/reader):

```bash
export JINA_API_KEY="jina_..."
```

Then use the bundled script:
```
{baseDir}/scripts/reader.sh "https://example.com"
{baseDir}/scripts/reader.sh --mode search "AI news 2025"
{baseDir}/scripts/reader.sh --mode ground "OpenAI founded 2015"
```

Options: `--mode`, `--selector`, `--remove`, `--format`, `--json`

---

## Method 2: DuckDuckGo Lite (Free - Recommended for Search)

Search without any API key using DuckDuckGo Lite.

### Basic Search
```
web_fetch url="https://lite.duckduckgo.com/lite/?q=YOUR+QUERY"
```

### Regional Search
```
web_fetch url="https://lite.duckduckgo.com/lite/?q=QUERY&kl=us-en"
```

Regions: `au-en`, `us-en`, `uk-en`, `de-de`, `fr-fr`

### Search Tips
- Use `+` for spaces: `python+tutorial`
- Use quotes for exact phrases: `%22exact+phrase%22`
- Skip first 1-2 results (ads)

---

## Method 3: Python ddgs (Fallback)

If web_fetch is blocked, use Python's `ddgs` package:

```bash
pip install ddgs
```

```python
from ddgs import DDGS
ddgs = DDGS()
results = ddgs.text("search query", max_results=5)
for r in results:
    print(f"{r['title']}: {r['url']}")
```

---

## Workflow: Search then Fetch

1. **Search** → DDG Lite to find relevant URLs
2. **Pick** → Identify best result(s)
3. **Fetch** → Jina Reader to extract full content

Example:
```
# Step 1: Find info about Next.js auth
web_fetch url="https://lite.duckduckgo.com/lite/?q=nextjs+authentication+docs"

# Step 2: Fetch the official docs
web_fetch url="https://r.jina.ai/http://nextjs.org/docs/app/..."
```

---

## Quick Reference

| Need | Method | Command |
|------|--------|---------|
| Find URLs | DDG Lite | `?q=search+terms` |
| Get page content | Jina Reader | `r.jina.ai/http://URL` |
| Advanced extraction | Jina API | `--mode search --json` |
| Python fallback | ddgs | `ddgs.text()` |
| Browser (if available) | Headless | `browser action=navigate` |

---

## Limitations

- Google search blocked (captcha)
- No date filtering via DDG Lite
- Jina free tier has rate limits
