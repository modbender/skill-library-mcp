---
name: protoss-voice
description: Apply Protoss-style (StarCraft) psionic effects to ANY audio file. Use as a post-processing layer for TTS or user recordings.
metadata:
  openclaw:
    emoji: "🔮"
    requires:
      bins:
        - ffmpeg
        - sox
    install:
      - id: brew
        kind: brew
        formula: "sox ffmpeg"
        bins:
          - sox
          - ffmpeg
        label: "Install Dependencies (brew)"
---

# Protoss Voice Effect

Applies a "Khala" psionic transformation chain to audio files using the V9 "Massive Void" engine.
**Modular Design:** This skill does NOT generate speech. It transforms existing audio.

## Usage

Run the script on any input audio file (wav, mp3, ogg, etc):

```bash
python3 skills/protoss-voice/protoss_fx.py <path_to_audio_file>
```

**Output:**
Creates a new file with suffix `_psionic.wav` in the same directory.

## Agent Protocol & Behavior

When acting as a Protoss persona (e.g., Selendis, Artanis, Zeratul, etc), the agent should:

1.  **Generate/Record Base Audio:**
    *   Use `kokoro-tts` (or any other TTS skill) to generate the raw speech.
    *   OR accept a user-provided recording.
2.  **Process (The "Black Box"):**
    *   Execute `protoss_fx.py` on the raw file.
    *   *Do not narrate this step unless debugging.*
3.  **Deliver Final Artifact:**
    *   Send the **processed** file (`_psionic`) using the `message` tool.
    *   Clean up raw/intermediate files silently if they are temporary.

## Integration Example (Kokoro)

```bash
# 1. Generate (Raw)
python3 skills/kokoro-tts/speak.py "En Taro Adun." -o raw.wav -v ef_dora

# 2. Transform (Psionic)
python3 skills/protoss-voice/protoss_fx.py raw.wav
# Output: raw_psionic.wav

# 3. Optimize for Transport (Telegram OGG)
ffmpeg -i raw_psionic.wav -c:a libopus -b:a 64k -vbr on final.ogg -y

# 4. Send
message(action="send", media="final.ogg", asVoice=true)
```

## Requirements

Requires `ffmpeg` and `sox` (Sound eXchange).

```bash
brew install ffmpeg sox
```
