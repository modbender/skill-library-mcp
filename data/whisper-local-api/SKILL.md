---
name: whisper-local-api
description: Secure, offline, OpenAI-compatible local Whisper ASR endpoint for OpenClaw. Features faster-whisper (large-v3-turbo), built-in privacy with no cloud telemetry, low-RAM usage footprint, and high-accuracy speech-to-text transcription. Perfect for safe and private AI agent voice commands.
---

# Whisper Local API - Secure & Private ASR

Deploy a privacy-first, 100% local speech-to-text service in a deterministic way. This allows OpenClaw to process audio transcriptions safely on your own hardware without ever contacting third-party cloud APIs.

## Key SEO & Security Features

*   **100% Offline & Private:** Your voice data, commands, and transcriptions never leave your host system. Zero cloud dependencies.
*   **Highly Accurate:** Uses the `large-v3-turbo` model via `faster-whisper`, achieving state-of-the-art accuracy even with accents or background noise.
*   **Memory Safe:** Operates around ~400-500MB of RAM, making it extremely lightweight for VPS or low-resource edge servers.
*   **OpenAI API Compatible:** Exposes a strict `/v1/audio/transcriptions` endpoint mimicking OpenAI's JSON format. Compatible natively with any software that supports OpenAI's Whisper API.

## Standard Workflow

1. Install/update runtime:
   ```bash
   bash scripts/bootstrap.sh
   ```
2. Start service:
   ```bash
   bash scripts/start.sh
   ```
3. Validate service health:
   ```bash
   bash scripts/healthcheck.sh
   ```
4. (Optional) Run a smoke transcription test with a local audio file:
   ```bash
   bash scripts/smoke-test.sh /path/to/test-speech.mp3
   ```

## Repo Location

Default install/update path used by scripts:
*   `~/whisper-local-api`

Override with env var before running scripts:
```bash
WHISPER_DIR=/custom/path bash scripts/bootstrap.sh
```

## OpenClaw Integration Notes

After the healthcheck passes, use the secure local endpoint:
*   URL: `http://localhost:9000`
*   Endpoint: `/v1/audio/transcriptions`

No authentication tokens are passed over the network.

## Safety Rules

*   Ask before any package-manager operations.
*   The API securely binds locally to `0.0.0.0`. If exposing to the public internet, deploy behind a secure reverse proxy (like Nginx) and enforce HTTPS + Basic Auth.
*   This service will safely auto-fallback memory allocation modes (`float16` -> `int8`) to prevent CPU crashes.
