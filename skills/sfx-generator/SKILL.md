---
name: sfx-generator
description: Generates sound effects from a text description using the ElevenLabs API. It validates the output and retries on failure.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🔊"
    tags: ["sfx", "sound", "effect", "generation", "elevenlabs"]
---

# Sound Effect (SFX) Generator

This skill generates a high-quality sound effect from a simple text description, powered by the ElevenLabs SFX API.

## When to Use

This skill is typically called by the `audio-conductor` when a request is classified as a sound effect. It can also be used directly when you know you need a specific sound effect.

- **User says**: "I need the sound of a laser blast."
- **User says**: "Generate a sound of a crowd cheering."

## Core Principles

- **Simplicity**: Takes a simple text prompt and returns an audio file.
- **Quality Control**: Automatically validates the generated audio and can retry if the quality is poor.
- **Parameter Tuning**: Allows for fine-tuning of duration and prompt influence for more creative control.

## Workflow

1.  **Receive SFX Request**: The skill is triggered with a `prompt` and optional `duration_seconds`.
2.  **Set Generation Parameters**: It prepares the request for the ElevenLabs SFX API, consulting `sfx-api-kb.md` for defaults and limits.
    *   `text`: The user's prompt.
    *   `duration_seconds`: (Optional) Target length between 0.5 and 30 seconds.
    *   `prompt_influence`: (Optional) A value between 0 and 1 to control creativity vs. prompt adherence. Defaults to 0.3.
3.  **Execute Generation**: It calls the ElevenLabs SFX API (`/v1/sound-generation`).
4.  **Quality Validation**: It performs a basic check on the output to ensure it's a valid audio file and meets a minimum quality standard (e.g., not silent, no obvious clipping).
5.  **Error Handling & Retry**: If the generation fails or the quality is unacceptable, it can retry up to 2 times.
6.  **Output Audio File**: It returns the final `sfx.mp3` file and its metadata.

## Input: `SFXRequest` Schema

```yaml
prompt: "A futuristic spaceship door opening with a pneumatic hiss."
# Optional parameters
params:
  duration_seconds: 3.5
  prompt_influence: 0.5
```

## Output: `SFXOutput` Schema

```yaml
sfx_output:
  audio_file: "spaceship_door_hiss.mp3"
  audio_url: "https://..."
  duration_ms: 3489
  model_used: "eleven_text_to_sound_v2"
  request_details:
    prompt: "A futuristic spaceship door opening with a pneumatic hiss."
```

## References

- **[sfx-api-kb.md](references/sfx-api-kb.md)**: Defines the ElevenLabs SFX API specifications, parameter details, and best practices.
