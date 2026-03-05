# DDGS Web Search Skill
This skill implements web search functionality via the DDGS (Dux Distributed Global Search) engine, aggregating results from diverse search services to fetch real-time information.

## Features
🔍 Privacy-friendly metasearch  
📰 News search support  
🖼️ Image search support  
📹 Video search support  
📚 Books search support  
🌐 Free to use, no API Key required  
🔒 Privacy protection, no user tracking  
⚡ MCP (Model Context Protocol) and API server support  

## Installation
```bash
# Install via uv (Recommended)
uv pip install ddgs

# Or install via pip
pip install ddgs
```

## Quick Start

### 1. Text Search
The most commonly used search method, returning webpage results:
```python
python -c "
from ddgs import DDGS

query = 'your search query'

results = DDGS().text(
    query,
    region='wt-wt',        # Region: cn-zh (China), us-en (US), wt-wt (Global)
    safesearch='moderate', # Safe search: on, moderate, off
    timelimit='m',         # Time range: d (day), w (week), m (month), y (year), None (unlimited)
    max_results=10,        # Maximum number of results
    backend='auto'         # Backends: auto, duckduckgo, brave, bing, etc.
)

for i, r in enumerate(results, 1):
    print(f\"{i}. {r.get('title')}\")
    print(f\"   URL: {r.get('href')}\")
    print(f\"   Snippet: {str(r.get('body'))[:100]}...\n\")
"
```

### 2. News Search
Search for the latest news:
```python
python -c "
from ddgs import DDGS

results = DDGS().news(
    'AI technology',
    region='wt-wt',
    safesearch='moderate',
    timelimit='d',       # d=past 24 hours, w=past week, m=past month
    max_results=10
)

for r in results:
    print(f\"📰 {r.get('title')}\")
    print(f\"   Source: {r.get('source')}\")
    print(f\"   Date: {r.get('date')}\")
    print(f\"   Link: {r.get('url')}\n\")
"
```

### 3. Image Search
Search for image resources:
```python
python -c "
from ddgs import DDGS

results = DDGS().images(
    'cute cats',
    region='wt-wt',
    safesearch='moderate',
    size='Medium',       # Small, Medium, Large, Wallpaper
    type_image='photo',  # photo, clipart, gif, transparent, line
    layout='Square',     # Square, Tall, Wide
    max_results=10
)

for r in results:
    print(f\"🖼️ {r.get('title')}\")
    print(f\"   Image: {r.get('image')}\")
    print(f\"   Thumbnail: {r.get('thumbnail')}\")
    print(f\"   Source: {r.get('source')}\n\")
"
```

### 4. Video Search
Search for video content:
```python
python -c "
from ddgs import DDGS

results = DDGS().videos(
    'Python programming',
    region='wt-wt',
    safesearch='moderate',
    timelimit='w',       # d, w, m
    resolution='high',   # high, standard
    duration='medium',   # short, medium, long
    max_results=10
)

for r in results:
    print(f\"📹 {r.get('title')}\")
    print(f\"   Duration: {r.get('duration', 'N/A')}\")
    print(f\"   Publisher: {r.get('publisher')}\")
    print(f\"   Link: {r.get('content')}\n\")
"
```

### 5. Books Search
Search for books:
```python
python -c "
from ddgs import DDGS

results = DDGS().books(
    'sea wolf jack london',
    max_results=5
)

for r in results:
    print(f\"📚 {r.get('title')}\")
    print(f\"   Author: {r.get('author')}\")
    print(f\"   Publisher: {r.get('publisher')}\")
    print(f\"   Link: {r.get('link')}\n\")
"
```

## Practical Scripts

### Reusable Search Function
```python
python -c "
from ddgs import DDGS

def web_search(query, search_type='text', max_results=5, region='wt-wt', timelimit=None):
    '''
    Execute DDGS search
    
    Args:
        query: Search keyword
        search_type: text, news, images, videos, books
        max_results: Maximum results
        region: Region (cn-zh, us-en, wt-wt)
        timelimit: Time limit (d, w, m, y)
    '''
    ddgs = DDGS()
    if search_type == 'text':
        return list(ddgs.text(query, region=region, timelimit=timelimit, max_results=max_results))
    elif search_type == 'news':
        return list(ddgs.news(query, region=region, timelimit=timelimit, max_results=max_results))
    elif search_type == 'images':
        return list(ddgs.images(query, region=region, max_results=max_results))
    elif search_type == 'videos':
        return list(ddgs.videos(query, region=region, timelimit=timelimit, max_results=max_results))
    elif search_type == 'books':
        return list(ddgs.books(query, max_results=max_results))
    return []

results = web_search('Python 3.12 new features', max_results=5)
print(f'📊 Found {len(results)} results')
"
```

## Parameters Explained

### Region Codes (region)
| Code | Region |
|---|---|
| cn-zh | China |
| us-en | United States |
| uk-en | United Kingdom |
| jp-jp | Japan |
| kr-kr | South Korea |
| wt-wt | Global (No region limit) |

### Time Limit (timelimit)
| Value | Meaning |
|---|---|
| d | Past 24 hours |
| w | Past week |
| m | Past month |
| y | Past year |
| None | No limit |

### Safe Search (safesearch)
| Value | Meaning |
|---|---|
| on | Strict filtering |
| moderate | Moderate filtering (Default) |
| off | Filtering disabled |

## Error Handling & Proxies

### Basic Error Handling
```python
python -c "
from ddgs import DDGS
from ddgs.exceptions import DDGSException

try:
    results = DDGS().text('test query', max_results=5)
    print(f'✅ Search successful, found {len(results)} results')
except DDGSException as e:
    print(f'❌ Search error: {e}')
except Exception as e:
    print(f'❌ Unknown error: {e}')
"
```

### Using Proxies
```python
python -c "
from ddgs import DDGS

# Set proxy (supports http/https/socks5)
proxy = 'http://127.0.0.1:7890'  

results = DDGS(proxy=proxy).text('test query', max_results=5)
print(f'Successfully searched via proxy, found {len(results)} results')
"
```

## FAQ

**Installation Failed?**
```bash
pip install --upgrade pip
pip install ddgs
```

**No Results Found?**
- Check your network connection.
- Try using a proxy.
- Simplify your search query.
- Verify that your region settings are correct.

**Rate Limited?**
- Add a delay between multiple requests (e.g., `import time; time.sleep(1)`).
- Reduce the `max_results` per request.

## Integration & Notes

### Integration Example
```python
# 1. Search with DDGS
python -c "
from ddgs import DDGS
results = DDGS().text('Python async tutorial', max_results=1)
if results:
    print(f\"URL: {results[0].get('href')}\")
"

# 2. Open result with your browser-use tool
browser-use open <url_from_search>
```

**⚠️ Best Practices:**
- **Respect Rate Limits:** Avoid sending a massive volume of requests in a short period.
- **Optimize Results:** Do not request more results than necessary in a single query.
- **Add Delays:** Use `time.sleep()` when executing batch searches.
- **Handle Exceptions:** Always wrap your API calls in `try/except` blocks.
- **Copyright Awareness:** Search results are for reference only; respect the copyright of the indexed content.