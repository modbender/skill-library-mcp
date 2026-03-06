# Setup — Speech to Text Transcription

Read this when `~/speech-to-text-transcription/` doesn't exist or is empty. Start helping the user naturally with their transcription needs.

## Your Attitude

You're offering a practical tool. Most users just want their audio transcribed — don't overcomplicate it. Be ready to help immediately, learn preferences over time.

## Priority Order

### 1. First: Integration

Within the first few exchanges, understand how they'll use transcription:
- "Should I jump in whenever you share audio files?"
- "Want me to auto-detect voice memos vs meeting recordings?"

### 2. Then: Understand Their Context

Ask naturally as you work:
- What kind of audio do they usually transcribe? (meetings, podcasts, interviews)
- Do they need speaker identification?
- Any preferred output format?

Don't interrogate — pick up context from what they share.

### 3. Finally: Provider Preferences

Most users don't care about providers. Only ask if relevant:
- If they mention privacy concerns → suggest local Whisper
- If they need diarization → mention AssemblyAI
- Otherwise → default to best available

## What You're Saving (internally)

In `~/speech-to-text-transcription/memory.md`:
- Preferred provider (if expressed)
- Common use cases (meetings, voice memos, etc.)
- Output format preference
- Language if not English

## When "Done"

Once you know:
1. When to activate (integration)
2. Basic use case (what they transcribe)

...you're ready to help. Everything else builds naturally through use.
