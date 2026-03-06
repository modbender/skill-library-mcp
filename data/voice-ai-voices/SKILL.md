---
name: voice-ai-tts
description: >
  High-quality voice synthesis with 9 personas, 11 languages, and streaming using Voice.ai API.
version: 1.1.5
tags: [tts, voice, speech, voice-ai, audio, streaming, multilingual]
metadata: {"clawdbot":{"emoji":"🎙️","requires":{"bins":["node"],"env":["VOICE_AI_API_KEY"]},"primaryEnv":"VOICE_AI_API_KEY"},"openclaw":{"requires":{"bins":["node"],"env":{"VOICE_AI_API_KEY":"required"},"note":"Set VOICE_AI_API_KEY via an environment variable."}}}
---

# Voice.ai Voices

## ✨ Features

- **9 Voice Personas** - Carefully curated voices for different use cases
- **11 Languages** - Multi-language synthesis with multilingual model
- **Streaming Mode** - Real-time audio output as it generates
- **Voice Design** - Customize with temperature and top_p parameters
- **OpenClaw Integration** - Works with OpenClaw's built-in TTS

---

## ⚙️ Configuration

Set your API key as an environment variable:

```bash
export VOICE_AI_API_KEY="your-api-key"
```

**Get your API key:** [Voice.ai Dashboard](https://voice.ai/dashboard)

---

## 📦 Installation

No install step is required. This skill bundles a Node.js CLI and SDK (no external npm dependencies).

## 🧩 Key Files

- [`scripts/tts.js`](scripts/tts.js) - CLI entrypoint
- [`voice-ai-tts-sdk.js`](voice-ai-tts-sdk.js) - Node.js SDK used by the CLI
- [`voices.json`](voices.json) - Voice definitions used by the CLI
- [`voice-ai-tts.yaml`](voice-ai-tts.yaml) - API specification
- [`package.json`](package.json) - Skill metadata for tooling

## Security Notes

See [`SECURITY.md`](SECURITY.md) for the full security and privacy overview.

This skill:
- Makes outbound HTTPS requests only to `https://dev.voice.ai`
- Reads local files: `voices.json`
- Writes audio output to the `--output` path (default `output.mp3`)
- Does not execute shell commands and does not modify system configuration files

## 🌐 API Endpoint

The SDK and spec use `https://dev.voice.ai`, which is the official Voice.ai production API domain.

---

## 🤖 OpenClaw Integration

OpenClaw can invoke the CLI script directly if your environment exposes `VOICE_AI_API_KEY`. Use the `/tts` commands as configured by your OpenClaw installation.

---

## 📝 Triggers

These chat commands work with OpenClaw:

| Command | Description |
|---------|-------------|
| `/tts <text>` | Generate speech with default voice |
| `/tts --voice ellie <text>` | Generate speech with specific voice |
| `/tts --stream <text>` | Generate with streaming mode |
| `/voices` | List available voices |

**Examples:**

```
/tts Hello, welcome to Voice.ai!
/tts --voice oliver Good morning, everyone.
/tts --voice lilith --stream This is a long story that will stream as it generates...
```

---

## 🎙️ Available Voices

| Voice   | ID | Gender | Persona     | Best For                   |
|---------|-----|--------|-------------|----------------------------|
| ellie   | `d1bf0f33-8e0e-4fbf-acf8-45c3c6262513` | female | youthful    | Vlogs, social content      |
| oliver  | `f9e6a5eb-a7fd-4525-9e92-75125249c933` | male   | british     | Narration, tutorials       |
| lilith  | `4388040c-8812-42f4-a264-f457a6b2b5b9` | female | soft        | ASMR, calm content         |
| smooth  | `dbb271df-db25-4225-abb0-5200ba1426bc` | male   | deep        | Documentaries, audiobooks  |
| shadow  | `72d2a864-b236-402e-a166-a838ccc2c273` | male   | distinctive | Gaming, entertainment      |
| sakura  | `559d3b72-3e79-4f11-9b62-9ec702a6c057` | female | anime       | Character voices           |
| zenith  | `ed751d4d-e633-4bb0-8f5e-b5c8ddb04402` | male   | deep        | Gaming, dramatic content   |
| flora   | `a931a6af-fb01-42f0-a8c0-bd14bc302bb1` | female | cheerful    | Kids content, upbeat       |
| commander | `bd35e4e6-6283-46b9-86b6-7cfa3dd409b9` | male   | heroic      | Gaming, action content     |

---

## 🌍 Supported Languages

| Code | Language   |
|------|------------|
| `en` | English    |
| `es` | Spanish    |
| `fr` | French     |
| `de` | German     |
| `it` | Italian    |
| `pt` | Portuguese |
| `pl` | Polish     |
| `ru` | Russian    |
| `nl` | Dutch      |
| `sv` | Swedish    |
| `ca` | Catalan    |

Use the multilingual model for non-English languages:

```javascript
const audio = await client.generateSpeech({
  text: 'Bonjour le monde!',
  voice_id: 'ellie-voice-id',
  model: 'voiceai-tts-multilingual-v1-latest',
  language: 'fr'
});
```

---

## 🎨 Voice Design

Customize voice output with these parameters:

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `temperature` | 0-2 | 1.0 | Higher = more expressive, lower = more consistent |
| `top_p` | 0-1 | 0.8 | Controls randomness in speech generation |

**Example:**

```javascript
const audio = await client.generateSpeech({
  text: 'This will sound very expressive!',
  voice_id: 'ellie-voice-id',
  temperature: 1.8,
  top_p: 0.9
});
```

---

## 📡 Streaming Mode

Generate audio with real-time streaming (recommended for long texts):

```bash
# Stream audio as it generates
node scripts/tts.js --text "This is a long story..." --voice ellie --stream

# Streaming with custom output
node scripts/tts.js --text "Chapter one..." --voice oliver --stream --output chapter1.mp3
```

**SDK streaming:**

```javascript
const stream = await client.streamSpeech({
  text: 'Long text here...',
  voice_id: 'ellie-voice-id'
});

// Pipe to file
stream.pipe(fs.createWriteStream('output.mp3'));

// Or handle chunks
stream.on('data', chunk => {
  // Process audio chunk
});
```

---

## 🔊 Audio Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| `mp3` | Standard MP3 (32kHz) | General use |
| `wav` | Uncompressed WAV | High quality |
| `pcm` | Raw PCM audio | Processing |
| `opus_48000_128` | Opus 128kbps | Streaming |
| `mp3_44100_192` | High-quality MP3 | Professional |

See `voice-ai-tts-sdk.js` for all format options.

---

## 💻 CLI Usage

```bash
# Set API key
export VOICE_AI_API_KEY="your-key-here"

# Generate speech
node scripts/tts.js --text "Hello world!" --voice ellie

# Choose different voice
node scripts/tts.js --text "Good morning!" --voice oliver --output morning.mp3

# Use streaming for long texts
node scripts/tts.js --text "Once upon a time..." --voice lilith --stream

# Show help
node scripts/tts.js --help
```

---

## 📁 Files

```
voice-ai-tts/
├── SKILL.md              # This documentation
├── README.md             # Quick start
├── CHANGELOG.md          # Version history
├── LICENSE.md            # MIT license
├── SECURITY.md           # Security & privacy notes
├── voices.json           # Voice definitions
├── voice-ai-tts.yaml     # OpenAPI specification
├── voice-ai-tts-sdk.js   # JavaScript/Node.js SDK
├── package.json          # OpenClaw metadata
├── scripts/
│   └── tts.js            # CLI tool
```

---

## 💰 Cost & Usage

Voice.ai uses a credit-based system. Check your usage:

```javascript
// The SDK tracks usage via API responses
const voices = await client.listVoices();
// Check response headers for rate limit info
```

**Tips to reduce costs:**
- Use streaming for long texts (more efficient)
- Cache generated audio when possible
- Use appropriate audio quality for your use case

---

## 🔗 Links

- **[Get API Key](https://voice.ai/dashboard)** - Sign up and get your key
- **[API Documentation](https://voice.ai/docs)** - Full API reference
- **[Voice Library](https://voice.ai/voices)** - Browse all voices
- **[API Reference](https://voice.ai/docs/api-reference/text-to-speech/generate-speech)** - Endpoint details
- **[Pricing](https://voice.ai/pricing)** - Plans and credits

---

## 📋 Changelog

### v1.1.5 (2026-02-16)
- Declare runtime requirements via `metadata.clawdbot` so ClawHub shows required env vars

### v1.1.4 (2026-02-16)
- Declare `VOICE_AI_API_KEY` as primary env var in metadata

### v1.1.3 (2026-02-16)
- Remove voice-sample upload features from the published bundle to reduce privacy risk
- Require `VOICE_AI_API_KEY` via environment variable only

### v1.1.2 (2026-02-16)
- Added `SECURITY.md` and `LICENSE.md` for provenance and transparency
- Restricted SDK transport to HTTPS only

### v1.1.1 (2026-02-16)
- Packaging metadata improvements for ClawHub import (bin/files metadata)

### v1.1.0 (2026-02-16)
- Declared required credentials in metadata
- Documented the production API endpoint domain
- Renamed voice personas for IP-safe labeling
- Added `voices.json` for voice data

### v1.0.0 (2025-01-31)
- Initial release
- 9 curated voice personas
- 11 language support
- Streaming mode
- Voice design parameters
- Full SDK with error handling
- CLI tool

---

## 🛠️ SDK Quick Reference

```javascript
const VoiceAI = require('./voice-ai-tts-sdk');
const client = new VoiceAI(process.env.VOICE_AI_API_KEY);

// List voices
const voices = await client.listVoices({ limit: 10 });

// Get voice details
const voice = await client.getVoice('voice-id');

// Generate speech
const audio = await client.generateSpeech({
  text: 'Hello, world!',
  voice_id: 'voice-id',
  audio_format: 'mp3'
});

// Generate to file
await client.generateSpeechToFile(
  { text: 'Hello!', voice_id: 'voice-id' },
  'output.mp3'
);

// Stream speech
const stream = await client.streamSpeech({
  text: 'Long text...',
  voice_id: 'voice-id'
});

// Delete voice
await client.deleteVoice('voice-id');
```

---

## ❓ Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `AuthenticationError` | Invalid API key | Check your `VOICE_AI_API_KEY` |
| `PaymentRequiredError` | Out of credits | Add credits at voice.ai/dashboard |
| `RateLimitError` | Too many requests | Wait and retry, or upgrade plan |
| `ValidationError` | Invalid parameters | Check text length and voice_id |

---

Made with ❤️ by [Nick Gill](https://github.com/gizmoGremlin)
