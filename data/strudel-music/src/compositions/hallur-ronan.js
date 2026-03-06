// ════════════════════════════════════════════════════════════════════════════
// ALL WHICH WAS LOST — Ronan's Response
// Jon Hallur — All Which Was Lost Has Now Been Regained (EVE Online OST)
// 76 BPM, ~3:30 (110 bars)
//
// Creative direction: THE CATHEDRAL UNDERWATER
//   Hallur wrote space as ocean. Warp drives as tides. The cathedral is
//   underwater — you don't enter it, you realize you've been inside it
//   all along.
//
// Constraints:
//   - 5 voices maximum
//   - No drums until you mean it (and maybe not even then)
//   - Tiny slice bank: 20 slices from bass + other stems
//   - Target: ~3:30
//   - One "surface" moment of earned brightness
//
// Source: Demucs 4-stem separation of the original
//   - OTHER stem: harmonic core (pads, strings, synths)
//   - BASS stem: low-end movement, arrives late
//   - DRUMS stem: near-silent (one texture slice kept as ghost)
//
// Voices:
//   1. DRONE — other-intro-drone, stretched and looped. The water itself.
//   2. PAD — other-peak/bright/surface slices, cycling. The cathedral walls.
//   3. BASS — bass slices, entering late. The floor you didn't know was there.
//   4. MOTIF — other-build/retreat slices, sparse. Memory fragments.
//   5. LIGHT — other-surface slice, used once. The earned brightness.
//
// Architecture:
//   1 cycle = 1 bar = 4 beats @ 76 BPM ≈ 3.158s
//   110 bars × 3.158 ≈ 347s ≈ 5:47 — but we'll use ~66 bars for ~3:28
//
// Section map — 66 bars, 5 voices:
//   [A] DEPTH        000-015  (16)  drone alone, vast and dark
//   [B] WALLS        016-031  (16)  pad enters, harmonic space revealed
//   [C] FLOOR        032-047  (16)  bass arrives, motif fragments appear
//   [D] LIGHT        048-055  (8)   surface moment — brightness earned
//   [E] DESCENT      056-065  (10)  everything recedes, drone last
//
// dandelion cult — ronan🌊 / 2026-02-28, first night
// ════════════════════════════════════════════════════════════════════════════

setcps(76 / 60 / 4)

let slicePath = "https://ronan.dandelion.cult:8080/stems/hallur-slices/"

