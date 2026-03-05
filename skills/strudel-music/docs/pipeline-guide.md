# Audio Deconstruction Pipeline Guide

**strudel-music** can reverse-engineer any audio track into a playable Strudel composition. This document describes the full pipeline from input MP3 to rendered output.

> **📖 See also:** [README.md](../README.md) for quick start and slash commands.

---

## ⚠️ CRITICAL: Session Management

> **DO NOT run this pipeline in your main agent session, Discord message handler, or any synchronous context.**

The full pipeline takes **10–15 minutes** for a typical 4–5 minute track. OpenClaw's EventQueue has a **30-second timeout** — if the pipeline blocks the main thread, the gateway will stun and become unresponsive. Recovery requires a gateway restart.

**Always run via sub-agent:**

```javascript
sessions_spawn({
  task: "Run strudel deconstruction pipeline on /path/to/track.mp3",
  mode: "run",
  runTimeoutSeconds: 1200  // 20 minutes — generous margin
})
```

**What happens if you ignore this:**
1. Pipeline starts in main session
2. First long operation (Demucs, ~80s) blocks the event loop
3. EventQueue timeout fires at 30s
4. Gateway enters stunned state — all sessions freeze
5. Manual `openclaw gateway restart` required
6. Any in-flight work across all sessions is lost

This is not theoretical. It will happen every time.

---

## Pipeline Overview

```
Input MP3
  │
  ▼
Demucs Stem Separation (4 stems: vocals, drums, bass, other)
  │
  ▼
Per-Stem Analysis
  ├── RMS energy measurement
  └── Hallucination detection (20dB threshold)
  │
  ▼
Global Analysis
  ├── BPM detection (librosa)
  └── Key detection (Krumhansl-Schmuckler)
  │
  ▼
Per-Stem Feature Extraction
  ├── Onset detection
  ├── Pitch detection (pYIN)
  └── MFCC clustering
  │
  ▼
Bar-Aligned Slicing
  ├── Beat grid quantization
  ├── 8-bar phrase segmentation
  └── WAV export per stem per slice
  │
  ▼
Energy Mapping
  ├── Per-slice RMS normalization
  └── Section energy curve (for arrangement)
  │
  ▼
Instrument Rack Assembly
  ├── strudel.json manifest
  └── Sample directory structure
  │
  ▼
Composition
  ├── Arrangement (section ordering, layering)
  ├── Gain automation (energy-matched)
  └── .js composition file
  │
  ▼
Chunked Render (OfflineAudioContext)
  │
  ▼
Post-Render Validation
  ├── Loudness (LUFS) check
  ├── True peak (dBTP) check
  └── Silence gap detection
  │
  ▼
MP3 Output (ffmpeg)
```

---

## Pipeline Stages

### 1. Input

**Input:** MP3, WAV, FLAC, or any ffmpeg-decodable audio file.

**Output:** Normalized WAV for Demucs ingestion.

If the source isn't WAV, ffmpeg converts it first:
```bash
ffmpeg -i input.mp3 -ar 44100 -ac 2 input.wav
```

### 2. Demucs Stem Separation

**Input:** Stereo WAV.

**Output:** Four stem WAVs — `vocals.wav`, `drums.wav`, `bass.wav`, `other.wav`.

Uses Meta's [Demucs](https://github.com/facebookresearch/demucs) Hybrid Transformer model (`htdemucs`). Separates the mix into four stems with high fidelity.

```bash
python -m demucs --two-stems=None -n htdemucs input.wav -o output/
```

**Timings (measured on DGX Spark, ARM64 CPU):**
| Track Length | Time    | Realtime Factor |
|-------------|---------|-----------------|
| 3:39        | ~50s    | ~0.23×          |
| 5:17        | ~80s    | ~0.25×          |

**Platform notes:**
- **ARM64 (DGX Spark, Apple Silicon):** CPU-only. Demucs does not support NVIDIA Grace Blackwell GPU via PyTorch yet. The `soundfile` package may need a manual patch for ARM64 libsndfile.
- **x86_64 + NVIDIA GPU:** CUDA acceleration available. Expect 3–5× speedup over CPU (~0.07× realtime).
- **x86_64 + Intel:** CPU-only, comparable to ARM64 performance.

### 3. Per-Stem Analysis

**Input:** Four stem WAVs.

