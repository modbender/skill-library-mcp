# Voice Email System - Full Setup Guide

A voice-controlled email system for accessibility. Send emails via natural speech commands.

## Overview

- **Voice Input**: Speak a command like "new email to john@example.com, subject Hello, body How are you, send"
- **Transcription**: Deepgram converts speech to text
- **Parsing**: Extract recipient, subject, and body from natural language
- **Sending**: Send email via Gmail API (gogcli)

## Requirements

1. Linux (tested on Ubuntu/Linux Mint)
2. OpenClaw gateway installed and running
3. Node.js 18+ (for gogcli)
4. gogcli with Gmail access
5. Deepgram API key for voice transcription

## Security Considerations

This skill requires:
- **Network access** - to reach Telegram, Deepgram, and Gmail APIs
- **Credential storage** - API keys in environment variables
- **Config modification** - enabling media/audio in OpenClaw

### Recommended: Use Test Accounts

For testing, create dedicated accounts:
- **Gmail**: Create a test Gmail account for development
- **Deepgram**: Use free tier with limited quota
- **Telegram**: Use a dedicated bot token

## Installation

### 1. Install OpenClaw (if not already)

```bash
npm install -g openclaw
openclaw gateway start
```

### 2. Install gogcli (safer method)

**Option A - via npm (recommended):**
```bash
npm install -g gogcli
```

**Option B - via binary:**
Download from https://gogcli.ai and verify the binary checksum.

### 3. Authenticate Gmail

```bash
gog auth add your-email@gmail.com
```

This opens a browser for OAuth. Complete the authentication.

**Note**: Use a dedicated test account for development.

### 4. Get Deepgram API Key

1. Go to https://console.deepgram.com
2. Sign up / Log in
3. Create a new project
4. Copy your API key (starts with `DG.`)
5. Add to environment or OpenClaw config (see below)

### 5. Configure OpenClaw

Edit `~/.openclaw/openclaw.json`:

```json
{
  "tools": {
    "media": {
      "audio": {
        "enabled": true,
        "models": [
          { "provider": "deepgram", "model": "nova-3" }
        ]
      }
    }
  },
  "env": {
    "DEEPGRAM_API_KEY": "YOUR_DEEPGRAM_KEY"
  }
}
```

### 6. (Optional) Configure ElevenLabs for Voice Responses

If you want voice responses:

```json
{
  "messages": {
    "tts": {
      "auto": "always",
      "provider": "elevenlabs",
      "elevenlabs": {
        "apiKey": "YOUR_ELEVENLABS_KEY",
        "voiceId": "YOUR_VOICE_ID"
      }
    }
  }
}
```

### 7. Install the Voice-Email Skill

```bash
clawhub install voice-email
```

### 8. Restart OpenClaw

```bash
openclaw gateway restart
```

## Usage

### Sending a Voice Email

1. Send a voice message on Telegram with this format:
   ```
   new email to [recipient], subject [subject], body [body], send
   ```

2. Examples:
   - "new email to john@example.com, subject Hello, body How are you, send"
   - "send email to mom@gmail.com, subject Dinner, body See you at 7pm, send"
   - "email to boss@company.com, subject Project Update, body Phase one complete, send"

3. The system will:
   - Transcribe your voice
   - Parse recipient, subject, and body
   - Send the email
   - Confirm the action (text or voice)

### Command Format

The parser looks for:
- **To**: Email address (after "to", "email to", "send to")
- **Subject**: Text after "subject"
- **Body**: Text after "body" (before "send")

## Testing / Validation

### Test Deepgram

```bash
# Replace with your key
export DEEPGRAM_API_KEY="YOUR_KEY"

# Test with a sample audio file
curl -X POST "https://api.deepgram.com/v1/listen" \
  -H "Authorization: Token $DEEPGRAM_API_KEY" \
  -H "Content-Type: audio/ogg" \
  --data-binary @test.ogg
```

### Test gogcli

```bash
gog auth status
gog gmail send --to "your-email@gmail.com" --subject "Test" --body "Voice email system working!"
```

### Test Full Pipeline

Send a voice message on Telegram:
```
new email to your-email@gmail.com, subject test, body hello world, send
```

## Troubleshooting

### Voice not being transcribed

Check Deepgram configuration:
```bash
echo $DEEPGRAM_API_KEY
```

### Email not sending

Check gogcli authentication:
```bash
gog auth status
```

Re-authenticate if needed:
```bash
gog auth add your-email@gmail.com
```

### Network issues

If voice messages fail to download:
- Check DNS: `resolvectl status`
- Try Cloudflare DNS: `sudo resolvectl dns tailscale0 1.1.1.1 1.0.0.1`
- Restart gateway: `openclaw gateway restart`

## Cost

- **gogcli**: Free (uses your Google account)
- **Deepgram**: Free tier available, then pay-per-use
- **ElevenLabs**: Pay-per-character (optional, for voice responses)

## Uninstall

```bash
clawhub uninstall voice-email
```

Then remove API keys from openclaw.json if desired.

## Backup

Before installing, backup your config:
```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak
```
