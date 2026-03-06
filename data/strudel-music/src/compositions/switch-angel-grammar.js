// switch-angel-grammar.js
// Credit: Switch Angel — "Patterns for Restarting the World" (https://youtube.com/@switch-angel)
// Grammar-extracted composition from Switch Angel "Music for the End of the Earth"
// NOT a note sequence — a generative pattern derived from statistical analysis
// Tempo: 157 BPM, Key: F# major / pentatonic-adjacent
// dandelion cult 🌫️🩸🌻 — 2026-02-24
//
// Statistical DNA (Cael/GB10 extraction):
//   Bass: 94.6% stepwise, C#/D/F#/C/B emphasis, 75% 32nd note granular
//   Drums: hat-dominant (49%), no downbeat emphasis, density builds
//   Synths: D#/B/F#/C#/D/E pentatonic, 81% stepwise, cyclical density

setcpm(157/4)

stack(
  // Bass — granular stepwise motion in F# major
  // 94.6% stepwise = almost never leaps, 75% 32nd = rapid texture
  note("cs2 d2 cs2 c2 b1 cs2 d2 cs2 fs1 cs2 d2 c2 b1 cs2 d2 b1")
    .s("sawtooth")
    .lpf(500)
    .gain(0.3)
    .decay(0.15)
    .sustain(0.1)
    .release(0.05),

  // Drums — hat-dominant, uniform subdivision, density building
  // 49% hat, 35% snare, 16% kick — no downbeat emphasis
  s("hh hh [sd,hh] hh hh hh [sd,hh] hh hh [sd,hh] hh hh hh [sd,hh] hh hh")
    .gain(0.35),

  // Kick — sparse, not on downbeats (anti-grid)
  s("~ ~ ~ bd ~ ~ ~ ~ ~ ~ bd ~ ~ ~ ~ bd")
    .gain(0.5),

  // Synths — D#/B/F#/C#/D pentatonic, stepwise, drone-like
  // Cyclical density: breathes in/out rather than building
  note("<ds2 b1 fs2 cs2 d2 ~ ~ ~ b1 ds2 ~ cs2 ~ ~ d2 ~ ~ ~ ~ fs2 ds2 ~ b1 ~ cs2 ~ ~ ~ d2 ~ ~ ~>")
    .s("triangle")
    .lpf(1800)
    .gain(0.15)
    .decay(0.7)
    .sustain(0.4)
    .release(0.3),

  // Pad — sustained chords from the harmonic field
  // F# major: F#/A#/C# → B/D#/F# → cycling
  note("<[fs3,as3,cs4] ~ ~ ~ ~ ~ ~ ~ [b3,ds4,fs4] ~ ~ ~ ~ ~ ~ ~>")
    .s("triangle")
    .lpf(1200)
    .gain(0.08)
    .decay(1.2)
    .sustain(0.5)
    .release(0.5)
)
