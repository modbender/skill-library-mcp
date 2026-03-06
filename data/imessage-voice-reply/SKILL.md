---
name: imessage-voice-reply
version: 1.0.1
description: Send voice message replies in iMessage using local Kokoro-ONNX TTS. Generates native iMessage voice bubbles (CAF/Opus) that play inline with waveform — not file attachments. Use when receiving a voice message in iMessage and wanting to reply with voice, enabling voice-to-voice iMessage conversations, or sending audio responses. Zero cost — all TTS runs locally. Requires BlueBubbles channel configured in OpenClaw.
---

# iMessage Voice Reply

Generate and send native iMessage voice messages using local Kokoro TTS. Voice messages appear as inline playable bubbles with waveforms — identical to voice messages recorded in Messages.app.

## How It Works

```
Your text response → Kokoro TTS (local) → afconvert (native Apple encoder) → CAF/Opus → BlueBubbles → iMessage voice bubble
```

## Setup

```bash
bash ${baseDir}/scripts/setup.sh
```

Installs: kokoro-onnx, soundfile, numpy. Downloads Kokoro models (~136MB) to `~/.cache/kokoro-onnx/`.

Requires: BlueBubbles channel configured in OpenClaw (`channels.bluebubbles`).

## Generating and Sending a Voice Reply

### Step 1: Generate audio

Write the response text to a temp file, then pass it via `--text-file` to avoid shell injection:

```bash
echo "Your response text here" > /tmp/voice_text.txt
${baseDir}/.venv/bin/python ${baseDir}/scripts/generate_voice_reply.py --text-file /tmp/voice_text.txt --output /tmp/voice_reply.caf
```

Alternatively, pass text directly (ensure proper shell escaping):

```bash
${baseDir}/.venv/bin/python ${baseDir}/scripts/generate_voice_reply.py --text "Your response text here" --output /tmp/voice_reply.caf
```

Options:
- `--voice af_heart` — Kokoro voice (default: af_heart)
- `--speed 1.15` — Playback speed (default: 1.15)
- `--lang en-us` — Language code (default: en-us)

**Security note:** The Python script uses argparse and subprocess.run with list arguments (no shell=True). Input is handled safely within the script. When calling from a shell, prefer `--text-file` for untrusted input to avoid shell metacharacter issues.

### Step 2: Send via BlueBubbles

Use the `message` tool:

```json
{
  "action": "sendAttachment",
  "channel": "bluebubbles",
  "target": "+1XXXXXXXXXX",
  "path": "/tmp/voice_reply.caf",
  "filename": "Audio Message.caf",
  "contentType": "audio/x-caf",
  "asVoice": true
}
```

**Critical parameters for native voice bubble:**
- `filename` must be `"Audio Message.caf"`
- `contentType` must be `"audio/x-caf"`
- `asVoice` must be `true`

All three are required for iMessage to render the message as an inline voice bubble with waveform instead of a file attachment.

## Voice Options

| Language | Female | Male |
|----------|--------|------|
| English | af_heart ⭐ | am_puck |
| Spanish | ef_dora | em_alex |
| French | ff_siwis | — |
| Japanese | jf_alpha | jm_beta |
| Chinese | zf_xiaobei | zm_yunjian |

## When to Reply with Voice

Reply with a voice message when:
- The user sent you a voice message (voice-for-voice)
- The user explicitly asks for an audio/voice response

Always include a text reply alongside the voice message for accessibility.

## Audio Format

- **macOS:** CAF container, Opus codec, 48kHz mono, 32kbps — encoded by Apple's native `afconvert`. Identical to what Messages.app produces.
- **Fallback:** MP3 via ffmpeg (works but may not render as native voice bubble on all iMessage versions).

## Cost

$0. Kokoro TTS runs entirely locally. No API calls for voice generation.

## Troubleshooting

**Voice message shows as file attachment** — Ensure all three parameters are set: `filename="Audio Message.caf"`, `contentType="audio/x-caf"`, `asVoice=true`.

**First word clipped** — The script prepends 150ms silence automatically. If still clipped, increase the silence pad in the script.

**Kokoro model not found** — Run `bash ${baseDir}/scripts/setup.sh`.

**afconvert not found** — Only available on macOS. Script falls back to ffmpeg/MP3 on Linux.
