---
name: qwen3-tts
description: Text-to-speech with Qwen3-TTS VoiceDesign. Design custom voices via natural language descriptions + seed-based timbre fixation. Includes OpenAI-compatible API server, one-click setup, and batch seed exploration tools. Use when generating speech, designing voices, or adding TTS to OpenClaw.
---

# Qwen3-TTS VoiceDesign

Text → Speech with natural language voice descriptions + seed-based timbre fixation.

## Quick Start

```bash
# Generate speech (uses server defaults)
TTS_URL=http://your-server:8881 scripts/say.sh "Hello world!"

# Save to file
scripts/say.sh "Save this" output.mp3

# Batch compare seeds (voice exploration)
scripts/batch_seeds.sh "Hello world!" 42 123 201 456 789 /tmp/seeds
```

## Environment Variables

All config via env vars — text is the only required argument:

| Variable | Default | Description |
|----------|---------|-------------|
| `TTS_URL` | `http://localhost:8881` | Server base URL (client side) |
| `TTS_SEED` | `4096` | Random seed → controls timbre |
| `TTS_INSTRUCT` | (generic female voice) | Voice description prompt |
| `TTS_MODEL_PATH` | `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign` | Model weights path |
| `TTS_PORT` | `8881` | Server listen port |
| `TTS_HOST` | `0.0.0.0` | Server bind address |
| `TTS_FORMAT` | `mp3` | Output format: `mp3` / `wav` |

Server reads from `.env` file in its directory. Client scripts read from shell env.

## Voice Description Example

```
30岁男性播音员，声音低沉磁性，
语速稳重从容，咬字清晰标准，
像新闻联播主播的专业感，又带一点温暖。
```

> **Tip:** Once you've found your perfect voice (description + seed), set them as server defaults in `.env`. Then client calls only need to pass `text`.

## API

### OpenAI-Compatible

```bash
curl -X POST $TTS_URL/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello!"}' -o speech.mp3
```

### Custom (seed + instruct override)

```bash
curl -X POST $TTS_URL/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!", "seed": 201, "instruct": "温柔女生"}' -o speech.mp3
```

### GET (quick test)

```bash
curl "$TTS_URL/tts?text=Hello&seed=201" -o test.mp3
```

## Seed Mechanics

Same `(description + seed)` → same timbre. Different seeds → completely different voices.

⚠️ **Seeds are purely random** — seed 42 and 43 can sound completely different. Finding a voice = opening blind boxes.

**Workflow:** fix description → batch 30-40 seeds → listen → shortlist 2-3 → compare across scenarios → pick.

## Deploy Your Own

```bash
# One-click setup (Python 3.10+ and CUDA GPU required)
bash scripts/setup.sh ./my-tts

# Configure voice in .env
echo 'TTS_SEED=201' >> ./my-tts/.env
echo 'TTS_INSTRUCT=Your voice description here' >> ./my-tts/.env

# Start server
bash scripts/setup.sh start ./my-tts
```

Setup installs: `qwen-tts`, `soundfile`, `pydub`, `uvicorn`, `fastapi`, `torch` (CUDA).
Downloads VoiceDesign model (~3.5GB) via ModelScope (China) or HuggingFace.

**Requirements:** CUDA GPU with 4GB+ VRAM, Python 3.10+, ~4GB disk.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/say.sh` | Generate speech — `say.sh "text" [output.mp3]` |
| `scripts/batch_seeds.sh` | Compare seeds — `batch_seeds.sh "text" seed1 seed2 ...` |
| `scripts/tts_server.py` | FastAPI server (fully env-configurable) |
| `scripts/setup.sh` | One-click deploy (venv + deps + model download) |

## OpenClaw Integration

In `openclaw.json`:
```json
{
  "env": { "OPENAI_TTS_BASE_URL": "http://<your-server>:8881/v1" },
  "messages": {
    "tts": {
      "provider": "openai",
      "openai": { "apiKey": "dummy", "model": "qwen3-tts", "voice": "default" },
      "timeoutMs": 120000
    }
  }
}
```

## Server Management

```bash
# Health check
curl -s $TTS_URL/health

# Start (foreground)
python tts_server.py

# Start (background, Linux/macOS)
nohup python tts_server.py > server.log 2>&1 &

# Auto-restart (Windows — scheduled task + guard script)
# Create tts_guard.bat:
#   @echo off
#   :loop
#   python tts_server.py
#   timeout /t 10
#   goto loop
# Register: schtasks /create /tn "TTS-Guard" /tr "tts_guard.bat" /sc onlogon /rl highest

# Auto-restart (Linux — systemd)
# See setup.sh output for systemd unit template

# Stop
# Linux/macOS: kill $(lsof -ti:8881)
# Windows: for /f "tokens=5" %a in ('netstat -aon ^| findstr :8881') do taskkill /PID %a /F
```

## Troubleshooting

- **Connection refused** → Server not running; start it
- **30s+ first request** → Cold start (model loading ~60s); subsequent requests 10-15s
- **Behind proxy** → Set `NO_PROXY=<server_ip>` on client side
- **Windows firewall** → `netsh advfirewall firewall add rule name="TTS" dir=in action=allow protocol=TCP localport=8881`
- **No flash-attn on Windows** → Expected; falls back to PyTorch SDPA (slower but works)
- **PowerShell corrupts Chinese** → Edit `.env`/config via Python or SCP, not PowerShell `Set-Content`
- **Process dies on SSH disconnect** → Use scheduled task (Windows) or systemd (Linux) instead of foreground

## Voice Design Tips

Describe like casting a voice actor:
- **Age/gender**: "18岁女大学生" / "30岁男性播音员"
- **Texture**: "柔和温暖" / "清脆明亮" / "低沉磁性"
- **Emotion**: "轻柔细腻" / "活泼开朗"
- **Accent**: "南方口音软糯" / "台湾腔" / "东北大碴子味"
- **Metaphor**: "像棉花糖" / "像播音主持" (helps the model capture feeling)

⚠️ **Timbre ≠ description.** Description controls style/emotion; seed controls timbre. Don't put personality traits ("灵动俏皮") in description — that's the seed's job.
