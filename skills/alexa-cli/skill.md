---
name: alexa-cli
description: Control Amazon Alexa devices and smart home via the `alexacli` CLI. Use when a user asks to speak/announce on Echo devices, control lights/thermostats/locks, send voice commands, or query Alexa.
homepage: https://github.com/buddyh/alexa-cli
metadata:
  {
    "openclaw":
      {
        "emoji": "🔊",
        "requires": { "bins": ["alexacli"] },
        "env": { "ALEXA_REFRESH_TOKEN": "optional" },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "buddyh/tap/alexacli",
              "bins": ["alexacli"],
              "label": "Install alexacli (brew)",
            },
            {
              "id": "go",
              "kind": "go",
              "module": "github.com/buddyh/alexa-cli/cmd/alexa@latest",
              "bins": ["alexacli"],
              "label": "Install alexa-cli (go)",
            },
          ],
      },
  }
---

# Alexa CLI

Use `alexacli` to control Amazon Echo devices and smart home via the unofficial Alexa API.

## Authentication

```bash
# Browser login (recommended)
alexacli auth

# Non-US accounts
alexacli auth --domain amazon.de
alexacli auth --domain amazon.co.uk

# Check auth status
alexacli auth status
alexacli auth status --verify    # validate token against API

# Remove credentials
alexacli auth logout
```

Token is valid ~14 days. Configuration stored in `~/.alexa-cli/config.json`.

## Devices

```bash
alexacli devices
alexacli devices --json
```

## Text-to-Speech

```bash
# Speak on a specific device
alexacli speak "Hello world" -d "Kitchen Echo"

# Announce to ALL devices
alexacli speak "Dinner is ready!" --announce

# Device name matching is flexible
alexacli speak "Build complete" -d Kitchen
```

## Voice Commands (Smart Home Control)

Send any command as if you spoke it to Alexa:

```bash
# Lights, switches, plugs
alexacli command "turn off the living room lights" -d Kitchen
alexacli command "dim the bedroom lights to 50 percent" -d Bedroom

# Thermostats
alexacli command "set thermostat to 72 degrees" -d Bedroom
alexacli command "what's the temperature inside" -d Kitchen

# Locks
alexacli command "lock the front door" -d Kitchen

# Music
alexacli command "play jazz music" -d "Living Room"
alexacli command "stop" -d "Living Room"

# Questions
alexacli command "what's the weather" -d Kitchen

# Timers
alexacli command "set a timer for 10 minutes" -d Kitchen
```

## Ask (Get Response Back)

Send a command and capture Alexa's text response:

```bash
alexacli ask "what's the thermostat set to" -d Kitchen
# Output: The thermostat is set to 68 degrees.

alexacli ask "what's on my calendar today" -d Kitchen --json
```

## Alexa+ (LLM Conversations)

Interact with Amazon's LLM-powered assistant:

```bash
# Quick start - auto-selects conversation
alexacli askplus -d "Echo Show" "What's the capital of France?"

# Multi-turn retains context
alexacli askplus -d "Echo Show" "What about Germany?"

# List conversations
alexacli conversations

# View conversation history
alexacli fragments "amzn1.conversation.xxx"
```

## Audio Playback

Play MP3 audio through Echo devices:

```bash
alexacli play --url "https://example.com/audio.mp3" -d "Echo Show"
```

Requirements: MP3 at 48kbps, 22050Hz sample rate, HTTPS URL.

## History

```bash
alexacli history
alexacli history --limit 5
alexacli history --json
```

## Command Reference

| Command | Description |
|---------|-------------|
| `alexacli devices` | List all Echo devices |
| `alexacli speak <text> -d <device>` | Text-to-speech on device |
| `alexacli speak <text> --announce` | Announce to all devices |
| `alexacli command <text> -d <device>` | Voice command (smart home, music, etc.) |
| `alexacli ask <text> -d <device>` | Send command, get response back |
| `alexacli conversations` | List Alexa+ conversation IDs |
| `alexacli fragments <id>` | View Alexa+ conversation history |
| `alexacli askplus -d <device> <text>` | Alexa+ LLM conversation |
| `alexacli play --url <url> -d <device>` | Play MP3 via SSML |
| `alexacli auth` | Browser login or manual token |
| `alexacli auth status [--verify]` | Show auth status |
| `alexacli auth logout` | Remove credentials |
| `alexacli history` | View recent voice activity |

## Notes

- Uses Amazon's unofficial API (same as Alexa app)
- Refresh token valid ~14 days, re-run `alexacli auth` if expired
- Device names support partial, case-insensitive matching
- For AI/agentic use, `alexacli command` with natural language is preferred
- Add `--verbose` or `-v` to any command for debug output
