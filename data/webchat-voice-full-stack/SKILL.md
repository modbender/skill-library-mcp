---
name: webchat-voice-full-stack
description: >
  One-step full-stack installer for OpenClaw WebChat voice input with local
  speech-to-text. Deploys faster-whisper STT backend plus HTTPS/WSS WebChat
  proxy with mic button in one command. Push-to-Talk (hold to speak) and Toggle
  mode with keyboard shortcuts (Ctrl+Space PTT, Ctrl+Shift+M continuous recording).
  Real-time VU meter, localized UI (English, German, Chinese), interactive
  language selection during install. No recurring API costs, runs fully local
  after initial model download (~1.5 GB). Combines faster-whisper-local-service
  and webchat-voice-proxy.
  Keywords: voice input, microphone, WebChat, speech to text, STT, local
  transcription, whisper, full stack, one-click, voice button, push-to-talk,
  PTT, keyboard shortcut, i18n.
---

# WebChat Voice Full Stack

Meta-installer that orchestrates two standalone skills in the correct order:

1. **`faster-whisper-local-service`** — local STT backend (HTTP on 127.0.0.1:18790)
2. **`webchat-voice-proxy`** — HTTPS/WSS proxy + mic button for WebChat Control UI

## Prerequisites

Both skills must be installed before running this meta-installer:

```bash
clawdhub install faster-whisper-local-service
clawdhub install webchat-voice-proxy
```

Additionally required on the system:
- Python 3.10+
- `gst-launch-1.0` (GStreamer, from OS packages)
- Internet access on first run (model download ~1.5 GB for `medium`)

## Deploy

```bash
bash scripts/deploy.sh
```

Optional overrides (passed through to downstream scripts):

```bash
VOICE_HOST=10.0.0.42 VOICE_HTTPS_PORT=8443 TRANSCRIBE_PORT=18790 WHISPER_LANGUAGE=auto bash scripts/deploy.sh
```

## What this does (via downstream scripts)

This skill does **not** contain deployment logic itself. It calls `deploy.sh` from each sub-skill. Here is what those scripts do:

### faster-whisper-local-service deploys:
- Creates Python venv at `$WORKSPACE/.venv-faster-whisper/`
- Installs `faster-whisper==1.1.1` via pip
- Writes `transcribe-server.py` to `$WORKSPACE/voice-input/`
- Creates + enables systemd user service `openclaw-transcribe.service`
- Downloads model weights from Hugging Face on first run (~1.5 GB for medium)

### webchat-voice-proxy deploys:
- Copies `voice-input.js` and `https-server.py` to `$WORKSPACE/voice-input/`
- Injects `<script>` tag into Control UI `index.html`
- Adds HTTPS origin to `gateway.controlUi.allowedOrigins` in `openclaw.json`
- Creates + enables systemd user service `openclaw-voice-https.service`
- Installs gateway startup hook at `~/.openclaw/hooks/voice-input-inject/`
- Auto-generates self-signed TLS cert on first run

For full details, security notes, and uninstall instructions, see each skill's SKILL.md.

## Verify

```bash
bash scripts/status.sh
```

## Uninstall

Uninstall each skill separately:

```bash
# Proxy (service, hook, UI injection, gateway config)
bash skills/webchat-voice-proxy/scripts/uninstall.sh

# Backend (service, venv)
systemctl --user stop openclaw-transcribe.service
systemctl --user disable openclaw-transcribe.service
rm -f ~/.config/systemd/user/openclaw-transcribe.service
systemctl --user daemon-reload
```

## Notes

- This meta-skill is a convenience wrapper. All actual logic lives in the two sub-skills.
- Review both sub-skills' scripts before running if you haven't already.
- The `WORKSPACE` and `SKILLS_DIR` paths are configurable via environment variables (default: `~/.openclaw/workspace` and `~/.openclaw/workspace/skills`).
