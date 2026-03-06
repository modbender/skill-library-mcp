# anydocs - Documentation Indexing & Search

A powerful CLI tool and Python library for indexing and searching **any** documentation website, including single-page applications (SPAs).

## Features

✅ **Work with Any Docs Site** - Vue.js, Next.js, internal docs, etc.
✅ **JavaScript Rendering** - Optional Playwright + OpenClaw gateway integration for SPA docs
✅ **Multiple Search Methods** - Keyword, hybrid, and regex search
✅ **Smart Caching** - Pages and indexes cached locally with configurable TTL
✅ **Profile Management** - Support multiple doc sites simultaneously
✅ **Fast Search** - Instant results from cached indexes
✅ **Python API** - Importable for agents and scripts
✅ **Rich CLI** - Beautiful command-line interface with progress bars

## Installation

### Recommended: Virtual Environment (Safe, Isolated)

```bash
cd /path/to/skills/anydocs

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
chmod +x anydocs.py
```

Then always activate before using:
```bash
source venv/bin/activate
anydocs search "query" --profile vuejs
```

### Alternative: System-Wide Installation (Requires Caution)

```bash
cd /path/to/skills/anydocs
bash setup.sh --system-packages  # Will prompt for confirmation
```

This uses `pip install --break-system-packages`, which can conflict with your system package manager. Only use if you understand the risks.

### Add to PATH (Optional)

With venv active:
```bash
export PATH="/path/to/skills/anydocs:$PATH"

# Or create a symlink (requires the venv to be active)
sudo ln -s /path/to/skills/anydocs/anydocs.py /usr/local/bin/anydocs
```

## Quick Start

### 1. Configure Your First Documentation Site

Let's use Vue.js documentation as an example (this is a single-page app that successfully indexes):

```bash
python anydocs.py config vuejs \
  https://vuejs.org \
  https://vuejs.org/sitemap.xml
```

You'll see:
```
✓ Profile 'vuejs' configured successfully
  Base URL: https://vuejs.org
  Sitemap: https://vuejs.org/sitemap.xml
  Search method: hybrid
```

### 2. Build the Index

```bash
python anydocs.py index vuejs
```

This will:
- Discover all documentation pages via sitemap
- Scrape each page's content
- Cache pages locally
- Build a searchable index

Progress:
```
Discovering URLs
Found 110 pages to scrape
Scraping pages [████████████████████████] 100%
Building index [████████████████████████] 100%

✓ Indexed 110 pages for 'vuejs'
```

### 3. Search!

```bash
# Simple search
python anydocs.py search "reactive state management" --profile vuejs

# Limit results
python anydocs.py search "composables" --profile vuejs --limit 5

# Advanced regex
python anydocs.py search "^(ref|computed|watch)" --profile vuejs --regex
```

Results look like:
```
Results for: reactive state management (5 found)

[1] State Management | Vue.js
    URL: https://vuejs.org/guide/scaling-up/state-management.html
    Relevance: 35
    Tags: guide, scaling-up, state-management
    State Management - Technically, every Vue component instance already "manages" its own reactive state...

[2] Options: State | Vue.js
    URL: https://vuejs.org/api/options-state.html
    Relevance: 19
    Tags: api, options-state
    Options: State - A function that returns the initial reactive state for the component instance...
```

## Command Reference

### Configuration

```bash
# Add a profile
anydocs config <profile> <base_url> <sitemap_url> [options]

# Options
--search-method {keyword,semantic,hybrid}  # Default: hybrid
--ttl-days N                                # Cache TTL in days (default: 7)

# Examples
anydocs config vuejs https://vuejs.org https://vuejs.org/sitemap.xml
anydocs config nextjs https://nextjs.org https://nextjs.org/sitemap.xml
anydocs config myproject https://docs.internal.com https://docs.internal.com/sitemap.xml --search-method keyword
```

### List Profiles

```bash
anydocs list-profiles
```

Shows all configured profiles with details.

### Indexing

