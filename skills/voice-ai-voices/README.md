# Voice.ai Voices

High-quality voice synthesis with 9 personas, 11 languages, and streaming using the Voice.ai API.

Requires Node.js 18+.

## Quick Start

```bash
# Set API key
export VOICE_AI_API_KEY="your-key-here"

# Generate speech
node scripts/tts.js --text "Hello world!" --voice ellie

# Streaming for long text
node scripts/tts.js --text "Once upon a time..." --voice lilith --stream
```

## Configuration

The CLI requires `VOICE_AI_API_KEY` to be set as an environment variable.

## API Endpoint

The SDK uses `https://dev.voice.ai`, which is the official Voice.ai production API domain.

## Voices

Voice definitions live in `voices.json`. Use the CLI with `--voice <name>`:

```
ellie, oliver, lilith, smooth, shadow, sakura, zenith, flora, commander
```

## Documentation

- `SKILL.md` for full usage and examples
- `voice-ai-tts.yaml` for the API spec
- `voice-ai-tts-sdk.js` for SDK usage

## Security

See `SECURITY.md` for a clear list of what the skill reads/writes locally and what endpoints it contacts.

## Links

- Voice.ai Dashboard: https://voice.ai/dashboard
- Voice.ai Docs: https://voice.ai/docs
