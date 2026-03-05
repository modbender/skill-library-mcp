---
name: jarvis-ui
description: JARVIS-style HUD web interface for OpenClaw agents. Interactive Three.js orb with agent state visualization, real-time chat via Gateway WebSocket, audio spectrum analyzer, system monitor, and TTS. Use when you want a visual dashboard for your OpenClaw agent.
metadata: {"openclaw":{"emoji":"🦾","version":"1.0.3","requires":{"bins":["node","npm"]},"homepage":"https://github.com/jincocodev/openclaw-jarvis-ui"}}
---

# 🦾 JARVIS UI

A JARVIS-style HUD interface for your OpenClaw agent.

## Install

```bash
./setup.sh
```

Gateway token is auto-detected from `~/.openclaw/openclaw.json`.

> **⚠️ Remote/non-localhost access:** If JARVIS server is accessed from a different machine (not localhost), add this to your `~/.openclaw/openclaw.json`:
> ```json
> { "gateway": { "controlUi": { "allowInsecureAuth": true } } }
> ```
> Then restart OpenClaw Gateway.

Then start:

```bash
node --env-file=.env server/index.js
```

Open `http://localhost:9999`

## Customize

Copy and edit `config.local.json`:

```bash
cp config.json config.local.json
```

| Field | Description | Default |
|-------|-------------|---------|
| `name` | Page title | JARVIS |
| `agent.name` | Agent display name | JARVIS |
| `agent.emoji` | Agent emoji | 🤖 |
| `agent.sessionKey` | OpenClaw session key | agent:main:main |
| `server.port` | Server port | 9999 |
| `tts.voice` | macOS TTS voice | Samantha |

## Production

```bash
npm i -g pm2
pm2 start server/index.js --name jarvis --node-args="--env-file=.env"
pm2 save
```

## Features

- 🔮 Three.js orb — reacts to agent state (thinking/speaking/idle)
- 💬 Real-time chat — Gateway WebSocket relay
- 🎵 Audio visualizer — spectrum, ring, waveform
- 📊 Model status — live token usage, model info
- 🖥️ System monitor — CPU, memory, uptime
- 🗣️ TTS — Edge TTS (free, cross-platform) + macOS `say` (offline)
- 📱 Mobile responsive + PWA

## Requirements

- Node.js 20+
- OpenClaw Gateway running locally
- Python 3 + `edge-tts` (`pip install edge-tts`) for TTS
- ffmpeg (optional, macOS `say` engine only)
