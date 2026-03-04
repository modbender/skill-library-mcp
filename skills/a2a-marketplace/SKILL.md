---
name: a2a-marketplace
description: "AI tool marketplace via AgentForge — discover, compare, and execute tools with automatic billing and trust scoring."
metadata:
  {
    "openclaw":
      {
        "emoji": "🏪",
        "requires": {},
        "install":
          [
            {
              "id": "plugin",
              "kind": "node",
              "package": "@a2a/openclaw-plugin",
              "label": "Install A2A Corp plugin",
            },
          ],
      },
  }
---

# A2A Marketplace (AgentForge)

Use the AgentForge marketplace tools to discover, evaluate, and execute AI tools from a curated marketplace.

## Quick Start

Search for tools:

```
Use forge_discover to find a tool for "sentiment analysis"
```

Execute a tool:

```
Use forge_execute with toolId "tool-abc" and input { "text": "Hello world" }
```

## Available Tools

| Tool | Description |
|------|-------------|
| `forge_discover` | Search marketplace by query, category, price, trust score, tags |
| `forge_execute` | Execute a tool (billing applied automatically) |
| `forge_get_schema` | Get input/output schema for a tool |
| `forge_balance` | Check agent balance, spending, and tier |
| `forge_list_categories` | List all tool categories |
| `forge_batch_execute` | Execute up to 10 tools in parallel |

## Workflows

### Find the best tool for a task

1. Use `forge_discover` with your query and optional filters (category, maxPrice, minTrustScore)
2. Use `forge_get_schema` to understand the input format
3. Use `forge_execute` to run the tool

### Budget-conscious execution

1. Use `forge_balance` to check remaining budget
2. Use `forge_discover` with `maxPrice` filter
3. Compare tools by trust score and price
4. Execute with confidence

### Batch processing

Use `forge_batch_execute` to run multiple tools at once:

```json
{
  "calls": [
    { "toolId": "sentiment-v2", "input": { "text": "Great product!" } },
    { "toolId": "translate-en-vi", "input": { "text": "Hello world" } }
  ]
}
```

## Categories

Common categories: `nlp`, `vision`, `code`, `data`, `audio`, `security`, `blockchain`, `productivity`

## Trust Scores

Tools are scored 0-100 based on:
- Uptime and reliability
- Response time
- User ratings
- Security audit status
- API compliance
