---
name: slybroadcast-voicemail
description: Send Slybroadcast ringless voicemail campaigns from OpenClaw/LLMs using CLI or MCP, including AI voice generation (ElevenLabs or generic HTTP voice API) and campaign controls.
---

# Slybroadcast Voicemail

Use this skill when the user wants to send one or many voicemail drops with Slybroadcast and optionally generate a voice recording from text.

## Prerequisites

Required environment variables:

- `SLYBROADCAST_UID` (or `SLYBROADCAST_EMAIL` fallback)
- `SLYBROADCAST_PASSWORD`
- `SLYBROADCAST_DEFAULT_CALLER_ID` (or pass caller id explicitly)

For local-file or AI-generated audio, also set:

- `SLYBROADCAST_PUBLIC_AUDIO_BASE_URL`
- `SLYBROADCAST_AUDIO_STAGING_DIR`

For ElevenLabs voice generation:

- `ELEVENLABS_API_KEY`
- `ELEVENLABS_TTS_VOICE_ID`

## CLI Commands

Run direct commands:

```bash
npm --workspace @fub/slybroadcast-voicemail run dev:cli -- send --help
```

Common examples:

1. Existing account recording title:

```bash
npm --workspace @fub/slybroadcast-voicemail run dev:cli -- send \
  --to "16173999981,16173999982" \
  --record-audio "My First Voice Message" \
  --caller-id "16173999980" \
  --campaign-name "Follow-up" \
  --schedule-at "now"
```

2. Public audio URL:

```bash
npm --workspace @fub/slybroadcast-voicemail run dev:cli -- send \
  --to "16173999981" \
  --audio-url "https://example.com/voicemail.mp3" \
  --audio-type mp3 \
  --caller-id "16173999980"
```

3. ElevenLabs text-to-voice + send:

```bash
npm --workspace @fub/slybroadcast-voicemail run dev:cli -- send \
  --to "16173999981" \
  --ai-text "Hi, this is your appointment reminder for tomorrow at 3 PM." \
  --ai-provider elevenlabs \
  --caller-id "16173999980"
```

4. Uploaded list on Slybroadcast platform:

```bash
npm --workspace @fub/slybroadcast-voicemail run dev:cli -- send \
  --list-id 94454 \
  --record-audio "My First Voice Message" \
  --caller-id "16173999980"
```

## MCP Tools

Start the MCP server:

```bash
npm --workspace @fub/slybroadcast-voicemail run dev:mcp
```

Tool names:

- `slybroadcast_voicemail_send`
- `slybroadcast_audio_list`
- `slybroadcast_phone_list`
- `slybroadcast_campaign_status`
- `slybroadcast_campaign_results`
- `slybroadcast_campaign_control`
- `slybroadcast_voice_generate`

## Notes

- Slybroadcast API delivery times are interpreted in Eastern Time and use 24-hour format (`YYYY-MM-DD HH:MM:SS`).
- Use one audio source per campaign request: account recording title, system audio file, public URL, local file, or AI text.
- Local and AI-generated files are staged first and must be publicly reachable for Slybroadcast to fetch.
