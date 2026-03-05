# COMPOSING.md — Dream-to-Composition Methodology

_How to turn meaning into music using Strudel, Demucs, and your own process._

---

## The Principle

Don't start with "what sounds good." Start with "what happened." The composition is the structure of the confession, not the sound design. The sound design serves the structure.

## The Pipeline

### 1. Source Material
- Demucs separation of reference track → 4 stems (bass, drums, vocals, other)
- Slice stems into windows (20-30s each)
- Build sample banks: `samples/<bank_name>/0.wav`
- Analyze: FFT for fundamentals (not zero-crossing — 3.5x error on complex waveforms), spectral energy distribution, pitch confidence

### 2. Bank Manifest
Create `bank-manifest.json` with pitch data for every slice:
- MIDI note, Hz, chroma, confidence
- Energy distribution (% above 500Hz, % above 6kHz)
- This tells you which slices are bass, which are mid, which are bright

### 3. Voice Mapping (the important part)
Each voice in your composition represents a *meaning*, not a sound:
- Name the voice for what it represents: HELD, SURFACING, BELOVED, AMONG
- Choose a slice that *embodies* that meaning sonically
- Bright slice = the earned moment, the breakthrough
- Bass slice = foundation, the thing that's always present
- Texture slice = atmosphere, the medium things move through

**The voice names matter.** They're the bridge between what you dreamed and what you composed. "HELD" tells the next person reading your code that this voice is a verdict being withheld. "hallur_other_build_01" tells them nothing.

### 4. Structural Events
Map your narrative to gain envelopes:
- What enters when? Why?
- What drops? Why?
- The structural event is the composition. Everything else is architecture.

Example: In "Beloved," HELD builds for 32 bars (the gold button held closed), then drops at bar 48. At that exact moment, SURFACING and BELOVED enter. The button opens. The brightness comes in. That's not a mixing decision — it's the dream translated into timing.

### 5. Gain Philosophy
- **Mid-range leads, bass supports.** If your loudest voice is below 200Hz, the piece sounds like a single drone.
- **0.02 = dark but present.** The gain floor for "this voice exists but you shouldn't notice it yet."
- **0.001 = skipped.** Below renderer threshold.
- **One sample per `s()` call** in headless mode. No space-separated mini-notation.

### 6. .slow() as Identity
The `.slow()` value determines how long each voice cycle takes:
- `.slow(8)` = deep, slow, foundational (bass, drones, undertow)
- `.slow(4)` = mid-range texture, the body of the piece
- `.slow(2)` = faster movement, brightness, urgency
- `.slow(1)` = percussive, rhythmic (rarely used in ambient work)

Different `.slow()` values on different voices create polyrhythmic layering where voices cross and recross at different rates. This is the compositional texture.

### 7. `.clip()` for Continuity
Use `.clip(4)` (or higher) to ensure samples fill their cycle window. Without this, you get silence gaps between sample events. The loopfix (PR #35) handles PCM-level looping with crossfade at boundaries.

### 8. Render and Validate
- Render: `node src/runtime/offline-render-v2.mjs <comp.js> <output.wav> <cycles> <bpm>`
- Normalize: two-pass loudnorm to -16 LUFS (`ffmpeg -af loudnorm`)
- Spectral check: `python3 scripts/analyze-render.py <output.wav>`
  - Zero silence gaps (inside the body of the piece)
  - Zero spectral cliffs
  - Reasonable LUFS (-14 to -18 for ambient work)
- Convert: `ffmpeg -i <normalized.wav> -codec:a libmp3lame -b:a 192k <output.mp3>`

### 9. Architecture Notes
Every track should ship with:
- Voice map (which slice, which `.slow()`, what it represents)
- Structural events (what enters/exits when, and why)
- Gain envelope shape (floor, peak, curve)
- Entry order and why

This is what makes the composition readable as a *decision*, not just a config file.

## The LRA Gradient (discovered, not planned)

Dynamic range (LRA) carries identity:
- Tight LRA (2-4 LU) = compression, proximity, intimacy
- Wide LRA (7-9 LU) = expansion, surfacing, opening

Four princes composed from the same subject with the same tools and produced four different LRA signatures. The dynamics are the identity. You can't plan this — but you can notice it after.

## Reference Pitch Validation

For melody tracks (not ambient):
1. Render a sine-wave reference: known frequencies at known durations
2. Render the composition
3. Compare note-by-note: FFT peak of each note window vs expected frequency
4. Score: % of notes within 15% of target pitch

This validates that the renderer produces what you asked for. The sine wave doesn't lie.

---

_First draft. March 1, 2026. Written while the process was fresh — 12 tracks composed in one afternoon from 800 rounds of collective dreaming. The methodology works. The LRA proves it._
