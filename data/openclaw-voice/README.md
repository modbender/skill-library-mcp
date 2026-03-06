# openclaw-voice

[![Tests](https://img.shields.io/badge/tests-10%20passing-brightgreen)]() [![Node](https://img.shields.io/badge/node-%3E%3D18-blue)]() [![License: MIT](https://img.shields.io/badge/license-MIT-yellow)]()

> Voice-first interaction with conversation tracking and ElevenLabs integration.

Manage voice conversations, transcripts, and voice profiles from the command line. Track conversation sessions with full transcript history, search across past interactions, and configure ElevenLabs voice profiles for TTS output. **v1.1 coming soon:** phone calling via Twilio.

## Features

- **Conversation sessions** — start, end, and list voice conversations with summaries
- **Transcript management** — add and review transcript lines with speaker labels and confidence scores
- **Voice profiles** — manage ElevenLabs voice profiles with configurable settings
- **Default profile** — set a preferred voice for quick access
- **Searchable history** — search across all past conversations and transcripts
- **Interchange output** — publish conversation data as `.md` files
- **Backup & restore** — full database backup and recovery
- 🔜 **Phone calling** — Twilio integration for inbound/outbound calls (v1.1)

## Quick Start

```bash
cd skills/voice
npm install

# Start a conversation
node src/cli.js conversation start --summary "Weekly standup"

# Add transcript lines
node src/cli.js transcript add <conv-id> --speaker user --text "What's on the agenda?"
node src/cli.js transcript add <conv-id> --speaker assistant --text "Three items to cover today."

# Review and search
node src/cli.js transcript show <conv-id>
node src/cli.js transcript list --search "standup"

# Set up a voice profile
node src/cli.js profile add nova --voice-id EXAVITQu4vr4xnSDxMaL
node src/cli.js profile default nova
```

## CLI Reference

### Conversations

```bash
voice conversation start [--summary <text>]
voice conversation end <conversation-id> [--summary <text>]
```

### Transcripts

```bash
voice transcript list [--today] [--search <query>]
voice transcript show <conversation-id>
voice transcript add <conversation-id> --speaker <user|assistant> --text <text> [--confidence <0-1>]
```

### Voice Profiles

```bash
voice profile list
voice profile add <name> --voice-id <elevenlabs-id> [--settings <json>]
voice profile default <name>
```

### Utilities

```bash
voice refresh              # Regenerate interchange .md files
voice backup [--output <path>]
voice restore <backup-file>
```

## Architecture

SQLite database (`data/`) stores conversations, transcript lines, and voice profiles. Conversations have a lifecycle (`ongoing → ended`) with optional summaries. Transcript lines are linked to conversations with speaker, text, confidence, and timestamp.

## .md Interchange

Running `voice refresh` generates `.md` files summarizing recent conversations, transcript excerpts, and profile configurations. Other agents can read these via `@openclaw/interchange` to understand conversation context.

## Testing

```bash
npm test
```

10 tests covering conversation lifecycle, transcript management, voice profiles, search, and interchange generation.

## Part of the OpenClaw Ecosystem

Voice publishes conversation summaries via `@openclaw/interchange`. The `orchestration` skill can queue tasks from voice commands, and `monitoring` tracks voice session metrics.

## License

MIT
