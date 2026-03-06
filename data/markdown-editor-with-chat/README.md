# Markdown Editor with Chat

A lightweight, self-contained markdown editor that serves files from a local directory with optional OpenClaw gateway chat integration.

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- 📁 **Filesystem-based**: Point to any directory containing markdown files
- 🗄️ **No database**: Files are the source of truth
- 🌲 **Folder navigation**: Browse nested directories with breadcrumb navigation
- 👁️ **Live preview**: See rendered markdown as you type
- 💬 **Optional chat**: Connect to OpenClaw gateway for AI assistance
- 📦 **Zero dependencies**: Pure Node.js, self-contained HTML

## Quick Start

```bash
# Clone the repo
git clone https://github.com/telegraphic-dev/markdown-editor-with-chat.git
cd markdown-editor-with-chat

# Start with CLI arguments (recommended)
node scripts/server.mjs --folder /path/to/your/markdown/files

# Or with short flags
node scripts/server.mjs -f /path/to/markdown -p 3333

# Or with environment variables
export MARKDOWN_DIR=/path/to/your/markdown/files
node scripts/server.mjs
```

Open http://localhost:3333 in your browser.

## Enable Chat

To enable AI chat, set the OpenClaw gateway credentials:

```bash
export OPENCLAW_GATEWAY_URL=http://127.0.0.1:18789
export OPENCLAW_GATEWAY_TOKEN=your-gateway-token
```

The chat panel will appear when these are configured.

## Configuration

### CLI Arguments (recommended)

| Argument | Short | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| `--folder` | `-f` | Yes* | - | Directory containing markdown files |
| `--port` | `-p` | No | 3333 | Server port |
| `--host` | `-h` | No | 127.0.0.1 | Server host |
| `--help` | | No | | Show help message |

*Required unless `MARKDOWN_DIR` env var is set.

### Environment Variables (fallback)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MARKDOWN_DIR` | Yes* | - | Directory containing markdown files |
| `PORT` | No | 3333 | Server port |
| `HOST` | No | 127.0.0.1 | Server host |
| `OPENCLAW_GATEWAY_URL` | No | - | Gateway URL for chat |
| `OPENCLAW_GATEWAY_TOKEN` | No | - | Gateway auth token |

*CLI arguments take precedence over environment variables.

## Security

- Server binds to localhost only by default
- Path traversal protection prevents accessing files outside MARKDOWN_DIR
- Gateway tokens are never exposed to the browser
- All secrets via environment variables (never in code)

## Use Cases

- Browse and edit OpenClaw pearls
- Personal markdown wiki
- Note-taking with AI assistance
- Documentation browser

## License

MIT
