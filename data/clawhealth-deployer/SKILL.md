---
name: clawhealth-deployer
description: Deploy ClawHealth (Open Wearables) on this machine and connect it to OpenClaw; users then link data via the ClawHealth iOS app (our published SDK). Does not install OpenClaw—user must already have OpenClaw installed.
metadata:
  openclaw:
    requires:
      bins: ["docker", "git", "make", "node"]
    emoji: "❤️"
---

# ClawHealth Deployer

Deploy **ClawHealth** (the Open Wearables backend) on this machine and wire it into OpenClaw’s MCP. Users **link their data** with the **ClawHealth iOS app** (built on our published SDK) so the assistant can answer “How did I sleep last week?” or “What were my steps?” using real health data.

**Prerequisite:** OpenClaw is already installed and running (e.g. via [openclaw.ai](https://openclaw.ai/) or ClawHub). This skill only deploys ClawHealth and connects it to your existing OpenClaw.

## What this skill does

1. Clones the ClawHealth (Open Wearables) repo to `~/ClawHealth` (or `$CLAWHEALTH_INSTALL_DIR`) if not already present.
2. Runs `make deploy-openclaw`: starts Docker (PostgreSQL, Redis, API), runs migrations, seeds sample data, creates an API key, and writes MCP config.
3. Merges the **open-wearables** MCP server into your OpenClaw config (`~/.clawdbot/clawdbot.json5`) so the gateway can talk to ClawHealth.
4. Reminds you to restart the gateway. Users then **link data** by installing the **ClawHealth iOS app** (our published SDK) and syncing HealthKit to this backend—then OpenClaw can query their real data.

## When to use

- User says they want to “deploy ClawHealth”, “install ClawHealth”, “connect health data to OpenClaw”, or “set up Open Wearables for OpenClaw”.
- User already has OpenClaw and wants their assistant to query sleep, activity, or workout data.

## How to run (for the agent)

1. **Check environment:** Ensure `docker`, `git`, `make`, and `node` are available. If Docker isn’t running, prompt the user to start it.
2. **Run the install script** from this skill’s directory:
   ```bash
   bash scripts/install.sh
   ```
   Optional env vars:
   - `CLAWHEALTH_INSTALL_DIR` — where to clone/use the repo (default: `~/ClawHealth`).
   - `CLAWHEALTH_REPO_URL` — repo URL (default: `https://github.com/the-momentum/open-wearables.git`).
3. **Restart OpenClaw gateway** so it loads the new MCP server:
   ```bash
   clawdbot gateway restart
   ```
4. **Tell the user** the two next steps:
   - **Link data:** Install the **ClawHealth iOS app** (we publish it with our SDK) and sign in / point it at this ClawHealth backend to sync HealthKit and wearable data. That’s how real health data gets into ClawHealth so OpenClaw can query it.
   - **Try in chat:** In OpenClaw (e.g. Telegram/WhatsApp), ask “Who can I query health data for?” or “How did I sleep last week?” (sample data is seeded immediately; once they use the iOS app, their own data will appear.)

## Linking data (iOS app + SDK)

We help users **link their data** to the deployed ClawHealth backend via our **iOS app**, which is built with our **published SDK** (HealthKit sync, secure token flow). After deploying with this skill, direct users to:

- **ClawHealth iOS app** — App Store / TestFlight (or link from [ClawHealth website](https://github.com/the-momentum/open-wearables) when available). They install the app, sign in or connect to their ClawHealth instance, and sync; then OpenClaw can query that data.
- **SDK docs** — [Open Wearables Sync SDK](https://docs.openwearables.io/sdk) and [Flutter SDK (iOS)](https://docs.openwearables.io/sdk/flutter) for developers who embed the same sync in their own apps.

## If the user already has ClawHealth running elsewhere

They can add the MCP server manually: run `make deploy-openclaw` inside their ClawHealth repo to get the config snippet, then merge the printed `mcp.servers["open-wearables"]` block into `~/.clawdbot/clawdbot.json5`. Or they can use the same install script with `CLAWHEALTH_INSTALL_DIR` pointing at their existing clone.

## Links

- [ClawHealth / Open Wearables repo](https://github.com/the-momentum/open-wearables)
- [Sync SDK & iOS (Flutter SDK)](https://docs.openwearables.io/sdk) — how the iOS app links data
- [OpenClaw](https://openclaw.ai/)
- [ClawHub](https://clawhub.ai/)
