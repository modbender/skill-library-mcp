---
name: avatar
description: Interactive AI avatar with Simli video rendering and ElevenLabs TTS
emoji: "\U0001F9D1\u200D\U0001F4BB"
homepage: https://github.com/Johannes-Berggren/openclaw-avatar
metadata:
  clawdis:
    skillKey: avatar
    os: [macos, linux, windows]
    requires:
      bins: [node, npm]
      env: [SIMLI_API_KEY, ELEVENLABS_API_KEY]
    install:
      - npm install -g openclaw-avatar
    config:
      requiredEnv:
        - SIMLI_API_KEY
        - ELEVENLABS_API_KEY
      example: |
        SIMLI_API_KEY=your-simli-api-key
        ELEVENLABS_API_KEY=your-elevenlabs-api-key
    cliHelp: |
      openclaw-avatar - Interactive AI avatar frontend

      Usage: openclaw-avatar [options]

      Starts the avatar server at http://localhost:5173
      Requires SIMLI_API_KEY and ELEVENLABS_API_KEY environment variables.
---

# Avatar Skill

Interactive AI avatar interface for OpenClaw with real-time lip-synced video and text-to-speech.

## Features

- **Voice Responses**: Speaks conversational summaries using ElevenLabs TTS
- **Visual Avatar**: Realistic lip-synced video via Simli
- **Detail Panel**: Shows formatted markdown alongside spoken responses
- **Multi-language**: Supports multiple languages for speech and TTS
- **Slack/Email**: Forward responses to Slack DMs or email (when configured)
- **Stream Deck**: Optional hardware control with Elgato Stream Deck

## Setup

1. Get API keys:
   - [Simli](https://simli.com) - Avatar rendering
   - [ElevenLabs](https://elevenlabs.io) - Text-to-speech

2. Set environment variables:
   ```bash
   export SIMLI_API_KEY=your-key
   export ELEVENLABS_API_KEY=your-key
   ```

3. Start the avatar:
   ```bash
   openclaw-avatar
   ```

4. Open http://localhost:5173

## Response Format

When responding to avatar queries, use this format:

```
<spoken>
A short conversational summary (1-3 sentences). NO markdown, NO formatting. Plain speech only.
</spoken>
<detail>
Full detailed response with markdown formatting (bullet points, headers, bold, etc).
</detail>
```

### Guidelines

1. **spoken**: Brief, natural, conversational. This is read aloud.
2. **detail**: Comprehensive information with proper markdown.
3. Always include both sections.

## Example

User: "What meetings do I have today?"

```
<spoken>
You have three meetings today. Your first one is a team standup at 9 AM, then a product review at 2 PM, and finally a 1-on-1 with Sarah at 4 PM.
</spoken>
<detail>
## Today's Meetings

### 9:00 AM - Team Standup
- **Duration**: 15 minutes
- **Attendees**: Engineering team

### 2:00 PM - Product Review
- **Duration**: 1 hour
- **Attendees**: Product, Design, Engineering leads

### 4:00 PM - 1:1 with Sarah
- **Duration**: 30 minutes
- **Notes**: Follow up on project timeline
</detail>
```

## Session Key

Avatar responses use session key: `agent:main:avatar`
