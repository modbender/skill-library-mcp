# ElevenLabs STT for OpenClaw

A clean, local OpenClaw skill that transcribes audio with ElevenLabs Speech‑to‑Text (Scribe v2). It supports diarization, audio‑event tagging, JSON output, and optional webhook‑based async processing so users can choose how they want to run it.

---

## ✨ Features

- **Scribe v2** transcription (default model)
- **Speaker diarization** (`--diarize`)
- **Audio event tags** (`--events`) — e.g., `[laughing]`, `[chuckles]`
- **Word‑level JSON output** (`--json`)
- **Language hinting** (`--lang en`, `--lang hu`, etc.)
- **Async webhooks** (`--webhook`, `--webhook-id`, `--webhook-metadata`)
- **Cloud URL input** (`--url https://...`) for hosted files
- **Advanced controls**: timestamps granularity, entity detection, keyterms, multi‑channel
- **Concurrency‑safe** via a filesystem lock (no parallel requests)
- **No .env sourcing** — reads only explicit environment variables

---

## ✅ Requirements

- `curl`
- `jq`
- `python3` (for realtime/live listener)
- `ffmpeg` + `websocat` (for realtime/live listener)
- ElevenLabs API key set in environment:

```bash
export ELEVENLABS_API_KEY="sk_..."
export ALLOW_LOCAL_FILE=true   # required to transcribe local files
```

---

## 🚀 Usage

From inside the skill folder:

```bash
# Basic transcription (local file)
ALLOW_LOCAL_FILE=true scripts/transcribe.sh /path/to/audio.ogg

# Diarization + language hint
ALLOW_LOCAL_FILE=true scripts/transcribe.sh /path/to/audio.ogg --diarize --lang en

# JSON output with word timings
ALLOW_LOCAL_FILE=true scripts/transcribe.sh /path/to/audio.ogg --json

# Audio‑event tagging
ALLOW_LOCAL_FILE=true scripts/transcribe.sh /path/to/audio.ogg --events
```

### Model override
The valid Speech‑to‑Text models are:

- `scribe_v1`
- `scribe_v1_experimental`
- `scribe_v2` (default)

Example:

```bash
scripts/transcribe.sh /path/to/audio.ogg --model scribe_v1_experimental
```

---

## 🛰️ Webhooks (Async)

Use webhooks if you want the job to run asynchronously and receive results later. This is ideal for longer files or when you don’t want to block the CLI while transcription runs.

```bash
scripts/transcribe.sh /path/to/audio.ogg --webhook
scripts/transcribe.sh /path/to/audio.ogg --webhook --webhook-id abc123 \
  --webhook-metadata '{"job":"call-001","owner":"dan"}'
```

### Quick test (Beeceptor)

1. Create a Beeceptor endpoint (or any HTTPS webhook URL).
2. Add it in ElevenLabs → Webhooks and enable **Transcription completed**.
3. Copy the **Webhook ID** from ElevenLabs.
4. Run:

```bash
scripts/transcribe.sh /path/to/audio.ogg --webhook --webhook-id <ID> \
  --webhook-metadata '{"test":"beeceptor"}'
```

You’ll see the payload arrive in Beeceptor within ~1–2 minutes.

---

## ☁️ Cloud URL Input

Transcribe from a public HTTPS URL instead of uploading a file:

```bash
scripts/transcribe.sh --url https://example.com/audio.mp3 --lang en
```

---

## 🔧 Advanced Flags

```bash
--timestamps none|word|character   # word is default
--num-speakers N                   # 1–32
--diarization-threshold X          # 0–1
--use-multi-channel                # split multi‑channel audio
--entity-detection MODE            # e.g. all|pii|phi|pci|offensive_language
--keyterms "a,b,c"                  # bias key terms
--enable-logging true|false        # default true
```

---

## 🔒 Concurrency Safety

The script uses a lock to prevent parallel requests. If you see:

```
Error: Another transcription is currently running. Please wait a moment.
```

…just wait for the prior request to finish and retry.

---

## Troubleshooting

- **422 Invalid model** → use only the Scribe models above.
- **429 Too Many Requests** → you hit rate limits; wait or reduce usage.
- **503 Service Unavailable** → ElevenLabs outage; retry later.

---

## Files

- `SKILL.md` — OpenClaw skill manifest
- `scripts/transcribe.sh` — transcription CLI

---

## ⚡ Realtime Streaming (WebSocket)

Two realtime options are included:

### 1) File streamer

`realtime.sh` converts any audio file to 16k mono PCM, chunks it, and streams it to ElevenLabs over WebSocket using `scribe_v2_realtime`.

```bash
brew install ffmpeg websocat
scripts/realtime.sh /path/to/audio.ogg
```

### 2) Live listener (mic)

`live_listen.sh` streams your **microphone** into ElevenLabs realtime STT and can **speak back** using TTS. It supports **toggle** (press key to start/stop) or **always‑on**. Toggle mode now runs a separate streaming process for stability.

```bash
brew install ffmpeg websocat

# Always-on, ElevenLabs TTS response
scripts/live_listen.sh --mode always --tts elevenlabs

# Toggle mode, macOS say() voice
scripts/live_listen.sh --mode toggle --tts say --key Q
```

Optional response hook:
```bash
# Run a custom command on each final transcript
scripts/live_listen.sh --mode toggle --on-transcript 'echo "$TEXT"'
```

Options:
- `--mode always|push`
- `--tts elevenlabs|say|none`
- `--device :0` (macOS avfoundation device)
- `--lang en` (optional language hint)
- `--voice-id <ID>` (ElevenLabs voice ID)
