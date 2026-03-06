---
name: remotion-excalidraw-tts
description: Generate a narrated Remotion video from an Excalidraw (.excalidraw) diagram using text-to-speech (macOS say) and render to MP4. Use when creating explainer videos with pan/zoom + focus highlights over Excalidraw diagrams, with automated voiceover generation and Remotion CLI rendering.
---

# Remotion + Excalidraw + TTS (Local)

Use this skill to turn an **Excalidraw diagram** + a **voiceover script** into a rendered **MP4** using:

- Remotion (render)
- Excalidraw (render the .excalidraw JSON directly)
- TTS via **macOS `say`** (offline)

## Quick start (one command)

Run:

```bash
python3 skills/remotion-excalidraw-tts/scripts/make_video.py \
  --diagram /absolute/path/to/diagram.excalidraw \
  --voiceover-text /absolute/path/to/voiceover.txt \
  --out /absolute/path/to/out.mp4
```

Optional: drive camera/focus/subtitles via storyboard JSON:

```bash
python3 skills/remotion-excalidraw-tts/scripts/make_video.py \
  --diagram /absolute/path/to/diagram.excalidraw \
  --voiceover-text /absolute/path/to/voiceover.txt \
  --storyboard-json /absolute/path/to/storyboard.json \
  --out /absolute/path/to/out.mp4
```

What it does:
1) copies the Remotion template project from `assets/template/remotion-project/` into a temp workdir
2) writes `public/diagram.excalidraw`
3) generates `public/voiceover.mp3` via `say` + `ffmpeg`
4) sets composition duration to match the voiceover length
5) renders MP4 with `npx remotion render`

## Inputs

- `--diagram`: `.excalidraw` JSON file (from Excalidraw export)
- `--voiceover-text`: plain text file (Chinese supported)

Optional:
- `--voiceover-mp3`: if you already have audio, skip TTS
- `--tts-backend`: `say` (default) | `openai` | `elevenlabs`
- `--fps`: default `30`

TTS backends:
- **macOS say**: `--tts-backend say --voice Tingting --rate 220`
- **OpenAI**: `--tts-backend openai --openai-model gpt-4o-mini-tts --openai-voice alloy` (requires `OPENAI_API_KEY`)
- **ElevenLabs**: `--tts-backend elevenlabs --elevenlabs-voice-id <voiceId> --elevenlabs-model eleven_multilingual_v2` (requires `ELEVENLABS_API_KEY`)

## Customizing scenes (pan/zoom/highlights)

### Option A: edit TypeScript storyboard

Template code lives in:
- `assets/template/remotion-project/src/video/storyboard/storyboard.ts`

Edit scenes:
- `cameraFrom/cameraTo` (x/y/scale)
- `focus` rectangle (x/y/width/height + label)
- `subtitle`

### Option B (recommended): provide `storyboard.json`

Pass `--storyboard-json /abs/path/storyboard.json`.

Schema reference:
- `references/storyboard.schema.json`

Minimal example:

```json
{
  "scenes": [
    {
      "name": "intro",
      "durationSec": 10,
      "subtitle": "很多智能体隔天就失忆。",
      "cameraFrom": {"x": 0, "y": 0, "scale": 1},
      "cameraTo": {"x": 0, "y": 0, "scale": 1},
      "focus": {"x": 140, "y": 120, "width": 1640, "height": 340, "label": "问题"}
    }
  ]
}
```

## Requirements

- macOS (for `say`)
- `ffmpeg` + `ffprobe`
- Node.js + npm (the script will run `npm i` in the temp project)
