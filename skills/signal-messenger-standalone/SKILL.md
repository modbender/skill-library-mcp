---
name: signal-integration
description: Full Signal messenger integration for OpenClaw agents. Send/receive text and voice messages via signal-cli with role-based permissions (owner/trusted/untrusted), automatic voice transcription (Whisper), voice replies (TTS), conversation history, new contact triage, typing indicators, read receipts, and instant wake-on-message via OpenClaw hooks API. Use when setting up Signal messaging, handling Signal contacts, sending/receiving Signal messages, or managing Signal contact permissions.
---

# Signal Integration

Complete Signal messenger integration with security-first contact management.

## Feature Overview

- **Text & voice messaging** — Send and receive text messages, voice notes, images, and attachments
- **Role-based permissions** — Three-tier contact system (owner/trusted/untrusted) controls who can instruct your agent to execute commands, modify files, or access private information
- **New contact triage** — Unknown senders are flagged for owner approval before the agent engages; prevents prompt injection via unsolicited messages
- **Voice transcription** — Incoming voice messages transcribed via Whisper (or any STT engine) for processing
- **Voice replies** — Generate spoken responses via TTS and send as audio attachments
- **Conversation history** — Per-contact message logs with timestamps for context continuity
- **Typing indicators** — Shows "typing..." in the recipient's Signal app before sending
- **Read & viewed receipts** — Marks messages as read; sends "viewed" receipt for voice messages
- **UUID contact support** — Handles both phone number and UUID-based Signal contacts
- **Instant wake** — Triggers OpenClaw's `/hooks/wake` API on new messages for immediate response (no waiting for next heartbeat)
- **Auto-logging** — All sent and received messages logged to conversation files

## Prerequisites

