# FlowConcierge 🦞

**Any business. AI receptionist. Live in hours.**

Point it at your website. It scrapes your content, builds a knowledge base, spins up a VAPI voice assistant, auto-buys a phone number via Twilio, and logs every call to HubSpot CRM with optional SMS follow-ups.

Free OpenClaw skill from the Flow team.

---

## Prerequisites

You need accounts on (all have free/trial tiers):

| Service | What it does | Get started |
|---------|-------------|-------------|
| **VAPI** | AI voice agent | [vapi.ai](https://vapi.ai) |
| **Twilio** | Phone number + SMS | [twilio.com](https://twilio.com) — $15 trial credit |
| **HubSpot** | Free CRM | [hubspot.com](https://hubspot.com) — free forever |

---

## Install

```bash
npx clawhub@latest install windseeker1111/flowconcierge
cd skills/flowconcierge && bash install.sh
```

`install.sh` handles everything: scrapling, Playwright browsers, and adds a `flowconcierge` command to your shell. Open a new terminal after it runs.

---

## Quickstart

**Step 1 — Set up your AI receptionist:**
```bash
flowconcierge setup https://yourbusiness.com \
  --name "My Business" \
  --vapi-key YOUR_VAPI_KEY \
  --twilio-sid YOUR_TWILIO_SID \
  --twilio-token YOUR_TWILIO_TOKEN
```

That's it. FlowConcierge will:
- Scrape your website (3-tier Scrapling cascade — punches through Cloudflare)
- Upload a knowledge base to VAPI
- Create a voice assistant with a warm professional voice
- Auto-buy a local Twilio phone number and connect it

**Step 2 — Start the webhook server (to log calls to HubSpot):**
```bash
flowconcierge webhook \
  --hubspot-key YOUR_HUBSPOT_KEY \
  --twilio-sid YOUR_TWILIO_SID \
  --twilio-token YOUR_TWILIO_TOKEN \
  --twilio-from +15550001234 \
  --business-name "My Business" \
  --sms-followup
```

**Step 3 — Make it public (so VAPI can reach your webhook):**
```bash
ngrok http 8080
# Copy the https URL and add --webhook-url to your setup command
```

---

## Command Reference

### `setup` — Create a new AI receptionist

```bash
# From a website URL (auto-scrapes)
flowconcierge setup https://mybusiness.com --vapi-key KEY

# From your own knowledge base file
flowconcierge setup --kb my-kb.md --name "Grand Hotel" --vapi-key KEY

# Full setup with auto phone number + preferred area code
flowconcierge setup https://mybusiness.com \
  --name "My Business" \
  --vapi-key KEY \
  --twilio-sid SID \
  --twilio-token TOKEN \
  --area-code 415 \
  --webhook-url https://your-ngrok-url.ngrok.io
```

Options:
- `--name` — Business name (auto-detected from URL if not set)
- `--vapi-key` — VAPI API key (or set `VAPI_API_KEY` env var)
- `--twilio-sid` / `--twilio-token` — Auto-buy a phone number
- `--phone` — Connect an existing phone number instead
- `--area-code` — Preferred area code for auto-bought number
- `--webhook-url` — VAPI server URL for call event delivery
- `--kb` — Path to a markdown knowledge base file
- `--lang` — Language code (default: `en`)

---

### `webhook` — Log calls to HubSpot + send SMS follow-ups

```bash
flowconcierge webhook \
  --port 8080 \
  --hubspot-key KEY \
  --twilio-sid SID \
  --twilio-token TOKEN \
  --twilio-from +15550001234 \
  --business-name "My Business" \
  --sms-followup
```

Listens for VAPI `end-of-call-report` events. For each call:
1. Creates/updates a HubSpot contact from the caller's phone number
2. Logs a call note with summary and transcript
3. Sends an SMS follow-up to the caller (if `--sms-followup`)

Environment variables (alternative to flags):
- `HUBSPOT_API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_FROM_NUMBER`

---

### `list` — Show active assistants

```bash
flowconcierge list --vapi-key KEY
```

---

### `delete` — Remove an assistant

```bash
flowconcierge delete asst_abc123 --vapi-key KEY
```

---

## How it works

```
Your website
    │
    ▼ FlowConcierge scrapes it (3-tier cascade)
    │
    ▼ Uploads knowledge base to VAPI
    │
    ▼ Creates voice assistant (GPT-4o-mini + ElevenLabs Rachel)
    │
    ▼ Buys a Twilio phone number and connects it
    │
    ▼ Caller dials in → VAPI answers, uses your KB to respond
    │
    ▼ Call ends → webhook fires → HubSpot contact logged
    │
    ▼ SMS follow-up sent to caller
```

---

*Free from the Flow team 🦞*
