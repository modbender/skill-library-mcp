# Changelog

## [2.0.0] - 2026-02-15

### Added
- **DTMF / IVR navigation** - AI can now navigate automated phone menus (IVR systems) by sending touch-tone digits through the audio stream. When the AI hears "press 1 for ...", it uses the `send_dtmf` tool to press buttons on the keypad — speaking a number out loud does not work, so this is essential for interacting with phone trees.
- **Pure µ-law DTMF tone generation** - No external dependencies; DTMF tones are generated as ITU-standard dual-frequency pairs, encoded to µ-law (8kHz mono), and injected directly into the Twilio media stream.
- **Wait character support** - Use `w` in digit strings (e.g., `1w123#`) to insert 500ms pauses between tone groups, useful for multi-stage IVR inputs.
- **Playback-aware injection** - DTMF tones wait for current AI audio playback to finish (via Twilio mark events) before injecting, preventing tone corruption. Includes a 5-second safety timeout.

## [1.3.0] - 2026-02-14

### Changed
- **Simplified webhook security** - Removed `skipSignatureVerification` and `allowNgrokFreeTier` config options. Twilio signatures are always verified; ngrok URL mismatches are logged but allowed (since URL reconstruction can vary). Self-test requests use a separate internal token.
- **Updated security docs** - SKILL.md now explains how verification actually works instead of scary warnings.

### Fixed
- **Stale call cleanup** - Calls stuck in non-terminal state for >5 minutes are automatically cleaned up on startup. Prevents "Maximum concurrent calls reached" errors after gateway crashes or restarts.

## [1.2.1] - 2026-02-14

### Fixed
- **Pre-flight WebSocket check** - Now tests both HTTP webhook AND WebSocket media stream endpoint before placing calls. Previously, calls could be initiated even if the WebSocket path was unreachable (e.g., ngrok tunnel misconfigured), resulting in silent calls with empty transcripts.

## [1.2.0] - 2026-02-05

### Fixed
- **Hangup timing** - Calls no longer cut off mid-sentence when AI decides to hang up. Now uses Twilio mark events to wait for audio playback to complete before disconnecting.
- **Safety timeout** - Added 30-second fallback timeout in case Twilio mark event is never received.

## [1.1.0] - 2026-02-02

### Added
- **Call completion callbacks** - Agent is now triggered when calls complete, enabling multi-call workflows (e.g., "call to ask a question, then call back with the answer")
- AI-initiated hangup when goals are achieved
- Security and usage responsibility disclaimers

### Changed
- Requires `hooks.enabled: true` and `hooks.token` in OpenClaw config for callbacks to work
- Updated documentation with complete setup instructions

## [1.0.0] - 2026-02-02

### Added
- Initial release
- AI-powered voice calls via OpenAI Realtime API + Twilio
- Persona support with custom goals and opening lines
- Full-duplex conversation with GPT-4o
- Automatic transcript capture
