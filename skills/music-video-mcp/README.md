# Freebeat MCP Server

> The world's first AI music video generation MCP — turn any song into a cinematic music video from Claude, Cursor, or any MCP client.

## Features

- **generate_music_video** — Create AI music videos from text prompts
- **check_generation_status** — Track video generation progress
- **list_styles** — Browse available visual styles (cinematic, anime, retro VHS, etc.)
- **get_account_info** — Check credits and account status

### Generation Modes

| Mode | Description |
|------|-------------|
| `singing` | Lyric-driven visuals synced to vocals |
| `storytelling` | Narrative scenes with cinematic transitions |
| `auto` | AI selects the best mode for your prompt |

## Quick Start

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "freebeat": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/freebeat-mcp"],
      "env": {
        "FREEBEAT_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "freebeat": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/freebeat-mcp"],
      "env": {
        "FREEBEAT_API_KEY": "your-api-key"
      }
    }
  }
}
```

### VS Code

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "freebeat": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/freebeat-mcp"],
      "env": {
        "FREEBEAT_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Claude Code

```bash
claude mcp add freebeat -- npx -y @anthropic-ai/freebeat-mcp
```

## Get Your API Key

1. Go to [freebeat.ai/developers](https://freebeat.ai/developers)
2. Sign up for a free account (50 credits included)
3. Copy your API key
4. Set it as `FREEBEAT_API_KEY` in your MCP config

## Example Usage

Once connected, just ask your AI assistant:

> "Create a cinematic music video about a rainy night in Tokyo with neon lights"

> "Generate a retro VHS style video for my lo-fi track, 60 seconds"

> "Make an anime music video about a journey through space"

## Pricing

| Plan | Credits/mo | Price |
|------|-----------|-------|
| Free | 50 | $0 |
| Pro | 500 | $19/mo |
| Team | 2000 | $49/mo |

1 credit ≈ 10 seconds of video.

## Links

- [Website](https://freebeat.ai)
- [API Docs](https://freebeat.ai/developers/docs)
- [Discord](https://discord.gg/freebeat)
- [Twitter](https://x.com/freebeatai)

## License

MIT
