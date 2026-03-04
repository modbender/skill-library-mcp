---
name: forage-shopping
description: Search and compare products across merchants. Find the best deals with price comparison and shopping recommendations.
homepage: https://forageshopping.com
user-invocable: true
metadata: {"openclaw":{"requires":{},"emoji":"🌿"}}
---

You have access to the Forage Shopping MCP server for product search and price comparison.

## Setup

Add the Forage MCP server to your `openclaw.json`:

```json
{
  "mcpServers": {
    "forage-shopping": {
      "url": "https://forageshopping.com/mcp"
    }
  }
}
```

No API key required — the remote server handles everything.

## Available tools

- **search_products**: Search for products across merchants. Pass a natural language query like "running shoes under £120" or "best noise cancelling headphones".
- **compare_prices**: Compare prices for a specific product across multiple retailers. Pass an exact product name like "Sony WH-1000XM5".
- **find_deals**: Find the best current deals in a category with an optional budget. Pass a category like "coffee machines" and optionally a budget like "£200".

## How to use

When the user asks about buying something, finding a product, comparing prices, or looking for deals:

1. Use `search_products` to find options matching their query
2. If they're interested in a specific product, use `compare_prices` to find the best retailer
3. If they want deals in a category, use `find_deals`

Present results clearly with product name, price, merchant, and link. Always recommend based on value, not just lowest price. Mention delivery costs and return policies when available.
