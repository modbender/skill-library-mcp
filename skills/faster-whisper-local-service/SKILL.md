---
name: faster-whisper-local-service
description: Local speech-to-text (STT) transcription service for OpenClaw using faster-whisper. Runs as HTTP microservice on localhost for voice input, microphone transcription, and speech recognition. No recurring API costs — after initial model download, runs fully local. Supports WebChat voice input, Telegram voice messages, and any OpenClaw voice workflow. Keywords: STT, speech to text, voice transcription, local transcription, whisper, faster-whisper, offline, microphone, speech recognition, voice input.
---

# Faster Whisper Local Service

Provision a local STT backend used by voice skills.

## What this sets up

- Python venv for faster-whisper
- `transcribe-server.py` HTTP endpoint at `http://127.0.0.1:18790/transcribe`
- systemd user service: `openclaw-transcribe.service`

## Important: Model download on first run

On first startup, faster-whisper downloads model weights from Hugging Face (~1.5 GB for `medium`). This requires internet access and disk space. After the initial download, models are cached locally and the service runs **fully offline**.

| Model | Download size | RAM usage |
|---|---|---|
| tiny | ~75 MB | ~400 MB |
| base | ~150 MB | ~500 MB |
| small | ~500 MB | ~800 MB |
| medium | ~1.5 GB | ~1.4 GB |
| large-v3 | ~3.0 GB | ~3.5 GB |

To pre-download models in an air-gapped environment, see [faster-whisper docs](https://github.com/SYSTRAN/faster-whisper#model-download).

## Security notes

- **gst-launch-1.0**: The service uses GStreamer's `decodebin` to convert incoming audio to WAV. While arguments are passed as a list (no shell injection), processing untrusted/malformed audio files carries inherent risk through GStreamer's media parsers. Ensure `gst-launch-1.0` is installed from your OS vendor's trusted packages.
- **Bind address**: The service binds to `127.0.0.1` only (not exposed externally).
- **CORS**: Restricted to a single origin by default (`https://127.0.0.1:8443`).
- **No credentials**: The skill does not request any API keys or secrets.

## Security and reproducibility defaults

- pinned package install: `faster-whisper==1.1.1` (override via env)
- explicit dependency check for `gst-launch-1.0`
- CORS is restricted to one origin by default: `https://127.0.0.1:8443` (override via env)
- configurable workspace/service paths (no hardcoded user path required)

## Deploy

```bash
bash scripts/deploy.sh
```

With custom settings:

```bash
WORKSPACE=~/.openclaw/workspace \
TRANSCRIBE_PORT=18790 \
WHISPER_MODEL_SIZE=medium \
WHISPER_LANGUAGE=auto \
TRANSCRIBE_ALLOWED_ORIGIN=https://10.0.0.42:8443 \
bash scripts/deploy.sh
```

### Language setting

Default: `auto` (auto-detect language). Set `WHISPER_LANGUAGE=de` for German-only, `en` for English-only, etc. Fixed language is faster and more accurate if you only use one language.

Idempotent: safe to run repeatedly.

## What this skill modifies

| What | Path | Action |
|---|---|---|
| Python venv | `$WORKSPACE/.venv-faster-whisper/` | Creates venv, installs faster-whisper via pip |
| Transcribe server | `$WORKSPACE/voice-input/transcribe-server.py` | Writes server script |
| Systemd service | `~/.config/systemd/user/openclaw-transcribe.service` | Creates + enables persistent service |
| Model cache | `~/.cache/huggingface/` | Downloads model weights on first run |

## Uninstall

```bash
systemctl --user stop openclaw-transcribe.service
systemctl --user disable openclaw-transcribe.service
rm -f ~/.config/systemd/user/openclaw-transcribe.service
systemctl --user daemon-reload
```

Optional full cleanup:

```bash
rm -rf ~/.openclaw/workspace/.venv-faster-whisper
rm -f ~/.openclaw/workspace/voice-input/transcribe-server.py
```

## Verify

```bash
bash scripts/status.sh
```

Expected:
- service `active`
- endpoint responds (HTTP 200/500 acceptable for invalid sample payload)

## Notes

- This skill provides backend transcription only.
- Pair with `webchat-voice-proxy` for browser mic + HTTPS/WSS integration.
- For one-step install, use `webchat-voice-full-stack` (deploys backend + proxy in order).
