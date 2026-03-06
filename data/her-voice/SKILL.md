---
name: Her Voice
description: "Give your agent a voice. Use when the user wants the agent to speak, read aloud, or have voice responses."
metadata:
  openclaw:
    emoji: "🎙️"
    requires:
      bins: ["python3", "espeak-ng"]
---

# Her Voice 🎙️

**Give your agent a voice.** Audio responses powered by Kokoro TTS — a compact, naturally expressive model running entirely on-device.

### ✨ Features  

Highly optimized response time thanks to on-the-fly audio streaming technology. 100% free, no API keys required. Inspired by Samantha and Sky.  

- **⚡ On-the-fly Streaming** — Audio plays as it generates, very low latency
- **👄 The Voice of an angel** — Cutting-edge local text-to-speech model Kokoro TTS
- **🧠 TTS Daemon** — Keep the model warm in RAM for instant responses (can be disabled to save RAM)
- **🖥️ Persist Mode** — Drag & drop audio, paste text, use as a voice station
- **🔧 Fully Configurable** — Voice, speed, visualizer, notification sounds
- **🍎 MLX + PyTorch** — Native Metal acceleration on Apple Silicon, PyTorch fallback everywhere else
- **🎨 Real-time Visualizer** — Floating 60fps LED bars that react to speech (macOS only)

## First-Run Setup

```bash
python3 SKILL_DIR/scripts/setup.py
```

> **Note:** `SKILL_DIR` is the root directory of this skill — the agent resolves it automatically when running commands.

The setup wizard will:
1. Detect platform and select TTS engine (MLX on Apple Silicon, PyTorch elsewhere)
2. Find or install the appropriate TTS backend (mlx-audio or kokoro)
3. Install `espeak-ng` (Homebrew on macOS, apt on Linux)
4. Patch espeak loader if needed (macOS compatibility)
5. Compile the native visualizer binary (macOS only)
6. Download the Kokoro model
7. Create config at `~/.her-voice/config.json`

Check status anytime:
```bash
python3 SKILL_DIR/scripts/setup.py status
```

### Post-Setup: Names & Pronunciation

After setup, configure the agent and user names:
```bash
python3 SKILL_DIR/scripts/config.py set agent_name "Jackie"
python3 SKILL_DIR/scripts/config.py set user_name "Matúš"
python3 SKILL_DIR/scripts/config.py set user_name_tts "Mah-toosh"
```

**TTS pronunciation tip:** If the user's name is non-English, figure out a phonetic English spelling that Kokoro will pronounce correctly. Store it in `user_name_tts` and use that spelling whenever speaking the name aloud. The real name stays in `user_name` for display purposes.

## Speaking Text

```bash
# Basic usage
python3 SKILL_DIR/scripts/speak.py "Hello, world!"

# Skip visualizer for this call
python3 SKILL_DIR/scripts/speak.py --no-viz "Quick note"

# Save to file instead of playing
python3 SKILL_DIR/scripts/speak.py --save /tmp/output.wav "Save this"

# Override voice or speed
python3 SKILL_DIR/scripts/speak.py --voice af_bella --speed 1.2 "Faster!"

# Pipe text from stdin
echo "Piped text" | python3 SKILL_DIR/scripts/speak.py
```

### Options

| Flag | Description |
|------|-------------|
| `--no-viz` | Skip the visualizer for this call |
| `--persist` | Keep visualizer open after playback ends |
| `--save PATH` | Save audio to WAV file instead of playing |
| `--voice NAME` | Override the configured voice |
| `--speed N` | Override the configured speed multiplier |
| `--mode MODE` | Override visualizer mode (`v2` or `classic`) |

## Agent Workflow

When the user wants voice responses:

1. **Check voice mode** — is voice enabled or did the user ask for it?
2. **Play notification sound** (instant feedback while TTS generates):
   ```bash
   afplay /System/Library/Sounds/Blow.aiff &
   ```
