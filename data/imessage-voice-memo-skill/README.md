# iMessage Voice Memo Skill for OpenClaw

Send **native iMessage voice bubbles** (not file attachments) via BlueBubbles.

![Voice Bubble Demo](https://img.shields.io/badge/Status-Working-brightgreen)
![Platform](https://img.shields.io/badge/Platform-macOS-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- 🎤 **Native voice bubbles** — Appears with waveform, tap to play (not as file attachment)
- 🗣️ **ElevenLabs TTS** — Natural-sounding voice synthesis
- ⚡ **Fast** — End-to-end in ~0.4 seconds
- 🔄 **Bidirectional** — Send and receive voice memos via iMessage

## Requirements

- **macOS** (for `afconvert`)
- **BlueBubbles Server** running locally with **Private API enabled**
- **ElevenLabs API key** (for TTS)

## Installation

1. Clone this repo:
```bash
git clone https://github.com/amzzzzzzz/imessage-voice-memo-skill.git
cd imessage-voice-memo-skill
```

2. Copy the skill to your OpenClaw workspace:
```bash
cp -r . ~/.openclaw/workspace/skills/voice-memo-imessage/
```

3. Add required environment variables to `~/.openclaw/.env`:
```bash
ELEVENLABS_API_KEY=your-key-here
BLUEBUBBLES_PASSWORD=your-bluebubbles-password
```

4. Make the script executable:
```bash
chmod +x ~/.openclaw/workspace/skills/voice-memo-imessage/send-voice-memo.sh
```

## Usage

### Command Line
```bash
./send-voice-memo.sh "Hey, how's it going?" +1234567890
```

### From OpenClaw Agent
The agent can invoke this skill to send voice responses.

## How It Works

### The Working Formula

After extensive debugging, we discovered the exact parameters needed for native voice bubbles:

```bash
# 1. Generate TTS (ElevenLabs)
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}" \
  -d '{"text": "...", "model_id": "eleven_turbo_v2_5"}'

# 2. Convert to Opus CAF @ 24kHz (REQUIRED format for iMessage)
afconvert input.mp3 output.caf -f caff -d opus@24000 -c 1

# 3. Send via BlueBubbles with EXACT parameters
curl -X POST ".../api/v1/message/attachment" \
  --form-string "chatGuid=any;-;+PHONE" \  # NOT iMessage;-; !
  -F "method=private-api" \                 # REQUIRED
  -F "isAudioMessage=true" \                # REQUIRED
  -F "attachment=@output.caf;type=audio/x-caf"
```

### Critical Parameters

| Parameter | Correct Value | Wrong Value | Effect |
|-----------|--------------|-------------|--------|
| chatGuid | `any;-;+PHONE` | `iMessage;-;+PHONE` | Wrong = API timeouts |
| method | `private-api` | omitted or `apple-script` | Wrong = file attachment instead of voice bubble |
| Audio format | Opus @ 24kHz | PCM @ 44.1kHz | Wrong = 0-second unplayable audio |

### Why Pre-Conversion?

BlueBubbles' built-in conversion uses **PCM @ 44.1kHz**, but iMessage voice memos require **Opus @ 24kHz**. Pre-converting with `afconvert` bypasses this issue.

## Performance

| Step | Time | Notes |
|------|------|-------|
| TTS | ~0.25s | ElevenLabs turbo model |
| Convert | ~0.04s | Native macOS afconvert |
| Send | ~0.15s | Local BlueBubbles API |
| **Total** | **~0.4s** | 🚀 |

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ELEVENLABS_API_KEY` | Yes | - | Your ElevenLabs API key |
| `BLUEBUBBLES_PASSWORD` | Yes | - | BlueBubbles server password |
| `ELEVENLABS_VOICE_ID` | No | `21m00Tcm4TlvDq8ikWAM` | Voice ID (default: Rachel) |
| `ELEVENLABS_MODEL_ID` | No | `eleven_turbo_v2_5` | TTS model |
| `BLUEBUBBLES_URL` | No | `http://127.0.0.1:1234` | BlueBubbles server URL |

### Voice Options

Default voice is **Rachel** — a natural, expressive female voice. You can use any ElevenLabs voice by changing `ELEVENLABS_VOICE_ID`.

**Expressive tags** (for emotional delivery):
- `[laughs]` — Natural laughter
- `[sighs]` — Expressive sigh  
- `[excited]` — Energetic delivery

Example: `"[excited] Oh my god, it worked!"`

## Cost

- ~$0.04 per 30-second voice memo (ElevenLabs)
- 10 messages/day ≈ $12/month

## Troubleshooting

### Voice memo arrives as file attachment (not voice bubble)
- Ensure `method=private-api` is set
- Ensure BlueBubbles Private API is enabled and helper is connected
- Check API response for `"isAudioMessage": true`

### API times out
- Use `any;-;+PHONE` format (NOT `iMessage;-;+PHONE`)
- Restart BlueBubbles if consistently slow

### Audio is 0 seconds / unplayable
- Ensure pre-conversion to Opus @ 24kHz
- Verify format: `afinfo output.caf` should show `opus @ 24000 Hz`

## Related

- [BlueBubbles](https://bluebubbles.app) — iMessage bridge for non-Apple devices
- [ElevenLabs](https://elevenlabs.io) — AI voice synthesis
- [OpenClaw](https://github.com/openclaw/openclaw) — AI agent framework

## License

MIT License — see [LICENSE](LICENSE)

## Credits

Developed by Amy & Amz while debugging BlueBubbles voice memos at 4am. 🌙

Special thanks to the BlueBubbles team and the OpenClaw community.
