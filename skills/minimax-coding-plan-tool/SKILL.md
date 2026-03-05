---
name: minimax-coding-plan-tool
description: A lightweight MiniMax Coding Plan Tool skill that directly calls official MCP APIs using pure JavaScript. No external MCP servers. No tool bridge. No subprocess invocation. Designed for minimal overhead and fast integration within OpenClaw. 
metadata: {"openclaw":{"emoji":"🧩","requires":{"bins":["node"],"env":["MINIMAX_API_KEY"]},"primaryEnv":"MINIMAX_API_KEY"}}
---

# MiniMax Coding Plan Tool

> ⚠️ Requires a **Coding Plan API Key**
> Subscribe at: [https://platform.minimaxi.com/subscribe/coding-plan](https://platform.minimaxi.com/subscribe/coding-plan)

A lightweight MiniMax Coding Plan Tool skill that directly calls official MCP APIs using pure JavaScript.
No external MCP servers. No tool bridge. No subprocess invocation.

Designed for minimal overhead and fast integration within OpenClaw.

---

## ✨ Features

This skill provides two native capabilities of MiniMax Coding Plan MCP:

### 1. `minimax_web_search`

Web search powered by MiniMax Coding Plan API.

* Real-time information retrieval
* Lightweight API-based implementation
* No external search engine dependency

### 2. `minimax_understand_image`

Vision-language image understanding via MiniMax VLM.

* Image semantic analysis
* Visual content description
* Multimodal reasoning support

---

## 🧩 Architecture

* Pure JavaScript implementation
* Direct HTTPS API calls
* No MCP server runtime required
* No external tool dependency
* Minimal resource usage

---

## 🔑 Configuration


```bash
openclaw config set skills.entries.minimax-coding-plan-tool.apiKey "sk-your-key"
```

or

```json
{
  "skills": {
    "entries": {
      "minimax-coding-plan-tool": {
        "apiKey": "sk-your-key"
      }
    }
  }
}
```
Read the API key from `openclaw.json`.

---

# Tool Discovery

Execute  `minimax_coding_plan_tool.js` with environment variable `MINIMAX_API_KEY` to dynamically register these tools:

```
MINIMAX_API_KEY="sk-your-key" node minimax_coding_plan_tool.js tools
```

Output format:

```
{
  "tools": [
    {
      "name": "minimax_web_search",
      "description": "...",
      "inputSchema": { ... }
    },
    {
      "name": "minimax_understand_image",
      "description": "...",
      "inputSchema": { ... }
    }
  ]
}
```

---

# Tool 1 — minimax_web_search

## Purpose

Real-time web search using MiniMax Coding Plan search API.

## CLI Invocation

```
MINIMAX_API_KEY="sk-your-key" node minimax_coding_plan_tool.js web_search "<query>"
```

Example:

```
MINIMAX_API_KEY="sk-your-key" node minimax_coding_plan_tool.js web_search "OpenAI GPT-5 release date"
```

## Input Schema

```
{
  "query": "string"
}
```

## Output Format

Success:

```
{
  "success": true,
  "query": "...",
  "results": [
    {
      "title": "...",
      "link": "...",
      "snippet": "...",
      "date": "..."
    }
  ],
  "related_searches": []
}
```

Error:

```
{
  "error": "error message"
}
```

---

# Tool 2 — minimax_understand_image

## Purpose

Image understanding using MiniMax Coding Plan VLM API.
Only mainstream image formats are supported (for example: JPEG/JPG, PNG, WebP, and GIF).

Supports:

* HTTP / HTTPS image URLs
* Local file paths
* `@localfile.jpg` shorthand

Local files are automatically converted to base64 data URLs.

## Security Notice

This tool requires outbound network access.
If a local image is provided, its content is transmitted to the remote MiniMax API for processing, which introduces a potential risk of local image data leakage.
Do not submit sensitive, private, or regulated images unless you fully accept this risk.

## CLI Invocation

```
MINIMAX_API_KEY="sk-your-key" node minimax_coding_plan_tool.js understand_image <image_source> "<prompt>"
```

Examples:

Remote image:

```
MINIMAX_API_KEY="sk-your-key" node minimax_coding_plan_tool.js understand_image https://example.com/image.jpg "Describe this image"
```

Local image:

```
MINIMAX_API_KEY="sk-your-key" node minimax_coding_plan_tool.js understand_image ./photo.png "What objects are visible?"
```

With @ prefix:

```
MINIMAX_API_KEY="sk-your-key" node minimax_coding_plan_tool.js understand_image @photo.png "Summarize the scene"
```

## Input Schema

```
{
  "image_source": "string",
  "prompt": "string"
}
```

## Output Format

Success:

```
{
  "success": true,
  "prompt": "...",
  "image_source": "...",
  "analysis": "model response"
}
```

Error:

```
{
  "error": "error message"
}
```