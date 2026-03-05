---
name: edge-tts-english
description: Generate high-quality English (and multilingual) audio using Microsoft Edge TTS. Use when the user asks to "speak this", "pronounce", "read aloud", "say this in English", "озвучь голосом", "прочитай по-английски", "произнеси", or wants to hear text spoken with a native accent for language learning or pronunciation practice. Supports American and British English voices (male and female). Requires edge-tts installed via pipx. Sends the resulting MP3 directly to the user.
---

# Edge TTS English

Generate native-quality English audio using Microsoft Edge TTS (`/root/.local/bin/edge-tts`).

## Workflow

1. Run `scripts/speak.sh "<text>" [voice] [output_path]`
2. Send the resulting MP3 to the user via `message` tool with `media=<output_path>`

```bash
bash scripts/speak.sh "Hello, world!" en-US-AriaNeural /tmp/tts_out.mp3
```

## Voices

| Voice | Style |
|---|---|
| `en-US-AriaNeural` | Female, American (default) |
| `en-US-JennyNeural` | Female, American, warm |
| `en-US-GuyNeural` | Male, American |
| `en-GB-SoniaNeural` | Female, British |
| `en-GB-RyanNeural` | Male, British |

List all voices: `/root/.local/bin/edge-tts --list-voices | grep en-`

## Notes

- Scripts path: resolve relative to this skill's directory
- edge-tts binary: `/root/.local/bin/edge-tts`
- Default output: `/tmp/edge_tts_output.mp3`
- Always send audio via `message` tool (`media` param), not as text
