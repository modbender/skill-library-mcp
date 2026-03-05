# 🦾 JARVIS UI

A JARVIS-style HUD dashboard for [OpenClaw](https://github.com/openclaw/openclaw) agents.

Interactive 3D orb that visualizes your agent's state in real-time — thinking, responding, idle — with live chat, system monitoring, and audio visualization.

![JARVIS UI Preview](assets/images/desktop-red.png)

### Theme Variants

| Cyan | Green |
|------|-------|
| ![Cyan Theme](assets/images/theme-cyan.png) | ![Green Theme](assets/images/theme-green.png) |

### Mobile

<img src="assets/images/mobile.png" alt="Mobile UI" width="300">

## Features

### 🔮 3D Orb
Interactive Three.js orb with real-time agent state visualization. Shows **IDLE**, **THINKING**, or **RESPONDING** status with color-coded text. Draggable, audio-reactive, with orbiting particle system.

### 💬 Live Chat
Real-time streaming chat via OpenClaw Gateway WebSocket.
- Markdown rendering (code blocks, links, lists)
- Chat history — loads previous conversations on page load (configurable: 20/50/100/200 messages)
- File upload — drag & drop, paperclip button, or Ctrl+V paste for images
- Bubble-style UI with timestamps and sender labels

### 📊 System Monitor
Live system metrics pushed via SSE.
- CPU usage, memory, uptime
- Current model name and token count
- Auto-updating, no polling

### 🎵 Audio Visualizer
Three-layer audio visualization that reacts to TTS playback:
- **Spectrum** — frequency bar graph
- **Ring** — concentric circles that pulse with audio
- **Waveform** — oscilloscope-style wave display

### 📋 Task Manager
Full CRUD task board with real-time sync.
- Priority levels, progress tracking, tags
- Persistent storage (server-side JSON)
- SSE push — updates appear instantly across tabs

### 🧠 Memory Timeline
Displays daily topics extracted from your agent's `memory/*.md` files.
- Shows `##` headings as topic entries per day
- Collapsible days, TODAY/YESTERDAY labels
- "More" button to load older entries (7 days at a time)

### ⏰ Schedule
View and control your agent's scheduled tasks.
- **Heartbeat** — shows system heartbeat status and interval
- **Cron Jobs** — toggle enable/disable directly from the UI

### 🔧 Skills Browser
Scans and displays all installed skills (workspace + global).

### 🗣️ TTS (Text-to-Speech)
Dual engine support:
- **Edge TTS** (default) — free, 300+ voices, multilingual
- **macOS `say`** — offline fallback, requires ffmpeg
- Switchable from the Controls panel

### 🎨 Theme System
One-click color scheme switching via HSL hue rotation.
- 6-color palette in Controls panel (red, orange, green, cyan, blue, purple)
- Affects entire UI: panels, orb, particles, spectrum, background
- Persisted in localStorage

### ⚡ Power Save Mode
Reduce resource usage for background monitoring.
- Throttles render from 60fps to 15fps
- Disables background animations, particles, scan lines
- Toggle from Controls panel, persisted in localStorage

### 📱 Mobile Ready
Responsive UI with touch gestures.
- Swipe up/down on chat header for fullscreen/collapse
- Floating toolbar for quick panel access
- PWA — installable as a home screen app

## Quick Start

### From ClawHub
```bash
npx clawhub install jarvis-ui
cd skills/jarvis-ui
./setup.sh   # auto-detects Gateway token
node --env-file=.env server/index.js
```

### From GitHub
```bash
git clone https://github.com/jincocodev/openclaw-jarvis-ui.git
cd openclaw-jarvis-ui
./setup.sh   # auto-detects Gateway token
node --env-file=.env server/index.js
```

Open `http://localhost:9999`

### ⚠️ Remote Access (non-localhost)

If running JARVIS on a remote server (not localhost), OpenClaw Gateway requires a secure context. Add this to `~/.openclaw/openclaw.json`:

```json
{ "gateway": { "controlUi": { "allowInsecureAuth": true } } }
```

Then restart the Gateway: `openclaw gateway restart`

## Get Your Gateway Token

`setup.sh` auto-detects your token from `~/.openclaw/openclaw.json`. If auto-detection fails, set it manually:

```bash
echo "GATEWAY_TOKEN=your_token" > .env
```

Find your token: run `openclaw status` or check `~/.openclaw/openclaw.json` → `gateway.token`.

## Customize

```bash
cp config.json config.local.json
# Edit config.local.json — it overrides config.json
```

```json
{
  "name": "My Agent HUD",
  "agent": {
    "name": "Friday",
    "emoji": "💎",
    "sessionKey": "agent:main:main"
  },
  "server": {
    "port": 9999,
    "gatewayUrl": "ws://127.0.0.1:18789"
  },
  "tts": {
    "engine": "edge",
    "edgeVoice": "en-US-AriaNeural",
    "edgeVoiceAlt": "zh-TW-HsiaoChenNeural",
    "voice": "Samantha",
    "maxChars": 500
  }
}
```

| Key | Description | Default |
|-----|-------------|---------|
| `name` | Dashboard title | `"JARVIS"` |
| `agent.name` | Agent display name | `"JARVIS"` |
| `agent.emoji` | Agent emoji | `"🤖"` |
| `agent.sessionKey` | OpenClaw session to connect | `"agent:main:main"` |
| `server.port` | Server port | `9999` |
| `server.gatewayUrl` | Gateway WebSocket URL | `"ws://127.0.0.1:18789"` |
| `tts.engine` | TTS engine (`edge` or `say`) | `"edge"` |
| `tts.edgeVoice` | Primary Edge TTS voice | `"en-US-AriaNeural"` |
| `tts.edgeVoiceAlt` | Fallback Edge TTS voice | — |
| `tts.voice` | macOS `say` voice name | `"Samantha"` |
| `tts.maxChars` | Max characters per TTS request | `500` |

**Popular Edge TTS voices:**

| Language | Voice |
|----------|-------|
| English (US) | `en-US-AriaNeural`, `en-US-GuyNeural` |
| 中文 (台灣) | `zh-TW-HsiaoChenNeural`, `zh-TW-YunJheNeural` |
| 中文 (大陸) | `zh-CN-XiaoxiaoNeural`, `zh-CN-YunxiNeural` |
| 日本語 | `ja-JP-NanamiNeural` |

Full list: `python3 -m edge_tts --list-voices`

## Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Development (Vite HMR + backend) |
| `npm run build` | Build static files to `dist/` |
| `npm start` | Production server (serves `dist/`) |

## Production (pm2)

```bash
npm i -g pm2
npm run build
pm2 start server/index.js --name jarvis --node-args="--env-file=.env"
pm2 save
```

## Requirements

- Node.js 20+
- OpenClaw Gateway running locally
- Python 3 + `edge-tts` (default TTS engine: `pip install edge-tts`)
- ffmpeg (optional, only needed for macOS `say` engine)

## Architecture

```
Browser (Vite SPA)
  └→ src/main.js
       ├→ core/ (scene, audio, particles)
       └→ components/ (chat, tasks, skills, memory, schedule, ...)

Server (Express + WebSocket)
  └→ server/
       ├→ index.js       — entry point + middleware
       ├→ gateway.js     — Gateway WS relay
       ├→ sse.js         — SSE broadcast
       ├→ tts.js         — TTS engine (Edge + macOS)
       ├→ system-monitor.js
       └→ routes/        — REST API endpoints
```

## Credits

Based on the [Three.js Orb Visualizer](https://codepen.io/filipz/pen/yyyRgry) by [Filip Zrnzevic](https://codepen.io/filipz) — original concept, 3D orb design, and audio visualization. Adapted into an OpenClaw agent dashboard by [Jincoco](mailto:jincoco88912@gmail.com).

## License

ISC
