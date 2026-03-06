# Search APIs Reference (Standard v3.0)

## Google Custom Search API
- **Endpoint**: `https://www.googleapis.com/customsearch/v1`
- **Requires**: `GOOGLE_API_KEY`, `GOOGLE_CSE_ID`
- **Purpose**: Official, high-quality search results.

## Wikipedia OpenSearch API
- **Endpoint**: `https://en.wikipedia.org/w/api.php`
- **Parameters**: `action=opensearch`, `format=json`, `namespace=0`
- **Purpose**: Fast, structured encyclopedia lookups.

## Reddit Search API
- **Endpoint**: `https://www.reddit.com/search.json`
- **Requires**: Proper `User-Agent` (handled by script).
- **Purpose**: Community discussions and real-time sentiment.

## Google News (GNews) RSS
- **Endpoint**: `https://news.google.com/rss/search`
- **Purpose**: Latest news headlines and tracking current events.

## DuckDuckGo Stealth (Scrapling)
- **Endpoint**: `https://duckduckgo.com/html/`
- **Requires**: `scrapling` package in a dedicated venv.
- **Purpose**: Privacy-respecting scraping for anti-bot bypass.
