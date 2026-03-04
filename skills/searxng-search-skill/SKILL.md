# SearXNG Advanced Search Skill

```markdown
---
name: searxng-skill
description: Advanced Python library for SearXNG metasearch with retry logic, timeout handling, and comprehensive search patterns.
homepage: https://github.com/yourusername/searxng-skill
metadata: {"clawdbot":{"emoji":"🔍","requires":{"python":">=3.8","packages":["requests","urllib3","python-dotenv"]},"install":[{"id":"pip","kind":"pip","package":"searxng-skill","label":"Install searxng-skill (pip)"},{"id":"local","kind":"local","command":"pip install -e .","label":"Install from source"}]}}
---

# searxng-skill

Use `searxng-skill` for privacy-focused metasearch with local/remote SearXNG instances. Supports retry logic, timeout handling, and advanced search patterns.

## Setup (once)

**Environment variables (recommended)**
```bash
# Create .env file
cat > .env << EOF
SEARXNG_URL=http://localhost:8080
SEARXNG_TIMEOUT=10
SEARXNG_MAX_RETRIES=3
SEARXNG_RETRY_DELAY=1.0
SEARXNG_BACKOFF_FACTOR=2.0
SEARXNG_VERIFY_SSL=true
SEARXNG_LANGUAGE=en
EOF
```

**Or configuration file**
```bash
# Create config.json
cat > config.json << EOF
{
  "instance_url": "http://localhost:8080",
  "default_timeout": 10,
  "max_retries": 3,
  "retry_delay": 1.0,
  "backoff_factor": 2.0,
  "verify_ssl": true,
  "default_language": "en"
}
EOF
```

**Initialize in code**
```python
from searxng_skill import SearXNGSkill, SearXNGConfig

# From environment
config = SearXNGConfig.from_env()
skill = SearXNGSkill(config=config)

# From file
config = SearXNGConfig.from_file("config.json")
skill = SearXNGSkill(config=config)

# Direct
skill = SearXNGSkill(instance_url="http://localhost:8080")
```

## Common Commands

**Basic search**
```python
from searxng_skill import SearXNGSkill

skill = SearXNGSkill(instance_url="http://localhost:8080")
results = skill.search("Python programming")

# Access results
for result in results["results"][:10]:
    print(f"{result['title']} - {result['url']}")
```

**Category search**
```python
from searxng_skill import SearchCategory

# Single category
results = skill.search("AI", categories=[SearchCategory.NEWS])

# Multiple categories
results = skill.search(
    "climate change",
    categories=[SearchCategory.NEWS, SearchCategory.SCIENCE]
)
```

**Time-filtered search**
```python
from searxng_skill import TimeRange

# Recent news (last 24 hours)
news = skill.news_search("AI breakthrough", time_range=TimeRange.DAY)

# Last week
results = skill.search("Python", time_range=TimeRange.WEEK)
```

**Image search**
```python
from searxng_skill import SafeSearch

images = skill.image_search(
    "nature photography",
    safesearch=SafeSearch.STRICT
)

for img in images[:10]:
    print(f"{img['title']}: {img.get('img_src', 'N/A')}")
```

**Video search**
```python
videos = skill.video_search("Python tutorial")

for video in videos[:5]:
    print(f"{video['title']} ({video.get('duration', 'N/A')})")
```

**Advanced search with operators**
```python
results = skill.advanced_search(
    query="machine learning",
    exact_phrase="deep learning",
    exclude_words=["tutorial", "beginner"],
    site="github.com",
    filetype="pdf"
)
```

**Engine-specific search**
```python
results = skill.search(
    "quantum computing",
    engines=["google", "duckduckgo", "wikipedia"]
)
```

**Structured search**
```python
response = skill.search_structured("artificial intelligence")

print(f"Query: {response.query}")
print(f"Total: {response.number_of_results}")

for result in response.results[:5]:
    print(f"{result.title} [{result.engine}]")
    print(f"  {result.url}")
    print(f"  Score: {result.score}\n")
```

**Autocomplete**
```python
suggestions = skill.autocomplete("artificial int")
# ['artificial intelligence', 'artificial intelligence news', ...]
```

**Multi-category search**
```python
categorized = skill.multi_category_search(
    "climate change",
    categories=[
        SearchCategory.GENERAL,
        SearchCategory.NEWS,
        SearchCategory.SCIENCE
    ]
)

for category, results in categorized.items():
    print(f"{category}: {len(results)} results")
```

**Parallel searches**
```python
queries = ["Python", "JavaScript", "Go", "Rust"]
results = skill.parallel_search(queries, categories=[SearchCategory.IT])

for query, result_data in results.items():
    print(f"{query}: {len(result_data.get('results', []))} results")
```

**Paginated search**
```python
# Get multiple pages
all_results = []
for page in range(1, 4):
    results = skill.search("AI", page=page)
    all_results.extend(results["results"])

print(f"Total results: {len(all_results)}")
```

**Health check**
```python
if skill.health_check():
    print("✓ SearXNG instance is healthy")
else:
    print("✗ Instance unavailable")
```

**Get engine info**
```python
engines = skill.get_engines_info()

for engine in engines[:10]:
    print(f"{engine.name} - {', '.join(engine.categories)}")
    print(f"  Enabled: {engine.enabled}")
```

**Export results**
```python
from searxng_skill.utils import export_results_json, export_results_csv

results = skill.search("machine learning")

# Export to JSON
export_results_json(results, "results.json")

