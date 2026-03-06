# Upgrading to v4.0

## What Changed

Version 4.0 introduces **AGENT.md** — all voice assistant prompts (personality, conversational rules, booking flow, greetings, etc.) are now stored in an editable markdown file instead of being hardcoded in TypeScript.

This means you can customize how Amber speaks, greets callers, handles bookings, and more — without touching any code.

## Is It a Breaking Change?

**No.** If you update the runtime without creating an `AGENT.md` file, everything works exactly as before. The runtime falls back to hardcoded prompts when `AGENT.md` is not found.

## Upgrade Steps

### 1. Update the runtime

Pull the latest code or update your ClawHub package:

```bash
git pull origin main
cd runtime && npm install && npm run build
```

### 2. (Optional) Adopt AGENT.md

Copy the included `AGENT.md` to start customizing:

```bash
# AGENT.md is already at the skill root — one level above runtime/
ls AGENT.md
```

Edit it to match your preferences. The runtime loads it automatically on startup.

### 3. Restart

```bash
npm start
# or restart your service/launchd/systemd
```

## AGENT.md Overview

The file uses `## Heading` sections that the runtime parses at startup. Template variables are auto-replaced:

| Variable | Source | Example |
|----------|--------|---------|
| `{{ASSISTANT_NAME}}` | `ASSISTANT_NAME` env var | Amber |
| `{{OPERATOR_NAME}}` | `OPERATOR_NAME` env var | Abe |
| `{{ORG_NAME}}` | `ORG_NAME` env var | Flixxaid |
| `{{DEFAULT_CALENDAR}}` | `DEFAULT_CALENDAR` env var | Abe |
| `{{CALENDAR_REF}}` | Derived from `DEFAULT_CALENDAR` | the Abe calendar |

### Sections

| Section | Controls |
|---------|----------|
| **Personality** | General assistant behavior |
| **Conversational Rules** | Pause-after-questions, breathing room |
| **Style: Friendly** | Tone for standard callers |
| **Style: GenZ** | Tone for GenZ-configured numbers |
| **Inbound Call Instructions** | Full inbound screening behavior |
| **Outbound Call Instructions** | Outbound call behavior |
| **Booking Flow** | Strict 9-step appointment booking process |
| **Inbound Greeting** / **Outbound Greeting** | Opening lines |
| **Silence Followup: Inbound** / **Outbound** | What to say after caller silence |
| **Witty Fillers** | Conversational fillers during tool calls |

### Custom Path

Set `AGENT_MD_PATH` in your `.env` to load from a different location:

```bash
AGENT_MD_PATH=/path/to/my/custom-agent.md
```

## No Changes Required To

- `.env` file — all existing env vars work as before
- Twilio webhook URLs
- Dashboard
- OpenClaw gateway configuration

## Questions?

Open an issue on [GitHub](https://github.com/batthis/amber-openclaw-voice-agent/issues).
