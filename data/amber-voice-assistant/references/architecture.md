# Architecture (Amber Voice Assistant)

## Goal
Provide a phone-call voice assistant that can consult OpenClaw during the call for facts, context, or task specific lookup.

## Core components

1. **Telephony edge (Twilio)**
   - Handles PSTN call leg (inbound/outbound).
2. **Realtime voice runtime**
   - Manages STT/LLM/TTS loop.
3. **Bridge service**
   - Intercepts tool/function calls from realtime model.
   - For `ask_openclaw` requests, forwards question to OpenClaw session/gateway.
4. **OpenClaw brain**
   - Returns concise result for voice playback.

## Typical call flow

1. Call connects.
2. Assistant greets caller.
3. Caller asks question.
4. Voice runtime triggers `ask_openclaw` when needed.
5. Bridge queries OpenClaw (timeout + fallback enforced).
6. Assistant replies with synthesized answer.

## Required behavior

- **Timeouts:** protect call UX from long pauses.
- **Graceful degradation:** if OpenClaw lookup is unavailable, assistant says it cannot verify right now and offers callback/escalation.
- **Safety checks:** outbound call intent, payment/deposit handoff, and consent boundaries.
- **Auditability:** log call IDs, timestamps, and major tool events.

## Known limitations

- “Open tracking” style certainty does not apply here either: call-side model/tool failures can appear as latency or partial answers.
- Latency depends on network, provider load, model selection, and tunnel quality.
- Availability and quality can vary by host machine and plugin/runtime versions.
