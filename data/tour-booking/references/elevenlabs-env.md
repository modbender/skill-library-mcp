# ElevenLabs Environment Variables

Required for live outbound calls:
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_AGENT_ID`

Optional:
- `ELEVENLABS_OUTBOUND_URL`
  - Defaults to `https://api.elevenlabs.io/v1/convai/phone-calls` in this skill.
  - Override if ElevenLabs changes endpoint path or your account uses a different route.

Recommended safety defaults:
- Run dry-run first for every new workflow.
- Allow `--live` only after payload inspection.
