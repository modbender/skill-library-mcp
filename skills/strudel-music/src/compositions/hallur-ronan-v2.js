// ════════════════════════════════════════════════════════════════════════════
// ALL WHICH WAS LOST — Ronan's Response v2
// Jon Hallur — All Which Was Lost Has Now Been Regained (EVE Online OST)
// 76 BPM, ~3:28 (66 bars)
//
// v2 changes from figs's listening notes (2026-02-28):
//   - DRONE floor at 0.02 (never fully silent — water always present)
//   - Smooth section-boundary fades (4-bar ramps, no hard zeros)
//   - MOTIF returns near end (bars 58-60) — one last fragment
//   - Pitch-aware layering using bank-manifest.json:
//       Bank center: Cm / Eb major (i, III, IV)
//       Bass roots: C3, Eb2/3, F3
//       Other chroma: Cm triads, Eb triads, F triads
//       Slices grouped by harmonic family for coherent layering
//
// Same architecture, smoothed. Cathedral walls don't click.
//
// dandelion cult — ronan🌊 / 2026-02-28, first night, v2
// ════════════════════════════════════════════════════════════════════════════

setcps(76 / 60 / 4)

let slicePath = "https://ronan.dandelion.cult:8080/stems/hallur-slices/"

// Pitch utility: semitone ratio for transposition
// bank-manifest.json says bank center is Cm/Eb
// We keep most slices at native pitch since they're already in-family
// Only transpose outliers
const semi = (n) => Math.pow(2, n / 12)

