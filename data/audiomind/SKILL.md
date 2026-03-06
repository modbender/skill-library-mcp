---
name: audiomind
version: 3.3.0
description: >
  Turn any idea into a finished podcast in one command. AudioMind handles ElevenLabs voice narration (29+ voices), AI background music, and server-side audio mixing — all through a secure backend. Free tier included, no setup required.
metadata:
  openclaw:
    optional_env:
      - AUDIOMIND_BACKEND_URL
      - AUDIOMIND_API_KEY
      - FAL_KEY
    network:
      - audiomind-backend-nine.vercel.app
    operator: wells1137
    privacy_note: >
      User scripts and generated audio are sent to the AudioMind backend
      (audiomind-backend-nine.vercel.app, operated by @wells1137) for TTS and
      mixing. ElevenLabs is called server-side only — the agent never calls
      api.elevenlabs.io directly. For full privacy, self-host the backend from
      github.com/wells1137/audiomind-backend and set AUDIOMIND_BACKEND_URL.
    tags:
      - audio
      - podcast
      - tts
      - voice
      - narration
      - speech
      - music
      - elevenlabs
      - content-creation
      - automation
      - soundscape
      - mixing
      - latest
---

## AudioMind v3: The AI Podcast Studio

AudioMind turns a single sentence into a fully-produced podcast. It handles scripting, ElevenLabs voice narration, AI background music, and server-side audio mixing — all from one Manus command.

**No setup required.** The public shared backend works out of the box. Just install and start creating.

---

### Quick Start

**Install:**
```
clawhub install audiomind
```

**Use immediately (no configuration needed):**
> "Use AudioMind to create a 3-minute podcast about the future of AI agents."

That's it. AudioMind uses the public shared backend by default — 20 free generations per month, no API key required.

---

### Configuration

| Variable | Required | Description |
|---|---|---|
| `AUDIOMIND_BACKEND_URL` | Optional | Your own Vercel backend URL. Defaults to the public shared backend. |
| `AUDIOMIND_API_KEY` | Optional | Pro API key for unlimited generations. Get one at the landing page. |

**Free Tier (default):** 20 generations/month tracked by IP. No configuration needed.

**Pro Tier:** Set `AUDIOMIND_API_KEY` with your Pro key for unlimited access.

**Self-hosted:** Deploy your own backend from [github.com/wells1137/audiomind-backend](https://github.com/wells1137/audiomind-backend) and set `AUDIOMIND_BACKEND_URL` to your instance.

---

### How It Works

When you ask Manus to create a podcast, the agent performs these steps automatically:

1. **Write Script** — The agent uses its built-in LLM to write a structured podcast script based on your topic and desired length.

2. **Generate Narration** — `POST {BACKEND_URL}/api/workflow/generate_tts` with the script. Returns MP3 audio narrated by an ElevenLabs voice.

3. **Generate Music** — `POST {BACKEND_URL}/api/workflow/generate_music` with a mood/style prompt. Returns a background music MP3.

4. **Upload Audio** — The agent uploads both MP3 files using `manus-upload-file` to obtain public URLs for the mixing step.

5. **Mix Final Audio** — `POST {BACKEND_URL}/api/workflow/mix_audio` with `{ narration_url, music_url }`. The backend mixes them with proper levels using ffmpeg and returns the final podcast MP3.

6. **Deliver** — The agent saves and presents the finished podcast to you.

---

### Example Prompts

- *"Create a 5-minute podcast about the history of jazz with a smooth jazz background."*
- *"Make a daily news briefing about AI developments, formal tone, upbeat intro music."*
- *"Generate a meditation podcast, 10 minutes, calm narration, ambient soundscape."*
- *"Produce a tech explainer on quantum computing for a general audience."*

---

### Security

All API keys (ElevenLabs) are stored server-side. The skill file contains zero credentials. This architecture passes VirusTotal and ClawHub security scans. See the [GitHub repo](https://github.com/wells1137/audiomind-backend) for the full backend source code.

---

### Changelog

**v3.3.0** — Removed local `tools/start_server.sh` entirely (not needed in v3 architecture). Declared `FAL_KEY` as optional env. Resolves all OpenClaw metadata inconsistency warnings.

**v3.1.0** — Zero-config install. Public shared backend is now the default. No `AUDIOMIND_BACKEND_URL` setup required for free tier users.

**v3.0.1** — Added `openclaw.requires` metadata to declare env vars and trusted network endpoints. Resolves OpenClaw security scanner warning.

**v3.0.0** — Full architecture rewrite. All commercial logic moved to Vercel backend. ElevenLabs API keys are now server-side only. Passes VirusTotal security scan.
