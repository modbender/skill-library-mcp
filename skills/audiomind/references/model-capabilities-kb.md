# Model Capabilities KB

This document serves as a registry for the capabilities and API endpoints of the various audio generation models dispatched by the `audio-conductor`.

## 1. ElevenLabs

- **Provider**: ElevenLabs
- **Primary Use**: High-quality TTS, Music, and Sound Effects.

### 1.1 Text-to-Speech (TTS)

- **API Endpoint**: `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`
- **Key Parameters**:
  - `text`: The script to be spoken.
  - `voice_id`: The ID of the chosen speaker.
  - `model_id`: `eleven_multilingual_v2` (standard), `eleven_turbo_v2` (low latency).
  - `voice_settings`: `{ "stability": 0.5, "similarity_boost": 0.75 }`
- **Internal Skill**: `produce-final-narration`

### 1.2 Music Generation

- **API Endpoint**: `https://api.elevenlabs.io/v1/music/compose`
- **Key Parameters**:
  - `composition_plan`: A detailed JSON object defining the music structure (see `music-generator` skill for schema).
  - `music_length_ms`: Total duration in milliseconds.
  - `instrumental`: `true` or `false`.
- **Internal Skill**: `music-generator`

### 1.3 Sound Effects (SFX) Generation

- **API Endpoint**: `https://api.elevenlabs.io/v1/sound-effects`
- **Key Parameters**:
  - `text`: A textual description of the sound effect.
  - `duration_seconds`: The desired length of the sound effect.
- **Internal Skill**: `sfx-generator)

## 2. Suno

- **Provider**: Suno
- **Primary Use**: High-quality music generation, especially with vocals.
- **API Endpoint**: (Assumed, based on typical API design) `https://api.suno.ai/v1/generate`
- **Key Parameters**:
  - `prompt`: A natural language description of the song.
  - `style`: e.g., "acoustic", "pop", "rock".
  - `make_instrumental`: `true` or `false`.
  - `duration`: in seconds.
- **Internal Skill**: (Future integration) `suno-music-generator`

## 3. Beatoven.ai

- **Provider**: Beatoven.ai
- **Primary Use**: Royalty-free background music and sound effects for content creators.
- **API Endpoint**: (Assumed) `https://api.beatoven.ai/v1/sfx/generate`
- **Key Parameters**:
  - `text`: Description of the sound effect.
  - `category`: e.g., "nature", "urban", "cinematic".
- **Internal Skill**: (Future integration) `beatoven-sfx-generator`
