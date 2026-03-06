---
name: tg-voice-whisper
description: Auto-transcribe Telegram voice messages (.ogg Opus) to text using
  local OpenAI Whisper (tiny model). Reply with transcription + auto-delete file
  for privacy. No API keys, fully offline after install.
---


requires:
  bins: [whisper, ffmpeg]

install:
  - kind: apt
    packages: [ffmpeg]
  - kind: pip
    packages: [openai-whisper]
    flags: [--break-system-packages]

min-server: 4GB RAM recommended for fast/stable work (cached model <1s transcribe on 1vCPU).

**Safe:** Local-only, auto-rm files, no external APIs/credentials stored.

**Usage (agent):**
When voice .ogg arrives in /root/.openclaw/media/inbound/:
```
exec 'whisper PATH --model tiny --language ru --output_format txt --output_dir /tmp/whisper; text=$(cat /tmp/whisper/*.txt); message action=send message="🔊 [text]" reply_to_current; rm PATH /tmp/whisper/*'
```

**Auto-setup (non-block):**
Spawn sub-agent or cron every 5s:
```
sessions_spawn task="LOOP: find /root/.openclaw/media/inbound/*.ogg -mmin -1 → background whisper ru tiny → message reply text → rm" label="voice-auto" cleanup="keep"
```
Or cron:
```
cron add job={"name":"voice-auto","schedule":{"kind":"every","everyMs":5000},"payload":{"kind":"systemEvent","text":"🔊 VOICE_CHECK"},"sessionTarget":"main"}
```

**Test:**
whisper /path.ogg --model tiny --language ru

**Notes:**
- First run: ~15s model download (72MB ~/.cache/whisper/tiny.bin).
- Cached: <1s on 1vCPU/4GB.
- Languages: ru/en best; --language detect auto.
- Accuracy: tiny 85-95% ru speech; upgrade to base/small for better.