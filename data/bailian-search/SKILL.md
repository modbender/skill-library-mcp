---
name: bailian-search
description: "Real-time web search powered by Alibaba Cloud Bailian (DashScope) MCP service. Use when: user asks for latest news, real-time information, current events, or facts that may have changed recently. Requires: DASHSCOPE_API_KEY environment variable."
homepage: https://bailian.console.aliyun.com
metadata:
  {
    "openclaw":
      {
        "emoji": "🔍",
        "requires": { "bins": ["curl", "python3"], "env": ["DASHSCOPE_API_KEY"] },
      },
  }
---

# Bailian Search

Real-time web search powered by Alibaba Cloud Bailian (DashScope) MCP service.

## Overview

This skill integrates with Alibaba Cloud Bailian's Web Search MCP (Model Context Protocol) service, enabling AI assistants to retrieve real-time information from the internet, improving response accuracy and timeliness.

## Features

- 🔍 Real-time web search
- 🌐 Global information coverage
- ⚡ Fast response via SSE (Server-Sent Events)
- 🔒 Secure API key management
- 🛠️ Easy integration with OpenClaw

## Prerequisites

1. **Alibaba Cloud Account**: Register at [Alibaba Cloud Bailian](https://bailian.console.aliyun.com)
2. **API Key**: Obtain a DashScope API Key from the console

## Installation

### Using ClawHub (Recommended)

```bash
openclaw skill install bailian-search
# or
clawhub install bailian-search
```

### Manual Installation

```bash
# Clone to OpenClaw workspace
git clone <repository-url> ~/.openclaw/workspace/skills/bailian-search

# Or download and extract to:
# ~/.openclaw/workspace/skills/bailian-search/
```

## Configuration

### Set Environment Variable

**Option 1: Temporary (current session)**
```bash
export DASHSCOPE_API_KEY="your-dashscope-api-key"
```

**Option 2: Permanent (recommended)**

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):
```bash
echo 'export DASHSCOPE_API_KEY="your-dashscope-api-key"' >> ~/.zshrc
source ~/.zshrc
```

**Option 3: OpenClaw Config**
```bash
openclaw config set env.DASHSCOPE_API_KEY "your-dashscope-api-key"
```

## Usage

### Command Line

```bash
# After setting environment variable
./search.sh "latest tech news"

# Or one-liner
DASHSCOPE_API_KEY="your-key" ./search.sh "OpenAI GPT-5 release"
```

### Via AI Assistant

Once configured, simply ask your AI assistant:
- "Search for today's tech news"
- "Find OpenAI's latest announcements"
- "Look up 2025 China EV sales data"

The AI will automatically use this skill to fetch real-time information.

## How It Works

This skill connects to Alibaba Cloud Bailian's **MCP SSE (Server-Sent Events)** service:

1. Receives user search query
2. Establishes SSE connection to Bailian MCP server
3. Retrieves real-time search results
4. Returns structured content to the AI

## MCP Configuration (Advanced)

For use with other MCP-compatible clients (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "WebSearch": {
      "type": "sse",
      "name": "Alibaba Cloud Bailian Web Search",
      "description": "Real-time web search powered by Tongyi Lab's Text-Embedding, GTE-reRank, Query Rewriting, and Search Judgment models.",
      "baseUrl": "https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/sse",
      "headers": {
        "Authorization": "Bearer ${DASHSCOPE_API_KEY}"
      }
    }
  }
}
```

## API Reference

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DASHSCOPE_API_KEY` | Yes | Alibaba Cloud DashScope API Key |

### Command Arguments

```bash
./search.sh <query>
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `query` | string | Yes | Search query string |

## Troubleshooting

**Error: "DASHSCOPE_API_KEY environment variable is not set"**

Solution: Ensure the environment variable is set:
```bash
export DASHSCOPE_API_KEY="your-key"
```

**Empty results or timeout**

1. Verify your API key is valid
2. Check network connectivity
3. Bailian service may take time to respond, please be patient

**How to get DashScope API Key?**

1. Visit [Alibaba Cloud Bailian Console](https://bailian.console.aliyun.com)
2. Register/login with Alibaba Cloud account
3. Create an API Key in the console
4. Copy the key and set it as environment variable

## Privacy & Security

- Your API key is never hardcoded in the skill files
- API key is read from environment variables only
- No data is stored or logged by this skill
- All requests go directly to Alibaba Cloud servers

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please submit issues or pull requests via ClawHub.

## Acknowledgments

- Alibaba Cloud Bailian (DashScope) for providing the MCP service
- OpenClaw team for the skill framework
- MCP community for the protocol specification

## Links

- [Alibaba Cloud Bailian](https://bailian.console.aliyun.com)
- [DashScope Documentation](https://help.aliyun.com/document_detail/611474.html)
- [OpenClaw Documentation](https://docs.openclaw.ai)
- [ClawHub Registry](https://clawhub.com)