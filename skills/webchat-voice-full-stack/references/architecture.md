# Architecture

Meta-skill orchestration order:

1. `faster-whisper-local-service`
   - Creates local STT endpoint on `127.0.0.1:18790/transcribe`
2. `webchat-voice-proxy`
   - Injects UI voice script
   - Starts HTTPS/WSS proxy on `:8443`
   - Adds gateway allowed origin

Rationale:
- Backend first avoids proxy/UI working without transcription.
- Keeps each component independently maintainable and reusable.
