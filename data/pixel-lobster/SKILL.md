---
name: pixel-lobster
description: "Pixel art desktop lobster that lip-syncs to OpenClaw TTS speech. Use when: (1) user wants a visual avatar for their AI agent, (2) user wants a desktop overlay that animates when their agent speaks, (3) user asks to set up or configure the pixel lobster. Guides the user to install, configure, and launch the bundled Electron app."
tags: ["avatar", "tts", "desktop", "overlay", "lip-sync", "electron", "xtts", "animation"]
---

# Pixel Lobster

A transparent desktop overlay featuring a pixel art lobster that animates when your OpenClaw agent speaks. Powered by envelope data from your local TTS server — the lobster's mouth only moves during AI speech, not music or system audio.

The app is fully bundled inside this skill — no external repository clone required.

## Requirements

- Node.js 18+ with `npx` available
- A running TTS server exposing `GET /audio/envelope` (XTTS on port 8787, or any OpenAI-compatible TTS via the OpenClaw TTS proxy)
- Windows or Linux desktop (macOS not supported)

## Install

The app is included in this skill at `<skill_dir>/app/`. Install dependencies once:

```bash
cd <skill_dir>/app
npm install
```

## Configure

Edit `<skill_dir>/app/config.json` before launching. Key settings:

| Key | Default | Description |
|-----|---------|-------------|
| `audioMode` | `"tts"` | `"tts"` reacts only to TTS speech; `"system"` captures all audio output |
| `ttsUrl` | `"http://127.0.0.1:8787"` | Base URL of your TTS server |
| `monitor` | `"primary"` | `"primary"`, `"secondary"`, `"left"`, `"right"`, or display index |
| `lobsterScale` | `4` | Sprite scale (4 = 480px tall lobster) |
| `clickThrough` | `false` | Start with click-through mode on so the lobster doesn't block clicks |
| `swimEnabled` | `true` | Enable swimming animation |

## Launch

```bash
cd <skill_dir>/app
npx electron .
```

Or use the included helper script (handles first-run `npm install` automatically):

```bash
bash <skill_dir>/scripts/launch.sh
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| F8 | Move window to next monitor (cycles through all displays) |
| F9 | Toggle click-through mode |
| F12 | Toggle DevTools |

## OpenClaw Integration

With OpenClaw and a local XTTS server, set `audioMode` to `"tts"` and point `ttsUrl` at your XTTS instance. The lobster polls the envelope endpoint at 45ms intervals during active speech and 500ms when idle — no perceptible CPU cost.

If you use the OpenClaw TTS proxy (port 8788), point `ttsUrl` at port 8787 (the XTTS server directly), not the proxy — the envelope endpoint is on the TTS server, not the proxy layer.

## Lip Sync Notes

If the mouth movement is ahead of or behind the audio:

- Mouth moves too early: increase `ttsPlayStartOffsetMs` (default 1100ms)
- Mouth moves too late: decrease `ttsPlayStartOffsetMs`

The default is tuned for PowerShell MediaPlayer on Windows. Other playback methods may need adjustment.

## Mouth Shapes

Six visemes drive natural speech animation:

- **A** — wide open "ah"
- **B** — wide grin "ee"
- **C** — round "oh"
- **D** — small pucker "oo"
- **E** — medium "eh"
- **F** — teeth "ff"

Plus **X** (closed) for silence and pauses. Spring physics and variety enforcement prevent robotic repetition.
