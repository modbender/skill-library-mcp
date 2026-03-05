# Exa MCP Setup

## Enabled Tools
- `web_search_exa`
- `web_search_advanced_exa`
- `people_search_exa`

## When to Use Which Tool
- `web_search_exa`: Use for broad discovery and fast first-pass research.
- `web_search_advanced_exa`: Use for targeted research that needs stricter filters or deeper result control.
- `people_search_exa`: Use for person-centric lookups (people, roles, teams, profiles).

## Hosted Endpoint Template
Use a fixed tool list:

`https://mcp.exa.ai/mcp?exaApiKey=${EXA_API_KEY}&tools=web_search_exa,web_search_advanced_exa,people_search_exa`

Keep the tool order stable for easier diffs.

## Generic MCP Server Snippet
```json
{
  "mcpServers": {
    "exa": {
      "transport": {
        "type": "streamable-http",
        "url": "https://mcp.exa.ai/mcp?exaApiKey=${EXA_API_KEY}&tools=web_search_exa,web_search_advanced_exa,people_search_exa"
      }
    }
  }
}
```

## Troubleshooting
- `429` can indicate free-tier or rate-limit constraints. Retry with narrower scope or use an API key with higher limits.
- If a tool is unavailable, confirm the `tools=` query parameter includes valid Exa tool names.
