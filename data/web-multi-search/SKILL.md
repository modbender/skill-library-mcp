---
name: web-multi-search
description: Search the web using multiple search engines simultaneously (Bing, Yahoo, Startpage, Aol, Ask) via async-search-scraper, iterating through result pages.
metadata:
  clawdis:
    emoji: "🔍"
    primaryEnv: python
    requires:
      bins:
        - python3
        - pip
    install:
      - python3 -m pip install -r requirements.txt
      - python3 -m pip install git+https://github.com/soxoj/async-search-scraper.git --no-deps
---

# Web Multi-Search

Search the web across **multiple search engines at once** using [async-search-scraper](https://github.com/soxoj/async-search-scraper). Collects results from Bing, Yahoo, Startpage, Aol, and Ask, iterating through multiple result pages.

## Setup

```bash
cd skills/web-multi-search
python3 -m pip install -r requirements.txt
python3 -m pip install git+https://github.com/soxoj/async-search-scraper.git --no-deps
```

> **Note:** The library must be installed from the GitHub URL, not PyPI. The `--no-deps` flag is required because the library pins `bs4` (wrong package name); the real dependencies are already in `requirements.txt`.

### Linux (apt) fallback
If `pip` isn't available, install the system packages:

```bash
sudo apt-get update
sudo apt-get install -y python3-requests python3-aiohttp python3-aiohttp-socks python3-bs4
```


## Usage

Run the search script with a query:

```bash
python3 web_multi_search.py "your search query"
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--pages` | `3` | Number of result pages per engine |
| `--engines` | all working | Comma-separated list: `bing,yahoo,startpage,aol,ask` |
| `--proxy` | none | HTTP/SOCKS proxy URL |
| `--timeout` | `10` | HTTP timeout in seconds |
| `--output` | `json` | Output format: `json`, `csv`, `text` |
| `--unique-urls` | off | Deduplicate results by URL |
| `--unique-domains` | off | Deduplicate results by domain |

### Examples

```bash
# Basic search, 3 pages per engine, JSON output
python3 web_multi_search.py "python async tutorial"

# Search only Bing and Yahoo, 5 pages each
python3 web_multi_search.py "machine learning" --engines bing,yahoo --pages 5

# Unique URLs only, CSV output
python3 web_multi_search.py "OpenClaw skills" --unique-urls --output csv

# Use a proxy
python3 web_multi_search.py "privacy tools" --proxy socks5://127.0.0.1:9050
```

### Output format

JSON output (default) returns an array of result objects:

```json
[
  {
    "engine": "Bing",
    "host": "example.com",
    "link": "https://example.com/page",
    "title": "Page Title",
    "text": "Snippet of the page content..."
  }
]
```

### How the agent should use this

When you need to search the web for information:

1. Run the script with the user's query.
2. Parse the JSON output to extract relevant links and snippets.
3. Use the results to answer the user or to fetch specific pages for deeper reading.

```bash
# Quick search and capture output
RESULTS=$(python3 /path/to/skills/web-multi-search/web_multi_search.py "query here" 2>/dev/null)
echo "$RESULTS" | python3 -c "import json,sys; data=json.load(sys.stdin); [print(r['link'], r['title']) for r in data[:10]]"
```

## Available search engines

| Engine | Status |
|--------|--------|
| Bing | Working |
| Yahoo | Working |
| Startpage | Working |
| Aol | Working |
| Ask | Working |
| Google | Not working (requires JS) |
| DuckDuckGo | Not working (CAPTCHA) |
| Dogpile | Not working (HTTP 403) |
| Mojeek | Not working (HTTP 403) |
| Qwant | Not working (HTTP 403) |
| Torch | Requires TOR proxy |

## Troubleshooting

- **Import errors**: Make sure you installed the library from the GitHub URL with `--no-deps`.
- **Empty results / bans**: Search engines may rate-limit. Increase delay or use fewer pages.
- **Torch engine**: Only works with a running TOR proxy at `socks5://127.0.0.1:9050`.
