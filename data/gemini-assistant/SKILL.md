---
name: gemini-assistant
description: General-purpose AI assistant using Gemini API with voice and text support. Use when you need a smart AI assistant that can answer questions, have conversations, or help with general tasks using Google's Gemini models with audio/text capabilities.
metadata:
  openclaw:
    emoji: "🤖"
---

# Gemini Assistant

A general-purpose AI assistant powered by Google's Gemini API. Supports both text and voice interactions.

## Usage

### Text Mode

```bash
cd ~/.openclaw/agents/kashif/skills/gemini-assistant && python3 handler.py "Your question or message"
```

### Voice Mode

```bash
cd ~/.openclaw/agents/kashif/skills/gemini-assistant && python3 handler.py --audio /path/to/audio.ogg "optional context"
```

## Response Format

The handler returns a JSON response:

```json
{
  "message": "[[audio_as_voice]]\nMEDIA:/tmp/gemini_voice_xxx.ogg",
  "text": "Text response from Gemini"
}
```

## Configuration

Set your Gemini API key:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Or create a `.env` file in the skill directory:

```
GEMINI_API_KEY=your-api-key-here
```

## Model Options

The default model is `gemini-2.5-flash-native-audio-preview-12-2025` for audio support.

To use a different model, edit `handler.py`:

```python
MODEL = "gemini-2.0-flash-exp"  # For text-only
```

## Requirements

- `google-genai>=1.0.0`
- `numpy>=1.24.0`
- `soundfile>=0.12.0`
- `librosa>=0.10.0` (for audio input)
- FFmpeg (for audio conversion)

## Features

- 🎙️ Voice input/output support
- 💬 Text conversations
- 🔧 Configurable system instructions
- ⚡ Fast responses with Gemini Flash