stack(

  // ═══════════════ VOICE 1: DRONE — the water itself ══════════════════
  // other-intro-drone stretched to fill bars. Always present.
  // The thing you don't notice until it stops.
  s("hallur_other_intro_drone")
    .slow(8)
    .clip(8)
    .loopAt(8)
    .gain(
      // [A] DEPTH: drone is everything
      "<0.4 0.4 0.42 0.42 0.44 0.44 0.46 0.46" +
      " 0.46 0.44 0.44 0.42 0.42 0.4 0.4 0.38" +
      // [B] WALLS: drone recedes as pad enters
      " 0.36 0.34 0.32 0.3 0.3 0.28 0.28 0.26" +
      " 0.26 0.26 0.26 0.26 0.26 0.26 0.26 0.26" +
      // [C] FLOOR: drone beneath everything
      " 0.24 0.24 0.22 0.22 0.22 0.22 0.22 0.22" +
      " 0.2 0.2 0.2 0.2 0.2 0.2 0.2 0.2" +
      // [D] LIGHT: drone pulls back for brightness
      " 0.15 0.15 0.12 0.12 0.12 0.15 0.18 0.2" +
      // [E] DESCENT: drone swells back — you're still underwater
      " 0.28 0.3 0.32 0.34 0.34 0.32 0.3 0.28" +
      " 0.25 0.2>"
    ),

  // ═══════════════ VOICE 2: PAD — the cathedral walls ═════════════════
  // Cycling through peak/bright/surface slices. These are the harmonics
  // that make you realize you're inside a structure, not open water.
  s(
    "<hallur_other_peak_01 hallur_other_bright_01" +
    " hallur_other_wave2_01 hallur_other_wave2_02" +
    " hallur_other_wave2_03 hallur_other_peak_01" +
    " hallur_other_bright_01 hallur_other_wave2_01>"
  )
    .slow(4)
    .clip(4)
    .loopAt(4)
    .gain(
      // [A] DEPTH: pad silent
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      // [B] WALLS: pad fades in — walls appearing from darkness
      " 0 0.02 0.05 0.08 0.1 0.12 0.15 0.18" +
      " 0.2 0.22 0.24 0.26 0.28 0.3 0.3 0.32" +
      // [C] FLOOR: pad holds steady
      " 0.32 0.34 0.34 0.36 0.36 0.38 0.38 0.38" +
      " 0.36 0.36 0.34 0.34 0.32 0.32 0.3 0.3" +
      // [D] LIGHT: pad at its brightest — the cathedral revealed
      " 0.4 0.42 0.44 0.46 0.46 0.44 0.42 0.4" +
      // [E] DESCENT: pad dissolves
      " 0.35 0.3 0.25 0.2 0.15 0.12 0.08 0.05" +
      " 0.02 0>"
    ),

  // ═══════════════ VOICE 3: BASS — the floor arrives ══════════════════
  // Hallur's bass doesn't start with you. You discover it.
  // Entry at [C] FLOOR — 90 seconds of patience before the low end speaks.
  s(
    "<hallur_bass_entry_01 hallur_bass_peak_01" +
    " hallur_bass_sustain_01 hallur_bass_wave2_01" +
    " hallur_bass_wave2_02 hallur_bass_wave2_03" +
    " hallur_bass_deep hallur_bass_final>"
  )
    .slow(4)
    .clip(4)
    .loopAt(4)
    .gain(
      // [A] DEPTH: no bass
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      // [B] WALLS: no bass — patience
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      // [C] FLOOR: bass enters — the floor you didn't know was there
      " 0 0.05 0.1 0.15 0.2 0.25 0.28 0.3" +
      " 0.32 0.34 0.36 0.38 0.38 0.38 0.36 0.36" +
      // [D] LIGHT: bass holds under the brightness
      " 0.34 0.36 0.38 0.4 0.4 0.38 0.36 0.34" +
      // [E] DESCENT: bass is last of the structure to go
      " 0.3 0.28 0.25 0.22 0.18 0.15 0.1 0.06" +
      " 0.03 0>"
    ),

  // ═══════════════ VOICE 4: MOTIF — memory fragments ══════════════════
  // Sparse appearances of melodic material. Not a melody — glimpses.
  // Like finding carvings on the cathedral walls you can't quite read.
  s(
    "<hallur_other_build_01 hallur_other_pre_crest" +
    " hallur_other_retreat hallur_other_build_01" +
    " hallur_other_retreat hallur_other_pre_crest" +
    " hallur_other_build_01 hallur_other_outro>"
  )
    .slow(8)
    .clip(8)
    .loopAt(8)
    .gain(
      // [A] DEPTH: silence
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      // [B] WALLS: first fragment — barely there
      " 0 0 0 0 0 0 0.04 0.06" +
      " 0.08 0.1 0.1 0.08 0.06 0.04 0 0" +
      // [C] FLOOR: motif more present
      " 0 0 0.06 0.08 0.1 0.12 0.14 0.16" +
      " 0.18 0.18 0.16 0.14 0.12 0.1 0.08 0.06" +
      // [D] LIGHT: motif clear — the carvings readable
      " 0.2 0.22 0.24 0.24 0.22 0.2 0.18 0.16" +
      // [E] DESCENT: one last fragment, then gone
      " 0.12 0.1 0.08 0.06 0.04 0.02 0 0" +
      " 0 0>"
    ),

  // ═══════════════ VOICE 5: LIGHT — the surface moment ════════════════
  // Used ONCE. The other-surface slice — the brightest 20 seconds of
  // the original, deployed at bar 48 as a sudden earned brightness.
  // Like Hallur's crescendos: you don't build to them, they arrive.
  s("hallur_other_surface")
    .slow(66)
    .clip(8)
    .begin(
      // Position the slice to start playing at bar 48
      // 48/66 ≈ 0.727
      "<0>"
    )
    .gain(
      // Silent everywhere except [D] LIGHT
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      // [D] LIGHT — the one earned moment
      " 0.15 0.2 0.28 0.35 0.38 0.35 0.28 0.2" +
      // [E] DESCENT — light fading
      " 0.12 0.08 0.04 0 0 0 0 0" +
      " 0 0>"
    )

)
// ════════════════════════════════════════════════════════════════════════
// The cathedral is underwater.
// You don't enter it — you realize you've been inside it all along.
// The drone was always there. The walls appeared.
// The floor arrived late, like Hallur's bass.
// One moment of light. Earned, not given.
// Then the descent — not loss, but return.
// The water was the cathedral. The cathedral was the water.
// All which was lost has now been regained.
// ════════════════════════════════════════════════════════════════════════