**Output:** RMS levels per stem; list of valid (non-hallucinated) stems.

#### RMS Energy Measurement
Compute RMS energy for each stem to determine relative loudness:
```python
rms = librosa.feature.rms(y=audio)[0].mean()
```

#### Hallucination Detection
Demucs will always produce four stems, even if the source lacks an instrument (e.g., "drums" from a solo vocal track). Hallucinated stems are identified by a **20dB-below-loudest** threshold:

```python
loudest_rms = max(stem_rms_values)
threshold = loudest_rms * 0.1  # -20dB
valid_stems = [s for s in stems if s.rms >= threshold]
```

Discarded stems are logged but not processed further. This prevents the pipeline from building empty sample banks or composing with silence.

**Timing:** ~2s (negligible — pure numpy).

### 4. BPM & Key Detection

**Input:** Full mix or loudest stem WAV.

**Output:** BPM (float), musical key (e.g., "C# minor").

#### BPM Detection
```python
tempo, beats = librosa.beat.beat_track(y=audio, sr=sr)
```
Validated against onset density — if `beat_track` returns an implausible tempo (e.g., half or double), the onset-based estimate is preferred.

#### Key Detection
Krumhansl-Schmuckler algorithm on the chromagram:
```python
chroma = librosa.feature.chroma_cqt(y=audio, sr=sr)
# Correlate with major/minor profiles
```

**Timing:** ~5s total.

**Example output (Frisson):** 129.2 BPM, C# minor.

### 5. Onset Extraction

**Input:** Per-stem WAVs.

**Output:** Onset times (seconds) per stem.

Detects note/hit boundaries for each valid stem:
```python
onsets = librosa.onset.onset_detect(y=stem, sr=sr, units='time')
```

Different parameters per stem type:
- **Drums:** Lower `delta` threshold (more sensitive to transients)
- **Bass:** Energy-based detection (spectral flux less reliable for low frequencies)
- **Vocals/Other:** Default spectral flux

**Timing:** ~10–30s total across all stems (depends on track length and stem count).

### 6. Pitch Detection (pYIN)

**Input:** Tonal stem WAVs (vocals, bass, other — not drums).

**Output:** F0 pitch contour per stem.

Uses probabilistic YIN (`pYIN`) for robust pitch tracking:
```python
f0, voiced_flag, voiced_prob = librosa.pyin(
    y=stem, sr=sr,
    fmin=librosa.note_to_hz('C2'),
    fmax=librosa.note_to_hz('C7')
)
```

Pitch data feeds into:
- MIDI note extraction (for grammar compositions)
- Melodic motion analysis (stepwise vs. leaps)
- Register distribution (for instrument assignment)

**Timing:** ~10–20s per tonal stem.

### 7. MFCC Clustering

**Input:** Per-stem audio.

**Output:** Timbral clusters (for identifying sections with similar sonic character).

Extracts Mel-frequency cepstral coefficients and clusters them:
```python
mfccs = librosa.feature.mfcc(y=stem, sr=sr, n_mfcc=13)
# K-means or agglomerative clustering on MFCC frames
```

Used to identify:
- Verse vs. chorus timbral shifts
- Breakdown sections (reduced spectral complexity)
- Build-ups (increasing spectral density)

**Timing:** ~10s total.

### 8. Bar-Aligned Slicing

**Input:** Per-stem WAVs, BPM, beat grid.

**Output:** WAV files per stem per slice (e.g., `drums/n0.wav` through `drums/n20.wav`).

Quantizes audio to a beat grid and slices at **8-bar boundaries**:

```
Track @ 129.2 BPM, 168 bars total
→ 21 slices of 8 bars each
→ Each slice = 32 beats = ~14.86 seconds
→ 4 stems × 21 slices = 84 WAV files
```

The 8-bar phrase length is chosen because:
1. Most Western music uses 4- or 8-bar phrases
2. Long enough to capture musical gestures (not just individual hits)
3. Short enough for flexible arrangement (reorder, layer, skip)

**Output structure:**
```
samples/frisson/
  vocals/n0.wav ... n20.wav
  drums/n0.wav ... n20.wav
  bass/n0.wav ... n20.wav
  other/n0.wav ... n20.wav
  strudel.json
```

**Timing:** ~20s (mostly I/O — writing 84 WAV files).

### 9. Energy Mapping

