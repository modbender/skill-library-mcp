# Claude Local Bridge

Access your local repos from Claude on your phone. No more being chained to your PC.

A secure bridge server that lets Claude (web, mobile, desktop) read and write files on your machine through an approval-gated MCP server. Every file access requires your explicit OK — nothing touches disk without you saying so.

```
┌──────────────────┐                          ┌────────────────────────┐
│  Claude Mobile   │    tunnel / LAN / VPN    │  Claude Local Bridge   │
│  Claude Web      │ ◄──────────────────────► │  (your PC)             │
│  Claude Desktop  │      MCP over SSE        │                        │
└──────────────────┘                          └──────────┬─────────────┘
                                                         │
                                               ┌─────────▼──────────┐
                                               │   Approval Gate    │
                                               │  (you approve each │
                                               │   file via dashboard│
                                               │   or phone)        │
                                               └─────────┬──────────┘
                                                         │
                                               ┌─────────▼──────────┐
                                               │   Local Files      │
                                               │  (sandboxed to     │
                                               │   workspace roots) │
                                               └────────────────────┘
```

## Features

- **MCP Server** — 7 tools Claude can call: browse, read, write, request access, list/revoke approvals, view audit log
- **Approval Gate** — every file read/write blocks until you approve via the dashboard
- **Real-time Dashboard** — industrial-themed web UI for managing approvals, browsing files, viewing audit logs
- **Sandboxed** — only directories you whitelist are accessible
- **Token Auth** — bearer token generated at startup for pairing
- **Audit Trail** — every access logged with timestamp, action, path, and outcome
- **WebSocket** — live push notifications for approval requests
- **Tunnel-ready** — works with Tailscale, Cloudflare Tunnel, NetBird, or any reverse proxy

## Quick Start

```bash
# Clone and install
git clone https://github.com/suhteevah/claude-local-bridge.git
cd claude-local-bridge
pip install -r requirements.txt

# Start the bridge (expose your project directories)
python -m app.main --roots ~/projects ~/code
```

The server starts and prints:

```
🔗 Bridge Ready
  HTTP API:   http://127.0.0.1:9120
  MCP (SSE):  http://127.0.0.1:9120/mcp/sse
  Dashboard:  http://127.0.0.1:9120/
  Token:      a1b2c3d4e5f6...
```

## Connect Claude

### Claude Desktop / Claude Code

Add to your MCP settings (`claude_desktop_config.json` or `.claude/settings.json`):

```json
{
  "mcpServers": {
    "local-bridge": {
      "url": "http://localhost:9120/mcp/sse"
    }
  }
}
```

### Claude Mobile (via tunnel)

Set up a tunnel (see [tunnel.md](tunnel.md)) so your phone can reach the server, then use the tunnel URL as the MCP endpoint.

**Quickest option** (no account needed):

```bash
# In a second terminal
cloudflared tunnel --url http://localhost:9120
# Gives you: https://random-words.trycloudflare.com
# Use: https://random-words.trycloudflare.com/mcp/sse
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `browse_files` | List the workspace file tree (no approval needed) |
| `request_file_access` | Request approval to read/write — blocks until you decide |
| `read_file` | Read a file (requires active READ approval) |
| `write_file` | Write to a file (requires active WRITE approval) |
| `list_approvals` | See all current approvals and their status |
| `revoke_approval` | Revoke an existing approval |
| `view_audit_log` | View the access history |

### How it works

1. Claude calls `browse_files` to see your project structure
2. Claude calls `request_file_access` with a reason ("I need to read src/main.py to fix the bug")
3. **Your dashboard shows the request** — you approve or deny
4. If approved, Claude can now `read_file` or `write_file` within the approved scope
5. Everything is logged in the audit trail

## Dashboard

The built-in web dashboard at `http://localhost:9120/` lets you:

- **Approve/deny** access requests in real-time (WebSocket-powered)
- **Browse** your workspace file tree
- **View** the full audit log with filtering
- **Monitor** server status and active approvals
- **Revoke** approvals at any time

Mobile-friendly design — manage approvals from your phone while Claude works.

## HTTP API

The full REST API is also available for custom integrations:

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | No | Server status and config |
| `GET` | `/files/tree` | Token | Directory tree listing |
| `GET` | `/files/read?path=...` | Token | Read file contents |
| `PUT` | `/files/write` | Token | Write file contents |
| `POST` | `/approvals/request` | Token | Request file access (blocking) |
| `GET` | `/approvals/` | No | List all approvals |
| `GET` | `/approvals/pending` | No | List pending requests |
| `POST` | `/approvals/{id}/decide` | No | Approve or deny |
| `DELETE` | `/approvals/{id}` | No | Revoke approval |
| `GET` | `/audit/` | No | Recent audit entries |
| `GET` | `/audit/path?path=...` | No | Audit for specific path |
| `WS` | `/ws/approvals` | No | Real-time approval WebSocket |

## Tunnel Options

See [tunnel.md](tunnel.md) for detailed setup guides. Summary:

| Solution | FOSS | Cost | Best For |
|----------|------|------|----------|
| **Tailscale** | Client: BSD-3 / [Headscale](https://github.com/juanfont/headscale) = full FOSS | Free | Personal phone access |
| **Cloudflare Tunnel** | Client: Apache 2.0 | Free | Sharing with others, public URL |
| **NetBird** | Full FOSS (BSD-3) | Free self-hosted | Full FOSS purity |
| **FRP** | Apache 2.0 | Free (needs VPS) | Self-hosted everything |

## CLI Options

```
python -m app.main --roots DIR [DIR ...] [OPTIONS]

Options:
  --roots           Workspace directories to expose (required, multiple allowed)
  --host            Bind address (default: 127.0.0.1, use 0.0.0.0 for LAN/tunnel)
  --port            Port number (default: 9120)
  --max-file-size-mb  Max file size limit in MB (default: 10)
```

## Security

- **Sandboxed roots** — only directories you explicitly pass via `--roots` are accessible
- **Extension blocklist** — `.env`, `.pem`, `.key`, `.p12`, `.pfx`, `.secret` are always blocked
- **Path traversal prevention** — `../` attacks are caught and rejected
- **Bearer token auth** — API endpoints require the token generated at startup
- **Approval gating** — every file read/write needs explicit human approval
- **Backup on write** — automatic `.bak` file created before any overwrite
- **Audit logging** — full trail of every access attempt (successful or not)

## Project Structure

```
claude-local-bridge/
├── app/
│   ├── main.py              # Entry point, FastAPI + MCP setup
│   ├── mcp/
│   │   └── server.py        # MCP tools (browse, read, write, approve...)
│   ├── middleware/
│   │   └── auth.py          # Bearer token authentication
│   ├── models/
│   │   └── schemas.py       # Pydantic models and enums
│   ├── routers/
│   │   ├── approvals.py     # Approval CRUD endpoints
│   │   ├── audit.py         # Audit log endpoints
│   │   ├── files.py         # File read/write endpoints
│   │   └── ws.py            # WebSocket for real-time approvals
│   └── services/
│       ├── approval_service.py  # Approval state management
│       ├── audit_service.py     # In-memory audit log
│       └── file_service.py      # Sandboxed file operations
├── dashboard/
│   ├── index.html           # Dashboard shell
│   ├── style.css            # Industrial console theme
│   └── bridge.js            # API client + WebSocket
├── requirements.txt
├── tunnel.md                # Tunnel setup guide
└── README.md
```

## License

MIT