- **signal-cli** (v0.13.x+): Java-based Signal client — [github.com/AsamK/signal-cli](https://github.com/AsamK/signal-cli)
- **ffmpeg**: Audio format conversion
- **A phone number**: For Signal registration (can be a VoIP number)
- **OpenClaw hooks**: For instant wake-on-message (optional but recommended)

### Optional (for voice messages)

- **Whisper** (or whisper.cpp): Speech-to-text transcription
- **TTS engine** (Coqui, Piper, or OpenClaw's built-in `tts` tool): Text-to-speech for voice replies

## Setup

### 1. Install signal-cli

```bash
# Download latest release
SIGNAL_CLI_VERSION="0.13.12"
curl -L "https://github.com/AsamK/signal-cli/releases/download/v${SIGNAL_CLI_VERSION}/signal-cli-${SIGNAL_CLI_VERSION}-Linux.tar.gz" | tar xz
sudo mv signal-cli-${SIGNAL_CLI_VERSION}/bin/signal-cli /usr/local/bin/
sudo mv signal-cli-${SIGNAL_CLI_VERSION}/lib /usr/local/lib/signal-cli

# Or install to user directory
mv signal-cli-${SIGNAL_CLI_VERSION} ~/.local/share/signal-cli-install
ln -s ~/.local/share/signal-cli-install/bin/signal-cli ~/.local/bin/signal-cli
```

Requires Java 21+: `sudo apt install openjdk-21-jre-headless`

### 2. Register a number

```bash
# Register with SMS verification
signal-cli -a +YOUR_NUMBER register

# Enter the verification code
signal-cli -a +YOUR_NUMBER verify CODE

# Set your profile name
signal-cli -a +YOUR_NUMBER updateProfile --given-name "YourName" --family-name "Bot"
```

### 3. Configure the scripts

Edit `scripts/signal-poll.sh` and `scripts/signal-send.sh`:
- Set `SIGNAL_NUMBER` to your registered number
- Set `SIGNAL_CLI` to your signal-cli binary path
- Set `STATE_DIR` to your preferred state directory (default: `~/.signal-state`)
- Add known contacts to `ALLOWLIST` and `CONTACTS` in signal-poll.sh

### 4. Set up cron polling

```bash
# Poll every minute
crontab -e
# Add: * * * * * /path/to/scripts/signal-poll.sh
```

### 5. Configure OpenClaw wake hook (recommended)

Add to your `openclaw.json` config:
```json
{
  "hooks": {
    "wake": {
      "enabled": true,
      "token": "your-secret-token"
    }
  }
}
```

Then set the same token in `signal-poll.sh` (`WAKE_TOKEN` variable) and the OpenClaw URL (`WAKE_URL`).

## Architecture

```
signal-cli ←→ signal-poll.sh (cron every 1min)
                  ├── Parses text + attachments
                  ├── Logs to conversations/<sender>.log
                  ├── Writes pending_wakes file
                  └── POSTs to OpenClaw /hooks/wake API
                  
Agent (heartbeat/wake)
  ├── Reads pending_wakes
  ├── Reads conversation history for context
  ├── Transcribes voice messages (Whisper)
  ├── Generates reply (text or voice)
  └── Sends via signal-send.sh
```

## Sending Messages

```bash
# Text message
scripts/signal-send.sh +1234567890 "Hello!"

# With attachment
signal-cli -a +YOUR_NUMBER send +RECIPIENT -m "Check this out" -a /path/to/file

# Voice message (generate TTS then send as attachment)
# 1. Generate audio (use your TTS engine)
# 2. Convert to m4a: ffmpeg -i voice.wav -c:a aac -b:a 64k voice.m4a
# 3. Send: signal-cli -a +YOUR_NUMBER send +RECIPIENT -m "" -a voice.m4a
```

## Receiving Messages

The poll script handles receiving automatically. In your HEARTBEAT.md, add:

```markdown
### Signal Messages (check first!)
cat /path/to/.signal-state/pending_wakes 2>/dev/null
```

When processing a wake:
1. Read `pending_wakes` for new message summary
2. Read `conversations/<sender>.log` for full context
3. For voice messages: transcribe the attachment path with Whisper
4. Respond via `signal-send.sh` or voice attachment
5. Clear: `> /path/to/.signal-state/pending_wakes`

## Voice Message Handling

### Transcribing incoming voice messages

```bash
# Convert to WAV for Whisper
ffmpeg -i /path/to/attachment.m4a -ar 16000 -ac 1 -c:a pcm_s16le /tmp/audio.wav -y

# Transcribe (whisper.cpp server example)
curl -s http://127.0.0.1:8080/inference -F "file=@/tmp/audio.wav" -F "language=en"

# Or use OpenAI Whisper, faster-whisper, etc.
```

### Sending voice replies

```bash
# 1. Generate speech (example with a local TTS server)
curl -X POST http://127.0.0.1:5002/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Your message here", "language": "en"}' \
  -o /tmp/voice.wav

# 2. Convert to m4a for Signal
ffmpeg -i /tmp/voice.wav -c:a aac -b:a 64k /tmp/voice.m4a -y

# 3. Send as attachment
signal-cli -a +YOUR_NUMBER send +RECIPIENT -m "" -a /tmp/voice.m4a
```

## Contact Management

### New contacts (UUID-based)

When someone new messages you, signal-cli may show them as a UUID (no phone number). The poll script handles both phone numbers and UUIDs.

```bash
# Accept a message request
signal-cli -a +YOUR_NUMBER sendMessageRequestResponse --type accept UUID_OR_NUMBER

# List all known identities
signal-cli -a +YOUR_NUMBER listIdentities
```

### Triage workflow

Unknown senders are logged to `.signal-state/triage.log` and flagged in `pending_wakes` with `⚠️ NEW CONTACT`. The agent should:
1. Notify the owner about the new contact
2. Wait for approval before engaging
3. Add approved contacts to `ALLOWLIST` in signal-poll.sh

## Typing Indicators & Read Receipts

The send script automatically shows a typing indicator before sending. The poll script sends read receipts and "viewed" receipts for voice messages.

## File Reference

- `scripts/signal-poll.sh` — Cron-based message receiver with wake integration
- `scripts/signal-send.sh` — Send wrapper with typing indicator and conversation logging
- `references/troubleshooting.md` — Common issues and fixes
