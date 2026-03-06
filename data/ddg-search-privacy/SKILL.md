---
name: duckduckgo-search
version: 1.0.0
description: DuckDuckGo web search for private tracker-free searching. Use when user asks to search the web find information online or perform web-based research without tracking. Ideal for web search queries finding online information research without tracking quick fact verification and URL discovery.
---

# DuckDuckGo Web Search

Private web search using DuckDuckGo API for tracker-free information retrieval.

## Core Features

- Privacy-focused search (no tracking)
- Instant answer support
- Multiple search modes (web, images, videos, news)
- JSON output for easy parsing
- No API key required

## Quick Start

### Basic Web Search

```python
import requests

def search_duckduckgo(query, max_results=10):
    """
    Perform DuckDuckGo search and return results.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 10)

    Returns:
        List of search results with title, url, description
    """
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 0
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Extract results
    results = []

    # Abstract (instant answer)
    if data.get("Abstract"):
        results.append({
            "type": "instant_answer",
            "title": "Instant Answer",
            "content": data["Abstract"],
            "source": data.get("AbstractSource", "DuckDuckGo")
        })

    # Related topics
    if data.get("RelatedTopics"):
        for topic in data["RelatedTopics"][:max_results]:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append({
                    "type": "related",
                    "title": topic.get("FirstURL", "").split("/")[-1].replace("-", " ").title(),
                    "content": topic["Text"],
                    "url": topic.get("FirstURL", "")
                })

    return results[:max_results]
```

### Advanced Usage (HTML Scraping)

```python
from bs4 import BeautifulSoup
import requests

def search_with_results(query, max_results=10):
    """
    Perform DuckDuckGo search and scrape actual results.

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        List of search results with title, url, snippet
    """
    url = "https://duckduckgo.com/html/"
    params = {"q": query}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.post(url, data=params, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for result in soup.find_all("a", class_="result__a", href=True)[:max_results]:
        results.append({
            "title": result.get_text(),
            "url": result["href"],
            "snippet": result.find_parent("div", class_="result__body").get_text().strip()
        })

    return results
```

## Search Operators

DuckDuckGo supports standard search operators:

| Operator | Example | Description |
|----------|---------|-------------|
| `""` | `"exact phrase"` | Exact phrase match |
| `-` | `python -django` | Exclude terms |
| `site:` | `site:wikipedia.org history` | Search specific site |
| `filetype:` | `filetype:pdf report` | Specific file types |
| `intitle:` | `intitle:openclaw` | Words in title |
| `inurl:` | `inurl:docs/` | Words in URL |
| `OR` | `docker OR kubernetes` | Either term |

## Search Modes

### Web Search
Default mode, searches across the web.

```python
search_with_results("machine learning tutorial")
```

### Images Search
```python
def search_images(query, max_results=10):
    url = "https://duckduckgo.com/i.js"
    params = {
        "q": query,
        "o": "json",
        "vqd": "",  # Will be populated
        "f": ",,,",
        "p": "1"
    }

    response = requests.get(url, params=params)
    data = response.json()

    results = []
    for result in data.get("results", [])[:max_results]:
        results.append({
            "title": result.get("title", ""),
            "url": result.get("image", ""),
            "thumbnail": result.get("thumbnail", ""),
            "source": result.get("source", "")
        })

    return results
```

### News Search
Add `!news` to the query:

```python
search_duckduckgo("artificial intelligence !news")
```

## Best Practices

### Query Construction

**Good queries:**
- `"DuckDuckGo API documentation" 2024` (specific, recent)
- `site:github.com openclaw issues` (targeted)
- `python machine learning tutorial filetype:pdf` (resource-specific)

**Avoid:**
- Vague single words (`"search"`, `"find"`)
- Overly complex operators that might confuse results
- Questions with multiple unrelated topics

### Privacy Considerations

DuckDuckGo advantages:
- ✅ No personal tracking
- ✅ No search history stored
- ✅ No user profiling
- ✅ No forced personalized results

### Performance Tips

1. **Use HTML scraping for actual results** - The JSON API provides instant answers but limited result lists
2. **Add appropriate delays** - Respect rate limits when making multiple queries
3. **Cache results** - Store common searches to avoid repeated API calls

## Error Handling

```python
def search_safely(query, retries=3):
    for attempt in range(retries):
        try:
            results = search_with_results(query)
            if results:
                return results
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff

    return []
```

## Output Formatting

### Markdown Format
```python
def format_results_markdown(results, query):
    output = f"# Search Results for: {query}\n\n"

    for i, result in enumerate(results, 1):
        output += f"## {i}. {result.get('title', 'Untitled')}\n\n"
        output += f"**URL:** {result.get('url', 'N/A')}\n\n"
        output += f"{result.get('snippet', result.get('content', 'N/A'))}\n\n"
        output += "---\n\n"

    return output
```

### JSON Format
```python
import json

def format_results_json(results, query):
    return json.dumps({
        "query": query,
        "count": len(results),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }, indent=2)
```

## Common Patterns

### Find Documentation
```python
search_duckduckgo(f'{library_name} documentation filetype:md')
```

### Recent Information
```python
search_duckduckgo(f'{topic} 2024 news')
```

### Troubleshooting
```python
search_duckduckgo(f'{error_message} {tool_name} stackoverflow')
```

### Technical Comparison
```python
search_duckduckgo('postgresql vs mysql performance 2024')
```

## Integration Example

```python
class DuckDuckGoSearcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def search(self, query, mode="web", max_results=10):
        """
        Unified search interface.

        Args:
            query: Search query
            mode: 'web', 'images', 'news'
            max_results: Maximum results

        Returns:
            Formatted results as list
        """
        if mode == "images":
            return self._search_images(query, max_results)
        elif mode == "news":
            return self._search_web(f"{query} !news", max_results)
        else:
            return self._search_web(query, max_results)

    def _search_web(self, query, max_results):
        # Implementation
        pass

    def _search_images(self, query, max_results):
        # Implementation
        pass
```

## Resources

### Official Documentation
- DuckDuckGo API Wiki: https://duckduckgo.com/api
- Instant Answer API: https://duckduckgo.com/params
- Search Syntax: https://help.duckduckgo.com/duckduckgo-help-pages/results/syntax/

### References
- HTML scraping patterns for result extraction
- Rate limiting best practices
- Result parsing and filtering
