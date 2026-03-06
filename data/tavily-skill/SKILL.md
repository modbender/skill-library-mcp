---
name: tavily-search
description: "Use Tavily API for real-time web search and content extraction. Use when: user needs real-time web search results, research, or current information from the web. Requires Tavily API key."
homepage: https://tavily.com
metadata: { "openclaw": { "emoji": "🔍", "requires": { "bins": ["curl", "jq"] } } }
---

# Tavily Search Skill

Use Tavily API for real-time web search and content extraction.

## When to Use

✅ **USE this skill when:**

- "Search the web for [topic]"
- "Find recent information about [subject]"
- "Get current news about [topic]"
- "Research [topic] online"
- "Find up-to-date information"

## When NOT to Use

❌ **DON'T use this skill when:**

- Simple URL fetching → use `web_fetch` tool
- No API key available → use `web_fetch` for specific URLs
- Historical/archival data → use specialized archives

## Setup

1. Get a Tavily API key from https://tavily.com
2. Set the API key in environment or config

## Configuration

Set your Tavily API key in one of these ways:

### Environment variable:
```bash
export TAVILY_API_KEY="your-api-key-here"
```

### OpenClaw config:
Add to your `openclaw.json`:
```json
{
  "tavily": {
    "apiKey": "your-api-key-here"
  }
}
```

## Usage Examples

### Basic Search
```bash
# Search for a topic
curl -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TAVILY_API_KEY" \
  -d '{
    "query": "latest AI developments 2026",
    "search_depth": "basic",
    "max_results": 5
  }' | jq .
```

### Research Query
```bash
# Get detailed research results
curl -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TAVILY_API_KEY" \
  -d '{
    "query": "climate change impact on agriculture 2026",
    "search_depth": "advanced",
    "max_results": 10,
    "include_answer": true,
    "include_images": false
  }' | jq .
```

### News Search
```bash
# Search for recent news
curl -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TAVILY_API_KEY" \
  -d '{
    "query": "technology news today",
    "search_depth": "basic",
    "max_results": 5,
    "include_raw_content": false
  }' | jq .
```

## API Parameters

- `query`: Search query string (required)
- `search_depth`: "basic" or "advanced" (default: "basic")
- `max_results`: Number of results (1-10, default: 5)
- `include_answer`: Include AI-generated answer (true/false)
- `include_images`: Include image URLs (true/false)
- `include_raw_content`: Include full page content (true/false)

## Error Handling

- Check API key is set: `echo $TAVILY_API_KEY`
- Test connection: Use the basic search example above
- Rate limits: Tavily has usage limits based on your plan

## Alternatives

If Tavily API is not available:
1. Use `web_fetch` for specific URLs
2. Use `web_search` with Kimi API (if configured)
3. Manual web browsing with `browser` tool