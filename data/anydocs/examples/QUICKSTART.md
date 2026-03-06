# anydocs Quick Start Examples

## Example 1: Discord Developer Docs

### Configure

```bash
python3 anydocs.py config discord \
  https://discord.com/developers/docs \
  https://discord.com/developers/docs/sitemap.xml
```

Output:
```
✓ Profile 'discord' configured successfully
  Base URL: https://discord.com/developers/docs
  Sitemap: https://discord.com/developers/docs/sitemap.xml
  Search method: hybrid
```

### Index (First Time)

```bash
python3 anydocs.py index discord
```

This will:
1. Fetch the sitemap
2. Discover all documentation pages
3. Scrape each page
4. Build a searchable index
5. Cache everything for fast subsequent searches

Expected output:
```
Indexing 'discord'...
Discovering URLs [####] 100%
Found 150 pages to scrape
Scraping pages [####] 100%
Building index [####] 100%

✓ Indexed 150 pages for 'discord'
```

### Search

```bash
# Simple search
python3 anydocs.py search "webhooks" --profile discord

# Search with limit
python3 anydocs.py search "rate limits" --profile discord --limit 5

# Regex search
python3 anydocs.py search "^(GET|POST)" --profile discord --regex
```

Output example:
```
Results for: webhooks (3 found)

[1] Webhook Resource
    URL: https://discord.com/developers/docs/resources/webhook
    Relevance: 45.2
    Tags: resources, webhooks, api
    Webhook represents a method for sending messages...

[2] Executing Webhooks
    URL: https://discord.com/developers/docs/resources/webhook#execute-webhook
    Relevance: 42.1
    Tags: webhooks, execute, api
    The POST method of this endpoint...
```

### Fetch Specific Page

```bash
python3 anydocs.py fetch "resources/webhook" --profile discord
```

Or by full URL:
```bash
python3 anydocs.py fetch "https://discord.com/developers/docs/resources/webhook"
```

## Example 2: Internal Company Docs

### Configure Custom Docs Site

```bash
python3 anydocs.py config company \
  https://docs.mycompany.local/api \
  https://docs.mycompany.local/api/sitemap.xml \
  --search-method keyword \
  --ttl-days 1
```

The `--ttl-days 1` option means the cache will refresh daily (useful for docs that change frequently).

### Index

```bash
python3 anydocs.py index company
```

### Search

```bash
python3 anydocs.py search "deployment" --profile company
python3 anydocs.py search "how to set up" --profile company
```

### Force Re-index

If your company docs updated:
```bash
python3 anydocs.py index company --force
```

## Example 3: Using in Python Code

### Simple Search

```python
#!/usr/bin/env python3
from lib.config import ConfigManager
from lib.cache import CacheManager
from lib.indexer import SearchIndex

# Load profile
config_mgr = ConfigManager()
config = config_mgr.get_profile("discord")

# Load cached index
cache_mgr = CacheManager()
index_data = cache_mgr.get_index("discord")

if index_data:
    index = SearchIndex.from_dict(index_data)
    results = index.search("webhooks", limit=5)
    
    for result in results:
        print(f"[{result['rank']}] {result['title']}")
        print(f"    Score: {result['relevance_score']}")
        print(f"    URL: {result['url']}")
else:
    print("Index not found. Run: anydocs index discord")
```

### Building a Custom Index

```python
from lib.scraper import DiscoveryEngine
from lib.indexer import SearchIndex
from lib.cache import CacheManager

# Scrape documentation
scraper = DiscoveryEngine(
    base_url="https://discord.com/developers/docs",
    sitemap_url="https://discord.com/developers/docs/sitemap.xml"
)

pages = scraper.fetch_all()
print(f"Scraped {len(pages)} pages")

# Build index
index = SearchIndex()
index.build(pages)

# Cache for next time
cache = CacheManager()
cache.save_index("discord", index.to_dict())

# Search
results = index.search("rate limits", limit=10)
for r in results:
    print(f"{r['title']} - {r['relevance_score']}")
```

## Example 4: Cache Management

### Check Cache Status

```bash
python3 anydocs.py cache status
```

Output:
```
Cache status:
  Location: /home/user/.anydocs/cache
  Pages cached: 150
  Indexes cached: 1
  Total size: 45.2 MB
```

### Clear Cache

Clear all:
```bash
python3 anydocs.py cache clear
```

Clear specific profile:
```bash
python3 anydocs.py cache clear --profile discord
```

## Example 5: Multiple Profiles

Configure multiple docs sites and search across them:

```bash
# Configure multiple profiles
python3 anydocs.py config discord https://discord.com/developers/docs https://discord.com/developers/docs/sitemap.xml
python3 anydocs.py config stripe https://stripe.com/docs https://stripe.com/docs/sitemap.xml
python3 anydocs.py config aws https://docs.aws.amazon.com https://docs.aws.amazon.com/sitemap.xml

# List all profiles
python3 anydocs.py list-profiles

# Index each
python3 anydocs.py index discord
python3 anydocs.py index stripe
python3 anydocs.py index aws

# Search each
python3 anydocs.py search "webhooks" --profile discord
python3 anydocs.py search "payment" --profile stripe
python3 anydocs.py search "lambda" --profile aws
```

## Tips & Tricks

### 1. First Index Takes Time
The first index build scrapes all pages and can take 5-15 minutes depending on site size. Subsequent searches are instant (cached).

### 2. Use Rate Limiting Wisely
The tool uses 0.5s delay between requests to respect server load. Increase for more respectful crawling:

```python
scraper = DiscoveryEngine(
    base_url="https://example.com",
    sitemap_url="https://example.com/sitemap.xml",
    rate_limit=2.0  # 2 seconds between requests
)
```

### 3. Search Method Comparison

- **keyword** - Fastest, best for single terms
- **hybrid** - Default, balances speed and relevance
- **regex** - Slower but powerful for patterns

### 4. Batch Operations in Code

```python
from lib.config import ConfigManager
from lib.indexer import SearchIndex
from lib.cache import CacheManager

profiles = ["discord", "stripe", "aws"]
cache = CacheManager()

for profile in profiles:
    index_data = cache.get_index(profile)
    if index_data:
        index = SearchIndex.from_dict(index_data)
        # Do something with index
```

## Troubleshooting

### "Profile not found"
```bash
python3 anydocs.py list-profiles  # Check available profiles
```

### "No index for profile"
```bash
python3 anydocs.py index <profile>  # Build the index
```

### Indexing is slow
This is normal! The tool rate-limits to respect server load. You can:
- Increase rate_limit in code: `rate_limit=2.0`
- Use `--force` flag to skip cache checks
- Run during off-peak hours

### Search returns no results
- Try with `--limit 20` to get more results
- Try simpler search terms
- Check if index exists: `anydocs list-profiles`

### Cache is too large
```bash
python3 anydocs.py cache clear  # Clear all
python3 anydocs.py config <profile> ... --ttl-days 1  # Shorter TTL
```

## Next Steps

- Read `README.md` for full documentation
- Check `SKILL.md` for detailed feature overview
- Run `python3 anydocs.py --help` for command reference
- Run `python3 test_anydocs.py` to verify installation

Enjoy!
