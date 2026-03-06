---
name: claude-local-bridge
description: Access local repos from Claude on your phone via approval-gated MCP bridge
---


# Claude Local Bridge

Access your local repos from Claude on your phone. Secure MCP bridge server with approval gating.

## What it does

Runs a local MCP server (over SSE) that gives Claude access to your files — but only after you explicitly approve each request from a real-time dashboard.

## Tools

- **browse_files** — List workspace file tree (no approval needed)
- **request_file_access** — Request approval to read/write files (blocks until you decide)
- **read_file** — Read an approved file's contents
- **write_file** — Write to an approved file
- **list_approvals** — See all current approvals
- **revoke_approval** — Revoke access
- **view_audit_log** — View access history

## Quick Start

```bash
git clone https://github.com/suhteevah/claude-local-bridge.git
cd claude-local-bridge
pip install -r requirements.txt
python -m app.main --roots ~/projects
```

Then connect Claude to `http://localhost:9120/mcp/sse`

## Security

- Sandboxed to whitelisted directories only
- Extension blocklist (.env, .pem, .key, etc.)
- Path traversal prevention
- Bearer token auth
- Every file access requires human approval
- Full audit trail

## Remote Access

Use Tailscale (free), Cloudflare Tunnel (free), or NetBird (FOSS) to access from your phone. See [tunnel.md](https://github.com/suhteevah/claude-local-bridge/blob/main/tunnel.md).
