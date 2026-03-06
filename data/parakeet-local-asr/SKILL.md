---
name: parakeet-local-asr
description: Install and operate local NVIDIA Parakeet ASR for OpenClaw with an OpenAI-compatible transcription API on Ubuntu/Linux and macOS (Intel/Apple Silicon). Use when the user wants private/local speech-to-text, voice transcription setup, ASR troubleshooting, or OpenClaw voice stack configuration with Parakeet (and optional Whisper fallback).
---

# Parakeet Local ASR

Run local Parakeet ASR in a deterministic way.

## Standard workflow

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
   bash scripts/smoke-test.sh /path/to/audio.mp3
   ```

## Repo location

Default install/update path used by scripts:
- `~/parakeet-asr`

Override with env var before running scripts:
```bash
PARAKEET_DIR=/custom/path bash scripts/bootstrap.sh
```

## OpenClaw integration notes

After healthcheck passes, use:
- URL: `http://localhost:9001`
- Endpoint: `/v1/audio/transcriptions`

If a user requests reliability over purity, keep Whisper as fallback provider.

## Safety rules

- Ask before elevated/package-manager operations.
- Do not kill unrelated processes.
- Keep changes scoped to ASR setup unless explicitly asked.
