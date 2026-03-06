# Changelog

## Unreleased

- Outbound reliability hardening:
  - Switched Twilio AMD to synchronous mode (`machineDetection=Enable`) so `AnsweredBy` is available at `/voice/answer` before bridging audio.
  - Added machine-answer handling that hangs up definite machine/fax detections and applies a short grace pause for `machine_start` to reduce false-positive immediate hangups.
- CLI reliability hardening:
  - `voicecall-rt call/status/active/inspect` now execute through gateway method calls instead of in-process state, preventing `Missing stream token` failures caused by process-local call context.
- Added `voicecall-rt inspect` (CLI and gateway method) to fetch Twilio call metadata and webhook event timeline by SID for debugging (`status`, timestamps, `duration`, `callStatus` transitions, `answeredBy`).
- Hardened webhook call correlation by resolving missing `callId` from `CallSid`, preventing outbound calls from falling back to `unknown`.
- Added structured webhook logs for `/voice/answer`, `/voice/status`, and `/voice/amd` to make answer/hangup sequencing easier to diagnose.
- Moved WebSocket stream auth to a path-based token form (`/voice/realtime-stream/:callId/:token`) with query-parameter fallback.
- Fixed webhook callback responses for `/voice/status` and `/voice/amd` to include `Content-Type`, preventing Twilio callback delivery errors.

## 0.1.2 (2026-02-16)

- Security hardening for `publicUrl`: now requires HTTPS origin-only URLs and blocks localhost/private/internal hosts.
- Twilio webhook authentication hardened: signed headers are now required on POST webhook routes.
- Prompt safety upgraded: added non-overridable legal/safety guardrails, prompt sanitization/truncation, and removed deceptive identity directives.
- Privacy hardening for local artifacts: call logs/debug recordings now use restrictive filesystem permissions.
- Packaging metadata cleanup: removed incorrect install metadata that implied the package creates a `bun` binary.

## 0.1.0 (2026-02-14)

- Initial release
- OpenAI Realtime API integration for speech-to-speech calls
- Twilio WebSocket media stream bridge
- "Listen first" outbound call behavior
- Intent-based system prompts (restaurant, appointment, price inquiry, general, custom)
- DTMF tone generation for IVR navigation
- Call state management and transcript persistence
- Debug mode with call recording and verbose logging
- Built-in status checker for setup verification
