# TrueNAS Skill

An AI agent skill for managing TrueNAS SCALE via its API. Check pool health, manage datasets and snapshots, monitor alerts, control apps, orchestrate Dockge container stacks, and manage bookmarks — all through natural language.

Works with [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [OpenClaw](https://github.com/openclaw/openclaw), [Cursor](https://cursor.com), and any tool supporting the [SKILL.md](https://agentskills.io) standard.

Part of [unsol.dev](https://unsol.dev)

## Prerequisites

- TrueNAS SCALE instance with API access
- `curl` and `jq` installed
- Node.js 18+ (for WebSocket and Dockge scripts)

## Installation

### OpenClaw (via ClawHub)

```bash
clawhub install truenas-skill
```

### Claude Code

```bash
git clone https://github.com/anotb/truenas-skill.git ~/.claude/skills/truenas-skill
cd ~/.claude/skills/truenas-skill && npm install
```

### Cursor / Other

Clone to your agent's skill directory and run `npm install`.

## Configuration

1. Generate an API key in TrueNAS UI > API Keys
2. Set environment variables (copy `.env.example` to `.env` and fill in values):

```bash
# Required
export TRUENAS_URL=https://10.0.0.5:444
export TRUENAS_API_KEY=your-api-key

# Optional: Dockge
export DOCKGE_URL=http://10.0.0.5:5001
export DOCKGE_USER=your-username
export DOCKGE_PASS=your-password
```

See `.env.example` for the full list of optional service API keys.

**Important:** TrueNAS auto-revokes API keys used over HTTP. Always use HTTPS.

> **Note:** The REST API (`/api/v2.0/`) is deprecated in TrueNAS 25.04 and fully removed in
> 26.04. This skill uses the WebSocket API as the primary method for forward compatibility.

## What You Can Do

| Task | How |
|------|-----|
| Check NAS health | Pool status, alerts, service state |
| Manage datasets | Create, list, delete ZFS datasets |
| Snapshots | Create manual snapshots, check schedules (via WebSocket) |
| Replication | Monitor replication job status |
| App management | List apps, check updates, install new apps |
| Dockge stacks | List and update Docker Compose stacks |
| Media requests | Add movies/shows via Overseerr/Radarr/Sonarr |
| Downloads | Check torrent/usenet queues |
| Bookmarks | Save, search, tag bookmarks via Karakeep |
| Monitoring | Plex sessions, sync status, notifications |

## Scripts

| Script | Description |
|--------|-------------|
| `scripts/truenas-ws.mjs` | WebSocket API client for TrueNAS |
| `scripts/dockge-list.mjs` | List Dockge stacks |
| `scripts/dockge-update.mjs` | Update Dockge stacks |

```bash
# Example: get system info via WebSocket
node scripts/truenas-ws.mjs system.info

# Example: list snapshots (filtered by dataset)
node scripts/truenas-ws.mjs zfs.snapshot.query '[[["dataset", "=", "pool/dataset"]]]'

# Example: list all stacks
node scripts/dockge-list.mjs

# Example: update all running stacks
node scripts/dockge-update.mjs
```

## Reference Files

The `references/` directory contains API patterns for common homelab services:

- **media-management.md** — Overseerr, Sonarr, Radarr, Prowlarr, Plex, Tautulli
- **app-installation.md** — TrueNAS native app installation guide
- **downloads.md** — qBittorrent, SABnzbd, FlareSolverr
- **homelab-services.md** — ntfy, Syncthing, n8n, NocoDB, ChangeDetection, Crafty
- **books-and-media.md** — Audiobookshelf, LazyLibrarian, Calibre-Web, MeTube
- **bookmarks.md** — Karakeep (AI-powered bookmark manager)

## Links

- [ClawHub](https://clawhub.ai/skills/truenas-skill) — install via `clawhub install truenas-skill`
- [GitHub](https://github.com/anotb/truenas-skill)

## License

MIT
