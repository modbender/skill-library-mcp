// ============================================================================
// BLOOM — Full-Length Elliott Composition
// Cosmic Gate & Pretty Pink [Black Hole Recordings]
// ============================================================================
// D minor, 126 BPM. 96-bar trance arrangement (~3:03).
//
// Structure (96 bars):
//   Intro     (bars  1-16):  kick builds, hi-hat enters, percussion layers
//   Build     (bars 17-32):  bass enters on D2/D1 pulse, lead teases
//   Breakdown (bars 33-40):  strip to lead melody, no kick
//   Drop      (bars 41-56):  full energy — all drums + bass + lead
//   2nd Build (bars 57-72):  variation, new lead pattern
//   Peak      (bars 73-88):  maximum density, all elements
//   Outro     (bars 89-96):  elements strip away
//
// Chord progression: Dm → Bb → C → Gm (i → VI → VII → iv)
// 4 bars per chord, cycling every 16 bars.
//
// Gain budget: 8 voices max, per-voice 0.08–0.15 to avoid clipping.
// All multi-value patterns use <> angle brackets (slowcat).
// ============================================================================

// --- TEMPO: 126 BPM ---
setcps(126/60/4)

// ============================================================================
// HELPER: bar-level gain envelopes
// Each <> value = one bar. 96 values total for 96 bars.
// ============================================================================

