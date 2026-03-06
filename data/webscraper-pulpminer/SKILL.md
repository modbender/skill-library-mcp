---
name: pulpminer
description: "Convert any webpage into structured JSON data using AI. Scrape websites, extract data into custom JSON schemas, and call saved APIs programmatically. Useful for web scraping, data extraction, content monitoring, lead generation, price tracking, and building data pipelines."
emoji: ⛏️
homepage: https://pulpminer.com
metadata: {"clawdbot":{"requires":{"env":["PULPMINER_API_KEY"]},"config":["pulpminer_api_key"]}}
---

# PulpMiner — AI Web Scraping & JSON API

PulpMiner converts any webpage into structured JSON using AI. You provide a URL and optionally a JSON template, and PulpMiner scrapes the page, runs it through an LLM, and returns clean structured data.

## Authentication

All API calls require the `apikey` header:

```
apikey: <PULPMINER_API_KEY>
```

Get your API key from https://pulpminer.com/api — click "Regenerate Key" if you don't have one.

## Core Workflow

PulpMiner works in two phases:

1. **Create a saved API** — Configure a URL, scraper, LLM, and optional JSON template via the PulpMiner dashboard at https://pulpminer.com/api
2. **Call the saved API** — Use the external endpoint with your API key to fetch structured JSON

## Calling a Saved API

### Static API (fixed URL)

```bash
curl -X GET "https://api.pulpminer.com/external/<apiId>" \
  -H "apikey: <PULPMINER_API_KEY>"
```

Returns JSON extracted from the configured webpage.

### Dynamic API (URL with variables)

For APIs saved with template URLs like `https://example.com/search?q={{query}}&page={{page}}`:

```bash
curl -X POST "https://api.pulpminer.com/external/<apiId>" \
  -H "apikey: <PULPMINER_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"query": "javascript frameworks", "page": "1"}'
```

The `{{variable}}` placeholders in the saved URL get replaced with the values you provide.

## Response Format

Successful responses return:

```json
{
  "data": { ... },
  "errors": null
}
```

Error responses return:

```json
{
  "data": null,
  "errors": "Error message describing what went wrong"
}
```

## Caching

- API responses are cached for **24 hours** by default
- If cache is older than 15 minutes, PulpMiner serves the cached version while refreshing in the background
- Cache can be disabled per-API in the dashboard settings

## Configuration Options (Set in Dashboard)

When creating a saved API at https://pulpminer.com/api, you can configure:

| Option | Description |
|--------|-------------|
| **URL** | The webpage to scrape |
| **JSON Template** | Optional JSON structure for the LLM to follow (e.g., `{"name": "", "price": ""}`) |
| **Render JS** | Enable for SPAs and JS-heavy pages (uses headless browser) |
| **CSS Selector** | Extract only a specific part of the page (e.g., `.product-list`, `#main-content`) |
| **Extra Instructions** | Additional guidance for the AI (e.g., "Only extract items with prices above $50") |
| **Dynamic URL** | Enable template variables in the URL with `{{variable}}` syntax |
| **Cache** | Toggle response caching on/off |

## Integration with Zapier

For async scraping in Zapier workflows:

```bash
# Static API
curl -X POST "https://api.pulpminer.com/external/zapier/get/<apiId>" \
  -H "apikey: <PULPMINER_API_KEY>" \
  -d '{"callbackURL": "https://hooks.zapier.com/..."}'

# Dynamic API
curl -X POST "https://api.pulpminer.com/external/zapier/post/<apiId>" \
  -H "apikey: <PULPMINER_API_KEY>" \
  -d '{"callbackURL": "https://hooks.zapier.com/...", "query": "value"}'
```

Returns `201` immediately. Sends scraped data to the callback URL when complete.

## Integration with n8n

Verify authentication:

```bash
curl -X GET "https://api.pulpminer.com/external/n8n/auth" \
  -H "apikey: <PULPMINER_API_KEY>"
```

Then use the standard `/external/<apiId>` endpoints for data fetching.

## Credits

- Each API call costs **0.25–0.4 credits** depending on the endpoint
- JavaScript rendering adds **0.1 credits** extra
- New users get **5 free credits**
- Purchase more at https://pulpminer.com/credits

## Tips

- Use **CSS selectors** to narrow down the scraped content and improve accuracy
- Provide a **JSON template** for consistent, predictable output structures
- Enable **JS rendering** only when needed — static pages scrape faster and cost fewer credits
- Use **extra instructions** to guide the AI (e.g., "Return dates in ISO 8601 format")
- For monitoring use cases, keep **caching enabled** to reduce credit usage
- Use the **playground** first to verify a URL is scrapable before saving an API config
- Dynamic APIs are ideal for search pages, paginated content, and parameterized URLs

## Links

- Website: https://pulpminer.com
- API Dashboard: https://pulpminer.com/api
