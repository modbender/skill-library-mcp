---
name: voice-memo
description: "Send native iMessage voice bubbles with ElevenLabs TTS via BlueBubbles. Use when: user asks to send a voice message, wants something spoken aloud, storytelling or summaries requested, or voice delivery would be more engaging than text. Requires ElevenLabs API key and BlueBubbles."
homepage: https://github.com/amzzzzzzz/imessage-voice-memo-skill
metadata: { "openclaw": { "emoji": "🎙️", "platform": "macOS", "requires": { "bins": ["curl", "afconvert"] }, "credentials": ["BLUEBUBBLES_PASSWORD", "ELEVENLABS_API_KEY"] } }
---

# Voice Memo

Send native iMessage voice bubbles (not file attachments) using ElevenLabs TTS and BlueBubbles.

## Quick Start

Run the script with text and recipient:

```bash
scripts/send-voice-memo.sh "Your message here" +14169060839
```

This will:
1. Generate TTS audio via ElevenLabs (Rachel voice by default)
2. Convert to Opus CAF @ 24kHz (iMessage native format)
3. Send as native voice bubble via BlueBubbles

## Requirements

- BlueBubbles running locally with Private API enabled
- ElevenLabs API key (for TTS)
- macOS (for `afconvert` audio conversion)
- Environment variables in `~/.openclaw/.env`:
  ```bash
  ELEVENLABS_API_KEY=your-key-here
  BLUEBUBBLES_PASSWORD=your-password-here
  # Optional overrides:
  ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Rachel (default)
  ELEVENLABS_MODEL_ID=eleven_turbo_v2_5      # Turbo v2.5 (default)
  ```

## The Working Formula

**Critical parameters discovered 2026-02-19:**

| Parameter | Value | Why |
|-----------|-------|-----|
| chatGuid | `any;-;+PHONE` | NOT `iMessage;-;` (causes timeouts) |
| method | `private-api` | Required for native bubble |
| isAudioMessage | `true` | Required |
| Audio format | Opus @ 24kHz in CAF | iMessage native format |
| Pre-convert | Yes | Don't let BlueBubbles convert (wrong codec) |

## Voice Options

**Default voice:** Rachel (ElevenLabs)
- Voice ID: `21m00Tcm4TlvDq8ikWAM`
- Model: `eleven_turbo_v2_5` (fast, natural)
- Cost: ~$0.04 per 30s message

**Expressive tags:**
- `[laughs]` — natural laughter
- `[sighs]` — expressive sigh
- `[excited]` — energetic delivery

Example: `"[excited] Oh my god, it worked!"`

For full voice list and IDs, see [VOICES.md](references/VOICES.md).

## Bidirectional Voice Memos

**Sending (Amz → Amy):**
Use this skill. Native voice bubbles appear with waveform UI.

**Receiving (Amy → Amz):**
BlueBubbles auto-converts incoming voice memos to MP3. OpenClaw transcribes via Whisper. Transcribed text flows into conversation context automatically.

**Memory note:** Incoming voice memo transcriptions flow into conversation context like any text message. They are NOT automatically persisted to memory or files — the agent must explicitly choose to store them, same as any conversation content. If you want to prevent transcriptions from being retained, instruct the agent not to record voice memo content in memory.

## Troubleshooting

**Voice bubble arrives as file attachment:**
- Check `method=private-api` is set
- Verify chatGuid uses `any;-;` prefix (not `iMessage;-;`)
- Check response has `"isAudioMessage": true`

**API times out:**
- Use `any;-;+PHONE` format for chatGuid
- Verify BlueBubbles Private API is enabled
- Restart BlueBubbles if consistently slow

**Audio is 0 seconds / unplayable:**
- Ensure pre-conversion to Opus @ 24kHz
- Don't let BlueBubbles convert (uses wrong codec)
- Verify with: `afinfo output.caf` (should show opus @ 24000 Hz)