stack(
  // ========================================================================
  // LAYER 1: KICK — four-on-the-floor trance kick
  // Intro: gradual entry from bar 1, out during breakdown (33-40), full at drop
  // ========================================================================
  s("bloom_kick")
    .struct("x ~ ~ ~ x ~ ~ ~ x ~ ~ ~ x ~ ~ ~")
    .gain("<0.06 0.07 0.08 0.08 0.09 0.09 0.10 0.10 0.10 0.10 0.11 0.11 0.11 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.13 0.13 0.13 0.13 0.13 0.13 0 0 0 0 0 0 0 0 0.13 0.13 0.13 0.13 0.13 0.13 0.13 0.13 0.13 0.13 0.13 0.13 0.14 0.14 0.14 0.14 0.13 0.13 0.13 0.13 0.13 0.13 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.15 0.15 0.15 0.15 0.15 0.15 0.15 0.15 0.12 0.10 0.08 0.06 0.05 0.04 0.03 0.02>"),

  // ========================================================================
  // LAYER 2: SNARE — beats 2 and 4 (offbeat)
  // Enters at bar 9, out during breakdown, full at drop
  // ========================================================================
  s("bloom_snare")
    .struct("~ ~ ~ ~ x ~ ~ ~ ~ ~ ~ ~ x ~ ~ ~")
    .gain("<0 0 0 0 0 0 0 0 0.06 0.06 0.07 0.07 0.08 0.08 0.08 0.08 0.09 0.09 0.09 0.09 0.09 0.09 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0 0 0 0 0 0 0 0 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.08 0.06 0.04 0.03 0.02 0 0 0>"),

  // ========================================================================
  // LAYER 3: HI-HAT (bloom_mid_perc) — 16th-note pattern
  // Enters at bar 5, dynamic accents on upbeats
  // ========================================================================
  s("bloom_mid_perc")
    .struct("x x x x x x x x x x x x x x x x")
    .gain("0.04 0.02 0.05 0.02 0.04 0.02 0.05 0.02 0.04 0.02 0.05 0.02 0.04 0.02 0.05 0.02")
    .mask("<0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0>"),

  // ========================================================================
  // LAYER 4: PERCUSSION (bloom_mid_perc1) — offbeat groove
  // Enters at bar 13, syncopated pattern
  // ========================================================================
  s("bloom_mid_perc1")
    .struct("~ ~ x ~ ~ ~ x ~ ~ x ~ ~ ~ ~ x ~")
    .gain(0.06)
    .mask("<0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0>"),

  // ========================================================================
  // LAYER 5: PERCUSSION 2 (bloom_mid_perc2) — extra ride/texture
  // Enters at peak section, adds density
  // ========================================================================
  s("bloom_mid_perc2")
    .struct("~ x ~ x ~ x ~ x ~ x ~ x ~ x ~ x")
    .gain(0.04)
    .mask("<0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0>"),

  // ========================================================================
  // LAYER 6: BASS — D minor progression (Dm → Bb → C → Gm)
  // 8th-note pulse. Each chord lasts 4 bars. Cycle = 16 bars.
  // Uses native-pitch samples: D2, As1(=Bb), C1, G1
  // Enters at bar 17 (Build section)
  // ========================================================================
  s("<bloom_bass_D2*8 bloom_bass_D2*8 bloom_bass_D2*8 bloom_bass_D2*8 bloom_bass_As1*8 bloom_bass_As1*8 bloom_bass_As1*8 bloom_bass_As1*8 bloom_bass_C1*8 bloom_bass_C1*8 bloom_bass_C1*8 bloom_bass_C1*8 bloom_bass_G1*8 bloom_bass_G1*8 bloom_bass_G1*8 bloom_bass_G1*8>")
    .gain("<0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.06 0.07 0.08 0.08 0.09 0.09 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.11 0.11 0.08 0.07 0.06 0.05 0.04 0.04 0.03 0.03 0.11 0.11 0.11 0.11 0.11 0.11 0.11 0.11 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.11 0.11 0.11 0.11 0.11 0.11 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.13 0.13 0.13 0.13 0.13 0.13 0.13 0.13 0.13 0.13 0.13 0.13 0.14 0.14 0.14 0.14 0.10 0.08 0.06 0.04 0.02 0 0 0>"),

  // ========================================================================
  // LAYER 7: BASS OCTAVE — D1 root reinforcement on downbeats
  // Adds weight at drop/peak sections. Quarter-note pulse.
  // ========================================================================
  s("bloom_bass_D1")
    .struct("x ~ ~ ~ ~ ~ ~ ~ x ~ ~ ~ ~ ~ ~ ~")
    .gain("<0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.08 0.08 0.08 0.08 0.08 0.08 0.08 0.08 0.08 0.08 0.09 0.09 0.09 0.09 0.09 0.09 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.09 0.09 0.09 0.09 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.06 0.04 0.02 0 0 0 0 0>"),

  // ========================================================================
  // LAYER 8: LEAD MELODY — D minor melodic phrases
  // Melody: D F E D C A Bb D (classic trance Dm motif)
  // All notes use native-pitch samples where available.
  //
  // Phase A (Build tease, bars 25-32): simple D-F motif, quiet
  // Phase B (Breakdown, bars 33-40): full melody exposed
  // Phase C (Drop, bars 41-56): melody with full energy
  // Phase D (2nd Build / Peak, bars 57-88): extended melody variation
  // ========================================================================

  // --- Lead Phase A: Tease (bars 25-32, 8 bars) ---
  s("<bloom_lead_D3 bloom_lead_D3 bloom_lead_F3 bloom_lead_F3 bloom_lead_E3 bloom_lead_E3 bloom_lead_D3 bloom_lead_D3>")
    .gain("<0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.04 0.05 0.06 0.07 0.08 0.08 0.09 0.09 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0>"),

  // --- Lead Phase B: Breakdown melody (bars 33-40, 8 bars) ---
  // Full motif: D3 → F3 → E3 → D3 → C3 → A2 → As2 → D3
  s("<bloom_lead_D3 bloom_lead_F3 bloom_lead_E3 bloom_lead_D3 bloom_lead_C3 bloom_lead_A2 bloom_lead_As2 bloom_lead_D3>")
    .gain("<0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.10 0.11 0.12 0.13 0.13 0.12 0.11 0.10 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0>"),

  // --- Lead Phase C: Drop melody (bars 41-56, 16 bars = 2x motif) ---
  // Same 8-note motif cycling twice over the drop
  s("<bloom_lead_D3 bloom_lead_F3 bloom_lead_E3 bloom_lead_D3 bloom_lead_C3 bloom_lead_A2 bloom_lead_As2 bloom_lead_D3 bloom_lead_D3 bloom_lead_F3 bloom_lead_E3 bloom_lead_D3 bloom_lead_C3 bloom_lead_A2 bloom_lead_As2 bloom_lead_D3>")
    .gain("<0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.10 0.11 0.11 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.11 0.11 0.10 0.10 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0>"),

  // --- Lead Phase D: 2nd Build + Peak variation (bars 57-88, 32 bars) ---
  // New pattern: ascending motif D3 → E3 → F3 → G2(octave up feel) → A2 → As2 → C3 → D3
  // Then descending: D3 → C3 → As2 → A2 → G2 → F3 → E3 → D3
  // 16 bars ascending + 16 bars descending = 32 bars
  s("<bloom_lead_D3 bloom_lead_E3 bloom_lead_F3 bloom_lead_G2 bloom_lead_A2 bloom_lead_As2 bloom_lead_C3 bloom_lead_D3 bloom_lead_D3 bloom_lead_E3 bloom_lead_F3 bloom_lead_G2 bloom_lead_A2 bloom_lead_As2 bloom_lead_C3 bloom_lead_D3 bloom_lead_D3 bloom_lead_C3 bloom_lead_As2 bloom_lead_A2 bloom_lead_G2 bloom_lead_F3 bloom_lead_E3 bloom_lead_D3 bloom_lead_D3 bloom_lead_C3 bloom_lead_As2 bloom_lead_A2 bloom_lead_G2 bloom_lead_F3 bloom_lead_E3 bloom_lead_D3>")
    .gain("<0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.08 0.09 0.10 0.10 0.11 0.11 0.12 0.12 0.12 0.12 0.12 0.12 0.13 0.13 0.13 0.13 0.13 0.13 0.13 0.13 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0 0 0 0 0 0 0 0>"),

  // ========================================================================
  // LAYER 9: PAD TEXTURE — sustained lead as pad (D3 root)
  // Slow whole-note D3 sustained across bars for atmosphere
  // Present in breakdown and underneath peak
  // ========================================================================
  s("bloom_lead_D3")
    .slow(4)
    .gain("<0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.06 0.07 0.08 0.09 0.09 0.08 0.07 0.06 0.04 0.04 0.04 0.04 0.04 0.04 0.04 0.04 0.04 0.04 0.04 0.04 0.04 0.04 0.04 0.04 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.06 0.06 0.06 0.06 0.06 0.06 0.06 0.06 0.06 0.06 0.06 0.06 0.06 0.06 0.06 0.06 0.04 0.03 0.02 0.01 0 0 0 0>")
)