3. **Speak the response:**
   ```bash
   python3 SKILL_DIR/scripts/speak.py "Response text here"
   ```
4. **Always provide text alongside voice** — accessibility matters.

### Notification Sound

The notification sound plays instantly (~0.1s) while TTS generates (~0.3-3s). This gives the user immediate feedback that the agent is responding.

Configure in `~/.her-voice/config.json`:
```json
{
  "notification_sound": {
    "enabled": true,
    "sound": "Blow"
  }
}
```

Available macOS sounds: `Blow`, `Bottle`, `Frog`, `Funk`, `Glass`, `Hero`, `Morse`, `Ping`, `Pop`, `Purr`, `Sosumi`, `Submarine`, `Tink`. Located in `/System/Library/Sounds/`.

## TTS Daemon

The daemon keeps the Kokoro model warm in RAM, eliminating ~1.1s of startup overhead per call.

The daemon auto-resolves the mlx-audio venv — no need to find the venv Python manually.

```bash
# Start (persists in background)
nohup python3 SKILL_DIR/scripts/daemon.py start > /tmp/her-voice-daemon.log 2>&1 & disown

# Status
python3 SKILL_DIR/scripts/daemon.py status

# Stop
python3 SKILL_DIR/scripts/daemon.py stop

# Restart
python3 SKILL_DIR/scripts/daemon.py restart
```

`speak.py` auto-detects the daemon: uses it if available, falls back to direct model loading.

**The daemon is optional.** Without it, speech still works — just ~1s slower per call as the model loads each time. Skip the daemon to save ~2.3GB RAM.

**Note:** The daemon writes its PID file and socket after the model is fully loaded and ready to accept connections. They live in `~/.her-voice/` with restricted permissions (owner-only access). The daemon won't survive a reboot — start it again after restart if needed.

## Visualizer

A floating overlay with three animated LED bars that react to speech in real-time. 60fps, native macOS (Cocoa + AVFoundation). **macOS only** — on other platforms, audio plays without the visualizer.

### Modes
- **v2** (default) — Three-tier pure red, center raw amplitude, sides with lag
- **classic** — Original smooth gradient look

### Controls
| Key | Action |
|-----|--------|
| ESC | Quit |
| Space | Pause/Resume (file mode) |
| ← → | Seek ±5s (file mode) |
| ⌘V | Paste text to speak (persist mode) |

### Persist Mode
Keep the visualizer on screen between playbacks. Use as a standalone voice station:
```bash
# Launch in persist mode (stays open, idle breathing animation)
~/.her-voice/bin/her-voice-viz --persist

# Stream mode + persist (stays open after speech ends)
python3 SKILL_DIR/scripts/speak.py --persist "Hello!"
```

In persist mode:
- **Drag & drop** audio files (.wav, .mp3, .aiff, .m4a) onto the visualizer to play them
- **⌘V** pastes clipboard text → streams directly from TTS daemon with full visualizer animation
- **Idle breathing** — subtle center bar pulse when waiting for input

### Standalone Usage
```bash
# Play a file with visualizer
~/.her-voice/bin/her-voice-viz --audio /path/to/file.wav

# Demo mode (simulated audio)
~/.her-voice/bin/her-voice-viz --demo

# Stream raw PCM
cat audio.raw | ~/.her-voice/bin/her-voice-viz --stream --sample-rate 24000
```

### Disable Visualizer
```bash
python3 SKILL_DIR/scripts/config.py set visualizer.enabled false
```

## Configuration

Config file: `~/.her-voice/config.json`

```bash
# View all settings
python3 SKILL_DIR/scripts/config.py status

# Get a value
python3 SKILL_DIR/scripts/config.py get voice

# Set a value (dot notation for nested keys)
python3 SKILL_DIR/scripts/config.py set speed 1.1
python3 SKILL_DIR/scripts/config.py set visualizer.mode classic
```

### Key Settings

