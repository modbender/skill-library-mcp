---
name: unified-web-search
description: Pick the best source (Tavily, Web Search Plus, Browser, or local files) for a query, run the search, and return ranked results with provenance.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔍",
        "requires": { "bins": ["node"], "env": ["TAVILY_API_KEY"] },
        "version": "1.1.0",
      },
  }
---

# Unified Web Search Skill

Intelligently select the best search source, aggregate results, and return ranked answers with provenance.

## Security

All search queries are validated and sanitized:
- Maximum query length: 500 characters
- Shell metacharacters are blocked to prevent command injection
- Local file searches are restricted to workspace directories only

## Tool API

### unified_web_search
Perform a unified search across multiple sources.

- **Parameters:**
  - `query` (string, required): The search query (alphanumeric, spaces, basic punctuation only)
  - `sources` (array of strings, optional): Array of sources to search. Defaults to `['tavily', 'web-search-plus', 'local']`. Options: `tavily`, `web-search-plus`, `browser`, `local`.
  - `max_results` (integer, optional): Maximum number of results to return. Defaults to `5`.

**Usage:**

```bash
# Search all sources
node skills/unified-web-search/index.js --query "my search term" --max_results 10

# Search specific sources
node skills/unified-web-search/index.js --query "AI developments" --sources '["tavily", "local"]' --max_results 10

# Search local files only
node skills/unified-web-search/index.js --query "meeting notes" --sources '["local"]'
```

## Implementation

The skill aggregates results from multiple sources:

- **Tavily:** AI-optimized web search with relevance scoring (requires `TAVILY_API_KEY`)
- **Web Search Plus:** Broader web search coverage (placeholder for future integration)
- **Browser:** Targeted site scraping (placeholder for future integration)
- **Local Files:** Searches workspace directories for matching filenames

Results are scored and ranked by relevance, then returned with source attribution in JSON format.

## Output Format

```json
[
  {
    "source": "tavily",
    "title": "Article Title",
    "url": "https://example.com/article",
    "score": 0.95,
    "content": "Brief excerpt from the article..."
  },
  {
    "source": "local",
    "title": "/path/to/file.txt",
    "snippet": "Found query in filename: file.txt",
    "score": 0.5
  }
]
```

## Environment Variables

- `TAVILY_API_KEY`: Required for Tavily search functionality. Get your key at https://app.tavily.com

## Error Handling

- Returns error if query is missing or empty
- Returns error if query contains disallowed characters
- Gracefully handles API failures (continues with other sources)
- Warns if TAVILY_API_KEY is not set

## Example

```bash
$ node skills/unified-web-search/index.js --query "climate change" --max_results 3
[
  {
    "source": "tavily",
    "title": "IPCC Climate Report 2024",
    "url": "https://ipcc.ch/report",
    "score": 0.92,
    "content": "The latest IPCC report shows..."
  },
  {
    "source": "tavily",
    "title": "Climate Action Tracker",
    "url": "https://climateactiontracker.org",
    "score": 0.87,
    "content": "Tracking government climate commitments..."
  },
  {
    "source": "local",
    "title": "/home/user/.openclaw/workspace/memory/climate-notes.md",
    "snippet": "Found query in filename: climate-notes.md",
    "score": 0.5
  }
]
```
