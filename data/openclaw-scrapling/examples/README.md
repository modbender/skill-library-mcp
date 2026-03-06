# Scrapling Examples

Example scripts demonstrating different Scrapling features.

## Files

| Example | Description | Use Case |
|---------|-------------|----------|
| `basic.py` | Fast HTTP scraping | Static HTML, no JavaScript |
| `stealth.py` | Anti-bot bypass | Cloudflare, bot detection |
| `dynamic.py` | JavaScript content | React, Vue, SPAs |
| `adaptive.py` | Survives redesigns | Frequently changing sites |
| `session.py` | Login & sessions | Authentication required |

## Running Examples

```bash
# Basic scraping
cd ~/.openclaw/skills/scrapling
python examples/basic.py

# Stealth mode (bypasses Cloudflare)
python examples/stealth.py

# Dynamic content (JavaScript apps)
python examples/dynamic.py

# Adaptive selectors
python examples/adaptive.py

# Session management (requires credentials)
python examples/session.py
```

## Creating Your Own

Copy an example and modify:

```bash
cp examples/basic.py my_scraper.py
nano my_scraper.py
python my_scraper.py
```

## CLI Tool

For quick scraping without writing Python:

```bash
# Basic
python scrape.py --url "https://example.com" --selector ".content"

# Stealth
python scrape.py --url "https://example.com" --stealth --selector ".content"

# With output
python scrape.py --url "https://example.com" --selector ".product" --output products.json
```
