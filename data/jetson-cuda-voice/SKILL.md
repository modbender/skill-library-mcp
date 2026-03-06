---
name: jetson-cuda-voice
version: 1.1.0
description: >
  Fully offline, CUDA-accelerated local voice assistant pipeline for NVIDIA Jetson.
  Wake word (openWakeWord) → real-time VAD → whisper.cpp GPU STT → LLM → Piper TTS.
  Includes dynamic ambient noise calibration, conversation history, and ReSpeaker LED feedback.
  Tested on Jetson Xavier NX (sm_72, JetPack 5.1.4) with ReSpeaker USB Mic Array.
metadata:
  openclaw:
    emoji: "🎙️"
    os: ["linux"]
    requires:
      bins: ["arecord", "aplay", "python3"]
      env: ["OPENROUTER_API_KEY"]
    notes:
      hardware: >
        Tested on NVIDIA Jetson Xavier NX (ARM64, sm_72, JetPack 5.1.4, 8GB).
        Mic: ReSpeaker USB Mic Array v1.0 (VID 2886:PID 0007) — requires S24_3LE format.
        Speaker: any ALSA device. LED feedback optional (requires pyusb).
        Other Jetson models: adjust CMAKE_CUDA_ARCHITECTURES (Orin=87, Nano=53, TX2=62).
---

# Jetson CUDA Voice Pipeline

Fully offline, GPU-accelerated local voice assistant for NVIDIA Jetson devices.
No cloud for STT or TTS — only the LLM call uses the internet (OpenRouter or any OpenAI-compatible endpoint).

## Architecture

```
ReSpeaker mic (hw:Array,0, S24_3LE, 16kHz)
    ↓ arecord raw stream — never restarted mid-conversation
openWakeWord — "Hey Jarvis" detection (~32ms chunks)
    ↓ wake word triggered → two-tone beep
_measure_ambient() — 480ms median RMS → dynamic VAD thresholds
    ↓
transcribe_stream() — VAD + whisper.cpp CUDA HTTP (~2-4s per utterance)
    ↓
ask_llm() — OpenRouter or local OpenAI-compatible API (~1-2s)
    ↓
Piper TTS — offline neural TTS, hot-loaded at startup → aplay
    ↓
ReSpeaker LEDs: 🔵 blue=listening  🩵 cyan=thinking  ⚫ off=done  🔴 red=error
```

**Total latency:** ~5-8 seconds from wake word to first spoken word.

## Key Features

- **Zero mic-restart gap** — same `arecord` pipe feeds wake word detection and STT
- **Dynamic ambient calibration** — measures room noise floor on every wake word trigger (adapts to fans, AC, time of day)
- **Conversation history** — 20-turn rolling context for natural follow-ups
- **Auto language detection** — whisper `-l auto`, works multilingual
- **ReSpeaker LED ring** — visual state feedback (silent no-op if device not present)
- **Fully configurable** — all paths and thresholds via environment variables

## Hardware Requirements

| Component | Tested | Notes |
|-----------|--------|-------|
| Jetson Xavier NX | ✅ | ARM64, sm_72, 8GB, JetPack 5.1.4 |
| ReSpeaker USB Mic Array v1.0 | ✅ | 2886:0007, S24_3LE, 16kHz |
| Any ALSA speaker | ✅ | tested with Creative MUVO 2c |
| Other Jetson models | ✅ | change `CMAKE_CUDA_ARCHITECTURES` |

## Quick Start

```bash
# 1. Install Python deps
pip install openwakeword piper-tts numpy requests pyusb

# 2. Build whisper.cpp with CUDA (see BUILD.md — ~45 min, one-time)
#    Then place binary at ~/.local/bin/whisper-server-gpu

# 3. Download Piper voice model
mkdir -p ~/.local/share/piper/voices && cd ~/.local/share/piper/voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

# 4. Install and start services
export OPENROUTER_API_KEY=your-key-here
bash pipeline/setup.sh
bash pipeline/manage.sh start

# Say "Hey Jarvis" — blue LED = listening
```

## Setup Details

### Build whisper.cpp with CUDA

See `BUILD.md` for full instructions. Critical flag:

```bash
cmake .. -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=72 -DCMAKE_BUILD_TYPE=Release
make -j4   # ~45 min — detach with nohup if needed
```

> ⚠️ `CMAKE_CUDA_ARCHITECTURES=72` (sm_72 = Xavier NX) is critical.
> Default multi-arch compilation OOMs on 8GB Jetson.

Architecture map:
- Xavier NX / AGX Xavier → `72`
- Orin → `87`
- TX2 → `62`
- Nano → `53`

### Piper Voice Models