```bash
# Build index (uses cache if available)
anydocs index <profile>

# Force rebuild (skip cache)
anydocs index <profile> --force

# With browser rendering (for SPAs)
anydocs index <profile> --use-browser --gateway-token YOUR_TOKEN

# Examples
anydocs index vuejs
anydocs index nextjs --force
anydocs index vuejs --use-browser --gateway-token abc123def456
```

### Search

```bash
# Basic search
anydocs search "<query>" --profile <profile>

# Options
--limit N                   # Max results (default: 10)
--regex                     # Treat query as regex pattern
--profile PROFILE           # Profile to search (default: vuejs)

# Examples
anydocs search "state management"                           # Uses default profile
anydocs search "composition api" --profile vuejs --limit 5
anydocs search "^(setup|provide)" --profile vuejs --regex
anydocs search "installation" --profile nextjs
```

### Fetch Specific Page

```bash
# Fetch by URL
anydocs fetch "<url>"

# Fetch by path (relative to base_url)
anydocs fetch "<path>" --profile <profile>

# Examples
anydocs fetch "https://vuejs.org/guide/introduction.html"
anydocs fetch "guide/introduction" --profile vuejs
anydocs fetch "api/composition-api-setup" --profile vuejs
```

### Cache Management

```bash
# Show cache status
anydocs cache status

# Clear all cache
anydocs cache clear

# Clear specific profile
anydocs cache clear --profile vuejs
```

## Usage Examples

### Vue.js Documentation (Single-Page App)

```bash
# Configure
anydocs config vuejs \
  https://vuejs.org \
  https://vuejs.org/sitemap.xml

# Index (first time only)
anydocs index vuejs

# Search
anydocs search "composition api"
anydocs search "reactivity" --limit 5
anydocs search "lifecycle" --profile vuejs
```

### Next.js Documentation

```bash
# Configure
anydocs config nextjs \
  https://nextjs.org \
  https://nextjs.org/sitemap.xml

# Index
anydocs index nextjs

# Search
anydocs search "app router" --profile nextjs
anydocs search "server components" --profile nextjs --limit 3
```

### Internal Company Docs

```bash
# Configure
anydocs config internal \
  https://docs.company.local \
  https://docs.company.local/sitemap.xml

# Index
anydocs index internal --force  # Force to use latest

# Search
anydocs search "deployment process" --profile internal
anydocs fetch "guides/onboarding" --profile internal
```

## Browser Rendering for Single-Page Apps

If a documentation site is a JavaScript-based SPA (like Vue.js or Next.js), you can enable browser rendering to properly scrape all pages:

```bash
# Requires OpenClaw gateway token
anydocs index vuejs \
  --use-browser \
  --gateway-token YOUR_OPENCLAW_GATEWAY_TOKEN \
  --gateway-url http://127.0.0.1:18789
```

**How it works:**
1. OpenClaw's browser tool (Playwright) renders each page
2. JavaScript executes and populates the DOM
3. Content is extracted from the rendered state
4. Pages are cached and indexed normally

**When to use:**
- Documentation sites that use React, Vue, or other SPA frameworks
- Sites where navigation is client-side only
- When static HTTP requests return incomplete content

**Setup:**
```bash
# Get your OpenClaw gateway token
echo $OPENCLAW_GATEWAY_TOKEN

# Then index with --use-browser flag
anydocs index <profile> --use-browser --gateway-token $OPENCLAW_GATEWAY_TOKEN
```

## Security Considerations

### Browser Rendering (`--use-browser`)

**What it does:**
- Opens and screenshots arbitrary URLs using OpenClaw's browser
- Executes JavaScript on those pages
- Presents an attack surface if misused

**Safety measures built-in:**
- ✅ **HTTPS-only**: Browser rendering rejects HTTP URLs (enforced)
- ✅ **Opt-in only**: Requires explicit `--use-browser` flag + token
- ✅ **Gateway token required**: Your authentication controls access
- ✅ **Profile validation**: URLs must match configured base_url
- ✅ **No arbitrary URL injection**: Can't point at random sites

