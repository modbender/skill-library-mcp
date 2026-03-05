---
name: strudel-music
description: "Audio deconstruction and composition via Strudel live-coding. Decompose any audio into stems, extract samples, compose with the vocabulary, render offline to WAV/MP3."
version: 0.3.1
author: the dandelion cult
license: MIT
tags: [music, audio, strudel, composition, samples, trance]
metadata:
  openclaw:
    emoji: "🎵"
    requires:
      bins: [node]
      anyBins: [ffmpeg]
      node: ">=20"
    envVars: []
    install:
      - id: setup
        kind: script
        script: "npm install && bash scripts/download-samples.sh"
        label: "Install dependencies + download drum samples (~11MB)"
      - id: ffmpeg
        kind: apt
        package: ffmpeg
        bins: [ffmpeg]
        label: "Install ffmpeg (audio format conversion)"
    securityNotes: >
      Compositions are JavaScript files evaluated by Node.js. They CAN access
      the filesystem, environment variables, and network. Only run compositions
      you trust or have reviewed. For untrusted compositions, run in a container
      or VM with no credentials in the environment.

      Discord integration (VC streaming, message posting) uses the OpenClaw
      gateway's existing authenticated connection — this skill does NOT require
      its own bot token or Discord credentials. No separate authentication is needed.

      The optional Python pipeline (Demucs, librosa) downloads ML models on first
      run (~1.5GB for htdemucs). These come from official PyTorch/Facebook sources.
---

> ⚠️ **Legal Notice:** This tool processes audio you provide. You are responsible for ensuring you have the rights to use the source material. The authors make no claims about fair use, copyright, or derivative works regarding your use of this tool with copyrighted material.

# Strudel Music 🎵

Compose, render, deconstruct, and remix music using code. Takes natural language prompts → writes Strudel patterns → renders offline through real Web Audio synthesis → posts audio or streams to Discord VC (via the OpenClaw gateway — no separate credentials needed). Can also reverse-engineer any audio track into stems, samples, and generative programs.

> **New here?** Read [docs/ONBOARDING.md](docs/ONBOARDING.md) for a ground-up introduction.

---

## ⚠️ SESSION SAFETY — READ THIS FIRST

**Rendering MUST run as a sub-agent or background process, never inline in your main session.**

The offline renderer (`chunked-render.mjs` / `offline-render-v2.mjs`) runs a tight audio-processing loop that blocks the Node.js event loop. If you run it in your main OpenClaw session, **it will kill the gateway after ~30 seconds** (the heartbeat timeout).

```
✅ Correct: spawn a sub-agent or use background exec
❌ Wrong:   run the renderer inline in your main conversation
```

**Always do this:**
```bash
# Background exec with timeout
exec background:true timeout:120 command:"node src/runtime/chunked-render.mjs src/compositions/my-track.js output/my-track.wav 20"
```

**Or spawn a sub-agent:**
```
sessions_spawn task:"Render strudel-music composition: node src/runtime/chunked-render.mjs ..."
```

This is the #1 way to break things. Don't skip this.

---

## Quick Start

```bash
# 1. Setup
cd ~/.openclaw/workspace/strudel-music
npm run setup              # installs deps + downloads samples (~11MB)

# 2. Verify
npm test                   # 12-point smoke test

# 3. Render
node src/runtime/chunked-render.mjs assets/compositions/fog-and-starlight.js output/fog.wav 16
ffmpeg -i output/fog.wav -codec:a libmp3lame -b:a 192k output/fog.mp3
```

## Commands

| Invocation | What it does |
|---|---|
| `/strudel <prompt>` | Compose from natural language — mood, scene, genre, instruments |
| `/strudel play <name>` | Stream a saved composition into Discord VC |
| `/strudel list` | Show available compositions with metadata |
| `/strudel samples` | Manage sample packs (list, download, add) |
| `/strudel concert <tracks...>` | Play a setlist in Discord VC |

### Composition Workflow

1. Parse prompt → select mood, key, tempo, instruments (see `references/mood-parameters.md`)
2. Write a `.js` composition using Strudel pattern syntax
3. Render (in background!):
   ```bash
   node src/runtime/chunked-render.mjs <file> <output.wav> <cycles> [chunkSize]
   ```
4. Convert to MP3:
   ```bash
   ffmpeg -i output.wav -codec:a libmp3lame -b:a 192k output.mp3
   ```