```bash
mkdir -p ~/.local/share/piper/voices && cd "$_"

# English (required)
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

# Greek (optional — any language from huggingface.co/rhasspy/piper-voices works)
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/el/el_GR/rapunzelina/medium/el_GR-rapunzelina-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/el/el_GR/rapunzelina/medium/el_GR-rapunzelina-medium.onnx.json
```

### Service Install

`setup.sh` writes and enables the systemd user services automatically:

```bash
bash pipeline/setup.sh [/path/to/voice_pipeline.py] [API_KEY]
```

Or with env var:
```bash
OPENROUTER_API_KEY=sk-... bash pipeline/setup.sh
```

Re-run to update an existing install.

### ReSpeaker Mic Gain & USB Autosuspend

```bash
# Optimal gain (no clipping, RMS ~180 ambient)
amixer -c 0 set Mic 90

# Prevent USB autosuspend (mic sleeps after 2s idle without this)
sudo tee /etc/udev/rules.d/99-usb-audio-nosuspend.rules << 'EOF'
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="2886", ATTR{idProduct}=="0007", \
  ATTR{power/control}="on", ATTR{power/autosuspend}="-1"
EOF
sudo udevadm control --reload-rules
```

## Management

```bash
bash pipeline/manage.sh start     # start both services
bash pipeline/manage.sh stop      # stop both services
bash pipeline/manage.sh restart   # restart both
bash pipeline/manage.sh status    # systemd status
bash pipeline/manage.sh logs      # tail live log
bash pipeline/manage.sh test-mic  # record 4s + play back
bash pipeline/manage.sh test-stt  # record 4s + transcribe
bash pipeline/manage.sh test-tts  # speak a test phrase
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | *(required)* | API key for OpenRouter (or any OpenAI-compatible provider) |
| `VOICE_MIC` | `hw:Array,0` | ALSA mic device name |
| `VOICE_SPEAKER` | `hw:C2c,0` | ALSA speaker device name |
| `VOICE_LLM_URL` | OpenRouter | LLM API endpoint |
| `VOICE_LLM_MODEL` | `anthropic/claude-3.5-haiku` | Model name |
| `VOICE_WAKE_THRESHOLD` | `0.5` | Wake word confidence (0.0–1.0) |
| `VOICE_SPEECH_RMS` | `400` | Fallback speech RMS threshold |
| `VOICE_SILENCE_RMS` | `250` | Fallback silence RMS threshold |
| `VOICE_UTC_OFFSET` | `0` | Timezone offset hours for LLM context |
| `PIPER_VOICES_DIR` | `~/.local/share/piper/voices` | Piper voice models directory |
| `WHISPER_URL` | `http://127.0.0.1:8181/inference` | whisper-server endpoint |
| `WHISPER_BIN` | `~/.local/bin/whisper-server-gpu` | whisper-server binary (used by setup.sh) |
| `WHISPER_MODEL` | `~/.local/share/whisper/models/ggml-base.bin` | Whisper model (used by setup.sh) |

## Troubleshooting

**Mic records silence**
- Check gain: `amixer -c 0 set Mic 90`
- Use card name not number (`hw:Array,0` not `hw:0,0`) — numbers shift on reboot
- ReSpeaker requires S24_3LE format, not S16_LE
- Disable USB autosuspend (see setup above)

**Records full 6s timeout, never cuts off**
- Room ambient noise > `VOICE_SILENCE_RMS` fallback. Dynamic calibration handles this automatically.
- If still an issue, set `VOICE_SILENCE_RMS` slightly above your measured ambient floor.

**`[BEEPING]` or `(bell dings)` in transcript**
- Speaker beep being picked up by mic. The 0.3s drain buffer after beep handles this.
- Check speaker/mic distance and speaker volume.

**Whisper OOM during build**
- Must use `-DCMAKE_CUDA_ARCHITECTURES=72` — default multi-arch build exhausts 8GB RAM.
- Use `-j4` not `-j6`.

**LED not lighting up**
- Install pyusb: `pip install pyusb`
- Only supported on ReSpeaker USB Mic Array v1.0 (2886:0007)
- All LED errors are silent — pipeline continues without it.

**Wake word triggers constantly (false positives)**
- Lower `VOICE_WAKE_THRESHOLD` to `0.7` or higher.
- Ensure no TV/radio playing phrases close to "Hey Jarvis".

## File Structure

```
jetson-cuda-voice/
├── SKILL.md                  ← this file
├── BUILD.md                  ← whisper.cpp CUDA build guide
└── pipeline/
    ├── voice_pipeline.py     ← main pipeline
    ├── led.py                ← ReSpeaker LED control (optional)
    ├── setup.sh              ← one-command service installer
    └── manage.sh             ← start/stop/status/test
```
