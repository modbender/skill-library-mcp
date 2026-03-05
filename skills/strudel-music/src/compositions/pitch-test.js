// ============================================================================
// PITCH-SHIFT TEST
// ============================================================================
// Tests both pitch-shift modes:
//   1. Percussive (kick) — playback rate resampling, changes duration
//   2. Tonal (synth_lead, bass) — WSOLA time-stretch, preserves duration
//
// Each layer plays one note per cycle using <> angle brackets.
// At cpm=30 (cps=0.5), each cycle = 2 seconds.
// ============================================================================

samples({
  bass_Cs1: 'samples/bass_Cs1/',
  kick: 'samples/kick/',
  synth_lead: 'samples/synth_lead/',
})

setcpm(30)

stack(
  // Tonal: bass_Cs1 (root C#1/MIDI25) → notes cs1, a1, e1, cs1
  // Expected: no shift, +8st, +3st, no shift
  s("bass_Cs1")
    .note("<cs1 a1 e1 cs1>")
    .gain(0.7)
    .clip(1),

  // Tonal: synth_lead (root C4/MIDI60) → notes c3, e3, g3, c4
  // Expected: -12st, -8st, -5st, 0st
  s("synth_lead")
    .note("<c3 e3 g3 c4>")
    .gain(0.35)
    .clip(1),

  // Percussive: kick (root C3/MIDI60) → notes c3, e3, g3, c4
  // Expected: -12st, -8st, -5st, 0st (duration changes)
  s("kick")
    .note("<c3 e3 g3 c4>")
    .gain(0.5)
)