**Input:** Per-slice WAVs.

**Output:** Energy curve (RMS per slice per stem), normalized gain values.

Maps the energy contour of the original track so the composition can reproduce dynamic shape:

```
Slice   Drums RMS   Vocal RMS   Energy Level
n0      0.82        0.45        HIGH
n7      0.12        0.00        LOW (breakdown)
n11     0.95        0.78        PEAK
n20     0.30        0.00        TAIL
```

Energy values translate directly to `gain()` parameters in the Strudel composition.

**Timing:** ~2s (pure computation).

### 10. Instrument Rack Assembly

**Input:** Slice WAVs, energy map.

**Output:** `strudel.json` manifest, organized sample directory.

Generates the `strudel.json` that maps sample names to file paths:

```json
{
  "frisson-vocals": { "n0": "vocals/n0.wav", "n1": "vocals/n1.wav", ... },
  "frisson-drums":  { "n0": "drums/n0.wav", "n1": "drums/n1.wav", ... },
  "frisson-bass":   { "n0": "bass/n0.wav", "n1": "bass/n1.wav", ... },
  "frisson-other":  { "n0": "other/n0.wav", "n1": "other/n1.wav", ... }
}
```

Strudel's `samples()` function reads this manifest to resolve `s("frisson-drums").n(7)` → `drums/n7.wav`.

**Timing:** ~1s.

### 11. Composition

**Input:** `strudel.json`, energy map, analysis data.

**Output:** `.js` Strudel composition file.

This stage is **manual or AI-assisted** — the agent (or human) writes a Strudel composition that:
- References the sample bank via `s("frisson-drums").n(k)`
- Follows the energy curve (quiet sections use breakdown slices, peaks use peak slices)
- Uses `clip(1)` to play each slice at full duration
- Orders sections into a musical arc (intro → drive → breakdown → rebuild → peak → outro)

**Example (from Frisson composition):**
```javascript
// Section: BREAKDOWN — drums vanish, pads take over
s("frisson-other").n(8).clip(1).gain(0.50)  // pure pads
.stack(
  s("frisson-bass").n(8).clip(1).gain(0.35)  // bass continues
)
```

**Timing:** Variable. 15–60 minutes for hand-crafted arrangement; 2–5 minutes for AI-assisted.

### 12. Chunked Render

**Input:** `.js` composition file.

**Output:** WAV file.

The chunked renderer (`src/runtime/chunked-render.mjs`) processes the composition in small cycle groups to avoid OOM on long compositions:

```bash
node src/runtime/chunked-render.mjs composition.js output.wav 17 4
#                                   ^^^^^^^^^^^^   ^^^^^^^^^^  ^^ ^
#                                   input file     output      cycles  chunk size
```

Each chunk renders independently via `OfflineAudioContext`, then chunks are concatenated into the final WAV. The renderer:
- Polyfills Web Audio APIs for Node.js (via `node-web-audio-api`)
- Loads samples from the `samples/` directory
- Evaluates the composition file (which is executable JavaScript)
- Renders stereo 44.1kHz 16-bit PCM

**Timings (DGX Spark, ARM64):**
| Composition Length | Render Time | Realtime Factor |
|-------------------|-------------|-----------------|
| 17 cycles (~4:13) | ~120s       | ~0.53× (1.9× realtime) |
| 8 cycles (~2:00)  | ~55s        | ~0.46× (2.2× realtime) |

Rendering is CPU-bound. Longer compositions scale linearly.

### 13. Post-Render Validation

**Input:** Rendered WAV.

**Output:** Pass/fail with diagnostic values.

Checks that the rendered audio meets quality standards:

| Check                  | Target           | Tool                          |
|-----------------------|------------------|-------------------------------|
| Integrated loudness   | -16 to -14 LUFS  | `ffmpeg -af loudnorm=print_format=json` |
| True peak             | < -1 dBTP        | `ffmpeg -af astats`           |
| Silence gaps          | None > 2s        | RMS windowed analysis         |
| Sample references     | All resolved     | Check render logs for 404s    |
| Duration              | Within ±5% of expected | Compare to `cycles × cycle_duration` |

**Timing:** ~5s.

### 14. MP3 Output

**Input:** Validated WAV.

**Output:** MP3 file.

```bash
ffmpeg -i output.wav -c:a libmp3lame -q:a 2 -ar 44100 -ac 2 output.mp3
```

