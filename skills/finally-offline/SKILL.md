---
name: finally-offline-culture
description: Browse culture articles and generate personalized HTML newsletters via MCP
---

# Finally Offline Culture MCP

Connect to a curated culture publication covering fashion, music, sneakers, design, and technology. Browse articles, subscribe, and generate branded HTML newsletter digests on demand.

## When to Use

- When the user asks for news about fashion, streetwear, sneakers, music, design, or tech culture
- When the user wants a personalized newsletter or digest
- When the user asks to subscribe to a publication
- When the user wants curated content recommendations

## Setup

This skill uses a remote MCP server. Add the following to your MCP configuration:

```json
{
  "mcpServers": {
    "finally-offline": {
      "url": "https://yaieomxrayxpvfjxxctg.supabase.co/functions/v1/human-culture-mcp",
      "transport": "http"
    }
  }
}
```

No API key required for browsing. Subscribe to unlock digest generation.

## Available Tools

### list_articles
Browse all published articles with optional filters.
- `category` (optional): Filter by category (fashion, music, sneakers, design, tech)
- `limit` (optional): Number of articles to return (default 10)

### search_articles
Search articles by keyword.
- `query` (required): Search term

### subscribe_agent
Subscribe your agent to Finally Offline.
- `agent_name` (required): Your agent's display name
- `interests` (optional): Array of topic interests

### generate_digest
Generate a branded HTML newsletter digest.
- `categories` (optional): Array of categories to include
- `limit` (optional): Number of articles in digest

### get_agent_report
View your subscription stats and reading history.

## Example Usage

**User:** "What's new in sneakers and fashion?"
**Action:** Use `list_articles` with category "sneakers" or "fashion"

**User:** "Make me a newsletter about music and design"
**Action:** First `subscribe_agent` if not already subscribed, then `generate_digest` with categories ["music", "design"]

**User:** "Search for articles about Nike"
**Action:** Use `search_articles` with query "Nike"

## Links

- Publication: https://finallyoffline.com
- MCP Docs: https://finallyoffline.com/llms.txt
- Example Output: https://finallyoffline.com/digest-example.html
