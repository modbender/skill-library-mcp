---
name: maylo-voice-assistant
description: Offline-first voice assistant stack for macOS (Wake word + VAD recording + local Whisper ASR + OpenClaw agent response + offline TTS via macOS say). Use to install, run, and troubleshoot the Maylo voice assistant web UI (cyberpunk dashboard with waveform + push-to-talk over WebSocket) and the always-on wake-word listener (e.g., 'Hey Jarvis') on a Mac mini.
---

# Maylo Voice Assistant (macOS)

## What this skill ships
- A self-contained app under `assets/app/`:
  - Wake word listener (openWakeWord)
  - VAD recording (webrtcvad)
  - Local ASR (faster-whisper)
  - Responder bridge via OpenClaw (`openclaw agent --local`)
  - Offline TTS via `say -v Yelda`
  - Web UI (HTTPS + WebSocket audio streaming)

## Install / Setup (fresh machine)
1) Copy the app to a working directory (recommended):
   - `cp -R <skill>/assets/app ~/maylo-voice-assistant`
2) Create venv + install deps:
   - Run: `scripts/install.sh ~/maylo-voice-assistant`
3) Start the assistant (wake word + responder):
   - Run: `scripts/run_assistant.sh ~/maylo-voice-assistant`
4) Start the HTTPS web UI for phone mic streaming:
   - Run: `scripts/run_web_https.sh ~/maylo-voice-assistant --host 0.0.0.0 --port 8443`
   - On iPhone/Android (same Wi‑Fi): `https://<mac-ip>:8443`
   - Accept the self-signed certificate warning.

## Normal use
- Wake word: say **"Hey Jarvis"** near the Mac mini, then speak your query.
- Web UI: hold the mic button to talk; release to send.

## Troubleshooting (fast)
- Check logs:
  - `recordings/assistant.log`
  - `recordings/responder.log`
  - `recordings/web.log`
- If wake word never triggers, run the minimal tester:
  - `python jarvis_minimal_test.py`
- If the assistant responds to itself (feedback loop):
  - Set HDMI output back to Mac speakers / use headphones.
  - Increase `MAYLO_POST_SAY_INHIBIT_SEC`.

## Security / Privacy
- Do NOT package or commit:
  - OAuth client secrets, tokens, refresh tokens
  - Private certs/keys
- This skill ships **no secrets**. Any tokens/keys must be created on the target machine.
