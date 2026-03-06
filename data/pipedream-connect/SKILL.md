---
name: pipedream-connect
description: Connect 2,000+ APIs with managed OAuth via Pipedream. Includes full UI integration for OpenClaw Gateway dashboard with per-agent app isolation.
metadata: {"openclaw":{"emoji":"🔌","requires":{"bins":["mcporter"],"openclaw":">=2026.1.0"},"category":"integrations"}}
---

# Pipedream Connect

Connect your AI agents to 2,000+ APIs with managed OAuth via Pipedream. Each agent gets its own isolated app connections and OAuth tokens.

## What's New (2026-03-01 v1.3.0)

- **Per-agent app connections** — App connections moved to Agents → [Agent] → Tools → Pipedream
- **Global tab = credentials only** — The Pipedream tab is now for platform auth (Client ID/Secret/Project ID) only
- **External User ID defaults to agent slug** — e.g. `main`, `scout-monitor` (not a UUID)
- **Live connected apps** — Refresh queries the Pipedream API for real connected accounts
- **Environment warning** — Agent panel shows a warning when running in development mode
- **New RPCs**: `pipedream.connect`, `pipedream.disconnect`, `pipedream.test` (per-agent, use `agentId` + `appSlug`)

## What's New (v1.3.0) — Vault-Backed Secrets

- **`clientId` and `clientSecret` stored in `~/.openclaw/secrets.json`** (OpenClaw vault) — no longer plaintext in `pipedream-credentials.json`
- **`PIPEDREAM_CLIENT_SECRET` removed from `mcporter.json` env** — client secret is never written to mcporter config
- **Auto-migration**: on first gateway start after upgrade, existing `pipedream-credentials.json` secrets are silently moved to vault and stripped from the file
- **Token refresh script** now reads from vault first (falls back to credentials.json → mcporter.json for backwards compat)
- **`pipedream-credentials.json`** now contains only non-sensitive fields: `projectId`, `environment`, `externalUserId`
- VirusTotal "suspicious" flag resolved — no plaintext credential files

## Architecture

```
Global Pipedream Tab
  └── Platform credentials (Client ID, Secret, Project ID, Environment)
  └── Agent quick-links table (→ navigate to per-agent config)

Agents → [Agent] → Tools → Pipedream
  └── External User ID (defaults to agent slug)
  └── Connected Apps (live from Pipedream API)
  └── Available Apps grid + Browse All Apps modal
  └── Manual slug entry
```

## Prerequisites

