---
name: serper
description: Google search via Serper API. Use when you need to search the web and the user has a Serper API key. Triggers on: (1) user asks to search the web, (2) user wants Google search results, (3) user provides a Serper API key.
metadata: { "openclaw": { "emoji": "🔍", "requires": { "bins": ["curl"], "env": ["SERPER_API_KEY"] } } }
---

# Serper Search

Use Serper API for Google search results.

## API Details

- **Endpoint**: `https://google.serper.dev/search`
- **Method**: POST
- **Headers**: `X-API-Key: $SERPER_API_KEY`, `Content-Type: application/json`
- **Body**: `{"q": "your query here"}`

## Usage

### With API Environment Key in

```bash
SERPER_API_KEY="your-key" curl -s -X POST "https://google.serper.dev/search" \
  -H "X-API-Key: $SERPER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"q": "your query"}'
```

### With Inline Key

```bash
curl -s -X POST "https://google.serper.dev/search" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"q": "your query"}'
```

## Script

Use the bundled `search` script:

```bash
./scripts/search "your query"
```

## Response Format

Returns JSON with:
- `organic[]` - Search results (title, link, snippet)
- `searchParameters.q` - Original query
- `credits` - Credits used

Example result:
```json
{
  "searchParameters": {"q": "test", "type": "search"},
  "organic": [
    {"title": "Result Title", "link": "https://...", "snippet": "Description...", "position": 1}
  ],
  "credits": 1
}
```

## Getting an API Key

1. Visit https://serper.dev
2. Sign up for an account
3. Get your API key from the dashboard
4. Set `SERPER_API_KEY` environment variable or pass the key inline
