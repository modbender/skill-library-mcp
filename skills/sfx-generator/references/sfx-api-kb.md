# ElevenLabs SFX API Knowledge Base

This document details the specifications for the ElevenLabs Sound Effects API, used by the `sfx-generator` skill.

- **API Endpoint**: `POST https://api.elevenlabs.io/v1/sound-generation`
- **Official Documentation**: [elevenlabs.io/docs/api-reference/text-to-sound-effects/convert](https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert)

## Request Body

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | string | **Yes** | The text description of the sound effect to generate. |
| `duration_seconds` | double | No | The desired duration of the sound in seconds. Must be between 0.5 and 30. If omitted, the model will guess the optimal duration. |
| `prompt_influence` | double | No | Controls how closely the generation follows the prompt, trading off for less variability. Must be between 0 and 1. Defaults to `0.3`. |
| `model_id` | string | No | The model to use for generation. Defaults to `eleven_text_to_sound_v2`. |

## Response

The API returns the generated sound effect directly as an MP3 file in the response body.

## Best Practices

- **Be Descriptive**: The more detailed and specific the `text` prompt, the better the result. Instead of "dog barking", try "a small terrier barking excitedly in the distance".
- **Use `prompt_influence` for Control**: 
  - For highly specific or technical sounds, increase `prompt_influence` to `0.7-0.9`.
  - For more creative or ambient sounds, keep it lower at `0.2-0.4`.
- **Manage Duration**: For sounds that need to sync with video, always specify `duration_seconds`. For ambient background tracks, letting the model decide can produce more natural results.
