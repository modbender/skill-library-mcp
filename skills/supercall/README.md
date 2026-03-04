# @xonder/supercall

OpenClaw plugin for AI-powered voice calls with persona support. Uses OpenAI Realtime API for ultra-low latency (~1s) voice conversations via Twilio.

## Features

- **AI Persona Calls**: Define a persona + goal, let GPT-4o handle the conversation
- **Full Realtime**: OpenAI Realtime API with bidirectional audio streaming
- **DTMF / IVR Navigation**: AI can navigate automated phone menus by sending touch-tone digits through the audio stream — no external dependencies, pure µ-law tone generation
- **Auto Hangup**: AI can terminate calls when goals are achieved
- **Ngrok Tunneling**: Built-in ngrok support for webhook URLs

## Installation

```bash
openclaw plugins install @xonder/supercall
```

Or manually:

```bash
npm install @xonder/supercall
# Then add to plugins.load.paths or copy to ~/.openclaw/extensions/
```

## Configuration

Add to your `~/.openclaw/openclaw.json`:

```json
{
  "hooks": {
    "enabled": true,
    "token": "your-secret-token-here"
  },
  "plugins": {
    "entries": {
      "supercall": {
        "enabled": true,
        "config": {
          "provider": "twilio",
          "fromNumber": "+1234567890",
          "twilio": {
            "accountSid": "ACxxxxxxxx",
            "authToken": "xxxxxxxx"
          },
          "streaming": {
            "openaiApiKey": "sk-xxxxxxxx"
          },
          "serve": {
            "port": 3335,
            "path": "/supercall"
          },
          "tunnel": {
            "provider": "ngrok",
            "ngrokDomain": "your-domain.ngrok.app"
          }
        }
      }
    }
  }
}
```

### Required: Hooks Configuration

Supercall uses OpenClaw's webhook system to trigger agent callbacks when calls complete. You **must** configure `hooks.enabled` and `hooks.token` for callbacks to work properly.

The `hooks.token` can be any random string — it's used to authenticate internal webhook requests. Generate one with:

```bash
openssl rand -hex 24
```

## Usage

The plugin registers a `supercall` tool that the agent can use:

```
Call +1234567890 as "Alex from scheduling" with goal "confirm appointment for tomorrow at 2pm"
```

Or via the tool directly:

```json
{
  "action": "persona_call",
  "to": "+1234567890",
  "persona": "Alex from scheduling",
  "openingLine": "Hi, this is Alex calling about your appointment.",
  "goal": "Confirm the appointment for tomorrow at 2pm"
}
```

## Requirements

- Twilio account with a phone number
- OpenAI API key with Realtime API access
- ngrok account (free tier works) or other tunnel solution

## Attribution

This project was originally forked from the OpenClaw `voice_call` plugin:
https://docs.clawd.bot/plugins/voice-call

## Disclaimer

**USE AT YOUR OWN RISK.** This software is provided "as is" without warranty of any kind. The author is not responsible for any damages, costs, or legal issues arising from use of this software.

**You are solely responsible** for how you use this tool. By using this software, you agree to:
- Comply with all applicable laws and regulations (including telemarketing, robocall, and consent laws)
- Obtain proper consent before making automated calls
- Not use this software for any illegal, fraudulent, harassing, or nefarious purposes
- Comply with Twilio's Acceptable Use Policy and OpenAI's Usage Policies

**This tool can make real phone calls that cost real money.** Monitor your usage and set appropriate limits in your Twilio account.

**AI Security Risks:** This software uses AI (GPT-4o) to conduct autonomous voice conversations. AI systems can behave unpredictably, hallucinate information, be manipulated through prompt injection, or say things you didn't intend. You should:
- Never give the AI access to sensitive information it shouldn't share
- Monitor call transcripts and outcomes
- Understand that AI responses are not guaranteed to be accurate or appropriate
- Not rely on this tool for critical, legal, or safety-sensitive communications

## License

MIT