1. **Pipedream Account** — [pipedream.com](https://pipedream.com)
2. **mcporter** — `npm install -g mcporter`
3. **OpenClaw Gateway** — v2026.1.0 or later

## Setup

### Step 1: Create OAuth Client & Project

1. Go to [pipedream.com/settings/api](https://pipedream.com/settings/api) → **New OAuth Client**
2. Copy **Client ID** and **Client Secret**
3. Go to [pipedream.com/projects](https://pipedream.com/projects) → create a project
4. Copy **Project ID** (`proj_...`)

### Step 2: Configure Platform Credentials

1. OpenClaw Dashboard → **Pipedream** tab → **Configure**
2. Enter Client ID, Client Secret, Project ID
3. Set **Environment** to `production` (not development — development tokens expire faster and have lower rate limits)
4. Click **Save Credentials**

### Step 3: Connect Apps Per Agent

1. Go to **Agents → [Agent] → Tools → Pipedream**
2. Verify the **External User ID** (defaults to agent slug, e.g. `main`)
3. Click **Connect** on any app in the grid — completes OAuth in a popup
4. Click **↻ Refresh** after OAuth completes to see the app appear in Connected Apps

### Step 4: Token Refresh (Recommended)

```bash
# Cron job — runs every 45 minutes
(crontab -l 2>/dev/null; echo "*/45 * * * * /usr/bin/python3 $HOME/openclaw/skills/pipedream-connect/scripts/pipedream-token-refresh.py >> $HOME/openclaw/logs/pipedream-cron.log 2>&1") | crontab -
```

## Per-Agent Isolation

Each agent uses a separate Pipedream `external_user_id`:

| Agent | External User ID | Pipedream Identity |
|-------|-----------------|-------------------|
| `main` | `main` | Isolated OAuth tokens |
| `scout-monitor` | `scout-monitor` | Isolated OAuth tokens |
| `scout-spark` | `scout-spark` | Isolated OAuth tokens |

Config stored at: `~/.openclaw/workspace/config/integrations/pipedream/{agentId}.json`

**External User ID defaults to agent slug.** Override it in Agents → Tools → Pipedream → Edit.

## RPC Reference

### Global (credentials)
| RPC | Params | Description |
|-----|--------|-------------|
| `pipedream.status` | — | Get global credential status + agent summaries |
| `pipedream.saveCredentials` | `clientId, clientSecret, projectId, environment` | Save platform credentials |
| `pipedream.getToken` | — | Get/refresh the platform OAuth access token |
| `pipedream.getConnectUrl` | `agentId, appSlug` | Get OAuth connect URL for a user+app |
| `pipedream.connectApp` | `agentId, appSlug` | Complete app connection + write to mcporter |
| `pipedream.disconnectApp` | `agentId, appSlug` | Disconnect app + remove from mcporter |
| `pipedream.refreshToken` | `agentId?, appSlug?` | Refresh token(s) — all or specific agent/app |
| `pipedream.activate` | `agentId, appSlug` | Activate an app (add to mcporter if not present) |

### Per-Agent
| RPC | Params | Description |
|-----|--------|-------------|
| `pipedream.agent.status` | `agentId` | Get config + live connected apps from API |
| `pipedream.agent.save` | `agentId, externalUserId` | Save per-agent config |
| `pipedream.agent.delete` | `agentId` | Remove per-agent config |
| `pipedream.connect` | `agentId, appSlug` | Get OAuth connect URL for agent |
| `pipedream.disconnect` | `agentId, appSlug` | Disconnect app + remove from mcporter |
| `pipedream.test` | `agentId, appSlug` | Test app connection |

## Using Connected Tools

```bash
# Gmail (agent: main → externalUserId: main)
mcporter call pipedream-main-gmail.gmail-find-email \
  instruction="Find unread emails from today"

# Google Calendar (agent: scout-monitor)
mcporter call pipedream-scout-monitor-google-calendar.google-calendar-find-event \
  instruction="Find events for tomorrow"
```

Server names follow the pattern: `pipedream-{externalUserId}-{appSlug}`

## Environment: Development vs Production

⚠️ **Use Production** for real work:
- Development tokens expire faster and have lower rate limits
- Set in: Pipedream tab → Edit credentials → Environment → Production
- The agent Pipedream panel shows a warning when running in development mode

## Security

| Behavior | Detail |
|----------|--------|
| **clientId** | Stored in `~/.openclaw/secrets.json` (vault, 0600) |
| **clientSecret** | Stored in `~/.openclaw/secrets.json` (vault, 0600) — never in plaintext config files |
| Non-secret config | `~/.openclaw/workspace/config/pipedream-credentials.json` — projectId, environment, externalUserId only |
| Per-agent config | `~/.openclaw/workspace/config/integrations/pipedream/{agentId}.json` |
| Access tokens (JWT) | Short-lived Bearer token in `mcporter.json` Authorization header — acceptable, refreshed every 45 min |
| mcporter env | `PIPEDREAM_CLIENT_SECRET` is **never** written to mcporter.json |
| External API calls | `api.pipedream.com`, `remote.mcp.pipedream.net` |
| Auto-migration | Existing plaintext credentials.json secrets automatically moved to vault on first gateway start |

## Troubleshooting

**Connected app not showing after OAuth**
→ Click ↻ Refresh — the panel queries the Pipedream API live for connected accounts

**`unknown method: pipedream.connect`**
→ Rebuild and restart gateway: `pnpm build && openclaw gateway restart`

**`No Pipedream credentials configured`**
→ Set up credentials in the global Pipedream tab first

**Development environment warning**
→ Edit credentials in Pipedream tab, change Environment to `production`, save

**Token expired**
→ Set up the 45-minute cron job above, or click Connect again to re-authorize

## Support

- **ClawHub**: [clawhub.ai/skills/pipedream-connect](https://clawhub.ai/skills/pipedream-connect)
- **Pipedream Docs**: [pipedream.com/docs](https://pipedream.com/docs)
- **MCP Apps**: [mcp.pipedream.com](https://mcp.pipedream.com)
- **OpenClaw Discord**: [discord.com/invite/clawd](https://discord.com/invite/clawd)

## Reference Files

| File | Purpose |
|------|---------|
| `reference/pipedream-backend.ts` | Gateway RPC handlers (all pipedream.* methods) |
| `reference/pipedream-views.ts` | Global Pipedream tab UI (Lit) |
| `reference/pipedream-controller.ts` | Global tab state management |
| `reference/agent-pipedream-views.ts` | Per-agent Pipedream panel UI (Agents → Tools → Pipedream) |
| `reference/agent-pipedream-controller.ts` | Per-agent state management |
| `reference/README.md` | Reference file notes |
| `scripts/` | Token refresh and utility scripts |
