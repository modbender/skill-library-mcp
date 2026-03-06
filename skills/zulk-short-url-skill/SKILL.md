---
name: zulk-url-shortener
description: "Premium AI-first URL shortening and management with real-time
  analytics and team collaboration via MCP. Use when shortening links for
  marketing, tracking AI interactions, or managing custom domains. Keywords:
  url, shortener, analytics, link management, mcp."
---


# Zulk URL Shortener Skill

This skill enables AI agents to manage short links using the Zu.lk MCP (Model Context Protocol) server.

## Overview

Zu.lk is an AI-first premium URL shortener designed for blazing-fast performance and seamless AI integration. This skill connects your agent to the Zulk MCP server, allowing it to:

- Create shortened URLs (e.g., `zu.lk/abcd`)
- Manage existing links and campaigns
- Access real-time analytics
- Collaborate with team members

## Installation

To use this skill, add the Zulk MCP server configuration to your AI assistant's settings (e.g., `mcp.json` or equivalent).

### Configuration Options

Choose the transport method that best fits your environment:

#### 1. Streamable HTTP (Recommended)
Fastest and most reliable communication.
```json
{
  "mcpServers": {
    "zulk-url-shortener": { "url": "https://mcp.zu.lk/mcp" }
  }
}
```

#### 2. SSE (Server-Sent Events)
Real-time streaming specialized for certain clients.
```json
{
  "mcpServers": {
    "zulk-url-shortener": { "url": "https://mcp.zu.lk/sse" }
  }
}
```

#### 3. Stdio (via mcp-remote)
Uses standard input/output via a remote bridge.
```json
{
  "mcpServers": {
    "zulk-url-shortener": {
      "command": "npx",
      "args": ["mcp-remote", "https://mcp.zu.lk/mcp"]
    }
  }
}
```

## Step-by-Step Instructions

1.  **Preparation**: Ensure you have a Zu.lk account or are ready to sign in via Google.
2.  **Configuration**: Add one of the JSON configurations above to your agent's MCP settings file.
3.  **Authentication**: When you first run a command like "shorten this link", the agent will present an OAuth URL. Follow the link to authenticate.
4.  **Verification**: Ask the agent "List my recently created links" to verify the connection is active.
5.  **Execution**: Use natural language to create links, e.g., "Create a short link for https://google.com with alias 'my-search'".

## Usage Examples

### Creating a Link
**Input**: "Shorten https://github.com/Zu-lk/zulk-short-url-skill"
**Output**: "Generated short link: https://zu.lk/z-skill"

### Checking Analytics
**Input**: "How many clicks did my 'newsletter' link get yesterday?"
**Output**: "Your 'newsletter' link received 1,240 clicks yesterday."

## Edge Cases & Troubleshooting

- **Auth Failure**: If authentication fails, ensure you are using the correct Google account. You may need to restart the agent to re-trigger the OAuth flow.
- **Alias Taken**: If a custom alias is already in use, the agent should suggest an alternative or append a random string.
- **Rate Limits**: If you exceed your plan's link limit, the MCP server will return an error indicating the limit has been reached.
- **Link Expiration**: Ensure you check if the link has an expiration date if it suddenly stops working.

## References
- [Official Website](https://zu.lk)
- [MCP Documentation](https://zu.lk/-/mcp)
