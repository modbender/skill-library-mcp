---
name: phone-caller
description: "Make AI-powered outbound phone calls using ElevenLabs voice + GPT brain + Twilio. Supports one-way pre-recorded messages AND live two-way conversations where the AI listens, thinks, and responds in real-time. Use when asked to call someone, leave a voice message, schedule a morning call, have an AI make a reservation or appointment, run a voice campaign, or set up interactive phone conversations. Requires Twilio + ElevenLabs credentials. Triggers on 'call', 'phone', 'voice message', 'reserve', 'book by phone', 'schedule a call', 'call and tell them'."
---

# phone-caller

Make AI-powered outbound calls via Twilio, voiced by ElevenLabs, with optional live GPT-powered conversation.

## Two Modes

**Mode 1: One-way message** — Generate audio with ElevenLabs, upload it, play it on a Twilio call. Simple, fast, no server needed.

**Mode 2: Interactive conversation** — Start `server.py`, call with a webhook URL. The AI listens to responses (Twilio STT), thinks (GPT), and speaks back (ElevenLabs) in real-time. Ends with auto-summary sent via iMessage.

## Required Credentials (env vars)

```bash
ELEVENLABS_API_KEY   # from elevenlabs.io
TWILIO_ACCOUNT_SID   # from console.twilio.com (starts with AC...)
TWILIO_AUTH_TOKEN    # from console.twilio.com
TWILIO_PHONE_NUMBER  # your Twilio number e.g. +12025551234
OPENAI_API_KEY       # for interactive mode brain
```

## Mode 1: One-way Call

```bash
python3 scripts/one_way_call.py \
  --to "+13105551234" \
  --text "Hey! Just calling to say good morning." \
  --voice "tyepWYJJwJM9TTFIg5U7"   # optional, defaults to Clara (Australian female)
```

See `references/voices.md` for curated voice IDs.

## Mode 2: Interactive Conversation

### Step 1 — Start a tunnel (needed so Twilio can reach your server)
```bash
npx localtunnel --port 5050 --subdomain my-caller
# Note the URL: https://my-caller.loca.lt
```

### Step 2 — Start the server
```bash
export CLARA_PUBLIC_URL="https://my-caller.loca.lt"
python3 scripts/server.py
```

### Step 3 — Make the call
```bash
python3 scripts/interactive_call.py \
  --to "+13105551234" \
  --url "https://my-caller.loca.lt" \
  --persona "You are calling a restaurant to book a table for 2 at 8pm tonight." \
  --opening "Hi! I'd like to make a reservation for two people this evening around 8pm. Do you have availability?"
```

When the call ends, a GPT-generated summary is automatically sent via iMessage to `MASTER_PHONE` env var.

## Scheduling a Call

Use macOS cron for timed calls:
```bash
# Add to crontab — this example calls at 8:45 AM
crontab -e
45 8 24 2 * python3 /path/to/scripts/one_way_call.py --to "+1..." --text "Good morning!" >> /tmp/call.log 2>&1
```

## Voice Selection

- Default: **Clara** `tyepWYJJwJM9TTFIg5U7` — Australian female, warm, clear, professional
- See `references/voices.md` for full curated list with IDs and descriptions

## Key Notes

- **Twilio trial accounts**: Can only call verified numbers. Upgrade or verify numbers at console.twilio.com → Verified Caller IDs
- **Audio hosting**: Scripts use tmpfiles.org for one-off calls (60 min TTL). For scheduled calls, server.py serves audio at `/audio/<file>` via the tunnel
- **localtunnel**: Free, no account needed. ngrok requires a free account + authtoken
- **Interactive mode latency**: ~3-5s per turn (ElevenLabs TTS + GPT + audio upload). Normal for phone conversations