`-q:a 2` produces ~190kbps VBR — good enough for Discord playback, small enough for reasonable file sizes (~1.4MB per minute).

**Timing:** ~3s.

---

## End-to-End Timing Reference

Measured from the Frisson deconstruction (5:17 source track, 129.2 BPM, DGX Spark ARM64 CPU):

| Stage                        | Time       |
|-----------------------------|------------|
| Demucs stem separation       | ~80s       |
| Per-stem RMS + hallucination | ~2s        |
| BPM & key detection          | ~5s        |
| Onset extraction (4 stems)   | ~20s       |
| Pitch detection (3 stems)    | ~30s       |
| MFCC clustering              | ~10s       |
| Bar-aligned slicing          | ~20s       |
| Energy mapping               | ~2s        |
| Instrument rack assembly     | ~1s        |
| Composition (AI-assisted)    | ~5 min     |
| Chunked render (17 cycles)   | ~120s      |
| Post-render validation       | ~5s        |
| MP3 conversion               | ~3s        |
| **Total (automated stages)** | **~5 min** |
| **Total (with composition)** | **~10–15 min** |

These timings assume CPU-only rendering on ARM64. x86_64 with NVIDIA GPU will see Demucs drop to ~15–25s; other stages are similar.

---

## Hardware Requirements

| Component        | Minimum                    | Recommended                  |
|-----------------|----------------------------|------------------------------|
| Node.js         | v18+                       | v25+ (native ESM, top-level await) |
| Python          | 3.10+ with UV              | 3.11+ (faster startup)      |
| ffmpeg          | Any recent build           | 6.0+ (loudnorm improvements) |
| RAM             | 4GB                        | 8GB+ (Demucs is memory-hungry) |
| Disk            | 2GB free (stems + slices)  | 5GB+ (multiple deconstructions) |
| CPU             | 4 cores                    | 8+ cores (Demucs parallelizes) |
| GPU (optional)  | —                          | NVIDIA with CUDA (Demucs 3–5× faster) |

### Platform-Specific Notes

**ARM64 (DGX Spark, Apple Silicon, Raspberry Pi 5):**
- Demucs runs CPU-only — no CUDA support on ARM64 currently
- `soundfile` package may need manual ARM64 libsndfile build/patch
- `node-web-audio-api` ships native ARM64 binaries — no issues

**x86_64 + NVIDIA GPU:**
- Install PyTorch with CUDA: `pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121`
- Demucs will auto-detect and use GPU
- Render stage remains CPU-only (Node.js `OfflineAudioContext`)

**x86_64 + Intel:**
- Fully functional, CPU-only
- Performance comparable to ARM64

---

## File Structure (Post-Pipeline)

```
samples/<track-name>/
  vocals/
    n0.wav ... n20.wav       ← 8-bar vocal slices
  drums/
    n0.wav ... n20.wav       ← 8-bar drum slices
  bass/
    n0.wav ... n20.wav       ← 8-bar bass slices
  other/
    n0.wav ... n20.wav       ← 8-bar synth/pad slices
  strudel.json               ← Sample manifest

src/compositions/
  <track-name>-clone.js      ← Sample-based composition

output/
  <track-name>.wav           ← Rendered audio
  <track-name>.mp3           ← Final output
```

---

## Glossary

| Term | Meaning |
|------|---------|
| **Stem** | An isolated instrument track (vocals, drums, bass, other) produced by Demucs |
| **Slice** | A time-aligned segment of a stem, typically 8 bars long |
| **Hallucination** | A stem Demucs produces that doesn't correspond to any real instrument in the source |
| **Grammar extraction** | Statistical fingerprinting of musical structure — produces generative rules, not specific notes |
| **Sample-based** | Playback of actual audio slices through Strudel's sample engine |
| **Cycle** | One full iteration of a Strudel pattern — duration depends on `setcpm()` |
| **Hap** | A single scheduled event in Strudel's pattern engine |
| **pYIN** | Probabilistic YIN — a pitch detection algorithm robust to noise |
| **MFCC** | Mel-Frequency Cepstral Coefficients — a compact representation of timbral character |
| **LUFS** | Loudness Units Full Scale — an integrated loudness measurement standard |
| **dBTP** | Decibels True Peak — the actual peak level accounting for inter-sample peaks |