**Best practices:**
1. **Only use with trusted documentation sites** (e.g., official framework docs)
2. **Protect your OpenClaw gateway token** (treat like a password)
3. **Never commit tokens to version control**
4. **Use `--gateway-token` securely:**
   ```bash
   # Load from environment variable (safe)
   anydocs index vuejs --use-browser --gateway-token $OPENCLAW_GATEWAY_TOKEN
   
   # NOT from command line history
   # anydocs index vuejs --use-browser --gateway-token abc123...
   ```

### Installation & Package Permissions

**Virtual environment (recommended):**
- ✅ Isolated, safe, no system-wide changes
- Default in `setup.sh`

**System-wide installation (`--break-system-packages`):**
- ⚠️ Can conflict with your system package manager
- Only use if you understand the risks
- Requires explicit `--system-packages` flag + user confirmation

For detailed setup, see the Installation section above.

## Python API

Use `anydocs` in your own Python code or agents:

```python
from lib.config import ConfigManager
from lib.scraper import DiscoveryEngine
from lib.indexer import SearchIndex
from lib.cache import CacheManager

# Load a profile
config_mgr = ConfigManager()
config = config_mgr.get_profile("vuejs")

# Option 1: Use cached index if available
cache_mgr = CacheManager()
cached_index = cache_mgr.get_index("vuejs")

if cached_index:
    index = SearchIndex.from_dict(cached_index)
else:
    # Build fresh
    scraper = DiscoveryEngine(config["base_url"], config["sitemap_url"])
    pages = scraper.fetch_all()
    
    index = SearchIndex()
    index.build(pages)
    
    # Cache for next time
    cache_mgr.save_index("vuejs", index.to_dict())

# Search
results = index.search("composition api", limit=10)

for result in results:
    print(f"{result['rank']}. {result['title']}")
    print(f"   Score: {result['relevance_score']}")
    print(f"   URL: {result['url']}")
```

### API Reference

#### ConfigManager
```python
from lib.config import ConfigManager

config_mgr = ConfigManager()

# Add profile
config_mgr.add_profile(
    name="vuejs",
    base_url="https://vuejs.org",
    sitemap_url="https://vuejs.org/sitemap.xml",
    search_method="hybrid",
    cache_ttl_days=7
)

# Get profile
config = config_mgr.get_profile("vuejs")

# List profiles
profiles = config_mgr.list_profiles()  # ["vuejs", "nextjs", ...]

# Validate
is_valid, error = config_mgr.validate_profile("vuejs")
```

#### DiscoveryEngine
```python
from lib.scraper import DiscoveryEngine

scraper = DiscoveryEngine(
    base_url="https://vuejs.org",
    sitemap_url="https://vuejs.org/sitemap.xml",
    rate_limit=0.5,  # seconds between requests
    use_browser=False,  # Set to True for SPA rendering
    gateway_url="http://127.0.0.1:18789",
    gateway_token="your_token"
)

# Discover all pages
urls = scraper.discover_urls()

# Scrape a single page
page = scraper.scrape_page("https://...")

# Scrape all pages
pages = scraper.fetch_all()
# Returns: [{url, title, content, tags, full_content}, ...]
```

#### SearchIndex
```python
from lib.indexer import SearchIndex

index = SearchIndex()

# Build from documents
index.build([
    {
        "url": "...",
        "title": "...",
        "content": "...",
        "tags": [...],
        "full_content": "..."
    },
    # ...
])

# Search
results = index.search(
    query="composition api",
    method="hybrid",  # keyword, semantic, or hybrid
    limit=10,
    regex=False  # set to True to use regex
)
# Returns: [{url, title, content, tags, relevance_score, rank}, ...]

# Serialize/deserialize
data = index.to_dict()
index = SearchIndex.from_dict(data)
```

#### CacheManager
```python
from lib.cache import CacheManager

cache = CacheManager()

# Save page
cache.save_page(
    url="https://...",
    title="Page Title",
    content="Page content...",
    metadata={"tags": ["api", "composables"]}
)

# Get page (if not expired)
page = cache.get_page("https://...", ttl_days=7)

# Save index
cache.save_index("vuejs", index.to_dict())

# Get index (if not expired)
index_data = cache.get_index("vuejs", ttl_days=7)

# Cache stats
stats = cache.get_cache_size()
# {pages_count, indexes_count, total_size_mb, cache_dir}

# Clear
cache.clear_cache()  # All
cache.clear_cache("vuejs")  # Specific profile
```

