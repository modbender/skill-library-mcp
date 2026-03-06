---
name: lan-media-server
description: Share images, screenshots, and files from the AI workspace to users on the local network via HTTP. Use when the agent needs to show images, browser screenshots, or any files to the user and the current channel doesn't support inline media (e.g., webchat, CLI). Starts a lightweight Node.js static file server on LAN, managed by systemd. Drop files in the shared directory and send the user a clickable URL.
---

# LAN Media Server

Lightweight HTTP file server for sharing agent-generated media (screenshots, images, documents) with users on the local network.

## Why

Many AI assistant channels (webchat, CLI, SSH) can't display inline images. This skill solves that by serving files over HTTP on your LAN — drop a file, send a link.

## Quick Start

```bash
bash scripts/setup.sh
```

This creates the shared directory, installs the server script, creates a systemd user service, and starts it.

**Default config:**
- Port: `18801`
- Serve directory: `$HOME/projects/shared-media`
- Accessible at: `http://<LAN_IP>:18801/<filename>`

Override with environment variables:
```bash
MEDIA_PORT=9090 MEDIA_ROOT=/tmp/media bash scripts/setup.sh
```

## Usage Pattern

When you need to show an image or file to the user:

1. Save/copy the file to the shared media directory
2. Send the user a link: `http://<server-LAN-IP>:<port>/<filename>`

Example for browser screenshots:
```bash
cp /path/to/screenshot.jpg ~/projects/shared-media/my-screenshot.jpg
# Then send: http://192.168.1.91:18801/my-screenshot.jpg
```

Use descriptive filenames — the directory is flat and user-visible.

## Management

```bash
# Check status
systemctl --user status media-server

# Restart
systemctl --user restart media-server

# View logs
journalctl --user -u media-server -f

# Stop and disable
systemctl --user stop media-server
systemctl --user disable media-server
```

## Security Notes

- Serves files only on LAN (0.0.0.0 but typically behind NAT)
- No authentication — don't put sensitive files in the shared directory
- Path traversal is blocked (files must be under MEDIA_ROOT)
- No directory listing — must know the exact filename
