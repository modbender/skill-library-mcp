---
name: markdown-editor-with-chat
description: Lightweight markdown editor with optional OpenClaw gateway chat. Filesystem-based, no database required.
metadata:
  openclaw:
    emoji: "📝"
    requires:
      bins: ["node"]
      env:
        - MARKDOWN_DIR
---

# Markdown Editor with Chat

A lightweight, self-contained markdown editor that serves files from a local directory with optional OpenClaw gateway chat integration.

## Features

- **Filesystem-based**: Point to any directory containing markdown files
- **No database**: Files are the source of truth
- **Folder navigation**: Browse nested directories
- **Live preview**: See rendered markdown as you type
- **Optional chat**: Connect to OpenClaw gateway for AI assistance
- **Zero external dependencies**: Pure Node.js, self-contained HTML

## Quick Start

```bash
# Start with CLI arguments (recommended)
node scripts/server.mjs --folder /path/to/markdown --port 3333

# Or short form
node scripts/server.mjs -f /path/to/markdown -p 3333

# With gateway chat enabled (via env vars)
export OPENCLAW_GATEWAY_URL=http://127.0.0.1:18789
export OPENCLAW_GATEWAY_TOKEN=your-token
node scripts/server.mjs -f /path/to/markdown
```

Then open http://localhost:3333 in your browser.

## CLI Arguments

| Argument | Short | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| `--folder` | `-f` | Yes* | - | Directory containing markdown files |
| `--port` | `-p` | No | 3333 | Server port |
| `--host` | `-h` | No | 127.0.0.1 | Server host (localhost only by default) |
| `--help` | | No | | Show help message |

*Required unless `MARKDOWN_DIR` env var is set.

## Environment Variables (fallback)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MARKDOWN_DIR` | Yes* | - | Directory containing markdown files |
| `PORT` | No | 3333 | Server port |
| `HOST` | No | 127.0.0.1 | Server host |
| `OPENCLAW_GATEWAY_URL` | No | - | Gateway URL for chat feature |
| `OPENCLAW_GATEWAY_TOKEN` | No | - | Gateway auth token |

CLI arguments take precedence over environment variables.

## Security

- **Localhost only by default**: Server binds to 127.0.0.1, rejects public IPs
- **Same-origin only**: No CORS headers, browser enforces same-origin policy
- **Path traversal protection**: Cannot access files outside MARKDOWN_DIR
- **No credentials in code**: All secrets via environment variables
- **Gateway proxy**: Tokens never exposed to browser

This is a local development tool. The API is intentionally simple (no auth) because it's designed for localhost use on directories you control.

## API Endpoints

- `GET /` - Serves the editor UI
- `GET /api/files` - List files and folders
- `GET /api/files/:path` - Get file content
- `PUT /api/files/:path` - Save file content
- `POST /api/files/:path` - Create new file
- `POST /api/chat` - Proxy chat to gateway (if configured)

## Use Cases

- Browse and edit OpenClaw pearls
- Personal markdown wiki
- Note-taking with AI assistance
- Documentation browser
