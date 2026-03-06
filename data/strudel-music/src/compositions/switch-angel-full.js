// switch-angel-full.js
// Credit: Switch Angel — "Patterns for Restarting the World" (https://youtube.com/@switch-angel)
// Full deconstruction: Switch Angel — "Music for the End of the Earth" (4:19)
// Pipeline: Demucs (Cael/GB10, 82s) → librosa MIDI → hand-assembled from extraction data
// Tempo: 156.6 BPM, Key: F# major / Eb minor
// dandelion cult 🌫️🩸🌻 — 2026-02-24

setcpm(157/4)

stack(
  // Bass — C#2/D2/C2/B1/F#1 centered (F# major territory)
  note("<cs2 ~ d2 ~ c2 ~ b1 ~ fs1 ~ cs2 ~ d2 ~ b1 ~ cs2 d2 ~ cs2 ~ b1 ~ ~ c2 ~ d2 ~ cs2 ~ ~ ~ ~ fs1 cs2 ~ ~ ~ b1 ~ ~ ~ ~ d2 ~ cs2 ~ ~>")
    .s("sawtooth")
    .lpf(500)
    .gain(0.35)
    .decay(0.35)
    .sustain(0.25)
    .release(0.1),

  // Kick — from sub-200Hz onsets (406 hits across 4:19)
  s("<bd ~ ~ ~ bd ~ ~ ~ bd ~ ~ ~ bd ~ ~ ~ bd ~ ~ ~ ~ ~ bd ~ bd ~ ~ ~ ~ ~ bd ~ ~ ~ bd ~ ~ bd ~ ~ ~ ~ bd ~ ~ ~ bd ~ ~ ~>")
    .gain(0.55),

  // Snare + hat pattern — from spectral band split
  s("<~ [sd,hh] hh hh ~ [sd,hh] hh ~ hh [sd,hh] hh [sd,hh] hh hh ~ hh ~ hh ~ hh [sd,hh] ~ hh ~ hh ~ [sd,hh] hh hh ~ hh ~ hh hh ~ [sd,hh] ~ hh hh [sd,hh] ~ hh ~ ~ hh hh>")
    .gain(0.4),

  // Chord scaffold — F# major: F#→A#m→D#m→B→C#
  note("<[fs3,as3,cs4] ~ ~ ~ [as3,cs4,f4] ~ ~ ~ [ds3,fs3,as3] ~ ~ ~ [b3,ds4,fs4] ~ [cs4,f4,gs4] ~>")
    .s("triangle")
    .lpf(1600)
    .gain(0.12)
    .decay(0.9)
    .sustain(0.35)
    .release(0.3),

  // Synth leads — D#2/B1/F#2 from "other" stem
  note("<ds2 ~ ~ b1 ~ ~ fs2 ~ ~ d2 ~ cs2 ~ ~ ~ ~ ~ b1 ~ ds2 ~ ~ ~ fs2 ~ d2 ~ ~ cs2 ~ ~ ~>")
    .s("triangle")
    .lpf(2200)
    .gain(0.18)
    .decay(0.5)
    .sustain(0.3)
    .release(0.2)
)
