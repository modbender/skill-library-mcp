---
name: plsreadme
description: Share markdown files and text as clean, readable web links via plsreadme.com. Use when someone asks to share a document, README, PRD, proposal, notes, or any markdown as a shareable link. Also triggers for "create a preview link", "share this as a page", or "make this readable". Requires the plsreadme MCP server (npx plsreadme-mcp).
---

# plsreadme

Share markdown as clean `plsrd.me` links. Two tools available via MCP:

## Setup

Add the MCP server to your client:

```json
{
  "mcpServers": {
    "plsreadme": {
      "command": "npx",
      "args": ["-y", "plsreadme-mcp"]
    }
  }
}
```

Or use the remote endpoint (zero install):

```json
{
  "mcpServers": {
    "plsreadme": {
      "url": "https://plsreadme.com/mcp"
    }
  }
}
```

## Tools

- **`plsreadme_share_file`** — Share a local `.md` file by path. Reads from disk, uploads, returns link.
- **`plsreadme_share_text`** — Share text directly (markdown preferred; plain text supported). Good for generated content, conversation output, or composed docs.

## Usage Guidelines

- Max file size: 200KB
- Links are permanent and publicly accessible — confirm with the user before sharing sensitive content
- If input is non-markdown, refactor it with your own model first (or let `plsreadme_share_text` auto-structure plain text)
- The first `# Heading` becomes the document title
- Output includes a readable URL and a raw markdown URL

## Example Prompts

- "Share this README on plsreadme"
- "Create a shareable link for docs/api.md"
- "Turn this into a readable web page I can send"
- "Share this PRD as a link"
