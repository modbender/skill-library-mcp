# Speech-to-Text (Realtime)

## WebSocket endpoint
- `wss://api.elevenlabs.io/v1/speech-to-text/realtime`

## Auth
- `xi-api-key` header, or
- `token` query param (single-use token for client-side sessions)

## Required params
- `model_id`

## Notes
- Supports partial and committed transcript events.
- Optional flags: timestamps, language detection, VAD settings.