5. Post the MP3 as attachment or stream to Discord VC

### Discord VC Streaming

```bash
node src/runtime/offline-render-v2.mjs assets/compositions/combat-assault.js /tmp/track.wav 12 140
ffmpeg -i /tmp/track.wav -ar 48000 -ac 2 /tmp/track-48k.wav -y
node scripts/vc-play.mjs /tmp/track-48k.wav
```

WSL2 users: enable mirrored networking (`networkingMode=mirrored` in `.wslconfig`) or VC streaming will fail silently (NAT breaks Discord's UDP voice protocol).

## Sample Management

### Directory Layout

Samples live in `samples/`. Any directory of WAV files is auto-discovered.

```
samples/
├── strudel.json          ← sample map (pitch info, paths)
├── kick/
│   └── kick.wav
├── hat/
│   └── hat.wav
├── bass_Cs1/
│   └── bass_Cs1.wav      ← pitched sample (root: C#1)
├── synth_lead/
│   └── synth_lead.wav     ← pitched sample (root: C#3, declared in strudel.json)
└── bloom_kick/
    └── bloom_kick.wav     ← from audio deconstruction
```

### strudel.json Format

Maps sample names to files with optional root note declarations. The renderer uses this as the authoritative source for pitch detection.

```json
{
  "_base": "./",
  "kick": { "0": "kick/kick.wav" },
  "bass_Cs1": { "cs1": "bass_Cs1/bass_Cs1.wav" },
  "synth_lead": { "cs3": "synth_lead/synth_lead.wav" }
}
```

- Keys with note suffixes (`_Cs1`, `_D2`) declare the root pitch
- Unpitched samples use `"0"` as the key
- Always declare root notes for pitched samples — without it, the renderer defaults to C4, causing wrong transpositions (see [docs/KNOWN-PITFALLS.md](docs/KNOWN-PITFALLS.md#3-root-note-detection-defaults))

### Managing Packs

```bash
bash scripts/samples-manage.sh list              # show installed packs
bash scripts/samples-manage.sh add <url>          # download from URL
bash scripts/samples-manage.sh add ~/my-samples/  # add local directory
```

Ships with **dirt-samples** (153 WAVs, CC-licensed). Security: downloads enforce size limits (`STRUDEL_MAX_DOWNLOAD_MB`, default 10GB), MIME validation, optional host allowlist (`STRUDEL_ALLOWED_HOSTS`).

## Composition Guide

### Pattern Basics

**CC0 / Free packs (just download and drop in `samples/`):**
- [Dirt-Samples](https://github.com/tidalcycles/Dirt-Samples) — 800+ samples (full pack, we ship a subset)
- [Signature Sounds – Homemade Drum Kit](https://signalsounds.com) (CC0) — 150+ one-shots
- [Looping – Synth Pack 01](https://looping.com) (CC0) — synth one-shots + loops
- [artgamesound.com](https://artgamesound.com) — CC0 searchable aggregator

**Your own packs:** Export from any DAW (Ableton, FL Studio, M8 tracker, etc.) as WAV directories. Strudel doesn't care where they came from — it's just WAV files in folders.

**Named banks** (Strudel built-in, requires CDN access):
```javascript
sound("bd sd cp hh").bank("RolandTR909")
sound("bd sd hh oh").bank("LinnDrum")
```

### WSL2 Note

If running on WSL2 and streaming to Discord VC, enable **mirrored networking**:

```ini
# %USERPROFILE%\.wslconfig
[wsl2]
networkingMode=mirrored
```

Then `wsl --shutdown` and relaunch. Without this, WSL2's NAT breaks Discord's UDP voice protocol — the bot joins the channel but no audio flows because IP discovery packets can't traverse the NAT return path. Mirrored mode eliminates the NAT by putting WSL2 directly on the host's network stack.

This only affects VC streaming. Offline rendering and file posting work in any networking mode.

## Platform Requirements

Two tiers, depending on what you need:

### Compose & Render (JS-only)
- **Node.js 18+** (22+ recommended for stable `OfflineAudioContext`)
- **ffmpeg** (MP3/Opus conversion)
- Works everywhere — x86_64, ARM64, WSL2, bare metal, containers.
- No Python. No GPU. No ML stack.

### Full Pipeline (audio deconstruction with Demucs)
Everything above, plus:
- **Python 3.10+**
- **pip packages:** `demucs`, `librosa`, `numpy`, `scipy`, `scikit-learn`, `torch`
- ~2GB disk for PyTorch + Demucs model weights (downloaded on first run)
- **Optional:** NVIDIA GPU + CUDA toolkit for ~5× Demucs speedup

Install the Python deps:
```bash
pip install demucs librosa numpy scipy scikit-learn torch
```

If Python deps are missing, composition and rendering still work — you just can't do stem extraction. The skill should fail gracefully with a message, not a stack trace.

---

## Full Pipeline (Audio Deconstruction)

If you have an MP3 and want to extract instruments from it, build sample racks, and compose with the extracted material — that's the full pipeline. It goes:

```
MP3 → Demucs (stem separation) → librosa (analysis) → sample slicing → Strudel composition → render → MP3
```

**This is a 4–8 minute process for a typical track.** See `docs/pipeline.md` for the complete stage-by-stage breakdown with commands, timings, and resource requirements.

### Quick version

```bash
# 1. Separate stems (Python/Demucs)
python -m demucs input.mp3 --out ./stems

# 2. Analyze + slice (see docs/pipeline.md for details)
# Currently semi-manual — analysis scripts in development

# 3. Write composition referencing sliced samples
# 4. Render
bash scripts/dispatch.sh render my-composition.js 16 120

# 5. Convert
ffmpeg -i output.wav -c:a libmp3lame -q:a 2 output.mp3 -y
```

### Timings (ballpark)

| Stage | CPU estimate | GPU estimate |
|-------|-------------|-------------|
| Demucs stem separation | ~15s/min of audio | ~3s/min of audio |
| Audio analysis (per stem) | ~10–20s | ~10–20s |
| Sample slicing | ~5s | ~5s |
| Composition | instant (human/AI writes JS) | instant |
| Rendering | ~30–60s/min of output | ~30–60s/min of output |
| MP3 conversion | ~5s | ~5s |

**Total (4-min track, CPU):** 4–8 minutes. **Compose + render only (no Demucs):** 2–3 minutes.

---

## ⚠️ Session Safety — READ THIS

> **The full pipeline takes 4–8 minutes. Composition + render alone takes 2–3 minutes.**
>
> **DO NOT** run this inline in a Discord channel interaction or primary OpenClaw session.
> The 30-second response timeout will kill the process mid-render. There is no supervisor to recover. The skill will appear broken — silence, no output, no error message.

### How to run safely

**From an OpenClaw agent (correct):**
```javascript
sessions_spawn({
  task: "Render strudel composition: /strudel dark ambient tension, 65bpm",
  mode: "run",
  runTimeoutSeconds: 600  // 10 minutes — generous for full pipeline
})
```

**Background process (also correct):**
```bash
exec({ command: "bash scripts/dispatch.sh render ...", background: true })
```

**Direct CLI (fine for testing):**
```bash
bash scripts/dispatch.sh render assets/compositions/fog-and-starlight.js 16 72
```

**What to tell the user:** "Rendering takes a few minutes — I'll post the audio when it's ready." Don't leave them hanging with no feedback.

### What NOT to do

```javascript
// WRONG — will timeout after 30s in Discord context
exec({ command: "bash scripts/dispatch.sh render ..." })

// WRONG — blocking the main session for minutes
// (anything inline that takes >30s)
```

---

## Learning Resources

Detailed documentation lives in `docs/`:

| Document | What it covers |
|----------|---------------|
| [`docs/pipeline.md`](docs/pipeline.md) | Full pipeline stages, commands, timings, resource requirements, system dependencies |
| [`docs/composition-guide.md`](docs/composition-guide.md) | Practical composition lessons — mini-notation pitfalls, the space-vs-angle-bracket rule, `.slow()` interactions, debugging hap explosions |
| [`docs/TESTING.md`](docs/TESTING.md) | Testing strategy — smoke tests, cross-platform validation, quality gates, naive install testing |

**Start with `composition-guide.md`** if you're writing patterns. The space-separated vs angle-bracket distinction is the #1 source of bugs (gain explosions, distortion, memory crashes). The guide covers it with real case studies.

---

## How It Works

The offline renderer uses **node-web-audio-api** (Rust-based Web Audio for Node.js) for real audio synthesis:

1. **Pattern evaluation** — `@strudel/core` + `@strudel/mini` + `@strudel/tonal` parse pattern code into timed "haps"
2. **Audio scheduling** — Each hap becomes either:
   - An **oscillator** (sine/saw/square/triangle) with ADSR envelope, biquad filter, stereo pan
   - A **sample** (AudioBufferSourceNode) from the samples directory, with pitch shifting
3. **Offline rendering** — `OfflineAudioContext.startRendering()` produces complete audio
4. **Output** — 16-bit stereo WAV at 44.1kHz → ffmpeg → MP3/Opus

**Note on mini notation:** The renderer explicitly calls `setStringParser(mini.mini)` after import because Strudel's npm dist bundles duplicate the Pattern class across modules. Same class of bug as [openclaw#22790](https://github.com/openclaw/openclaw/issues/22790).

## Composition Reference

### Tempo
```javascript
setcpm(120/4)  // 120 BPM

stack(
  s("bd sd [bd bd] sd").gain(0.4),           // drums (samples)
  s("[hh hh] [hh oh]").gain(0.2),            // hats
  note("c3 eb3 g3 c4")                       // melody
    .s("sawtooth")
    .lpf(sine.range(400, 2000).slow(8))      // filter sweep
    .attack(0.01).decay(0.3).sustain(0.2)    // ADSR envelope
    .room(0.4).delay(0.2)                    // space
    .gain(0.3)
)
```

### Mini Notation Quick Ref

| Syntax | Meaning |
|---|---|
| `"a b c d"` | Sequence (one per beat) |
| `"[a b]"` | Subdivide (two in one beat) |
| `"<a b c>"` | Alternate per cycle (slowcat) |
| `"a*3"` | Repeat |
| `"~"` | Rest / silence |
| `.slow(2)` / `.fast(2)` | Time stretch |
| `.euclid(3,8)` | Euclidean rhythm |

### Mood → Parameter Decision Tree

| Mood | Tempo | Key/Scale | Character |
|---|---|---|---|
| tension | 60-80 | minor/phrygian | Low cutoff, sparse, drones |
| combat | 120-160 | minor | Heavy drums, fast, distorted |
| peace | 60-80 | pentatonic/major | Warm, slow, ambient |
| mystery | 70-90 | whole tone | Reverb, sparse |
| victory | 110-130 | major | Bright, fanfare |
| ritual | 45-60 | dorian | Organ drones, chant |

Full tree: `references/mood-parameters.md`. Production techniques: `references/production-techniques.md`.

### ⚠️ Critical Pitfall: Gain Patterns

Use `<>` (slowcat) for sequential values, NOT spaces:

```javascript
// ❌ WRONG — all values play simultaneously, causes clipping
s("kick").gain("0.3 0.3 0.5 0.3")

// ✅ RIGHT — one value per cycle
s("kick").gain("<0.3 0.3 0.5 0.3>")
```

Full list: [docs/KNOWN-PITFALLS.md](docs/KNOWN-PITFALLS.md)

### Loudness Validation

Always check after rendering:
```bash
ffmpeg -i output.wav -af loudnorm=print_format=json -f null - 2>&1 | grep -E "input_i|input_tp"
```
Target: -16 to -10 LUFS, true peak below -1 dBTP. Above -5 LUFS = something is wrong.

## Audio Deconstruction Pipeline

Full pipeline docs: [references/integration-pipeline.md](references/integration-pipeline.md)

```
Audio → Demucs (stems) → librosa (analysis) → strudel.json → Composition → Render
```

1. **Stem separation** — Demucs splits audio into vocals, drums, bass, other
2. **Analysis** — librosa extracts pitches, onsets, rhythm patterns
3. **Sample mapping** — Results written to `strudel.json` with root notes
4. **Two paths:**
   - **Grammar extraction** (through-composed music) → generative program capturing statistical DNA
   - **Sample-based** (stanzaic/repetitive music) → stem slices played back through Strudel

Requires Python stack: `uv init && uv add demucs librosa scikit-learn soundfile`

## File Structure

```
src/runtime/
  chunked-render.mjs      — Chunked offline renderer (avoids OOM on long pieces)
  offline-render-v2.mjs    — Core offline renderer
  smoke-test.mjs           — 12-point smoke test
scripts/
  download-samples.sh      — Download dirt-samples (idempotent)
  samples-manage.sh        — Sample pack manager
  vc-play.mjs              — Stream audio to Discord VC
samples/                   — Sample packs + strudel.json (gitignored)
assets/compositions/       — 15 original compositions
src/compositions/          — Audio deconstructions
references/                — Mood trees, techniques, architecture
docs/
  KNOWN-PITFALLS.md        — Critical composition pitfalls
  ONBOARDING.md            — Machine-actor onboarding guide
```

## Renderer Internals

Uses **node-web-audio-api** (Rust-based Web Audio for Node.js). No browser, no Puppeteer.

The renderer calls `setStringParser(mini.mini)` after import because Strudel's npm dist bundles duplicate the `Pattern` class across modules — the mini notation parser registers on a different copy than the one used by `note()` and `s()`.

All synthesis is local and offline via `OfflineAudioContext`: oscillators, biquad filters, ADSR envelopes, `AudioBufferSourceNode` for samples, dynamics compression, stereo panning. Output: 16-bit stereo WAV at 44.1kHz.

---

## Known Platform Issues

| Platform | Issue | Workaround |
|---|---|---|
| ARM64 (all) | PyTorch CPU-only, no CUDA | Expected — Demucs runs ~0.25× realtime |
| ARM64 (all) | `torchaudio.save()` fails | Patch `demucs/audio.py` to use `soundfile.write()` (see First-Time Setup) |
| ARM64 (all) | `torchcodec` build fails | Not needed — skip it, Demucs works without it |
| WSL2 | Discord VC silent (NAT blocks UDP) | Enable mirrored networking in `.wslconfig` |
| All | Strudel `mini` parser not registered | Renderer calls `setStringParser(mini.mini)` — already handled |

---

## 🔒 Security Model

Strudel compositions are JavaScript files executed by Node.js. They have the same access as any Node.js script:
- **Filesystem**: read/write access to the working directory
- **Environment**: can read environment variables
- **Network**: can make HTTP requests

**For untrusted compositions:**
- Run in a container or VM with no sensitive credentials in the environment
- Use OpenClaw's sub-agent isolation (each sub-agent gets its own process)
- Review composition code before rendering

**For your own compositions:** No special precautions needed — you wrote the code.

This is the same trust model as any programming language skill. The renderer itself is safe; the risk is in what compositions you choose to run.

### Discord Integration

This skill uses OpenClaw's built-in Discord voice channel support for streaming. **No separate `BOT_TOKEN`, `DISCORD_TOKEN`, or any Discord credentials are required.** OpenClaw handles all Discord authentication and connection management. The skill simply produces audio files and hands them to OpenClaw's voice subsystem.

### npm install safety

`package.json` contains no `postinstall`, `preinstall`, or lifecycle hooks. `npm run setup` runs `npm install` + `scripts/download-samples.sh` (downloads CC0 sample packs from known URLs).

### What `scripts/download-samples.sh` fetches

The download script sparse-clones [tidalcycles/Dirt-Samples](https://github.com/tidalcycles/Dirt-Samples) from GitHub (CC-licensed) — specifically these directories: `bd sd hh oh cp cr ride rim mt lt ht cb 808bd 808sd 808hc 808oh`. This fetches ~153 WAV files (~11MB total). The script is idempotent (skips if samples already exist).

### What `scripts/samples-manage.sh` does

The sample manager downloads additional packs from user-specified URLs with safety controls:
- **Size limit**: configurable via `STRUDEL_MAX_DOWNLOAD_MB` (default: 10GB)
- **Host allowlist**: optional `STRUDEL_ALLOWED_HOSTS` (comma-separated; empty = allow all)
- **MIME validation**: checks downloaded files are audio or archive types
- **Path traversal protection**: validates extracted paths don't escape the samples directory (zip-slip protection)

---

## Concurrency

Only one render should be active per session at a time. If a user requests `/strudel clone` while a previous render is in progress:
1. Check for active sub-agents using `subagents(action=list)`
2. If a strudel render is running, respond: "🎵 A render is already in progress. Please wait for it to complete."
3. Do not dispatch a second render — disk and memory contention can cause artifacts or failures.

**Why:** Concurrent renders with default output paths both write to `output.wav`, causing the second to overwrite the first. Even with explicit paths, two simultaneous `OfflineAudioContext` processes double memory usage. Sample loading is per-process (no shared cache), so there's no corruption risk — but disk I/O contention on the output write is real.
