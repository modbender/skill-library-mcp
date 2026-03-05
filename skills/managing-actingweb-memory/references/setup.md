# Setup Guide

Only needed on first use or after losing credentials. Skip if memory tools are already working.

## Requirements

- **OpenClaw users**: mcporter must be installed (`npm install -g mcporter`)

## Option A — Platform-managed MCP (Claude.ai, ChatGPT, etc.)

Configure the MCP server directly in your AI platform's settings:

- **MCP endpoint:** `https://ai.actingweb.io/mcp`
- **Auth:** OAuth 2.0 (Google sign-in)

Follow your platform's guide for adding an MCP server, then sign in when prompted.

## Option B — mcporter (CLI agents, OpenClaw, custom setups)

**1. Install mcporter**

```bash
npm install -g mcporter
```

**2. Register the ActingWeb server**

```bash
mcporter config add actingweb https://ai.actingweb.io/mcp --auth oauth
```

**3. Authenticate**

```bash
mcporter auth actingweb --log-level debug
```

This opens a browser for Google OAuth. If it succeeds, skip to step 4.

**If authentication fails** (common in headless or GUI-less environments — the session closes before the browser callback completes):

The debug output prints a line like:
> `If the browser did not open, visit https://...`

Copy that URL. Then run the helper script from the skill's `scripts/` directory — it handles the full PKCE flow, starts a local callback server, and writes the token to mcporter's vault automatically:

```bash
bash scripts/manual-oauth.sh
```

Requirements for the script: `curl`, `python3`, `node`, `openssl`, `mcporter`.

**4. Verify**

```bash
mcporter list actingweb --schema
```

Should list the available memory tools. You're done.
