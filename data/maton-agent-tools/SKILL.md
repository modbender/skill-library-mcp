---
name: maton
description: Connect to SaaS tools via Maton AI. Includes full UI integration for Clawdbot Gateway dashboard. Use when setting up Maton integration, connecting apps (Gmail, Slack, Notion, HubSpot, etc.), or managing OAuth connections.
metadata: {"clawdbot":{"emoji":"🔗","requires":{"clawdbot":">=2026.1.0"},"category":"integrations"}}
---

# Maton AI

Connect your AI agent to SaaS tools via Maton's OAuth connection management. This skill provides:

- **Full UI Dashboard** — Configure API key, view connections, initiate OAuth flows
- **Multi-App Support** — Gmail, Slack, Notion, HubSpot, Jira, Google Workspace, and more
- **Connection Management** — Create, monitor, and delete app connections
- **API Keys Integration** — Maton API key appears in the API Keys tab for easy configuration

## Overview

Maton provides a unified API for connecting to SaaS tools via OAuth. Once connected, you can interact with these tools through Maton's AI capabilities or directly via their API.

## Prerequisites

1. **Maton Account** — Sign up at [maton.ai](https://maton.ai)
2. **API Key** — Get your API key from the Maton dashboard
3. **Clawdbot Gateway** — v2026.1.0 or later with UI enabled

## Quick Start

### Step 1: Get Your API Key

1. Go to [maton.ai](https://maton.ai) and sign in
2. Navigate to Settings → API Keys
3. Create or copy your API key

### Step 2: Configure in Clawdbot UI

**Option A: Via API Keys tab**
1. Open Clawdbot Dashboard → **Settings** → **API Keys**
2. Find "Maton" in the Environment Keys section
3. Enter your API key and click Save

**Option B: Via Maton tab**
1. Open Clawdbot Dashboard → **Tools** → **Maton**
2. Click **Configure**
3. Paste your API key
4. Click **Save**

### Step 3: Connect Apps

1. Go to **Tools** → **Maton**
2. Click **Connect App** and select an app (e.g., Gmail, Slack)
3. Complete the OAuth flow in the popup window
4. Once status shows **ACTIVE**, the connection is ready

## Supported Apps

Maton supports 50+ SaaS applications including:

| Category | Apps |
|----------|------|
| **Google Workspace** | Gmail, Calendar, Docs, Sheets, Drive, Slides, Ads, Analytics |
| **Productivity** | Notion, Airtable, Jira, Calendly |
| **Communication** | Slack, Outlook |
| **CRM** | HubSpot, Apollo |
| **Media** | YouTube |

## API Reference

### Base URL
```
https://ctrl.maton.ai
```

### Authentication
All requests require a Bearer token:
```bash
curl https://ctrl.maton.ai/connections \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/connections` | List all connections |
| POST | `/connections` | Create new connection |
| GET | `/connections/{id}` | Get connection details |
| DELETE | `/connections/{id}` | Delete connection |

### Connection Status

| Status | Description |
|--------|-------------|
| `PENDING` | OAuth flow not completed; `url` contains OAuth link |
| `ACTIVE` | Connection established and ready to use |
| `FAILED` | Connection failed; reconnection required |

## Architecture

### Configuration Storage

The Maton API key is stored in the main Clawdbot config file:

```json
{
  "env": {
    "MATON_API_KEY": "your-api-key-here"
  }
}
```

This integrates with the API Keys tab for centralized key management.

### Backend RPC Methods

| Method | Purpose |
|--------|---------|
| `maton.status` | Get API key status and connection count |
| `maton.save` | Validate and store API key |
| `maton.test` | Test the API key |
| `maton.disconnect` | Remove API key |
| `maton.connections` | List all connections |
| `maton.connect` | Create a new connection (returns OAuth URL) |
| `maton.delete` | Delete a connection |
| `maton.apps` | List supported apps |

### UI Components

| File | Purpose |
|------|---------|
| `maton-backend.ts` | Gateway RPC handlers |
| `maton-controller.ts` | UI state management |
| `maton-views.ts` | Lit HTML templates |

## Installation

See `reference/README.md` for detailed integration instructions.

### Quick Integration

1. Copy backend handler to `src/gateway/server-methods/maton.ts`
2. Copy UI files to `ui/src/ui/views/` and `ui/src/ui/controllers/`
3. Add "maton" tab to navigation
4. Add `MATON_API_KEY` to API keys discovery
5. Rebuild and restart

## UI Features

### Maton Tab (Tools → Maton)
- Connection status with active/pending counts
- API key configuration form
- Connected apps list with status badges
- App picker modal for new connections
- One-click OAuth flow initiation

### API Keys Tab Integration
- Shows "Maton" in Environment Keys section
- Direct input field for API key
- Save/Clear functionality

## Security

| Aspect | Implementation |
|--------|----------------|
| **Key Storage** | Main config file (`~/.clawdbot/clawdbot.json`) |
| **Key Access** | Never exposed to AI agent |
| **OAuth Tokens** | Managed by Maton (automatic refresh) |

**Best practices:**
- Rotate API keys periodically
- Review connected apps regularly
- Disconnect unused connections

## Troubleshooting

### "Unauthorized" error
- Verify your API key is correct
- Check that the key hasn't been revoked
- Regenerate in Maton dashboard if needed

### Connection stuck in PENDING
- OAuth flow wasn't completed
- Try the OAuth URL again
- Delete and recreate if URL expired

### Connection shows FAILED
- OAuth token may have expired
- Delete the connection and create new one

### Maton not in API Keys tab
- Ensure you're on Clawdbot v2026.1.0+
- Refresh the page after gateway restart

## Reference Files

- `reference/maton-backend.ts` — Gateway RPC handlers
- `reference/maton-controller.ts` — UI controller logic  
- `reference/maton-views.ts` — UI rendering (Lit)
- `reference/README.md` — Installation guide

## Support

- **Maton**: [maton.ai](https://maton.ai)
- **ClawdHub**: [clawdhub.com/skills/maton](https://clawdhub.com/skills/maton)
- **Discord**: [discord.com/invite/clawd](https://discord.com/invite/clawd)
