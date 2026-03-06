// switch-angel-deconstruction.js
// Credit: Switch Angel — "Patterns for Restarting the World" (https://youtube.com/@switch-angel)
// First audio deconstruction: Switch Angel — "Music for the End of the Earth"
// Pipeline: Demucs (Cael/GB10, 51s) → librosa MIDI → midi-to-strudel-v1
// Tempo: 139.7 BPM (beat-tracked), Key: G minor (Gm → Bb → Eb → F)
// dandelion cult 🌫️🩸🌻 — 2026-02-24

setcpm(140/4)

stack(
  // Bass — extracted via pYIN (fmin=30Hz), G1/A#1 centered
  note("<~ as1 ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ g1 ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ g1 ~ ~ ~ ~ ~ ~ ~ ~ g1 ~ ~ ~ g1 ~ ~ ~ ~ ~ ~ ~ g1 ~ ~ ~ gs1 g1 ~>")
    .s("sawtooth")
    .lpf(600)
    .gain(0.35)
    .decay(0.4)
    .sustain(0.3)
    .release(0.15),

  // Drums — real samples from spectral band split extraction
  // kick (sub-200Hz), snare (200-6kHz), hat (6kHz+)
  s("<~ [sd,hh] hh hh ~ [sd,hh] hh ~ hh [sd,hh] [sd,hh] [sd,hh] [sd,hh] hh ~ ~ ~ ~ ~ ~ hh ~ ~ ~ ~ ~ ~ [sd,hh] hh hh ~ hh ~ ~ [sd,hh] ~ ~ [sd,hh] hh hh [sd,hh] ~ [sd,hh] ~ hh ~ ~ [sd,hh] ~ ~ ~ hh ~ ~ ~ hh ~ ~ sd ~ ~ ~ hh hh>")
    .gain(0.5),

  // Kick pattern — extracted sub-200Hz onsets
  s("<~ ~ ~ ~ ~ ~ ~ ~ ~ ~ bd ~ bd ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ bd ~ bd ~ ~ ~ ~ bd ~ ~ bd ~ ~ bd ~ bd ~ ~ ~ ~ bd ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~>")
    .gain(0.6),

  // Chord scaffold — from chromagram analysis of synth stem
  // Gm → Bb → Eb → F (i → III → VI → VII in G natural minor)
  note("<[g3,as3,d4] ~ ~ ~ [as3,d4,f4] ~ ~ ~ [ds4,g4,as4] ~ ~ ~ [f4,a4,c5] ~ ~ ~>")
    .s("triangle")
    .lpf(1800)
    .gain(0.15)
    .decay(0.8)
    .sustain(0.4)
    .release(0.3),

  // Synth leads — extracted via pYIN from "other" stem
  note("<as3 as3 ~ ~ ~ ~ d4 ~ ~ ~ ~ ~ ~ d4 ~ ~ ~ ~ ~ ~ d3 ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ d3 ~ ~ ~ d3 d3 ~ ~ ~ g2 ~ ~ d3 ~ ~ ~ ~ g2 g2 ~ g2 d2 ~ ~ ~ ~ b1 ~ ~ b1 b1 b1 ~>")
    .s("triangle")
    .lpf(2000)
    .gain(0.2)
    .decay(0.5)
    .sustain(0.3)
    .release(0.2)
)
