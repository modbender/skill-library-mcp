# percept-voice-cmd

Voice command detection and action execution for OpenClaw agents.

## What it does

Detects wake words in ambient speech and routes voice commands to your OpenClaw agent for execution. Supports email, text, reminders, search, calendar, notes, and custom commands.

## When to use

- User says a wake word ("Hey Jarvis", "take notes", or custom)
- User wants hands-free control of their agent
- User asks to set up voice commands or wake words

## Requirements

- **percept-listen** skill installed and running
- **OpenClaw agent** accessible via CLI

## Supported actions

| Action | Example |
|--------|---------|
| Email | "Hey Jarvis, email Rob saying the report is ready" |
| Text | "Hey Jarvis, text David that I'm running late" |
| Reminder | "Hey Jarvis, remind me in 30 minutes to call the dentist" |
| Search | "Hey Jarvis, look up the weather in San Francisco" |
| Calendar | "Hey Jarvis, what's on my calendar today?" |
| Note | "Hey Jarvis, take a note that the server password changed" |
| General | "Hey Jarvis, [anything]" → forwarded to OpenClaw |

## Wake word configuration

Default wake words: `hey jarvis`, `take notes`, `send an email`

Configure via Percept dashboard (port 8960) → Settings → Wake Words, or directly in the database.

## How it works

1. Percept buffers incoming transcript segments
2. Wake word detected → extends buffer by 5 seconds for full command capture
3. 10-second continuation window after wake word (catches follow-up without repeating wake word)
4. Two-tier intent parsing: fast regex first, LLM fallback for complex commands
5. Contact resolution from address book (`percept/data/contacts.json`)
6. Command dispatched to OpenClaw CLI for execution

## Speaker authorization

Only approved speakers can trigger voice commands. Configure in:
- `percept/data/speakers.json` — map speaker IDs to names
- Dashboard → Settings → Speakers → toggle approved/owner

Unapproved speakers are logged but commands are not executed.

## Links

- **GitHub:** https://github.com/GetPercept/percept
