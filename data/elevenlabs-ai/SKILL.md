---
name: elevenlabs-ai
description: "OpenClaw skill for ElevenLabs APIs: text-to-speech,
  speech-to-speech, realtime speech-to-text, voices/models, and dialogue
  workflows."
---


# ElevenLabs API Skill (Advanced)

## Purpose
Provide a production-oriented guide for using ElevenLabs APIs via direct HTTPS (no SDK requirement), with clear auth, safety, and workflow guidance.

## Best fit
- You need text-to-speech or speech-to-speech conversion.
- You want realtime speech-to-text with low latency.
- You prefer direct HTTP calls with predictable outputs.

## Not a fit
- You require a full SDK integration and helpers.
- You need full conversational agents beyond audio I/O.

## Quick orientation
- Read `references/elevenlabs-authentication.md` for API keys and single-use tokens.
- Read `references/elevenlabs-text-to-speech.md` for TTS endpoints and payloads.
- Read `references/elevenlabs-speech-to-speech.md` for voice conversion.
- Read `references/elevenlabs-speech-to-text-realtime.md` for realtime STT WebSocket.
- Read `references/elevenlabs-text-to-dialogue.md` for multi-voice dialogue output.
- Read `references/elevenlabs-voices-models.md` for voice IDs and model discovery.
- Read `references/elevenlabs-safety-and-privacy.md` for zero-retention and safety rules.

## Required inputs
- API key (xi-api-key) or a single-use token when needed.
- Voice IDs and model IDs for your target use case.
- Output format choice (audio codec/sample rate/bitrate).

## Expected output
- A clear workflow plan, endpoint checklist, and operational guardrails.

## Operational notes
- Keep a strict allowlist for downstream destinations of audio output.
- Cache voice IDs and model IDs server-side.
- Keep payloads small and retry with backoff on throttling.

## Security notes
- Never log API keys or tokens.
- Use single-use tokens for client-side access.
