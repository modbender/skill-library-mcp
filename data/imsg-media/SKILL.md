---
name: imsg-media
description: Fetch iMessage/Messages.app attachments (voice memos and images) and process them — transcribe audio via Silicon Flow ASR (SenseVoiceSmall), and analyze images via the agent's vision model. Handles the full pipeline from locating the attachment to delivering results. Use when a user sends a voice message or image and you see the placeholder character "￼", or when they say "语音转文字", "看图", "识别图片", "transcribe this".
version: 1.0.1
metadata:
  openclaw:
    emoji: "🎙️"
    requires:
      bins:
        - imsg
      env:
        - SILICON_FLOW_KEY
      platform:
        - darwin
---

# imsg-media

Full iMessage multimedia pipeline:
- 🎙️ **Voice memo → text** via Silicon Flow ASR (SenseVoiceSmall, cloud, no local model)
- 🖼️ **Image → description/OCR** via agent's built-in vision model

## Requirements

### macOS permissions
- **Full Disk Access** must be granted to the process running OpenClaw
- Settings → Privacy & Security → Full Disk Access → add your terminal/app
- Without this, `imsg` cannot read `~/Library/Messages/chat.db` and will return `permissionDenied`

### API key (audio only)
- **Silicon Flow API key** — sign up free at https://siliconflow.cn
- **Long-term use:** add to `~/.openclaw/.env`: `SILICON_FLOW_KEY=sk-...`
- **Quick test / override:** pass `--api-key sk-...` directly to the script
- Image analysis does **not** require this key

### CLI dependency
- `imsg` CLI: `npm install -g imsg`

## Trigger conditions

Activate this skill when:
- Incoming message text contains the attachment placeholder `￼`
- User says "语音转文字", "转写", "识别语音", "transcribe"
- User says "看图", "识别图片", "读图", "OCR", "截图里写的什么"
- User references a photo/audio/file they just sent via iMessage

## Decision flow

```
Attachment detected?
├── Audio (.m4a / .caf / .wav / .mp3)  → transcribe via Silicon Flow ASR
├── Image (.jpg / .png / .heic / .gif) → read with vision model
└── Unknown / not downloaded            → increase --limit or ask user to resend
```

## Workflow

### Step 1 — Get the sender identifier
Always read from the message envelope:
- `[iMessage sender@example.com ...]` → use `sender@example.com`
- `[SMS +1234567890 ...]` → use `+1234567890`
- **Never hardcode an address**

### Step 2 — Fetch the attachment

```bash
# Run from the skill directory
cd ~/.openclaw/skills/imsg-voice-transcribe

python3 scripts/imsg_voice_transcribe.py fetch \
  --identifier "sender@example.com" \
  --limit 50
```

Returns JSON with `file`, `type` (`audio` or `image`), and metadata.

If nothing found, try `--limit 100`.

### Step 3a — Audio: transcribe

```bash
# One-liner (fetch + transcribe)
python3 scripts/imsg_voice_transcribe.py auto \
  --identifier "sender@example.com" \
  --limit 50 --raw

# Or transcribe a specific file
python3 scripts/imsg_voice_transcribe.py transcribe \
  --file /path/to/audio.m4a --raw

# Quick test with explicit API key (no env setup needed)
python3 scripts/imsg_voice_transcribe.py transcribe \
  --file /path/to/audio.m4a --api-key sk-... --raw
```

### Step 3b — Image: analyze

After `fetch` returns an image path (e.g. `{"file": "/path/to/photo.jpg", "type": "image"}`):

```bash
# Example: fetch image from a sender
python3 scripts/imsg_voice_transcribe.py fetch \
  --identifier "sender@example.com" --type image --limit 50
# → {"file": "/Users/.../Messages/Attachments/photo.jpg", "type": "image", ...}
```

Then in the agent:
1. If HEIC/HEIF: convert first → `sips -s format png "input.heic" --out "output.png"`
2. Open with the `read` tool → agent vision model processes it
3. Respond with: what it is, main subject, any text/OCR, notable details

Default image response format:
- **What it is:** photo / screenshot / document
- **Main subject:** 1–2 sentences
- **Text (OCR):** quote key text, or "无明显文字"
- **Details:** 3–5 bullets
- **Follow-up:** ask if they want OCR / table extraction / comparison / etc.

## Supported formats

| Format | Type | Notes |
|--------|------|-------|
| `.m4a` | Audio | Standard iMessage voice memo |
| `.caf` | Audio | Older iOS voice memo (AAC in CAF) |
| `.wav` `.mp3` | Audio | Other sources |
| `.jpg` `.jpeg` `.png` | Image | Standard photos |
| `.heic` `.heif` | Image | iPhone default — convert to PNG first |
| `.gif` | Image | Animated or static |

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `permissionDenied` | No Full Disk Access | Grant FDA in System Settings |
| `SILICON_FLOW_KEY not set` | Missing API key | Add to `~/.openclaw/.env` |
| `No attachments found` | Low limit or iCloud not synced | Increase `--limit`; ask user to resend |
| Request timed out | Network or large file | Retry; check file < 25MB |
| HEIC not displaying | Format not supported by `read` | Convert with `sips` first |
