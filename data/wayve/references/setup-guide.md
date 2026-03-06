# Wayve MCP — Setup Guide

## 1. Install the Skill

Find Wayve on [ClawHub.ai](https://clawhub.ai) and click **Install**, or run:

```bash
clawhub install wayve
```

## 2. Create a Wayve Account

1. Go to [gowayve.com](https://gowayve.com) and sign up
2. Verify your email via the OTP code you receive
3. Go to [gowayve.com/account](https://gowayve.com/account) → **API Keys** section
4. Generate a new key and copy it — it starts with `wk_live_`

## 3. Add Your API Key

Add your key to your OpenClaw secrets file (`~/.openclaw/secrets.json`):

```json
{
  "WAYVE_API_KEY": "wk_live_YOUR_API_KEY"
}
```

The key name must be `WAYVE_API_KEY` — this is the environment variable the MCP server reads at startup.

Then reference it in your OpenClaw config (`~/.openclaw/openclaw.json`):

```json
{
  "skills": {
    "entries": {
      "wayve": {
        "enabled": true,
        "apiKey": { "source": "file", "provider": "filemain", "id": "/WAYVE_API_KEY" }
      }
    }
  }
}
```

This keeps your key in the secrets file (which has restricted permissions) and out of your main config. OpenClaw resolves it at startup and injects it as the `WAYVE_API_KEY` environment variable for the MCP server.

## 4. Connect the MCP Server

You need **Node.js 18+** installed ([nodejs.org](https://nodejs.org)).

Run this in Claude Code:

```
/mcp add wayve -- npx -y @gowayve/wayve@^1.2.5
```

The pinned version (`@^1.2.5`) ensures you get a verified release. The MCP server picks up your `WAYVE_API_KEY` from the OpenClaw config automatically — no need to pass it as an argument.

## 5. Verify

Type `/wayve help` to see all available commands. If the assistant responds with a list of commands and calls `wayve_get_planning_context`, you're all set.

## 6. Get Started

- `/wayve setup` — first-time onboarding (create life buckets, set preferences)
- `/wayve plan` — plan your week
- `/wayve brief` — today's schedule
- `/wayve wrapup` — end-of-week reflection
- `/wayve time audit` — track where your time goes
- `/wayve life audit` — deep life review

## Troubleshooting

**No wayve tools showing up:** Make sure Node.js 18+ is installed (`node --version`) and restart Claude Code after adding the config.

**"Invalid API key":** Keys must start with `wk_live_`. Generate a new one at [gowayve.com/account](https://gowayve.com/account).

**Key not being picked up:** Make sure your key is in `~/.openclaw/secrets.json` under `/wayve/apiKey` and that `~/.openclaw/openclaw.json` has the secret reference under `skills.entries.wayve.apiKey`. Restart OpenClaw after changes.