| Key | Default | Description |
|-----|---------|-------------|
| `agent_name` | `""` | Agent's name (e.g. "Jackie") |
| `user_name` | `""` | User's real name |
| `user_name_tts` | `""` | Phonetic spelling for TTS (e.g. "Mah-toosh" for Matúš) |
| `voice` | `af_heart` | Base voice name |
| `voice_blend` | `{af_heart: 0.6, af_sky: 0.4}` | Voice blend weights |
| `speed` | `1.05` | Speech speed multiplier |
| `language` | `en` | Language code |
| `tts_engine` | `auto` | TTS engine: `auto`, `mlx`, or `pytorch` |
| `model` | `mlx-community/Kokoro-82M-bf16` | Model identifier (MLX) |
| `visualizer.enabled` | `true` | Show visualizer overlay |
| `visualizer.mode` | `v2` | Animation mode (v2/classic) |
| `visualizer.remember_position` | `true` | Save window position between sessions |
| `notification_sound.enabled` | `true` | Play sound before speaking |
| `notification_sound.sound` | `Blow` | macOS system sound name |
| `daemon.auto_start` | `true` | Advisory flag only — the daemon never self-starts. When `true`, the agent should start it on first voice use (saves ~1s/call, costs ~2.3GB RAM) |
| `daemon.socket_path` | `~/.her-voice/tts.sock` | Unix socket path |

## Voice Selection  

### Voice Blending  

Mix multiple voices for a unique sound. Configure `voice_blend` in config:
```json
{
  "voice_blend": {"af_heart": 0.6, "af_sky": 0.4}
}
```

The blended voice is stored as a `.safetensors` file in the model's voices directory (e.g., `af_heart_60_af_sky_40.safetensors`). Create it by running TTS once — `speak.py` looks for the pre-blended file automatically.

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| "mlx-audio not found" | Venv missing or broken | Run `setup.py` |
| "espeak-ng not found" | Phonemizer missing | `brew install espeak-ng` |
| Compilation failed | Xcode tools missing | `xcode-select --install` |
| "Model not found" | First run, no download | Run `setup.py` or speak once |
| Daemon "not running" | Crashed or rebooted | Start daemon again |
| No sound output | macOS audio permissions | Check System Settings → Sound → Output |
| Visualizer not showing | Binary not compiled | Run `setup.py` |
| "kokoro not found" | PyTorch venv missing | Run `setup.py` |
| PyTorch CUDA error | GPU driver mismatch | `pip install torch --force-reinstall` in kokoro venv |
| "soundfile not found" | Missing dependency | `pip install soundfile` in kokoro venv |

## Requirements

- **macOS + Apple Silicon** recommended for best experience (MLX engine + visualizer + notification sounds)
- **Linux/Intel Mac** supported via PyTorch Kokoro engine (no visualizer)
- **Windows** is not supported
- Xcode Command Line Tools for visualizer on macOS (`xcode-select --install`)
- `espeak-ng` for phonemization (`brew install espeak-ng` on macOS, `apt install espeak-ng` on Linux)
- ~500MB disk (model + venv)
- ~2.3GB RAM when daemon is running

## Uninstall

Remove all Her Voice data (config, venvs, compiled binary, daemon state):
```bash
python3 SKILL_DIR/scripts/daemon.py stop
rm -rf ~/.her-voice
```

## How It Works

1. **Kokoro 82M** — A compact neural TTS model with two backends: **MLX** (Apple's framework for native Metal GPU acceleration on Apple Silicon) and **PyTorch** (works everywhere). The engine is auto-detected based on platform, or can be forced via the `tts_engine` config option (`auto`, `mlx`, or `pytorch`)
2. **Streaming** — Audio generates and plays simultaneously. First sound in ~0.3s (with daemon) vs ~3s batch
3. **Visualizer** — Native macOS app (Swift/Cocoa) reads raw PCM from stdin, plays via AVAudioEngine with real-time amplitude metering
4. **Daemon** — Unix socket server holding the model in RAM. Eliminates Python import + model load overhead on every call
