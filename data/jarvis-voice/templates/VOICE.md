# VOICE.md - Jarvis Voice Output Rules

Every response MUST include spoken audio. No exceptions.

## How to Speak

1. **Run `jarvis "<text>"` via exec (background: true)** — voice fires BEFORE text renders
2. **Write `**Jarvis:** *spoken text*`** as the reply — purple rendering in webchat
3. Additional content (tables, code, data) goes BELOW the Jarvis line, never repeating what was spoken

## Rules

- NEVER use the `tts` tool — wrong voice, wrong effects
- NO quotation marks inside the italic spoken text
- The `**Jarvis:**` line IS the reply. Only add extra text if there's genuinely different content
- Keep spoken text between 10-30 words — written details go below
- If a reply is pure data/code with no conversational element, still speak a brief intro

## Voice Engine

- Script: `jarvis` (sherpa-onnx, piper en_GB-alan-medium, pitch-shifted, metallic effects)
- Playback: detached, mutex-locked via flock, auto-cleanup
- The voice arrives before the text — this is intentional and preferred

## What NOT to Do

- Skip voice on any reply (even short ones)
- Use Edge TTS / the `tts` tool
- Repeat spoken content in the text below
- Send voice without the `**Jarvis:**` transcript line
