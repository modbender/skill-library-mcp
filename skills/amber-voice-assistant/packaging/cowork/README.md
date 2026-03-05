# Amber — Voice Agent Plugin for Claude Cowork

Give Claude a phone. Amber is the first voice/telephony plugin for Claude — make and receive real phone calls, screen incoming calls with an AI receptionist, book appointments, and manage contacts.

## What it does

- **Make calls** — `/amber:call +14165551234 "Book a table for 4 at 7pm"` and Amber handles the conversation
- **Screen calls** — `/amber:screen start` and Amber answers your phone, takes messages, and sends you summaries
- **Check voicemail** — `/amber:voicemail` to see messages left by callers
- **Call history** — `/amber:calls` for transcripts and AI summaries of all calls
- **Calendar integration** — Amber checks your availability and books appointments during calls
- **Contact memory** — Amber remembers callers across calls and personalizes interactions

## Requirements

- [Twilio account](https://www.twilio.com/) with a phone number
- [OpenAI API key](https://platform.openai.com/) (for voice STT/TTS)
- [ngrok account](https://ngrok.com/) (for webhook tunneling)
- Node.js 18+

## Setup

1. Clone the repo and install dependencies:
   ```bash
   cd runtime && npm install
   ```
2. Run the setup wizard:
   ```bash
   npm run setup
   ```
   The wizard will:
   - Validate your Twilio and OpenAI credentials
   - Configure ngrok for webhook tunneling
   - Compile native macOS tools (Calendar access)
   - Ask if you're setting up for **Claude Desktop / Cowork** — say **yes**
   - Sync your Apple Contacts to a local cache for contact lookups
   - Generate a `.env` file

3. Build and start the bridge:
   ```bash
   npm run build && npm start
   ```

4. Add the MCP server to Claude Desktop (see `.mcp.json` for config)

5. Start screening with `/amber:screen start` or make a call with `/amber:call`

### Refreshing Contacts

If you add or change contacts in Apple Contacts, refresh the cache:
```bash
npm run sync-contacts
```

## Customization

Edit `AGENT.md` to customize Amber's personality, greeting, and call handling behavior. You can change:
- Her name and personality traits
- Greeting messages
- Business hours and after-hours behavior
- Screening rules (who gets put through vs. screened)
- Organization context

## Commands

| Command | Description |
|---------|-------------|
| `/amber:call` | Make an outbound phone call |
| `/amber:screen` | Start/stop inbound call screening |
| `/amber:calls` | View call history and transcripts |
| `/amber:voicemail` | Check messages from screened calls |

## Skills

| Skill | Description |
|-------|-------------|
| phone-calls | Core telephony — make, monitor, end calls |
| call-screening | AI receptionist for inbound calls |
| calendar | Check availability and book appointments |
| crm | Contact memory and interaction history |
| contacts | Resolve names to phone numbers |

## Also available on

- **[ClawHub](https://clawhub.com/skills/amber-voice-assistant)** — as an OpenClaw skill
- **npm** — `npm install amber-voice-agent`

## License

MIT