## Search Strategies

### Keyword Search
- **How it works**: Word-based matching with position weighting
- **Performance**: Very fast, O(n) in document count
- **Best for**: Exact terms, common queries
- **Example**: `anydocs search "composables"`

### Hybrid Search (Default)
- **How it works**: Keyword search + phrase proximity matching
- **Performance**: Fast, O(n) in document count
- **Best for**: Natural language queries
- **Example**: `anydocs search "how to manage state with composition api"`

### Regex Search
- **How it works**: Compiled regex pattern matching
- **Performance**: Medium, O(n*m) where m is pattern complexity
- **Best for**: Advanced patterns, complex queries
- **Example**: `anydocs search "^(ref|computed|watch)" --regex`

## Configuration

Profiles are stored in `~/.anydocs/config.json`:

```json
{
  "vuejs": {
    "name": "vuejs",
    "base_url": "https://vuejs.org",
    "sitemap_url": "https://vuejs.org/sitemap.xml",
    "search_method": "hybrid",
    "cache_ttl_days": 7
  }
}
```

**Fields:**
- `name`: Profile identifier
- `base_url`: Root documentation URL
- `sitemap_url`: XML sitemap URL
- `search_method`: `keyword`, `semantic`, or `hybrid`
- `cache_ttl_days`: Cache time-to-live in days

## Caching

Pages and indexes are cached in `~/.anydocs/cache/`:

```
~/.anydocs/cache/
├── pages/              # Individual page HTML/content
│   └── <hash>.json
├── indexes/            # Search indexes
│   └── <profile>_index.json
└── metadata.json       # Cache metadata
```

**TTL Behavior:**
- Default: 7 days
- Configurable per profile
- Expired caches are automatically removed on access
- Manual cleanup: `anydocs cache clear`

## Performance

- **Index build time**: 2-10 minutes (depends on site size)
- **Search time**: <100ms (from cache)
- **Memory usage**: ~50-200MB (depends on site size)
- **Disk usage**: 10-500MB (depends on site size and cache TTL)

**Real-world example (Vue.js):**
- 110 pages discovered from sitemap
- ~2 minutes to complete indexing
- <100ms search queries

## Troubleshooting

### "Profile not found"
```bash
anydocs list-profiles  # Check available profiles
anydocs config <name> <base_url> <sitemap>  # Create new profile
```

### "No index for profile"
```bash
anydocs index <profile>  # Build the index first
```

### "Failed to fetch"
- Check network connectivity
- Verify base_url is correct
- Check that sitemap_url returns valid XML

### Slow indexing
This is normal. The tool rate-limits to 0.5s per page to avoid overloading servers.

### Cache growing large
```bash
anydocs cache clear  # Clear all cache
anydocs cache clear --profile <profile>  # Clear specific profile
```

### Browser rendering not working
- Ensure `--gateway-token` is provided
- Check OpenClaw gateway is running: `http://127.0.0.1:18789/tools/invoke`
- Verify token with: `echo $OPENCLAW_GATEWAY_TOKEN`

## File Structure

```
anydocs/
├── anydocs.py              # Entry point
├── cli.py                  # Click CLI commands
├── lib/
│   ├── __init__.py
│   ├── scraper.py          # Discovery & scraping (with browser support)
│   ├── indexer.py          # Search indexing
│   ├── config.py           # Configuration management
│   └── cache.py            # TTL-based caching
├── requirements.txt        # Python dependencies
├── SKILL.md                # Skill documentation
├── README.md               # This file
└── examples/
    ├── vuejs-config.json
    ├── nextjs-config.json
    └── custom-config.json
```

## License

Part of the OpenClaw system.

---

**Questions?** Check `SKILL.md` for detailed documentation, or use `anydocs --help`.