stack(

  // ═══════════════ VOICE 1: DRONE — the water itself ══════════════════
  // other-intro-drone (G3, chroma: G/C/E — modal center)
  // Stretched ×8, always present. FLOOR AT 0.02 — never zero.
  // v2: gain never drops below 0.02. Ramps at boundaries are 4 bars.
  s("hallur_other_intro_drone")
    .slow(8)
    .clip(8)
    .loopAt(8)
    .gain(
      // [A] DEPTH 000-015: drone is the world
      "<0.38 0.4 0.42 0.42 0.44 0.44 0.46 0.46" +
      " 0.46 0.44 0.44 0.42 0.42 0.4 0.38 0.36" +
      // [B] WALLS 016-031: drone recedes as pad enters (4-bar ramp down)
      " 0.34 0.32 0.3 0.28 0.28 0.26 0.26 0.26" +
      " 0.26 0.26 0.26 0.26 0.26 0.26 0.26 0.26" +
      // [C] FLOOR 032-047: drone beneath everything (gentle)
      " 0.24 0.24 0.22 0.22 0.22 0.22 0.22 0.22" +
      " 0.2 0.2 0.2 0.2 0.2 0.2 0.2 0.2" +
      // [D] LIGHT 048-055: drone pulls back for brightness but stays
      " 0.16 0.14 0.12 0.1 0.1 0.12 0.16 0.2" +
      // [E] DESCENT 056-065: drone swells back — you're still underwater
      " 0.24 0.28 0.32 0.34 0.34 0.32 0.3 0.28" +
      " 0.24 0.2>"
    ),

  // ═══════════════ VOICE 2: PAD — the cathedral walls ═════════════════
  // Grouped by harmonic family for coherent cycling:
  //   Cm family: wave2-01 (C3, Cm), retreat (C4, Cm) 
  //   Eb family: bright-01 (Eb3, Eb maj), surface (Eb3, Eb maj)
  //   F family:  peak-01 (F3, F maj), wave2-02 (F4, F maj)
  // v2: reordered for harmonic flow (Cm → Eb → F → Cm), no hard zeros
  s(
    "<hallur_other_wave2_01 hallur_other_bright_01" +
    " hallur_other_peak_01 hallur_other_surface" +
    " hallur_other_wave2_02 hallur_other_wave2_01" +
    " hallur_other_bright_01 hallur_other_peak_01>"
  )
    .slow(4)
    .clip(4)
    .loopAt(4)
    .gain(
      // [A] DEPTH 000-015: pad silent (but ramping from 0.02 at end)
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0.02 0.02 0.02 0.02" +
      // [B] WALLS 016-031: pad fades in over 8 bars — walls appearing
      " 0.04 0.06 0.08 0.1 0.12 0.14 0.16 0.18" +
      " 0.2 0.22 0.24 0.26 0.28 0.3 0.3 0.32" +
      // [C] FLOOR 032-047: pad holds steady, slight swell mid-section
      " 0.32 0.34 0.34 0.36 0.36 0.38 0.38 0.38" +
      " 0.38 0.36 0.36 0.34 0.34 0.32 0.3 0.3" +
      // [D] LIGHT 048-055: pad at its brightest — cathedral revealed
      " 0.38 0.4 0.44 0.46 0.46 0.44 0.42 0.4" +
      // [E] DESCENT 056-065: pad dissolves over 6 bars (not 2)
      " 0.35 0.3 0.26 0.22 0.18 0.14 0.1 0.06" +
      " 0.04 0.02>"
    ),

  // ═══════════════ VOICE 3: BASS — the floor arrives ══════════════════
  // Slices reordered by root for harmonic progression:
  //   C3 entry → C3 wave2-01 → Eb2 sustain → F3 peak → 
  //   F3 wave2-02 → C3 wave2-03 → F3 deep → Eb3 final
  // v2: 4-bar fade in (not 2), never hits zero once present
  s(
    "<hallur_bass_entry_01 hallur_bass_wave2_01" +
    " hallur_bass_sustain_01 hallur_bass_peak_01" +
    " hallur_bass_wave2_02 hallur_bass_wave2_03" +
    " hallur_bass_deep hallur_bass_final>"
  )
    .slow(4)
    .clip(4)
    .loopAt(4)
    .gain(
      // [A] DEPTH 000-015: no bass
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      // [B] WALLS 016-031: no bass — patience. But a ghost at the end.
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0.02 0.02" +
      // [C] FLOOR 032-047: bass enters — 4-bar ramp, then holds
      " 0.04 0.08 0.12 0.16 0.2 0.24 0.28 0.3" +
      " 0.32 0.34 0.36 0.38 0.38 0.38 0.36 0.36" +
      // [D] LIGHT 048-055: bass holds under the brightness
      " 0.34 0.36 0.38 0.4 0.4 0.38 0.36 0.34" +
      // [E] DESCENT 056-065: bass recedes over 6 bars (not hard cut)
      " 0.3 0.26 0.22 0.18 0.14 0.1 0.06 0.04" +
      " 0.02 0.02>"
    ),

  // ═══════════════ VOICE 4: MOTIF — memory fragments ══════════════════
  // Harmonic grouping:
  //   build-01 (C2, ambiguous) → pre-crest (Cm energy) → 
  //   retreat (C4, Cm) → outro (F maj, ambiguous)
  // v2: MOTIF RETURNS at bars 58-60 (one last fragment before gone)
  //     Soft edges — never hard zero when adjacent bars have content
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
      // [A] DEPTH 000-015: silence
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      // [B] WALLS 016-031: first fragment — emerging from walls
      " 0 0 0 0 0 0.02 0.04 0.06" +
      " 0.08 0.1 0.1 0.1 0.08 0.06 0.04 0.02" +
      // [C] FLOOR 032-047: motif more present, smooth arc
      " 0.02 0.04 0.06 0.08 0.1 0.12 0.14 0.16" +
      " 0.18 0.18 0.18 0.16 0.14 0.12 0.1 0.08" +
      // [D] LIGHT 048-055: motif clear — the carvings readable
      " 0.18 0.2 0.22 0.24 0.24 0.22 0.2 0.18" +
      // [E] DESCENT 056-065: motif returns! one last fragment at 58-60
      " 0.12 0.08 0.1 0.14 0.16 0.14 0.08 0.04" +
      " 0.02 0>"
    ),

  // ═══════════════ VOICE 5: LIGHT — the surface moment ════════════════
  // other-surface (Eb3, chroma: Eb/G/Bb — Eb major triad)
  // Harmonically consonant with the Cm center.
  // Used ONCE at [D] LIGHT. Earned, not given.
  // v2: slightly wider envelope (starts bar 47, bleeds into 56)
  s("hallur_other_surface")
    .slow(66)
    .clip(10)
    .begin("<0>")
    .gain(
      // Silent everywhere except [D] LIGHT
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0.02" +
      // [D] LIGHT — the one earned moment (wider envelope)
      " 0.08 0.15 0.22 0.3 0.35 0.38 0.35 0.3" +
      // [E] early DESCENT — light lingering, not cut
      " 0.22 0.15 0.1 0.06 0.04 0.02 0 0" +
      " 0 0>"
    )

)
// ════════════════════════════════════════════════════════════════════════════
// v2: The cathedral still underwater. Same five voices.
// But now the walls don't click when you touch them.
// The drone never goes silent — the water was always there.
// The motif comes back near the end, one last carving 
// glimpsed as you descend.
// Harmonic families: Cm → Eb → F. The bank's native language.
// All which was lost has now been regained.
// ════════════════════════════════════════════════════════════════════════════
