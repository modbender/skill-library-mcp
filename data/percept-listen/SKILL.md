---
name: percept-listen
description: Ambient audio capture and transcription for OpenClaw agents via
  wearable devices.
---

# percept-listen

Ambient audio capture and transcription for OpenClaw agents via wearable devices.

## What it does

Connects a wearable microphone (Omi pendant or Apple Watch) to your OpenClaw agent. Audio is transcribed locally and streamed as structured conversation data — speaker-tagged, timestamped, and searchable.

## When to use

- User wants their agent to hear ambient conversations
- User asks to "start listening" or "turn on the mic"
- User mentions Omi pendant, wearable, or ambient audio

## Requirements

- **Percept server** running locally (`pip install getpercept && percept start`)
- **Omi pendant** paired via phone, OR Apple Watch with Percept app
- **Webhook** configured: Omi app → Settings → Webhooks → `https://<your-tunnel>/webhook/transcript`

## Setup

```bash
# Install Percept
pip install getpercept

# Start the receiver (default port 8900)
percept start

# Or run directly
PYTHONPATH=. python -m uvicorn src.receiver:app --host 0.0.0.0 --port 8900
```

Configure a tunnel (Cloudflare, ngrok, Tailscale) so Omi can reach your local server.

## How it works

1. Omi pendant captures audio → phone does STT → sends transcript segments via webhook
2. Percept receiver processes segments into conversations
3. Conversations are stored in local SQLite with FTS5 full-text search
4. All processing stays local — no audio leaves your machine

## Data locations

- **SQLite DB:** `percept/data/percept.db`
- **Live transcript:** `/tmp/percept-live.txt`
- **Conversations:** `percept/data/conversations/`

## Configuration

Wake words, speaker names, and all settings are managed via the Percept dashboard (port 8960) or directly in the SQLite database.

## Links

- **GitHub:** https://github.com/GetPercept/percept
- **Docs:** https://github.com/GetPercept/percept/docs
