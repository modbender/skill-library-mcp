---
name: macos-local-voice
description: "Local STT and TTS on macOS using native Apple capabilities. Speech-to-text via yap (Apple Speech.framework), text-to-speech via say + ffmpeg. Fully offline, no API keys required. Includes voice quality detection and smart voice selection."
metadata: { "openclaw": { "emoji": "🎙️", "requires": { "bins": ["yap", "say", "osascript"], "os": ["darwin"] } } }
---

# macOS Local Voice

Fully local speech-to-text (STT) and text-to-speech (TTS) on macOS. No API keys, no network, no cloud. All processing happens on-device.

## Requirements

- macOS (Apple Silicon recommended, Intel works too)
- `yap` CLI in PATH — install via `brew install finnvoor/tools/yap`
- `ffmpeg` in PATH (optional, needed for ogg/opus output) — `brew install ffmpeg`
- `say` and `osascript` are macOS built-in

## Speech-to-Text (STT)

Transcribe an audio file to text using Apple's on-device speech recognition.

```bash
node {baseDir}/scripts/stt.mjs <audio_file> [locale]
```

- `audio_file`: path to audio (ogg, m4a, mp3, wav, etc.)
- `locale`: optional, e.g. `zh_CN`, `en_US`, `ja_JP`. If omitted, uses system default.
- Outputs transcribed text to stdout.

### Supported STT locales

Use `node {baseDir}/scripts/stt.mjs --locales` to list all supported locales.

Key locales: `en_US`, `en_GB`, `zh_CN`, `zh_TW`, `zh_HK`, `ja_JP`, `ko_KR`, `fr_FR`, `de_DE`, `es_ES`, `pt_BR`, `ru_RU`, `vi_VN`, `th_TH`.

### Language detection tips

- If the user's recent messages are in Chinese → use `zh_CN`
- If in English → use `en_US`
- If mixed or unclear → try without locale (system default)

## Text-to-Speech (TTS)

Convert text to an audio file using macOS native TTS.

```bash
node {baseDir}/scripts/tts.mjs "<text>" [voice_name] [output_path]
```

- `text`: the text to speak
- `voice_name`: optional, e.g. `Yue (Premium)`, `Tingting`, `Ava (Premium)`. If omitted, auto-selects the best available voice based on text language.
- `output_path`: optional, defaults to a timestamped file in `~/.openclaw/media/outbound/`
- Outputs the generated audio file path to stdout.
- If `ffmpeg` is available, output is ogg/opus (ideal for messaging platforms). Otherwise aiff.

### Sending as voice note

After generating the audio file, send it using the `message` tool:

```
message action=send media=<path_from_tts.sh> asVoice=true
```

## Voice Management

List available voices, check readiness, or find the best voice for a language:

```bash
node {baseDir}/scripts/voices.mjs list [locale]     # List voices, optionally filter by locale
node {baseDir}/scripts/voices.mjs check "<name>"     # Check if a specific voice is downloaded and ready
node {baseDir}/scripts/voices.mjs best <locale>       # Get the highest quality voice for a locale
```

### Quality levels

- 1 = compact (low quality, always available)
- 2 = enhanced (mid quality, may need download)
- 3 = premium (highest quality, needs download from System Settings)

### If a voice is not available

Tell the user: "Voice X is not downloaded. Go to **System Settings → Accessibility → Spoken Content → System Voice → Manage Voices** to download it."

## Notes

- The `say` command silently falls back to a default voice if the requested voice is not available (exit code 0, no error). **Always** use `voices.mjs check` before calling `tts.mjs` with a specific voice name.
- Premium voices (e.g. `Yue (Premium)`, `Ava (Premium)`) sound significantly better but must be manually downloaded by the user.
- Siri voices are not accessible via the speech synthesis API.
