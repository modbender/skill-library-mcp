---
name: Hotbutter Voice Skill (Hosted Relay)
description: For a fully local alternative where no data leaves your machine,
  see hotbutter-os.
---

# Hotbutter Voice Skill (Hosted Relay)

**This skill routes data through hotbutter.ai.** Voice transcripts and agent responses are transmitted through the hosted relay server at `wss://hotbutter.ai`. This is a convenience skill — not a private or local-only solution.

For a fully local alternative where no data leaves your machine, see [hotbutter-os](https://github.com/hotbutter-ai/hotbutter-os).

For updates, follow [@DnuLkjkjh](https://x.com/DnuLkjkjh).

## Privacy & Data Flow

**Data that transits through hotbutter.ai:**
- Transcribed speech text (from browser speech-to-text)
- Agent response text (stdout from your local `openclaw` binary)

**Warning:** If your agent prints sensitive information (secrets, credentials, private data), that output will be sent through the relay. Avoid running agents that output secrets, or use `--relay-url` to point to a relay you control.

**Data that stays local:**
- Raw audio (processed in the browser, never transmitted)
- The `openclaw` binary execution (runs on your machine)
- Config file (`~/.hotbutter`)

## Required Dependencies

- **`openclaw` CLI** — must be installed and on your PATH

## How It Works

1. This skill connects via WebSocket to `wss://hotbutter.ai`
2. A pairing code and URL (`https://hotbutter.ai/app?code=XXXXXX`) are printed
3. Open the URL in your browser to start a voice session
4. Browser speech-to-text converts your voice to text, sent through the relay to this skill
5. This skill executes `openclaw agent --session-id <id> -m <text>` on your machine
6. The agent's text response is sent back through the relay and spoken via browser TTS

## Usage

```bash
# Start (connects to hotbutter.ai by default)
voice-bridge start

# Use your own relay for privacy
voice-bridge start --relay-url wss://your-relay.example.com

# Custom agent display name
voice-bridge start --agent-name "My Agent"
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--relay-url` | `wss://hotbutter.ai` | Relay WebSocket URL. Change this to use your own relay. |
| `--agent-name` | `Agent` | Display name shown in the voice client |

## First Run

On first run, the skill will prompt for an optional email (stored locally in `~/.hotbutter`). Subsequent runs connect immediately.
