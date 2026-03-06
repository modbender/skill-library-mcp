# ☎️ Amber — Phone-Capable Voice Agent

**A voice sub-agent for [OpenClaw](https://openclaw.ai)** — gives your OpenClaw deployment phone capabilities via a provider-swappable telephony bridge + OpenAI Realtime. Twilio is the default and recommended provider.

[![ClawHub](https://img.shields.io/badge/ClawHub-amber--voice--assistant-blue)](https://clawhub.ai/skills/amber-voice-assistant)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## What is Amber?

Amber is not a standalone voice agent — it operates as an extension of your OpenClaw instance, delegating complex decisions (calendar lookups, contact resolution, approval workflows) back to OpenClaw mid-call via the `ask_openclaw` tool.

### Features

- 🔉 **Inbound call screening** — greeting, message-taking, appointment booking
- 📞 **Outbound calls** — reservations, inquiries, follow-ups with structured call plans
- 🧠 **Brain-in-the-loop** — consults your OpenClaw gateway mid-call for calendar, contacts, preferences
- 👤 **Built-in CRM** — remembers every caller across calls; greets by name, references personal context naturally
- 📊 **Call log dashboard** — browse history, transcripts, captured messages, follow-up tracking
- ⚡ **Launch in minutes** — `npm install`, configure `.env`, `npm start`
- 🔒 **Safety guardrails** — operator approval for outbound calls, payment escalation, consent boundaries
- 🎛️ **Fully configurable** — assistant name, operator info, org name, voice, screening style
- 📝 **AGENT.md** — customize all prompts, greetings, booking flow, and personality in a single editable markdown file (no code changes needed)

## 🆕 What's New

### v5.3.1 — Security Scope Hardening (Feb 2026)

Addressed scanner feedback around instruction scope and credential handling:

- Tightened `ask_openclaw` usage rules to **call-critical, least-privilege actions only**
- Clarified credential hygiene guidance (dedicated Twilio/OpenAI credentials, minimal gateway token scope)
- Added setup-wizard preflight warnings for native build requirements (`better-sqlite3`) to reduce insecure/failed installs

### v5.3.0 — CRM Skill (Feb 2026)

Amber now has memory. Every call — inbound or outbound — is automatically logged to a local SQLite contact database. Callers are greeted by name. Personal context (pet names, recent events, preferences) is captured post-call by an LLM extraction pass and used to personalize future conversations. No configuration required — it works out of the box.

See [CRM skill docs](#-crm--contact-memory) below for details.

---

## Quick Start

```bash
cd runtime && npm install
cp ../references/env.example .env  # fill in your values
npm run build && npm start
```

Point your Twilio voice webhook to `https://<your-domain>/twilio/inbound` — done!

> **Switching providers?** Set `VOICE_PROVIDER=telnyx` (or another supported provider) in your `.env` — no code changes needed. See [SKILL.md](SKILL.md) for details.

## ♻️ Runtime Management — Staying Current After Recompilation

**Important:** Amber's runtime is a long-running Node.js process. It loads `dist/` once at startup. If you recompile (e.g. after a `git pull` and `npm run build`), **the running process will not pick up the changes automatically** — you must restart it.

```bash
# macOS LaunchAgent (recommended)
launchctl kickstart -k gui/$(id -u)/com.jarvis.twilio-bridge

# or manual restart
kill $(pgrep -f 'dist/index.js') && sleep 2 && node dist/index.js
```

### Automatic Restart (Recommended for Persistent Deployments)

Amber includes a `dist-watcher` script that runs in the background and automatically restarts the runtime whenever `dist/` files are newer than the running process. This prevents the "stale runtime" problem entirely.

To enable it, register the provided LaunchAgent:

```bash
cp runtime/scripts/com.jarvis.amber-dist-watcher.plist.example ~/Library/LaunchAgents/com.jarvis.amber-dist-watcher.plist
# Edit the plist to match your username/paths
launchctl load ~/Library/LaunchAgents/com.jarvis.amber-dist-watcher.plist
```

The watcher checks every 60 seconds and logs to `/tmp/amber-dist-watcher.log`.

> **Why this matters:** Skills and the router are loaded fresh at startup. A mismatch between a compiled `dist/skills/` and a hand-edited `handler.js` (or vice versa) will cause silent skill failures that are hard to diagnose. Always restart after any `npm run build`.

## 🔌 Amber Skills — Extensible by Design

Amber ships with a growing library of **Amber Skills** — modular capabilities that plug directly into live voice conversations. Each skill exposes a structured function that Amber can call mid-call, letting you compose powerful voice workflows without touching the bridge code.

Three skills are included out of the box:

### 👤 CRM — Contact Memory

Amber remembers every caller across calls and uses that memory to make every conversation feel personal.

- **Automatic lookup** — at the start of every inbound and outbound call, the runtime looks up the caller by phone number before Amber speaks a single word
- **Personalized greeting** — if the caller is known, Amber opens with their name and naturally references any personal context ("Hey Abe, how's Max doing?")
- **Invisible capture** — during the call, a post-call LLM extraction pass reads the full transcript and enriches the contact record with name, email, company, and `context_notes` — a short running paragraph of personal details worth remembering
- **Symmetric** — works identically for inbound and outbound calls; the number dialed on outbound is the CRM key
- **Local SQLite database** — stored at `~/.config/amber/crm.sqlite` (configurable via `AMBER_CRM_DB_PATH`); no cloud dependency. CRM contact data stays on your machine. Note: voice audio and transcripts are processed by OpenAI Realtime (a cloud service) — see [OpenAI's privacy policy](https://openai.com/policies/privacy-policy).
- **Private number safe** — anonymous/blocked numbers are silently skipped; no record created
- **Backfill-ready** — point the post-call extractor at old transcripts to prime the CRM from day one

> **Native dependency:** The CRM skill uses `better-sqlite3`, which requires native compilation. On macOS, run `sudo xcodebuild -license accept` before `npm install` if you haven't already accepted the Xcode license. On Linux, ensure `build-essential` and `python3` are installed.
>
> **Credential validation scope:** The setup wizard validates credentials only against official provider endpoints (Twilio API and OpenAI API) over HTTPS. It does not send secrets to arbitrary third-party services and does not print full secrets in console output.

### 📅 Calendar

Query the operator's calendar for availability or schedule a new event — all during a live call.

- **Availability lookups** — free/busy slots for today, tomorrow, this week, or any specific date
- **Event creation** — book appointments directly into the operator's calendar from a phone conversation
- **Privacy by default** — callers are only told whether the operator is free or busy; event titles, names, and locations are never disclosed
- Powered by `ical-query` — local-only, zero network latency

### 📬 Log & Forward Message

Let callers leave a message that is automatically saved and forwarded to the operator.

- Captures the caller's message, name, and optional callback number
- **Always saves to the call log first** (audit trail), then delivers via the operator's configured messaging channel
- Confirmation-gated — Amber confirms with the caller before sending
- Delivery destination is operator-configured — callers cannot redirect messages

### Build Your Own Skills

Amber's skill system is designed to grow. Each skill is a self-contained directory with a `SKILL.md` (metadata + function schema) and a `handler.js`. You can:

- **Customize the included skills** to fit your own setup
- **Build new skills** for your use case — CRM lookups, inventory checks, custom notifications, anything callable mid-call
- **Share skills** with the OpenClaw community via [ClawHub](https://clawhub.com)

See [`amber-skills/`](amber-skills/) for examples and the full specification to get started.

> **Note:** Each skill's `handler.js` is reviewed against its declared permissions. When building or installing third-party skills, review the handler source as you would any Node.js module.

---

## What's Included

| Path | Description |
|------|-------------|
| `AGENT.md` | **Editable prompts & personality** — customize without touching code |
| `amber-skills/` | Built-in Amber Skills (calendar, log & forward message) + skill spec |
| `runtime/` | Production-ready voice bridge (Twilio default) + OpenAI Realtime SIP |
| `dashboard/` | Call log web UI with search, filtering, transcripts |
| `scripts/` | Setup quickstart and env validation |
| `references/` | Architecture docs, env template, release checklist |
| `UPGRADING.md` | Migration guide for major version upgrades |

## Call Log Dashboard

Browse call history, transcripts, and captured messages in a local web UI:

```bash
cd dashboard
node scripts/serve.js       # serves on http://localhost:8787
```

Then open [http://localhost:8787](http://localhost:8787) in your browser.

| Button | Action |
|--------|--------|
| **⬇ (green)** | **Sync** — pull new calls from bridge logs and refresh data |
| **↻ (blue)** | Reload existing data from disk (no re-processing) |

> **Tip:** Use the **⬇ Sync** button right after a call ends to immediately pull it into the dashboard without waiting for the background watcher.

The dashboard auto-updates every 30 seconds when the watcher is running (`node scripts/watch.js`).

## Customizing Amber (AGENT.md)

All voice prompts, conversational rules, booking flow, and greetings live in [`AGENT.md`](AGENT.md). Edit this file to change how Amber behaves — no TypeScript required.

Template variables like `{{OPERATOR_NAME}}` and `{{ASSISTANT_NAME}}` are auto-replaced from your `.env` at runtime. See [UPGRADING.md](UPGRADING.md) for full details.

## Documentation

Full documentation is in [SKILL.md](SKILL.md) — including setup guides, environment variables, troubleshooting, and the call log dashboard.

## Support & Contributing

- **Issues & feature requests:** [GitHub Issues](https://github.com/batthis/amber-openclaw-voice-agent/issues)
- **Pull requests welcome** — fork, make changes, submit a PR

## License

[MIT](LICENSE) — Copyright (c) 2026 Abe Batthish
