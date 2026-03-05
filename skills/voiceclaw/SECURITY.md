# Security Policy

## Overview

VoiceClaw is a **local-only** voice I/O skill. The operational scripts (`transcribe.sh`, `speak.sh`) make **zero network requests** and send **no data to any external service**.

> The only network activity in this project is a **one-time optional setup step** (downloading the Whisper model from HuggingFace). This is not performed by the skill scripts — it is a manual prerequisite documented in SKILL.md.

---

## Design Principles

| Property | Detail |
|---|---|
| **Local-only inference** | All STT (Whisper) and TTS (Piper) runs on-device using pre-installed binaries |
| **Zero network calls during operation** | `transcribe.sh` and `speak.sh` make no HTTP requests whatsoever |
| **No cloud APIs** | No API keys, no external endpoints, no telemetry |
| **No credential handling** | Scripts accept no passwords, tokens, or secrets |
| **No eval/exec of untrusted input** | Text is piped to Piper via stdin, never shell-evaluated |
| **Input sanitization** | Voice name parameter sanitized to `[a-zA-Z0-9_-]` — prevents path traversal |
| **Temporary file cleanup** | WAV files written to `/tmp` are deleted via bash `trap` on script exit |
| **File existence checks** | All input files and model files verified before use |
| **Configurable paths** | No hardcoded system paths — all paths use env vars with safe defaults |

---

## Binary Requirements (Declared)

| Binary | Source | Network during operation |
|---|---|---|
| `whisper` (whisper.cpp) | Pre-installed local binary | ❌ None |
| `piper` | Pre-installed local binary (`pip install piper-tts`) | ❌ None |
| `ffmpeg` | System package (`apt install ffmpeg`) | ❌ None |

### Model Files

| File | Source | Network during operation |
|---|---|---|
| `ggml-base.en.bin` | Downloaded once at setup (HuggingFace) | ❌ None — static read-only file |
| `*.onnx` voice models | Pre-installed at `$VOICECLAW_VOICES_DIR` | ❌ None — static read-only files |

**Path configuration:**
- Whisper model: `$WHISPER_MODEL` (defaults to `$HOME/.cache/whisper/ggml-base.en.bin`)
- Piper voices: `$VOICECLAW_VOICES_DIR` (defaults to `$HOME/.local/share/piper/voices/`)
- No paths are hardcoded to any specific user or system directory.

---

## Threat Model

### Protected against

- **Path traversal** — voice name input is stripped to `[a-zA-Z0-9_-]`; any `../` or absolute path attempt results in an empty string, which fails the model existence check and exits cleanly
- **Temp file leakage** — `/tmp` WAV files deleted on script EXIT via `trap cleanup EXIT`, even on error
- **Shell injection** — TTS text is passed via stdin to Piper, not interpolated into a shell command

### Out of scope

- Adversarial audio content (e.g., prompt injection via voice) — model-level concern, not script-level
- Host system security (firewall, user permissions) — OpenClaw deployment concern

---

## Reporting a Vulnerability

Open an issue on [GitHub](https://github.com/Asif2BD/VoiceClaw/issues) or contact **M Asif Rahman** directly at [asif.im](https://asif.im).

Please do not disclose security vulnerabilities publicly before they are addressed.
