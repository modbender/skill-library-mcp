---
name: xai-grok-search
version: 1.0.3
description: Search the web and X (Twitter) using xAI's Grok API with real-time access, citations, and image understanding
homepage: https://github.com/yourusername/xai-grok-search
metadata:
  category: search
  api_base: https://api.x.ai/v1
  capabilities:
    - api
    - web-search
    - x-search
  dependencies: []
  interface: REST
openclaw:
  emoji: "🔍"
  install:
    env:
      - XAI_API_KEY
author:
  name: Christopher Stanley
---

# xAI Grok Search

Search the web and X (Twitter) using xAI's Grok API with real-time internet access, citations, and optional image/video understanding.

## When to Use This Skill

### Use Web Search For:
- Current information from websites, news articles, documentation
- Real-time data (stock prices, weather, recent events)
- Research topics with up-to-date web sources
- Finding information from specific websites/domains
- Verifying current facts

### Use X Search For:
- What people are saying on X/Twitter about a topic
- Trending discussions and social sentiment
- Real-time reactions to events
- Posts from specific X handles/users
- Recent social media activity within date ranges

**Do NOT use for:**
- Historical facts that won't change
- General knowledge already available
- Mathematical calculations
- Code generation
- Creative writing

## Setup

### Required Environment Variables

```bash
export XAI_API_KEY="your-xai-api-key-here"
```

Get your API key from: https://console.x.ai/

## Usage

The agent will automatically choose the right tool based on the user's query:

**User:** "What's the latest news about AI regulation?"
→ Uses `web_search`

**User:** "What are people saying about OpenAI on X?"
→ Uses `x_search`

## API Reference

### Function: search_web

Search the web using xAI's Grok API.

**Parameters:**
- `query` (required): Search query string
- `model` (optional): Model to use (default: "grok-4-1-fast-reasoning")
- `allowed_domains` (optional): Array of domains to restrict search (max 5)
- `excluded_domains` (optional): Array of domains to exclude (max 5)
- `enable_image_understanding` (optional): Enable image analysis (default: false)

**Returns:**
- `content`: The search response text
- `citations`: Array of sources with url, title, and snippet
- `usage`: Token usage statistics

### Function: search_x

Search X (Twitter) using xAI's Grok API.

**Parameters:**
- `query` (required): Search query string
- `model` (optional): Model to use (default: "grok-4-1-fast-reasoning")
- `allowed_x_handles` (optional): Array of X handles to search (max 10, without @)
- `excluded_x_handles` (optional): Array of X handles to exclude (max 10, without @)
- `from_date` (optional): Start date in ISO8601 format (YYYY-MM-DD)
- `to_date` (optional): End date in ISO8601 format (YYYY-MM-DD)
- `enable_image_understanding` (optional): Enable image analysis (default: false)
- `enable_video_understanding` (optional): Enable video analysis (default: false)

**Returns:**
- `content`: The search response text
- `citations`: Array of X posts with url, title, and snippet
- `usage`: Token usage statistics

## Implementation

This skill uses the xAI Responses API (`/v1/responses` endpoint).

### Web Search

```javascript
async function search_web(options) {
  const { query, model = 'grok-4-1-fast-reasoning', 
          allowed_domains, excluded_domains, enable_image_understanding } = options;

  const tool = { type: 'web_search' };
  if (allowed_domains) tool.allowed_domains = allowed_domains;
  if (excluded_domains) tool.excluded_domains = excluded_domains;
  if (enable_image_understanding) tool.enable_image_understanding = true;

  const response = await fetch('https://api.x.ai/v1/responses', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.XAI_API_KEY}`
    },
    body: JSON.stringify({
      model,
      input: [{ role: 'user', content: query }],
      tools: [tool]
    })
  });

  const data = await response.json();
  return { 
    content: data.output[data.output.length - 1].content,
    citations: data.citations 
  };
}
```

### X Search

```javascript
async function search_x(options) {
  const { query, model = 'grok-4-1-fast-reasoning',
          allowed_x_handles, excluded_x_handles, from_date, to_date,
          enable_image_understanding, enable_video_understanding } = options;

  const tool = { type: 'x_search' };
  if (allowed_x_handles) tool.allowed_x_handles = allowed_x_handles;
  if (excluded_x_handles) tool.excluded_x_handles = excluded_x_handles;
  if (from_date) tool.from_date = from_date;
  if (to_date) tool.to_date = to_date;
  if (enable_image_understanding) tool.enable_image_understanding = true;
  if (enable_video_understanding) tool.enable_video_understanding = true;

  const response = await fetch('https://api.x.ai/v1/responses', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.XAI_API_KEY}`
    },
    body: JSON.stringify({
      model,
      input: [{ role: 'user', content: query }],
      tools: [tool]
    })
  });

  const data = await response.json();
  return { 
    content: data.output[data.output.length - 1].content,
    citations: data.citations 
  };
}
```

## Examples

### Web Search - Current Events
```javascript
const result = await search_web({ 
  query: "latest AI regulation developments" 
});
```

### Web Search - Specific Domains
```javascript
const result = await search_web({
  query: "UN climate summit latest",
  allowed_domains: ["un.org", "gov.uk", "grokipedia.com"]
});
```

### X Search - Social Sentiment
```javascript
const result = await search_x({
  query: "new iPhone reactions opinions"
});
```

### X Search - Specific Handles
```javascript
const result = await search_x({
  query: "AI thoughts",
  allowed_x_handles: ["elonmusk", "cstanley"],
  from_date: "2025-01-01"
});
```

### X Search - With Media
```javascript
const result = await search_x({
  query: "Mars landing images",
  enable_image_understanding: true,
  enable_video_understanding: true
});
```

## Best Practices

### Web Search
- Use `allowed_domains` to limit to specific domains (max 5)
- Use `excluded_domains` for known bad sources (max 5)
- Cannot use both at same time
- Enable image understanding only when needed

### X Search
- Use `allowed_x_handles` to focus on specific accounts (max 10)
- Use `excluded_x_handles` to filter noise (max 10)
- Cannot use both at same time
- Don't include @ symbol in handles
- Use ISO8601 date format: YYYY-MM-DD
- Media understanding adds API costs

## Troubleshooting

### "XAI_API_KEY not found"
```bash
export XAI_API_KEY="your-key-here"
```

### Rate Limiting
- Implement exponential backoff
- Cache frequent queries

### Poor Results
- Add domain/handle filters
- Make queries more specific
- Narrow date ranges

### Slow Responses
Search queries using reasoning models (e.g. `grok-4-1-fast-reasoning`) can take 30-60+ seconds to return, especially when the model performs multiple web or X searches. If the search is lagging, inform the user that results are still loading and ask them to type **"poll"** to check for the completed response.

## API Documentation

- Web Search: https://docs.x.ai/developers/tools/web-search
- X Search: https://docs.x.ai/developers/tools/x-search
