---
name: audio-conductor
description: Intelligently dispatches requests to the appropriate audio generation model (Music, Sound Effects, or TTS). Use this as a unified entry point for all audio generation needs.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🎧"
    tags: ["audio", "conductor", "dispatcher", "music", "sfx", "tts", "elevenlabs"]
---

# Audio Conductor

This skill acts as an intelligent, unified dispatcher for all audio generation tasks. It analyzes a user's request and routes it to the most appropriate specialized model, whether it's for **Music**, **Sound Effects (SFX)**, or **Text-to-Speech (TTS)**.

## When to Use

Use this skill as the **primary entry point** for any audio-related request. Instead of deciding which specific model or skill to call, simply describe the desired audio output.

- **User says**: "Create a background track for my video."
- **User says**: "I need a sound effect of a door creaking."
- **User says**: "Generate a voice-over for this script."

This skill is designed to be called by high-level agent platforms like OpenClaw. It relies on the tools provided by the `elevenlabs-mcp-server` skill, which must be loaded in the agent's environment.

## Core Principles

- **Unified Interface**: Provides a single, consistent API for all audio generation, simplifying agent-level logic.
- **Intelligent Routing**: Automatically determines the `audio_type` (music, sfx, tts) from the user's prompt.
- **Model Abstraction**: Hides the complexity of individual model APIs (e.g., ElevenLabs Music vs. SFX vs. TTS), allowing for easier maintenance and upgrades.
- **Structured Input/Output**: Works with a standardized `AudioRequest` input and provides a predictable `AudioOutput`.

## Workflow

1.  **Receive Audio Request**: The skill is triggered with a prompt and optional parameters.
2.  **Analyze & Route**: It analyzes the `prompt` to determine the `audio_type`. See the `audio-routing-kb.md` for detailed classification logic.
    - If the prompt describes melodies, moods, or instruments -> `music`
    - If the prompt describes an event, action, or ambient noise -> `sfx`
    - If the prompt contains a clear script to be spoken -> `tts`
3.  **Delegate to Sub-Skill**: Based on the `audio_type`, it calls the appropriate internal generation skill (which is an implementation detail hidden from the end-user).
    - `music` -> Calls the `music-generator` skill with a `Composition Plan`.
    - `sfx` -> Calls the `sfx-generator` skill.
    - `tts` -> Calls the `tts-generator` skill (e.g., `produce-final-narration`).
4.  **Standardize Output**: It receives the generated audio file and metadata from the sub-skill and formats it into a standard `AudioOutput` object, including the URL, duration, and type.
5.  **Return Result**: The final, standardized output is returned to the calling agent.

## Input: `AudioRequest` Schema

```yaml
prompt: "A short, tense, cinematic swell, building in intensity."
# Optional parameters to refine the request
params:
  duration_ms: 5000
  # For TTS
  voice_id: "21m00Tcm4TlvDq8ikWAM"
  # For Music
  instrumental: true
```

## Output: `AudioOutput` Schema

```yaml
audio_output:
  audio_type: "sfx" # or "music", "tts"
  audio_file: "cinematic_swell_tense.wav"
  audio_url: "https://..."
  duration_ms: 4980
  model_used: "elevenlabs_sfx_v1"
  request_details:
    prompt: "A short, tense, cinematic swell, building in intensity."
```

## References

- **[audio-routing-kb.md](references/audio-routing-kb.md)**: Defines the logic and keywords used to classify an audio request into `music`, `sfx`, or `tts`.
- **[model-capabilities-kb.md](references/model-capabilities-kb.md)**: A knowledge base detailing the specific APIs and parameters for each underlying audio model (e.g., ElevenLabs, Suno, etc.).
