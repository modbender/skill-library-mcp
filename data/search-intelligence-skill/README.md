# 🔍 search-intelligence-skill

Advanced AI-powered search skill using SearXNG as the universal search backend.

**Zero API keys. Full privacy. 90+ engines. Intelligent dork generation.**

Give any AI agent the ability to search the entire internet like an expert
OSINT analyst, SEO engineer, and security researcher combined.

## Features

| Feature | Description |
|---|---|
| **Intent Parsing** | NLP-based classification into 14 intent categories (security, OSINT, SEO, academic, code, etc.) |
| **Dork Generation** | 100+ dork templates with automatic entity extraction and template filling |
| **90+ Engines** | Routes queries to the optimal SearXNG engines per intent |
| **Multi-Step Strategies** | 8 strategy types: broad-to-narrow, OSINT chain, deep dive, temporal, file hunt, etc. |
| **Cross-Engine Translation** | Translates operators between Google, Bing, Yandex, DuckDuckGo, Brave |
| **Result Analysis** | Multi-signal relevance scoring, deduplication, credibility assessment |
| **Auto-Refinement** | Detects poor results and automatically generates improved queries |
| **LLM-Ready Output** | `.to_context()` formats results for AI agent consumption |

## Quick Start

```bash
pip install -e .
```

```python
from search_intelligence_skill import SearchSkill

skill = SearchSkill(searxng_url="http://localhost:8888")

# Natural language → intelligent multi-engine search
report = skill.search("find exposed admin panels on example.com", depth="deep")
print(report.to_context())

# Top results as structured data
for r in report.top(5):
    print(f"[{r.relevance:.1f}] {r.title} — {r.url}")
```

## Search Depths

| Depth | Queries | Strategy | Use Case |
|---|---|---|---|
| `quick` | 1-2 | Single-step | Fast lookups |
| `standard` | 3-6 | Broad-to-narrow | General searching |
| `deep` | 6-12 | Multi-angle / Deep dive | Research, security audits |
| `exhaustive` | 12+ | OSINT chain / Full sweep | Complete investigations |

## Intent Categories

The skill automatically detects:

- **security** — vulnerability scanning, exposed files, admin panels
- **seo** — indexation, backlinks, competitors, technical SEO
- **osint** — people, emails, usernames, domains, companies, IPs
- **academic** — papers, datasets, authors
- **code** — repositories, packages, documentation, bugs
- **files** — documents, data files, media, archives
- **news** — breaking news, analysis, trends
- **images / videos / social / shopping / legal / medical**

## AI Agent Integration

```python
# In your agent's tool/skill handler:
from search_intelligence_skill import SearchSkill

skill = SearchSkill(searxng_url="http://your-searxng:8888")

def handle_search(user_query: str) -> str:
    report = skill.search(user_query, depth="standard")
    return report.to_context()  # Formatted for LLM context
```

## API Reference

### `SearchSkill`

| Method | Description |
|---|---|
| `.search(query, depth, ...)` | Full intelligent search pipeline |
| `.search_dork(dork_query, ...)` | Execute a raw dork directly |
| `.suggest_queries(query)` | Preview generated dorks without executing |
| `.build_dork(keyword, domain, ...)` | Build a custom dork from parameters |
| `.execute_strategy(name, target)` | Run a named strategy |
| `.search_batch(queries)` | Batch multiple searches |
| `.health_check()` | Check SearXNG connectivity |

### `SearchReport`

| Property | Type | Description |
|---|---|---|
| `.results` | `list[SearchResult]` | Scored, deduplicated results |
| `.top(n)` | `list[SearchResult]` | Top N results by relevance |
| `.to_context()` | `str` | LLM-formatted output |
| `.intent` | `SearchIntent` | Parsed intent details |
| `.strategy` | `SearchStrategy` | Strategy that was used |
| `.suggestions` | `list[str]` | Refinement suggestions |
| `.engines_used` | `list[str]` | Which engines returned results |
| `.timing_seconds` | `float` | Total execution time |

## Requirements

- Python 3.9+
- `httpx` (only external dependency)
- A running SearXNG instance

## License

MIT
