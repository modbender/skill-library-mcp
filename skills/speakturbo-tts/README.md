```
     ███████╗██████╗ ███████╗ █████╗ ██╗  ██╗ ████████╗██╗   ██╗██████╗ ██████╗  ██████╗ 
     ██╔════╝██╔══██╗██╔════╝██╔══██╗██║ ██╔╝ ╚══██╔══╝██║   ██║██╔══██╗██╔══██╗██╔═══██╗
     ███████╗██████╔╝█████╗  ███████║█████╔╝     ██║   ██║   ██║██████╔╝██████╔╝██║   ██║
     ╚════██║██╔═══╝ ██╔══╝  ██╔══██║██╔═██╗     ██║   ██║   ██║██╔══██╗██╔══██╗██║   ██║
     ███████║██║     ███████╗██║  ██║██║  ██╗    ██║   ╚██████╔╝██║  ██║██████╔╝╚██████╔╝
     ╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝ 
```

<h3 align="center">Talk to your Claude.</h3>

<p align="center">
  <a href="https://speakturbo-site.vercel.app"><img src="https://img.shields.io/badge/website-speakturbo-f97316.svg" alt="Website"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/latency-~90ms-brightgreen.svg" alt="Latency">
  <img src="https://img.shields.io/badge/platform-Apple%20Silicon-orange.svg" alt="Platform">
</p>

<p align="center">
  <strong>~90ms to first sound. Realistic. Local. Private. Fast.</strong>
</p>

<p align="center">
  <code>speakturbo "Hello world"</code> → <code>⚡ 92ms → ▶ 93ms → ✓ done</code>
</p>

---

## Install

**For AI Agents** (Claude Code, Cursor, Windsurf):
```bash
npx skills add EmZod/Speak-Turbo
```

**CLI only:**
```bash
pip install pocket-tts uvicorn fastapi
cd speakturbo-cli && cargo build --release
```

---

## Usage

```bash
speakturbo "Hello world"              # Play instantly
speakturbo "Hello" -o out.wav         # Save to file
speakturbo "Hello" -q                 # Quiet mode
speakturbo --list-voices              # Show voices
```

---

## Voices

```
alba      ██████████  Female (default)
marius    ██████████  Male
javert    ██████████  Male  
jean      ██████████  Male
fantine   ██████████  Female
cosette   ██████████  Female
eponine   ██████████  Female
azelma    ██████████  Female
```

---

## Performance

```
Time to first sound    ░░░░░░░░░░░░░░░░░░░░  ~90ms
First run (cold)       ████░░░░░░░░░░░░░░░░  2-5s  
Real-time factor       ████████████████░░░░  4x faster
```

---

## Architecture

```
                    ┌─────────────────┐
                    │   speakturbo    │
                    │   (Rust, 2.2MB) │
                    └────────┬────────┘
                             │ HTTP :7125
                             ▼
                    ┌─────────────────┐
                    │     daemon      │
                    │ (Python + MLX)  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Audio Output   │
                    │    (rodio)      │
                    └─────────────────┘
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No audio | `curl http://127.0.0.1:7125/health` |
| Daemon stuck | `pkill -f "daemon_streaming"` |
| Slow first run | Normal - model loading (2-5s) |

---

## See Also

Need voice cloning? Emotion tags? Try [**speak**](https://github.com/EmZod/speak).

---

<p align="center">
  <sub>MIT License · Built on <a href="https://github.com/kyutai-labs/pocket-tts">Pocket TTS</a></sub>
</p>
