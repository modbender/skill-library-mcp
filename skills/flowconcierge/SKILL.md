---
name: FlowConcierge
description: "AI phone receptionist for any business. Point it at your website and it scrapes your content, builds a knowledge base, spins up a VAPI voice assistant, connects a Twilio phone number, and logs every call to HubSpot CRM with optional SMS follow-ups. Free OpenClaw skill from the Flow team."
metadata: {"clawdbot":{"emoji":"🦞"}}
---

# FlowConcierge

**Any business. AI receptionist. Live in hours.**

Point it at your website. It scrapes your content, builds a knowledge base, spins up a VAPI voice assistant, auto-buys a phone number, and logs every call to HubSpot CRM — with optional SMS follow-ups to every caller.

Free from the Flow team. 🦞

## Prerequisites

You need accounts on (all have free/trial tiers):
- **VAPI** — AI voice agent ([vapi.ai](https://vapi.ai))
- **Twilio** — Phone number + SMS ($15 trial credit, number ~$1/mo)
- **HubSpot** — Free CRM (free forever tier)

## Install

```bash
npx clawhub@latest install windseeker1111/flowconcierge
cd skills/flowconcierge && bash install.sh
```

That's it. `install.sh` installs scrapling, sets up Playwright, and adds a `flowconcierge` command to your shell.

## Quickstart

**Step 1 — Spin up your AI receptionist:**
```bash
python3 scripts/flowconcierge.py setup https://yourbusiness.com \
  --name "My Business" \
  --vapi-key YOUR_VAPI_KEY \
  --twilio-sid YOUR_TWILIO_SID \
  --twilio-token YOUR_TWILIO_TOKEN
```

FlowConcierge will:
1. Scrape your website using a 3-tier Scrapling cascade (punches through Cloudflare)
2. Upload a structured knowledge base to VAPI
3. Create a voice assistant (GPT-4o-mini + ElevenLabs Rachel voice)
4. Auto-buy a local Twilio phone number and connect it

**Step 2 — Start the webhook server (logs calls to HubSpot):**
```bash
python3 scripts/flowconcierge.py webhook \
  --hubspot-key YOUR_HUBSPOT_KEY \
  --twilio-sid YOUR_TWILIO_SID \
  --twilio-token YOUR_TWILIO_TOKEN \
  --twilio-from +15550001234 \
  --business-name "My Business" \
  --sms-followup
```

**Step 3 — Expose your webhook (so VAPI can reach it):**
```bash
ngrok http 8080
# Copy the https:// URL and add --webhook-url to your setup command
```

## Commands

### `setup` — Create a new AI receptionist

```bash
# From a website URL (auto-scrapes)
python3 scripts/flowconcierge.py setup https://mybusiness.com --vapi-key KEY

# From your own knowledge base markdown file
python3 scripts/flowconcierge.py setup --kb my-kb.md --name "Grand Hotel" --vapi-key KEY

# Full setup — auto phone number, preferred area code, webhook URL
python3 scripts/flowconcierge.py setup https://mybusiness.com \
  --name "My Business" \
  --vapi-key KEY \
  --twilio-sid SID \
  --twilio-token TOKEN \
  --area-code 415 \
  --webhook-url https://your-ngrok-url.ngrok.io
```

Options:
- `--name` — Business name (auto-detected from URL if omitted)
- `--vapi-key` — VAPI API key (or set `VAPI_API_KEY` env var)
- `--twilio-sid` / `--twilio-token` — Auto-buy a Twilio phone number
- `--phone` — Connect an existing phone number instead
- `--area-code` — Preferred area code for auto-bought number
- `--webhook-url` — VAPI server URL for call event delivery
- `--kb` — Path to a markdown knowledge base file
- `--lang` — Language code (default: `en`)

### `webhook` — Log calls to HubSpot + send SMS follow-ups

```bash
python3 scripts/flowconcierge.py webhook \
  --port 8080 \
  --hubspot-key KEY \
  --twilio-sid SID \
  --twilio-token TOKEN \
  --twilio-from +15550001234 \
  --business-name "My Business" \
  --sms-followup
```

Listens for VAPI `end-of-call-report` events. On each call:
1. Creates or updates a HubSpot contact from the caller's phone number
2. Logs a call note with the AI-generated summary and transcript
3. Sends an SMS follow-up to the caller (if `--sms-followup` is set)

Environment variable alternatives: `HUBSPOT_API_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`

### `list` — Show active assistants

```bash
python3 scripts/flowconcierge.py list --vapi-key KEY
```

### `delete` — Remove an assistant

```bash
python3 scripts/flowconcierge.py delete asst_abc123 --vapi-key KEY
```

## How It Works

```
Your website URL
    │
    ▼  Scrapling 3-tier cascade (plain HTTP → stealth TLS → full JS)
    │
    ▼  Knowledge base uploaded to VAPI
    │
    ▼  Voice assistant created (GPT-4o-mini + ElevenLabs)
    │
    ▼  Twilio number bought and connected
    │
    ▼  Caller dials in → VAPI answers using your KB
    │
    ▼  Call ends → webhook → HubSpot contact + call note logged
    │
    ▼  SMS follow-up sent to caller automatically
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `VAPI_API_KEY` | VAPI API key |
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_FROM_NUMBER` | Your Twilio number for SMS |
| `HUBSPOT_API_KEY` | HubSpot private app token |

---

*Free from the Flow team 🦞*
