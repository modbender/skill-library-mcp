---
name: discord-connect-wizard
description: One-machine Discord bot onboarding wizard for OpenClaw. Use when setting up Discord for the first time (create bot, enable intents, invite to a guild, auto-write OpenClaw config, restart gateway, and complete DM pairing). Designed for local Mac/Windows/Linux hosts with a localhost web UI + optional browser automation guidance.
---

# Discord Connect Wizard (OpenClaw)

Run a localhost setup wizard that minimizes manual Discord steps.

Non-negotiable manual steps (Discord security):
- Complete Discord **login / CAPTCHA / 2FA** if prompted
- Copy the Bot Token once
- Click OAuth authorize once
- If DM pairing is needed: enable DMs in server privacy settings (Discord-side)

Wizard does:
- Creates a NEW OpenClaw `channels.discord.accounts.<accountId>` entry (never overwrites existing bots)
- Discovers guild/user IDs
- Writes config via `openclaw config set ... --json`
- Restarts gateway and approves pairing for that account

## Quick start

### Conversation mode (recommended)
Use browser automation + chat prompts. No localhost UI required.

Hard requirement: **agent opens and drives the Developer Portal via browser tool** (do not ask user to open pages or click around).
Resilience rule: if the browser tool times out / disconnects, the agent must **self-recover** (restart gateway/browser as needed) and retry. Only ask the user to click if recovery is impossible.
UX rule: whenever the user must act (login/CAPTCHA/MFA/OAuth authorize), send a screenshot + **ONE** instruction line.
If you need a deterministic step list, run:
```bash
node scripts/conversation-checklist.mjs
```
Then follow `references/conversation-mode.md`.

### Localhost UI mode (optional)
```bash
cd <skill_dir>
node scripts/wizard.mjs
# open http://127.0.0.1:8787
```

## Workflow

### 1) Create bot + enable intents (guided)
User steps you will see on screen:
- **Welcome to the Developer Portal** popup → click **Log In** (or **Create Account**)
- Complete any required **login / CAPTCHA / 2FA** (agent cannot bypass Discord security)

Then (agent-guided):
- Create app → Bot → enable **Message Content Intent** (required)
- Copy Bot Token (paste into wizard)

### 2) Invite bot to your server (guided)
Wizard generates an invite URL with scopes:
- `bot`
- `applications.commands`

and baseline permissions:
- View Channels, Send Messages, Read Message History, Embed Links, Attach Files (+ Add Reactions optional)

You still need to select the server and click **Authorize**.

### 3) Auto-discover IDs (automatic)
- Server ID: fetched from bot guild list after invite (if multiple, pick by name in wizard)
- Your User ID: fetched from your first DM to the bot (“hi”) (no Developer Mode copy/paste)

### 4) Write OpenClaw config + restart (automatic)
Wizard writes:
- `channels.discord.enabled=true`
- `channels.discord.token=...`
- `channels.discord.groupPolicy="allowlist"`
- `channels.discord.guilds.<guildId>.requireMention=false`
- `channels.discord.guilds.<guildId>.users=["<yourUserId>"]`

Then runs `openclaw gateway restart`.

### 5) Pairing (semi-automatic)
- You DM the bot once
- Wizard extracts the pairing code and runs `openclaw pairing approve discord <CODE>`

## Browser automation (optional)
If an OpenClaw agent with the `browser` tool is available, use it to:
- open Developer Portal pages
- scroll to the right sections (Intents, Token, OAuth URL generator)
- capture screenshots of the exact UI that requires user involvement (login/CAPTCHA/2FA, OAuth Authorize)

Do **not** attempt to bypass CAPTCHA/2FA; pause for manual completion.

## Files
- `scripts/wizard.mjs`: localhost wizard server + OpenClaw config writer
- `references/openclaw-discord-baseline.md`: official baseline config + troubleshooting pointers