# Export to CSV
export_results_csv(results["results"], "results.csv")
```

## Quick Reference

**Search Categories**
```python
SearchCategory.GENERAL      # General web search
SearchCategory.IMAGES       # Image search
SearchCategory.VIDEOS       # Video search
SearchCategory.NEWS         # News articles
SearchCategory.MAP          # Maps
SearchCategory.MUSIC        # Music
SearchCategory.IT           # IT/Tech
SearchCategory.SCIENCE      # Scientific papers
SearchCategory.FILES        # File search
SearchCategory.SOCIAL_MEDIA # Social media
```

**Time Ranges**
```python
TimeRange.DAY    # Last 24 hours
TimeRange.WEEK   # Last 7 days
TimeRange.MONTH  # Last 30 days
TimeRange.YEAR   # Last year
TimeRange.ALL    # All time
```

**Safe Search Levels**
```python
SafeSearch.NONE     # No filtering (0)
SafeSearch.MODERATE # Moderate filtering (1)
SafeSearch.STRICT   # Strict filtering (2)
```

## Notes

**Environment variable shortcuts**
- Set `SEARXNG_URL=http://localhost:8080` to avoid repeating instance URL
- Set `SEARXNG_LANGUAGE=en` for default language
- Set `SEARXNG_MAX_RETRIES=5` for custom retry behavior

**For scripting**
- Use `format=OutputFormat.JSON` for structured output (default)
- Set `verify_ssl=False` for local development only
- Implement rate limiting with `time.sleep()` between requests
- Use `health_check()` before batch operations

**Performance tips**
- Reuse `SearXNGSkill` instance for multiple searches
- Use `parallel_search()` for independent queries
- Cache results with `functools.lru_cache` for repeated queries
- Set appropriate timeouts: fast queries (5s), complex queries (30s)

**Retry behavior**
- Automatic retry with exponential backoff on timeout/connection errors
- Default: 3 retries, 1s initial delay, 2x backoff factor
- Customize: `max_retries`, `retry_delay`, `backoff_factor`
- No retry on HTTP 4xx/5xx errors

**Error handling**
```python
from searxng_skill.exceptions import TimeoutException, ConnectionException

try:
    results = skill.search("query", timeout=5)
except TimeoutException:
    print("Request timed out - try increasing timeout")
except ConnectionException:
    print("Cannot connect to instance - check URL and network")
```

**Fallback instance**
```python
try:
    skill = SearXNGSkill(instance_url="http://localhost:8080")
    results = skill.search("query")
except ConnectionException:
    # Fallback to public instance
    skill = SearXNGSkill(instance_url="https://searx.be")
    results = skill.search("query")
```

**Local instance setup**
```bash
# Docker
docker run -d -p 8080:8080 searxng/searxng

# Verify
curl http://localhost:8080/healthz
```

**Confirm before operations**
- Always validate query is not empty: `if query.strip(): ...`
- Check results exist: `if "results" in results: ...`
- Validate URLs before requests: `validate_url(url)`

## Advanced Usage

**Custom retry strategy**
```python
from searxng_skill.retry import RetryStrategy

strategy = RetryStrategy(
    max_retries=5,
    initial_delay=2.0,
    backoff_factor=1.5,
    max_delay=60.0,
    jitter=True
)

skill = SearXNGSkill(
    instance_url="http://localhost:8080",
    max_retries=5,
    retry_delay=2.0,
    backoff_factor=1.5
)
```

**Batch processing**
```python
import time

queries = ["Python", "Java", "Go", "Rust"]

for query in queries:
    results = skill.search(query)
    print(f"{query}: {len(results['results'])} results")
    time.sleep(1)  # Rate limiting
```

**Result deduplication**
```python
from searxng_skill.utils import deduplicate_results

results = skill.search("AI")
unique = deduplicate_results(results["results"], key="url")
```

**Merge multiple searches**
```python
from searxng_skill.utils import merge_search_results

r1 = skill.search("Python", engines=["google"])
r2 = skill.search("Python", engines=["duckduckgo"])

merged = merge_search_results([r1, r2])
```

**Logging**
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Searching for: Python")
results = skill.search("Python")
logger.info(f"Found {len(results['results'])} results")
```

## API Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `search()` | Basic search | `Dict[str, Any]` |
| `search_structured()` | Structured search | `SearchResponse` |
| `autocomplete()` | Get suggestions | `List[str]` |
| `image_search()` | Image-specific | `List[Dict]` |
| `news_search()` | News-specific | `List[Dict]` |
| `video_search()` | Video-specific | `List[Dict]` |
| `advanced_search()` | With operators | `Dict[str, Any]` |
| `multi_category_search()` | Multiple categories | `Dict[str, List]` |
| `parallel_search()` | Multiple queries | `Dict[str, Dict]` |
| `health_check()` | Instance status | `bool` |
| `get_engines_info()` | Engine details | `List[EngineInfo]` |

## Troubleshooting

**Connection refused**
```bash
# Check instance is running
curl http://localhost:8080/healthz

# Or in Python
if not skill.health_check():
    print("Instance is down")
```

**SSL errors (local development)**
```python
skill = SearXNGSkill(
    instance_url="http://localhost:8080",
    verify_ssl=False  # Only for local dev!
)
```

**Timeout issues**
```python
# Increase timeout
skill = SearXNGSkill(
    instance_url="http://localhost:8080",
    default_timeout=30
)

# Or per-request
results = skill.search("query", timeout=30)
```

**No results**
```python
# Check enabled engines
engines = skill.get_engines_info()
enabled = [e for e in engines if e.enabled]
print(f"Enabled: {len(enabled)} engines")

# Try specific engines
results = skill.search("query", engines=["duckduckgo"])
```
