---
name: minimax-mcp-call
description: MiniMax MCP tools - Web search and image understanding via MiniMax Coding Plan. Use when user needs web search, current information, or image analysis. Requires MiniMax Coding Plan API key.
---

# MiniMax MCP Tools

Web search and image understanding via MiniMax Coding Plan MCP.

## Capabilities

| Tool | Description |
|------|-------------|
| `web_search` | Search the web for current information, news, weather |
| `understand_image` | Analyze images, screenshots, diagrams |

## Requirements

- MiniMax Coding Plan API Key
- Node.js 18+
- uv (for MCP server)

## Setup

1. Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Configure API key:
```bash
echo 'MINIMAX_API_KEY=your-coding-plan-key' >> ~/.openclaw/.env
echo 'MINIMAX_API_HOST=https://api.minimaxi.com' >> ~/.openclaw/.env
```

## Usage

```bash
# Web search
~/.openclaw/skills/minimax-mcp-call/scripts/mcp_search.sh web_search "search query"

# Image understanding
~/.openclaw/skills/minimax-mcp-call/scripts/mcp_search.sh understand_image "image_url" "question"
```

## Quick Test

```bash
~/.openclaw/skills/minimax-mcp-call/scripts/mcp_search.sh web_search "hello"
```
