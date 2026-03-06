---
name: mslearn-mcp
description: Connect to Microsoft Learn MCP Server to search Microsoft documentation, fetch specific doc pages, and find code samples. Use when you need to query Microsoft Learn documentation, Azure docs, .NET docs, or find official Microsoft code examples. Works with mcporter for tool-based MCP interaction.
---

# Microsoft Learn MCP

Connect to the Microsoft Learn MCP (Model Context Protocol) Server to interact with Microsoft documentation through structured tools.

## Endpoint

```
https://learn.microsoft.com/api/mcp
```

This is a remote MCP server using streamable HTTP. It provides three main tools:
- `microsoft_docs_search` — Search Microsoft documentation
- `microsoft_docs_fetch` — Fetch specific documentation pages
- `microsoft_code_sample_search` — Search for official code samples

## Setup

### Add to mcporter config

```bash
mcporter config add --name mslearn --url https://learn.microsoft.com/api/mcp --type http
```

Or manually add to `~/.config/mcporter/config.json`:

```json
{
  "servers": {
    "mslearn": {
      "type": "http",
      "url": "https://learn.microsoft.com/api/mcp"
    }
  }
}
```

### Verify connection

```bash
mcporter list mslearn --schema
```

## Usage

### Search documentation

```bash
mcporter call mslearn.microsoft_docs_search query="Azure Functions triggers"
```

### Fetch a specific doc page

```bash
mcporter call mslearn.microsoft_docs_fetch url="https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings"
```

### Search code samples

```bash
mcporter call mslearn.microsoft_code_sample_search query="Python blob storage" language="python"
```

## Tool Reference

Tool schemas are dynamic. Always check current schema with:

```bash
mcporter list mslearn --schema
```

Common patterns:

| Tool | Typical parameters |
|------|-------------------|
| `microsoft_docs_search` | `query` (required), `locale` (optional, e.g., "en-us") |
| `microsoft_docs_fetch` | `url` (required, full Learn URL) |
| `microsoft_code_sample_search` | `query` (required), `language` (optional), `product` (optional) |

## Output formats

Default output is human-readable. Use `--output json` for structured data:

```bash
mcporter call mslearn.microsoft_docs_search query="Entra ID" --output json
```

## Notes

- No authentication required for the Learn MCP Server
- The server interface may change dynamically; always call `list` to get current tools
- For complex queries, prefer search over fetch; let the tool find relevant pages
- Locale defaults to en-us if not specified
