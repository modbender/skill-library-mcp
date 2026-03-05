# OpenClaw Avatar

Interactive AI avatar frontend for OpenClaw Hub with Simli video rendering and ElevenLabs text-to-speech.

## Quick Start

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Start the server**
   ```bash
   npm run dev
   ```

Open http://localhost:5173 to see your avatar.

## Configuration

### Environment Variables (`.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `SIMLI_API_KEY` | Yes | API key from [Simli](https://simli.com) |
| `ELEVENLABS_API_KEY` | Yes | API key from [ElevenLabs](https://elevenlabs.io) |
| `ELEVENLABS_VOICE_ID` | No | Override default voice ID |
| `SLACK_BOT_TOKEN` | No | Enable Slack integration |
| `OPENCLAW_TOKEN` | No | OpenClaw gateway auth token |

### Configuration File (`avatar.config.json`)

Copy the example and customize:

```bash
cp avatar.config.example.json avatar.config.json
```

```json
{
  "app": {
    "name": "My Avatar",
    "port": 5173
  },
  "avatars": [
    {
      "id": "default",
      "name": "Assistant",
      "faceId": "your-simli-face-id",
      "voiceId": "your-elevenlabs-voice-id",
      "default": true
    }
  ],
  "languages": [
    { "code": "en-US", "name": "English", "flag": "gb", "default": true }
  ]
}
```

## Getting API Keys

### Simli

1. Sign up at [simli.com](https://simli.com)
2. Create a new face or use a stock face
3. Copy your API key and face ID

### ElevenLabs

1. Sign up at [elevenlabs.io](https://elevenlabs.io)
2. Go to Profile Settings > API Keys
3. Copy your API key
4. (Optional) Create a custom voice and copy its ID

## Features

- Real-time avatar video with lip sync
- Text-to-speech responses
- Speech recognition input
- Multi-language support
- Markdown detail panel
- Slack/email forwarding
- Optional Stream Deck control

## Stream Deck (Optional)

To enable Stream Deck hardware control:

1. Install optional dependencies:
   ```bash
   npm install @elgato-stream-deck/node canvas
   ```

2. Enable in config:
   ```json
   {
     "integrations": {
       "streamDeck": { "enabled": true }
     }
   }
   ```

3. Connect your Stream Deck and restart the server

## Development

```bash
# Run in development mode
npm run dev

# Type check
npm run typecheck

# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```
openclaw-avatar/
├── src/
│   ├── config/        # Configuration system
│   ├── client/        # Browser client (Vite)
│   ├── server.ts      # Express server
│   └── streamdeck.ts  # Stream Deck integration
├── skills/avatar/     # OpenClaw skill definition
├── public/            # Static assets
└── index.html         # Entry point
```

## License

MIT
