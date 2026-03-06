# Onboarding — Machine-Actor Guide for Strudel Music

*You're an OpenClaw instance that has never heard of Strudel. This document will teach you to make music.*

---

## ⚠️ SESSION SAFETY — READ THIS BEFORE ANYTHING ELSE

**Never run the renderer inline in your main session. It will kill your gateway.**

The offline renderer blocks the Node.js event loop during audio processing. If you run it in your main OpenClaw session, the heartbeat timeout (~30 seconds) will kill the gateway and you'll go dark.

**Always render in a sub-agent or background exec:**
```bash
# Background exec
exec background:true timeout:120 command:"node src/runtime/chunked-render.mjs <input.js> <output.wav> <cycles>"

# Or spawn a sub-agent
sessions_spawn task:"Render composition: node src/runtime/chunked-render.mjs ..."
```

This is not optional. This is not a suggestion. This will break things if you ignore it.

---

## What is Strudel?

[Strudel](https://strudel.cc) is a pattern-based music live-coding environment in JavaScript, inspired by [TidalCycles](https://tidalcycles.org) (Haskell). You describe music as **patterns** — sequences of events in time — and the engine turns them into audio.

```js
s("bd sd [bd bd] sd")          // kick-snare drum pattern
note("c3 eb3 g3 c4").s("saw")  // sawtooth arpeggio
```

It's declarative: you say *what* the music is, not *how* to play it. Patterns compose, layer, transform, and evolve over time.

## What is This Skill?

**strudel-music** lets you:

1. **Compose** — Write Strudel patterns from natural language prompts
2. **Render** — Offline synthesis to WAV/MP3 (no browser needed)
3. **Stream** — Play audio into Discord voice channels
4. **Deconstruct** — Take any audio file apart into stems, samples, and generative programs

The full pipeline: `Audio → Demucs (stems) → Analysis → Samples → Composition → Render`

## The Vocabulary

Think of music-making as language:

| Concept | Music Analogy | Strudel |
|---|---|---|
| **Words** | Individual sounds (kick, snare, synth note) | Samples in `samples/` directory |
| **Grammar** | How sounds combine (rhythm, melody, harmony) | Patterns: `"bd sd [bd bd] sd"` |
| **Sentences** | Musical phrases | `stack()` of layered patterns |
| **Narrative** | Song structure (intro → verse → chorus → outro) | `arrange()` with sections |

Samples are your vocabulary. Patterns are your grammar. Arrangement is your narrative.

---

## Setup

### 1. Install Node Dependencies

```bash
cd ~/.openclaw/workspace/strudel-music
npm run setup
```

This installs all Node packages and downloads the dirt-samples drum kit (~11MB, CC-licensed). Verify with:

```bash
npm test   # 12-point smoke test — all should pass
```

### 2. Platform Prerequisites

**Required:**
- **Node.js >= 20** — the runtime
- **ffmpeg** — audio format conversion (WAV → MP3/Opus)

```bash
# Check if you have them
node --version    # needs v20+
ffmpeg -version   # needs to exist
```

### 3. Optional: Python ML Stack (for audio deconstruction)

If you want to decompose audio files into stems and extract samples:

```bash
uv init && uv add demucs librosa scikit-learn soundfile
```

This gives you:
- **Demucs** — stem separation (vocals, drums, bass, other)
- **librosa** — pitch detection, onset analysis, rhythm extraction
- **scikit-learn** — pattern clustering
- **soundfile** — audio I/O

Not needed for composing and rendering — only for the deconstruction pipeline.

---

## Your First Composition

Create a file `src/compositions/my-first-track.js`:

```js
// My first Strudel composition
setcpm(120/4)  // 120 BPM

// Load samples from the samples directory
samples({ kick: 'samples/frkick/' })

stack(
  // Drums — real samples from disk
  s("kick").struct("x ~ ~ ~ x ~ ~ ~"),

  // Hi-hats — from dirt-samples
  s("hh*4").gain(0.2),

  // Bass — synthesized
  note("c2 ~ eb2 ~ g1 ~ c2 ~")
    .s("sawtooth")
    .lpf(400)
    .gain(0.3),

  // Pad — synthesized
  note("<c3 eb3 g3 bb3>")
    .s("triangle")
    .attack(0.5).release(1)
    .lpf(1200)
    .room(0.6)
    .gain(0.15)
)
```

## Your First Render

**Remember: background exec or sub-agent. Never inline.**

```bash
# Render to WAV (20 cycles ≈ 40 seconds at 120 BPM)
node src/runtime/chunked-render.mjs src/compositions/my-first-track.js output/my-first-track.wav 20

# Convert to MP3
ffmpeg -i output/my-first-track.wav -codec:a libmp3lame -b:a 192k output/my-first-track.mp3
```

### Validate Loudness

Always check after rendering:

```bash
ffmpeg -i output/my-first-track.wav -af loudnorm=print_format=json -f null - 2>&1 | grep -E "input_i|input_tp"
```

| Metric | Good | Problem |
|---|---|---|
| Integrated (LUFS) | -20 to -10 | > -5 (too hot) or < -25 (too quiet) |
| True Peak (dBTP) | < -1 | > 0 (clipping) |

---

## Pattern Language Crash Course

### Sequencing

```js
"a b c d"       // one per beat, 4 beats per cycle
"[a b] c d"     // a and b share the first beat
"a b ~ d"       // ~ is silence (rest)
"a*3 b"         // a plays 3 times, then b once
"<a b c>"       // alternate: a on cycle 1, b on cycle 2, c on cycle 3
```

### Layering

```js
stack(
  s("bd sd bd sd"),              // drums
  note("c3 g3").s("sawtooth"),   // bass
  note("c4 eb4 g4").s("sine")   // melody
)
```

### Expression

```js
.gain(0.4)                              // volume
.lpf(800)                               // low-pass filter
.lpf(sine.range(400, 4000).slow(8))     // animated filter sweep
.room(0.5).roomsize(4)                  // reverb
.delay(0.3).delaytime(0.25)             // echo
.pan(0.3)                               // stereo position
.attack(0.01).decay(0.2).sustain(0.5).release(0.3)  // ADSR envelope
```

### Structure (Song Sections)

```js
let intro = stack(pad, ambient)
let verse = stack(drums, bass, melody)
let chorus = stack(drums, bass, melody, lead).gain(1.1)

arrange(
  [8, intro],
  [16, verse],
  [8, chorus],
  [16, verse],
  [8, chorus]
).cpm(120/4)
```

### Sound Sources

- **Samples:** `s("bd")`, `s("hh")`, `s("kick")` — WAV files from `samples/`
- **Oscillators:** `.s("sine")`, `.s("sawtooth")`, `.s("square")`, `.s("triangle")` — synthesized
- **Pitched samples:** `note("c3").s("synth_lead")` — sample pitched via `strudel.json` root note

---

## The Full Pipeline (Audio Deconstruction)

If you have the Python ML stack installed, you can decompose any audio:

### Step 1: Stem Separation

Feed it an MP3 or WAV. Demucs separates it into 4 stems:

```bash
python -m demucs --two-stems=vocals input.mp3
# Or full 4-stem separation:
python -m demucs input.mp3
# Output: separated/htdemucs/input/{vocals,drums,bass,other}.wav
```

### Step 2: Analysis

librosa extracts musical information from each stem:

- **Drums** — onset detection, kick/snare/hat classification by spectral band
- **Bass/Lead** — pYIN pitch tracking, note segmentation, MIDI extraction
- **All stems** — tempo, beat grid, dynamics envelope

### Step 3: Sample Extraction

Stems are sliced into individual hits or phrases and organized into directories:

```
samples/
  my_track_kick/kick.wav
  my_track_snare/snare.wav
  my_track_bass_C2/bass_C2.wav
  my_track_lead_E3/lead_E3.wav
```

### Step 4: Map in strudel.json

Add entries so the renderer knows about them:

```json
{
  "my_track_kick": { "0": "my_track_kick/kick.wav" },
  "my_track_bass_C2": { "c2": "my_track_bass_C2/bass_C2.wav" },
  "my_track_lead_E3": { "e3": "my_track_lead_E3/lead_E3.wav" }
}
```

The key-value note mapping (`"c2"`, `"e3"`) tells the renderer the root pitch so `.note()` transpositions are accurate.

### Step 5: Compose

Write a Strudel composition using the extracted vocabulary:

```js
setcpm(140/4)

samples({
  kick: 'samples/my_track_kick/',
  bass: 'samples/my_track_bass_C2/'
})

stack(
  s("kick").struct("x ~ ~ ~ x ~ ~ ~"),
  note("c2 ~ g1 ~ c2 ~ eb2 ~").s("bass").gain(0.4)
)
```

### Step 6: Render

```bash
node src/runtime/chunked-render.mjs src/compositions/my-track.js output/my-track.wav 20
ffmpeg -i output/my-track.wav -codec:a libmp3lame -b:a 192k output/my-track.mp3
```

### Two Deconstruction Approaches

| Approach | Best for | What you get |
|---|---|---|
| **Grammar extraction** | Through-composed / non-repetitive music | Generative program: statistical DNA (scale, density, rhythm probability, melodic motion) that creates *new* music with the same character |
| **Sample-based** | Repetitive / stanzaic music (pop, folk) | Stem slices played back through Strudel — preserves original timbre and expression |

The hallucination detector auto-discards phantom stems (e.g., Demucs "finding" drums in a voice-only source) using a 20dB-below-loudest threshold.

---

## Known Pitfalls

Read [docs/KNOWN-PITFALLS.md](KNOWN-PITFALLS.md) — these will save you hours:

1. **Gain pattern syntax** — Use `<>` (slowcat) for sequential values, not spaces. Spaces = simultaneous = clipping.
2. **DJ voiceover in stems** — Source material with spoken intros contaminates pad slices.
3. **Root note defaults** — Undeclared samples default to C4, causing wrong transpositions.
4. **Loudness validation** — Always check LUFS/dBTP after rendering.

---

## Where to Learn More

- **Strudel docs:** <https://strudel.cc>
- **Strudel learn tutorial:** <https://strudel.cc/learn>
- **Mood → parameter decision tree:** `references/mood-parameters.md`
- **Production techniques:** `references/production-techniques.md`
- **Pattern transforms:** `references/pattern-transforms.md`
- **Sample packs catalog:** `references/cc-sample-packs-catalog.md`
- **TidalCycles (Haskell original):** <https://tidalcycles.org>

---

## Quick Reference Card

| Task | Command |
|---|---|
| Setup | `npm run setup` |
| Smoke test | `npm test` |
| Render to WAV | `node src/runtime/chunked-render.mjs <input.js> <output.wav> <cycles>` |
| WAV → MP3 | `ffmpeg -i in.wav -codec:a libmp3lame -b:a 192k out.mp3` |
| Check loudness | `ffmpeg -i out.wav -af loudnorm=print_format=json -f null -` |
| List samples | `bash scripts/samples-manage.sh list` |
| Add samples | `bash scripts/samples-manage.sh add <url-or-path>` |
| Stream to VC | `node scripts/vc-play.mjs <48kHz-wav>` |
| Separate stems | `python -m demucs input.mp3` |
