# discord-connect-wizard

One-machine Discord bot onboarding wizard for **OpenClaw**.

Goal: turn the full Discord bot onboarding flow into **“only ask the human when absolutely required”**.

- Human-only steps (Discord security): **login / CAPTCHA / MFA / OAuth Authorize**
- Everything else: automated (create app, enable intents, write OpenClaw config, restart gateway, approve pairing)

---

## What this skill does

It helps you:

1. Create a new Discord Application + Bot
2. Enable required privileged intents (especially **Message Content Intent**)
3. Invite the bot to your server via OAuth2
4. Write OpenClaw config under a **new** account (never overwrites existing bots)
5. Restart OpenClaw gateway
6. Complete DM pairing (approve pairing for that specific account)

---

## Recommended: Conversation mode (no localhost UI)

Use this when you have an OpenClaw agent with the **browser** tool available.

### How to start

Just tell your OpenClaw agent something like:

> “Use discord-connect-wizard to connect a new Discord bot. Name it X and invite it to server Y.”

### UX rules (by design)

- The agent drives the Developer Portal end-to-end.
- The agent pauses only for:
  - Discord login / CAPTCHA / MFA
  - OAuth Authorize (select server + click Authorize)
- When you must act, the agent should send:
  - a screenshot
  - **one** instruction line

---

## Optional: Localhost wizard UI

Run a local web wizard if you prefer a step-by-step UI.

```bash
cd skills/discord-connect-wizard
node scripts/wizard.mjs
# open http://127.0.0.1:8787
```

Notes:
- Token is only shown once by Discord. Copy it immediately.
- The wizard writes config using `openclaw config set ... --json`.

---

## Troubleshooting

### OAuth page says “正在打开 Discord APP”
Normal redirect behavior. Wait a few seconds.

### DM to the bot doesn’t work
In the server privacy settings, enable **“Allow direct messages from server members”**, then DM the bot again.

### Pairing approval
Pairing is per account. Always approve pairing for the target accountId only.

---

## Files

- `SKILL.md` — skill entry + usage
- `references/conversation-mode.md` — deterministic conversation-mode flow
- `scripts/conversation-checklist.mjs` — checklist generator
- `scripts/wizard.mjs` — localhost wizard server
