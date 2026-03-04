---
name: clawatar
description: Give your AI agent a 3D VRM avatar body with animations, expressions, voice chat, and lip sync. Use when the user wants a visual avatar, VRM viewer, avatar companion, VTuber-style character, or 3D character they can talk to. Installs a web-based viewer controllable via WebSocket.
---

# Clawatar — 3D VRM Avatar Viewer

Give your AI agent a body. Web-based VRM avatar with 162 animations, expressions, TTS lip sync, and AI chat.

## Install & Start

```bash
# Clone and install
git clone https://github.com/Dongping-Chen/Clawatar.git ~/.openclaw/workspace/clawatar
cd ~/.openclaw/workspace/clawatar && npm install

# Start (Vite + WebSocket server)
npm run start
```

Opens at http://localhost:3000 with WS control at ws://localhost:8765.

Users must provide their own VRM model (drag & drop onto page, or set `model.url` in `clawatar.config.json`).

## WebSocket Commands

Send JSON to `ws://localhost:8765`:

### play_action
```json
{"type": "play_action", "action_id": "161_Waving"}
```

### set_expression
```json
{"type": "set_expression", "name": "happy", "weight": 0.8}
```
Expressions: `happy`, `angry`, `sad`, `surprised`, `relaxed`

### speak (requires ElevenLabs API key)
```json
{"type": "speak", "text": "Hello!", "action_id": "161_Waving", "expression": "happy"}
```

### reset
```json
{"type": "reset"}
```

## Quick Animation Reference

| Mood | Action ID |
|------|-----------|
| Greeting | `161_Waving` |
| Happy | `116_Happy Hand Gesture` |
| Thinking | `88_Thinking` |
| Agreeing | `118_Head Nod Yes` |
| Disagreeing | `144_Shaking Head No` |
| Laughing | `125_Laughing` |
| Sad | `142_Sad Idle` |
| Dancing | `105_Dancing`, `143_Samba Dancing`, `164_Ymca Dance` |
| Thumbs Up | `153_Standing Thumbs Up` |
| Idle | `119_Idle` |

Full list: `public/animations/catalog.json` (162 animations)

## Sending Commands from Agent

```bash
cd ~/.openclaw/workspace/clawatar && node -e "
const W=require('ws'),s=new W('ws://localhost:8765');
s.on('open',()=>{s.send(JSON.stringify({type:'speak',text:'Hello!',action_id:'161_Waving',expression:'happy'}));setTimeout(()=>s.close(),1000)})
"
```

## UI Features

- **Touch reactions**: Click avatar head/body for reactions
- **Emotion bar**: Quick 😊😢😠😮😌💃 buttons
- **Background scenes**: Sakura Garden, Night Sky, Café, Sunset
- **Camera presets**: Face, Portrait, Full Body, Cinematic
- **Voice chat**: Mic input → AI response → TTS lip sync

## Config

Edit `clawatar.config.json` for ports, voice settings, model URL. TTS requires ElevenLabs API key in env (`ELEVENLABS_API_KEY`) or `~/.openclaw/openclaw.json` under `skills.entries.sag.apiKey`.

## Notes

- Animations from [Mixamo](https://www.mixamo.com/) — credit required, non-commercial
- VRM model not included (BYOM — Bring Your Own Model)
- Works standalone without OpenClaw; AI chat is optional
