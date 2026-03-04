---
name: zapier-mcp
description: Connect 8,000+ apps via Zapier MCP. Includes full UI integration for Clawdbot Gateway dashboard. Use when setting up Zapier integration, connecting apps, or using Zapier tools via mcporter.
metadata: {"clawdbot":{"emoji":"⚡","requires":{"bins":["mcporter"],"clawdbot":">=2026.1.0"},"category":"integrations"}}
---

# Zapier MCP

Connect your AI agent to 8,000+ apps via Zapier's MCP (Model Context Protocol) integration. This skill provides:

- **Full UI Dashboard** — Configure your MCP URL, test connections, browse available tools
- **No OAuth Complexity** — Zapier handles all authentication flows
- **MCP Integration** — Tools are accessible via mcporter

## Overview

Zapier MCP exposes your configured Zapier actions as tools your agent can call. Unlike Pipedream (which requires OAuth token management), Zapier MCP uses a simple URL-based authentication — just paste your MCP URL and you're connected.

## Prerequisites

1. **Zapier Account** — Sign up at [zapier.com](https://zapier.com)
2. **mcporter** — MCP tool runner (`npm install -g mcporter`)
3. **Clawdbot Gateway** — v2026.1.0 or later with UI enabled

## Quick Start

### Step 1: Get Your Zapier MCP URL

1. Go to [zapier.com/mcp](https://zapier.com/mcp) and sign in
2. Configure which actions to expose (e.g., "Send Slack message", "Create Google Sheet row")
3. Copy your personalized MCP URL (looks like `https://actions.zapier.com/mcp/...`)

### Step 2: Configure in Clawdbot UI

1. Open Clawdbot Dashboard → **Tools** → **Zapier**
2. Click **Configure**
3. Paste your MCP URL
4. Click **Save**

That's it! Zapier will validate the URL and show how many tools are available.

### Step 3: Use Your Tools

Once connected, tools are available via mcporter:

```bash
# List available tools
mcporter list zapier-mcp --schema

# Call a tool
mcporter call zapier-mcp.<tool_name> --args '{"instructions": "your request"}'
```

## Usage Patterns

### The `instructions` Parameter

Every Zapier tool accepts an `instructions` parameter. Zapier's AI interprets this to fill in missing parameters:

```bash
# ❌ Vague - may prompt for clarification
mcporter call zapier-mcp.slack_send_message \
  --args '{"instructions": "Send a message"}'

# ✅ Specific - AI can resolve parameters
mcporter call zapier-mcp.slack_send_message \
  --args '{"instructions": "Send \"Hello team!\" to the #general channel"}'
```

### The `output_hint` Parameter

Control what data is returned:

```bash
mcporter call zapier-mcp.google_sheets_find_row \
  --args '{
    "instructions": "Find row where email is bob@example.com",
    "output_hint": "name, email, phone number"
  }'
```

### Common Tool Patterns

```bash
# Slack
mcporter call zapier-mcp.slack_send_message \
  --args '{"instructions": "Send \"Build complete!\" to #deployments"}'

# Gmail
mcporter call zapier-mcp.gmail_send_email \
  --args '{"instructions": "Send email to bob@example.com with subject \"Meeting\" and body \"See you at 3pm\""}'

# Google Sheets
mcporter call zapier-mcp.google_sheets_create_row \
  --args '{"instructions": "Add row with Name=John, Email=john@example.com to Sales Leads spreadsheet"}'

# Notion
mcporter call zapier-mcp.notion_create_page \
  --args '{"instructions": "Create page titled \"Meeting Notes\" in the Team Wiki database"}'

# Calendar
mcporter call zapier-mcp.google_calendar_create_event \
  --args '{"instructions": "Create meeting \"Team Standup\" tomorrow at 10am for 30 minutes"}'
```

## Architecture

### How It Works

1. You configure actions in Zapier's MCP dashboard
2. Zapier generates a unique MCP URL for your account
3. Clawdbot stores the URL in mcporter config
4. When you call a tool, mcporter sends a JSON-RPC request to Zapier
5. Zapier executes the action and returns results

### Files Modified

| Location | Purpose |
|----------|---------|
| `~/clawd/config/mcporter.json` | MCP server configuration with Zapier URL |

### Backend Endpoints

The skill uses these gateway RPC methods:

| Method | Purpose |
|--------|---------|
| `zapier.status` | Get connection status and tool count |
| `zapier.save` | Validate and store MCP URL |
| `zapier.test` | Test the connection |
| `zapier.disconnect` | Remove Zapier from mcporter config |
| `zapier.tools` | List all available tools |

### SSE Response Format

Zapier MCP uses Server-Sent Events format:

```
event: message
data: {"result":{"tools":[...]},"jsonrpc":"2.0","id":1}
```

The backend automatically parses this format.

## UI Features

The Zapier page in Clawdbot dashboard provides:

- **Connection Status** — Shows if configured and tool count
- **MCP URL Configuration** — Paste and validate your URL
- **Test Connection** — Verify the URL works
- **Tool Browser** — Expandable groups showing all available tools by app

### Tool Grouping

Tools are automatically grouped by app:
- QuickBooks Online (47 tools)
- Google Sheets (12 tools)
- Slack (8 tools)
- etc.

## Comparison: Zapier vs Pipedream

| Feature | Zapier MCP | Pipedream Connect |
|---------|------------|-------------------|
| Setup | Paste URL | OAuth + credentials |
| Token refresh | Not needed | Every 45 minutes |
| Apps | 8,000+ | 2,000+ |
| Cost | Zapier subscription | Pipedream subscription |
| Complexity | Simple | More control |

**Use Zapier when:** You want simple setup and already use Zapier.

**Use Pipedream when:** You need fine-grained OAuth control or prefer Pipedream's pricing.

## Troubleshooting

### "Connection test failed"
- Verify the URL is correct (should start with `https://actions.zapier.com/mcp/`)
- Check that you've configured at least one action in Zapier's MCP dashboard
- Try regenerating the MCP URL in Zapier

### "No tools available"
- Go to [zapier.com/mcp](https://zapier.com/mcp) and add some actions
- Click "Refresh" in the Clawdbot UI after adding actions

### "followUpQuestion" in response
- Zapier needs more information. Be more specific in your `instructions` parameter.
- Example: Instead of "find customer", use "find customer named Acme Corp"

### Tool not found
- Run `mcporter list zapier-mcp` to see available tools
- Tool names use underscores: `quickbooks_online_find_customer`
- You may need to add the action in Zapier's MCP configuration

## Adding App-Specific Skills

Once Zapier MCP is connected, you can create app-specific skills for commonly used integrations. See:

- `zapier-quickbooks` — QuickBooks Online tools with detailed parameter documentation

These skills provide deeper documentation for specific apps while using the same underlying Zapier MCP connection.

## Reference Files

This skill includes reference implementations:

- `reference/zapier-backend.ts` — Gateway RPC handlers
- `reference/zapier-controller.ts` — UI controller logic
- `reference/zapier-views.ts` — UI rendering (Lit)

These are for reference when building custom integrations or debugging.

## Security Considerations

| Behavior | Description |
|----------|-------------|
| **URL contains auth** | Your MCP URL includes authentication — treat it like a password |
| **Stored in config** | URL saved to `~/clawd/config/mcporter.json` |
| **External API calls** | Calls `actions.zapier.com` |

**Best practices:**
- Don't share your MCP URL publicly
- Regenerate the URL if compromised (in Zapier dashboard)
- Review which actions are exposed in Zapier's MCP settings

## Support

- **ClawdHub**: [clawdhub.com/skills/zapier-mcp](https://clawdhub.com/skills/zapier-mcp)
- **Zapier MCP**: [zapier.com/mcp](https://zapier.com/mcp)
- **Zapier Help**: [help.zapier.com](https://help.zapier.com)
- **Clawdbot Discord**: [discord.com/invite/clawd](https://discord.com/invite/clawd)
