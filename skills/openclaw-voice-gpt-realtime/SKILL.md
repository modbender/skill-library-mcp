---
name: openclaw-voice-gpt-realtime
description: Make real phone calls through your OpenClaw agent via OpenAI's Realtime API. ~200-300ms latency, natural voice, IVR navigation, voicemail detection.
version: 0.1.4
homepage: https://github.com/connorcallison/openclaw-voice-gpt-realtime
metadata:
  openclaw:
    emoji: "\U0001F4DE"
    requires:
      bins:
        - bun
    install:
      - kind: node
        package: openclaw-voice-gpt-realtime
---

# Voice Calls (OpenAI Realtime)

Make real phone calls through your OpenClaw agent. Ask it to book a restaurant, check store hours, schedule an appointment — it dials the number, handles the conversation, and reports back with structured results.

Uses OpenAI's Realtime API for single-model speech-to-speech with ~200-300ms response latency. No separate STT or TTS — one model does it all.

## Setup

This skill requires a Twilio account and an OpenAI API key with Realtime API access.

1. Set your credentials in the plugin config (via OpenClaw settings or `openclaw.json`):
   - `twilio.accountSid` — your Twilio Account SID
   - `twilio.authToken` — your Twilio Auth Token
   - `fromNumber` — a Twilio voice-capable phone number (E.164 format, e.g. `+17075551234`)
   - `openai.apiKey` — your OpenAI API key
   - `publicUrl` — a public HTTPS origin that routes to the plugin's server (port 3335 by default). Must not be localhost/private/internal.

2. Set up a tunnel (Cloudflare Tunnel, ngrok, Tailscale Funnel, etc.) so Twilio can reach the webhook server.

3. Verify setup:
```bash
openclaw voicecall-rt status
```

## Usage

Just tell your agent what to call and why:

> "Call Tony's Pizza at +14155551234 and reserve a table for 4 on Friday at 7pm"

> "Call the barbershop at +14155559876 and book a haircut for Saturday morning"

> "Call +14155550000 and ask if they have the iPhone 16 Pro in stock"

The agent writes a system prompt for the voice AI, dials the number, and the voice AI handles the conversation autonomously — including navigating phone menus (DTMF), detecting voicemail, and reporting the outcome. The plugin wraps prompts with safety guardrails and blocks deceptive identity behavior.

### CLI

```bash
openclaw voicecall-rt call -n +14155551234 -t "Check store hours"
openclaw voicecall-rt status
openclaw voicecall-rt active
```

### Inbound calls

Optionally receive calls by enabling `inbound.enabled` and setting a policy (`open` or `allowlist`). Disabled by default.

## Cost

~$0.31/min total (~$0.06 OpenAI input + ~$0.24 OpenAI output + ~$0.014 Twilio). A typical 5-minute call costs ~$1.55.

## Notes

- The voice AI waits for the callee to speak before talking ("listen first") — no awkward overlap on pickup.
- Server binds to `127.0.0.1` by default. Only exposed via your tunnel.
- Max 5 concurrent calls by default (configurable via `calls.maxConcurrent`).
- Debug mode (`debug: true`) enables call recording, verbose logging, and latency metrics; recordings/transcripts may contain sensitive data.
