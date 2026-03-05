# MiniMax MCP Tools

Web search and image understanding via MiniMax Coding Plan MCP.

## Features

- 🔍 **Web Search** - Real-time web search powered by MiniMax
- 🖼️ **Image Understanding** - Analyze and describe images

## Prerequisites

1. MiniMax Coding Plan API Key (get from https://platform.minimaxi.com)
2. Node.js 18+
3. uv (for MCP server)

## Installation

### 1. Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Configure API Key

```bash
# Add to ~/.openclaw/.env
echo 'MINIMAX_API_KEY=your-coding-plan-key' >> ~/.openclaw/.env
echo 'MINIMAX_API_HOST=https://api.minimaxi.com' >> ~/.openclaw/.env
chmod 600 ~/.openclaw/.env
```

## Usage

### Web Search

```bash
~/.openclaw/skills/minimax-mcp-call/scripts/mcp_search.sh web_search "search query"
```

Example:
```bash
~/.openclaw/skills/minimax-mcp-call/scripts/mcp_search.sh web_search "今天天气"
```

### Image Understanding

```bash
~/.openclaw/skills/minimax-mcp-call/scripts/mcp_search.sh understand_image "image_url" "question"
```

Example:
```bash
~/.openclaw/skills/minimax-mcp-call/scripts/mcp_search.sh understand_image "https://example.com/image.png" "描述这张图片"
```

## Files

```
minimax-mcp-call/
├── SKILL.md           # OpenClaw skill definition
├── README.md          # This file
└── scripts/
    ├── mcp_client.mjs # MCP client (Node.js)
    └── mcp_search.sh  # Easy wrapper script
```

## License

MIT
