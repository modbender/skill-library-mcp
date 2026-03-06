# Pipeline

> **⚠️ SESSION SAFETY WARNING**
>
> The full pipeline takes **4–8 minutes** for a typical track. Do NOT run it in:
> - A **primary/main OpenClaw session** — it will block the agent for minutes and may timeout
> - A **Discord channel interaction** — the 30-second response timeout will kill the process mid-render
>
> **Run it via:**
> - **Sub-agent**: `sessions_spawn` with `mode: "run"` and adequate `runTimeoutSeconds` (≥600)
> - **Background process**: `exec` with `background: true`
> - **Direct CLI**: `bash scripts/dispatch.sh render <file.js> [cycles] [bpm]`
>
> If you skip this, the skill will appear broken — the process dies silently after 30s and produces no output. There is no supervisor to recover. Most users won't know what happened.

## Overview

```
Audio file
  │
  ├─ 1. Demucs stem separation (Python, GPU-heavy)
  │     → vocals.wav, drums.wav, bass.wav, other.wav
  │
  ├─ 2. Audio analysis (Python — librosa)
  │     → onset times, pitch data, MFCC clusters, section boundaries
  │
  ├─ 3. Sample slicing & instrument rack building
  │     → phrase-level WAV slices in samples/<trackname>/
  │
  ├─ 4. Composition (JS — Strudel pattern code)
  │     → .js file with stack(), note(), s() patterns
  │
  ├─ 5. Rendering (JS — chunked Float32 mixer)
  │     → 16-bit stereo WAV at 44.1kHz
  │
  └─ 6. MP3 conversion (ffmpeg)
        → final .mp3
```

## Stages

### 1. Stem Separation — Demucs

**What:** Splits a mixed audio file into four stems (vocals, drums, bass, other/synths) using Meta's Hybrid Transformer model.

**Tools:** Python, PyTorch, [Demucs](https://github.com/facebookresearch/demucs)

**Command:**
```bash
python -m demucs --two-stems=vocals input.mp3   # vocal isolation
python -m demucs input.mp3                        # full 4-stem split
```

**Hallucination detection:** Phantom stems (e.g., "drums" extracted from a voice-only source) are discarded when they measure >20dB below the loudest stem.

### 2. Audio Analysis

**What:** Extracts musical structure from each stem — onset detection, pitch tracking (pYIN), MFCC clustering for timbre grouping, spectral band splitting for drums (kick <200Hz, snare 200–6kHz, hat >6kHz).

**Tools:** Python, [librosa](https://librosa.org), numpy, scipy, scikit-learn

**Output:** Per-stem data — note onsets, pitches with confidence, amplitude-derived velocity, section boundaries, scale/mode detection, density curves.

### 3. Sample Slicing

**What:** Cuts stems into phrase-level WAV slices at musically meaningful boundaries (onset clusters, section breaks). Builds an instrument rack — a directory of named WAV files that Strudel's `s()` function can address.

**Tools:** Python (scipy for WAV I/O), librosa (for boundary detection)

**Output:** `samples/<trackname>/` directory with numbered/named slices.

### 4. Composition

**What:** A Strudel `.js` file that arranges the extracted data into a playable pattern. Two paths:

- **Grammar extraction** (through-composed music): Statistical DNA — scale, density, rhythm probability, melodic motion — generates *similar but new* music.
- **Sample-based** (stanzaic/repetitive music): Direct playback of sliced stems through Strudel's sample engine.

**Tools:** Human or AI writes JavaScript. No computation cost.

### 5. Rendering

**What:** Evaluates the Strudel pattern in an `OfflineAudioContext` (via `node-web-audio-api`). Real oscillators, biquad filters, ADSR envelopes, dynamics compression, stereo panning, sample playback via `AudioBufferSourceNode`. Chunked Float32 mixing to manage memory.

**Tools:** Node.js, `node-web-audio-api`, `@strudel/core`, `@strudel/mini`, `@strudel/webaudio`

**Command:**
```bash
node src/runtime/offline-render-v2.mjs <input.js> <output.wav> <cycles> <bpm>
```

**Output:** 16-bit stereo WAV at 44.1kHz.

### 6. MP3 Conversion

**What:** Converts rendered WAV to MP3 (or Opus for VC streaming).

**Tools:** ffmpeg

**Command:**
```bash
ffmpeg -i output.wav -c:a libmp3lame -q:a 2 output.mp3 -y
```

## Timings

Benchmarked on real tracks. Your mileage varies with hardware and track complexity.

| Stage | Estimate | Notes |
|-------|----------|-------|
| Demucs (CPU) | ~15s per minute of audio | 3:39 track ≈ 55s |
| Demucs (GPU/CUDA) | ~3s per minute of audio | NVIDIA recommended |
| Audio analysis | ~10–20s per stem | 4 stems × 10–20s |
| Sample slicing | ~5s | I/O bound |
| Composition | instant | Human/AI writes JS |
| Rendering | ~30–60s per minute of output | 5:16 render ≈ 120s |
| MP3 conversion | ~5s | ffmpeg, trivial |

**Total for a 4-minute track (CPU):** 4–8 minutes end-to-end.

**Composition + render only (no Demucs):** 2–3 minutes — this path is JS-only, no Python required.

## Resource Requirements

| Resource | Demucs | Renderer | Combined |
|----------|--------|----------|----------|
| RAM | 200–500 MB | 50–150 MB | 300–650 MB |
| Disk | 100–500 MB (stems + samples) | ~50 MB (WAV output) | 150–550 MB |
| GPU | Optional (CUDA for 5× speedup) | Not used | — |
| CPU | Heavy (PyTorch inference) | Moderate (Float32 mixing) | — |

## System Dependencies

**Required (all paths):**
- Node.js 20+ (22+ recommended for stable `OfflineAudioContext`)
- ffmpeg (MP3/Opus conversion, VC streaming)

**Required (composition + render only — JS path):**
- Just Node.js and ffmpeg. No Python.

**Required (full pipeline with Demucs):**
- Python 3.10+
- pip packages: `demucs`, `librosa`, `numpy`, `scipy`, `scikit-learn`, `torch`
- ~2GB disk for PyTorch + Demucs model weights (first run)

**Optional:**
- NVIDIA GPU + CUDA toolkit (5× Demucs speedup)
- `@discordjs/voice` deps for VC streaming (sodium-native, opusscript)

## Running the Pipeline

### Composition + render (JS only, no Python)

```bash
# Write or select a composition
bash scripts/dispatch.sh render assets/compositions/fog-and-starlight.js 16 72
```

### Full pipeline (Demucs → analysis → composition → render)

```bash
# 1. Separate stems
python -m demucs input.mp3 --out ./stems

# 2. Analyze + slice (scripts in development)
# Currently manual — see src/compositions/ for examples

# 3. Write composition referencing sliced samples
# 4. Render
bash scripts/dispatch.sh render my-composition.js 16 120
```

### From an OpenClaw agent

```javascript
// CORRECT — spawn a sub-agent
sessions_spawn({
  task: "Render strudel composition fog-and-starlight",
  mode: "run",
  runTimeoutSeconds: 600
})

// WRONG — will timeout after 30s in Discord context
exec({ command: "bash scripts/dispatch.sh render ..." })
```
