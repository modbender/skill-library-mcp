# Voice (Edge TTS)

Text-to-speech skill using Microsoft Edge TTS with real-time streaming playback.

## Quick Start

```bash
# Install dependencies
pip install edge-tts

# Install ffmpeg (for streaming)
# Windows: https://github.com/GyanD/codexffmpeg/releases
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

## Usage

```javascript
// Streaming playback (recommended)
await skill.execute({
  action: 'stream',
  text: '你好，我是小九'
});
```

See SKILL.md for full documentation.
